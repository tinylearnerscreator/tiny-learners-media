"""SQLite post queue shared by the MCP server and the background worker.

Each row is one video going to one platform. Rows that belong to the same
request share a group_id. Workers claim rows with a time-limited lease so the
MCP server's in-process worker and the Windows scheduled-task worker never
upload the same post twice, and a crashed upload is picked up again once its
lease expires.
"""

from __future__ import annotations

import json
import os
import socket
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS posts (
    id            TEXT PRIMARY KEY,
    group_id      TEXT NOT NULL,
    platform      TEXT NOT NULL,          -- youtube | tiktok
    source        TEXT NOT NULL,          -- path, Drive link, or URL as given
    options       TEXT NOT NULL,          -- JSON: metadata + platform settings
    status        TEXT NOT NULL,          -- see STATUSES
    run_after     TEXT,                   -- ISO UTC; worker waits until then
    progress      REAL DEFAULT 0,         -- 0..1 upload progress
    detail        TEXT DEFAULT '',        -- human-readable last step / error
    local_file    TEXT,                   -- prepared file actually uploaded
    resume        TEXT,                   -- JSON: resumable session state
    result        TEXT,                   -- JSON: platform ids / urls
    attempts      INTEGER DEFAULT 0,
    lease_owner   TEXT,
    lease_until   TEXT,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS posts_group ON posts(group_id);
CREATE INDEX IF NOT EXISTS posts_status ON posts(status);
"""

# draft     -> created, waiting for the user's approval (nothing uploaded)
# queued    -> approved; worker will run it once run_after has passed
# working   -> a worker holds the lease and is preparing/uploading
# processing-> uploaded; platform is still processing (poll for final state)
# done      -> finished (published, scheduled on YouTube, or in TikTok inbox)
# failed    -> gave up; detail has the reason
# cancelled -> user cancelled before it ran
STATUSES = ("draft", "queued", "working", "processing", "done", "failed", "cancelled")
MAX_ATTEMPTS = 5
LEASE_MINUTES = 10


def now() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds")


def worker_id() -> str:
    return f"{socket.gethostname()}:{os.getpid()}"


class Store:
    def __init__(self, db_file: Path):
        self.db_file = db_file
        with self._conn() as c:
            c.executescript(SCHEMA)

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.db_file, timeout=30, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        try:
            yield conn
        finally:
            conn.close()

    # -- creation -----------------------------------------------------------------
    def create(self, group_id: str, platform: str, source: str, options: dict,
               run_after: datetime | None) -> str:
        pid = uuid.uuid4().hex[:10]
        ts = iso(now())
        with self._conn() as c:
            c.execute(
                "INSERT INTO posts (id, group_id, platform, source, options, status, run_after,"
                " created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?)",
                (pid, group_id, platform, source, json.dumps(options), "draft",
                 iso(run_after) if run_after else None, ts, ts),
            )
        return pid

    # -- reads --------------------------------------------------------------------
    def get(self, post_id: str) -> dict | None:
        with self._conn() as c:
            row = c.execute("SELECT * FROM posts WHERE id=?", (post_id,)).fetchone()
        return _row(row) if row else None

    def group(self, group_id: str) -> list[dict]:
        with self._conn() as c:
            rows = c.execute("SELECT * FROM posts WHERE group_id=? ORDER BY platform DESC",
                             (group_id,)).fetchall()
        return [_row(r) for r in rows]

    def find(self, ident: str) -> list[dict]:
        """Accept either a post id or a group id."""
        one = self.get(ident)
        return [one] if one else self.group(ident)

    def recent(self, limit: int = 20, status: str | None = None) -> list[dict]:
        q, args = "SELECT * FROM posts", []
        if status:
            q += " WHERE status=?"
            args.append(status)
        q += " ORDER BY created_at DESC LIMIT ?"
        args.append(limit)
        with self._conn() as c:
            return [_row(r) for r in c.execute(q, args).fetchall()]

    # -- state changes ------------------------------------------------------------
    def update(self, post_id: str, **fields) -> None:
        for k in ("options", "resume", "result"):
            if k in fields and not isinstance(fields[k], (str, type(None))):
                fields[k] = json.dumps(fields[k])
        fields["updated_at"] = iso(now())
        cols = ", ".join(f"{k}=?" for k in fields)
        with self._conn() as c:
            c.execute(f"UPDATE posts SET {cols} WHERE id=?", (*fields.values(), post_id))

    def approve_group(self, group_id: str) -> int:
        with self._conn() as c:
            cur = c.execute(
                "UPDATE posts SET status='queued', updated_at=? WHERE group_id=? AND status='draft'",
                (iso(now()), group_id))
            return cur.rowcount

    def cancel(self, ident: str) -> int:
        with self._conn() as c:
            cur = c.execute(
                "UPDATE posts SET status='cancelled', updated_at=? WHERE (id=? OR group_id=?)"
                " AND status IN ('draft','queued')", (iso(now()), ident, ident))
            return cur.rowcount

    def retry(self, ident: str) -> int:
        with self._conn() as c:
            cur = c.execute(
                "UPDATE posts SET status='queued', attempts=0, lease_owner=NULL, lease_until=NULL,"
                " updated_at=? WHERE (id=? OR group_id=?) AND status='failed'",
                (iso(now()), ident, ident))
            return cur.rowcount

    def claim(self, owner: str) -> dict | None:
        """Atomically take the next due job (queued/processing, or a working job
        whose previous worker died)."""
        t = iso(now())
        lease = iso(now() + timedelta(minutes=LEASE_MINUTES))
        with self._conn() as c:
            c.execute("BEGIN IMMEDIATE")
            row = c.execute(
                "SELECT id FROM posts WHERE ("
                "  status IN ('queued','processing') OR"
                "  (status='working' AND (lease_until IS NULL OR lease_until < ?))"
                ") AND (run_after IS NULL OR run_after <= ?)"
                " AND (lease_until IS NULL OR lease_until < ?)"
                " ORDER BY created_at LIMIT 1", (t, t, t)).fetchone()
            if not row:
                c.execute("COMMIT")
                return None
            c.execute("UPDATE posts SET lease_owner=?, lease_until=?, updated_at=? WHERE id=?",
                      (owner, lease, t, row["id"]))
            c.execute("COMMIT")
        return self.get(row["id"])

    def heartbeat(self, post_id: str, owner: str) -> None:
        with self._conn() as c:
            c.execute("UPDATE posts SET lease_until=? WHERE id=? AND lease_owner=?",
                      (iso(now() + timedelta(minutes=LEASE_MINUTES)), post_id, owner))

    def release(self, post_id: str, **fields) -> None:
        self.update(post_id, lease_owner=None, lease_until=None, **fields)


def _row(row: sqlite3.Row) -> dict:
    d = dict(row)
    for k in ("options", "resume", "result"):
        d[k] = json.loads(d[k]) if d.get(k) else None
    return d
