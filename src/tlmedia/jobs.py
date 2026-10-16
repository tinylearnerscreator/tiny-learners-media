"""Draft -> approve -> prepare -> upload -> confirm pipeline.

Nothing is uploaded until the user approves a draft. Approved jobs are run by
whichever worker claims them first: the thread inside the MCP server (so
posting starts immediately) or the Windows scheduled task (so scheduled and
interrupted posts still go out when Claude is closed).
"""

from __future__ import annotations

import logging
import threading
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from . import media, sources, tiktok, youtube
from .auth import AuthError, google_token, tiktok_token
from .config import Config, load_config, paths
from .store import MAX_ATTEMPTS, Store, iso, now, worker_id

log = logging.getLogger("tlmedia")
RETRY_DELAYS_MIN = [1, 5, 15, 60]
TIKTOK_POLL_S = 20
TIKTOK_POLL_LIMIT = timedelta(hours=2)


def store() -> Store:
    return Store(paths().db_file)


# -- scheduling helpers -------------------------------------------------------------
def parse_when(when: str | None) -> datetime | None:
    if not when:
        return None
    dt = datetime.fromisoformat(when.strip().replace("Z", "+00:00"))
    if dt.tzinfo is None:  # naive = the PC's local time
        dt = dt.astimezone()
    dt = dt.astimezone(timezone.utc)
    if dt < now() + timedelta(minutes=2):
        raise ValueError(f"scheduled time {when} is in the past (or under 2 minutes away)")
    return dt


# -- drafting -----------------------------------------------------------------------
def create_draft(source: str, platforms: list[str], opts: dict, scheduled_at: str | None,
                 cfg: Config | None = None) -> dict:
    cfg = cfg or load_config()
    platforms = [p.lower().strip() for p in platforms]
    bad = [p for p in platforms if p not in ("youtube", "tiktok")]
    if bad or not platforms:
        raise ValueError(f"platforms must be youtube and/or tiktok, got {platforms}")

    defaults = {
        "youtube_privacy": cfg.default("youtube_privacy", "private"),
        "made_for_kids": cfg.default("made_for_kids", True),
        "contains_synthetic_media": cfg.default("contains_synthetic_media", True),
        "ai_generated": cfg.default("tiktok_ai_generated", True),
        "youtube_category_id": cfg.default("youtube_category_id", "27"),
        "tiktok_mode": cfg.tiktok.get("default_mode", "inbox"),
        "tiktok_privacy": "SELF_ONLY",
        "tiktok_format": "auto",
    }
    opts = {**defaults, **{k: v for k, v in opts.items() if v is not None}}
    when = parse_when(scheduled_at)

    file_report = quick_inspect(source, cfg)
    group_id = uuid.uuid4().hex[:8]
    s = store()
    for p in platforms:
        o = dict(opts)
        run_after = None
        if when and p == "youtube":
            o["publish_at"] = iso(when).replace("+00:00", "Z")  # YouTube publishes it natively
        elif when and p == "tiktok":
            run_after = when  # TikTok has no native scheduling: worker waits
        s.create(group_id, p, source, o, run_after)
    return {"group_id": group_id, "preview": preview(group_id, file_report)}


def quick_inspect(source: str, cfg: Config) -> dict:
    """Cheap look at the file for the preview; never downloads a large Drive file."""
    kind = sources.classify(source)
    try:
        if kind == "local":
            info = media.probe(sources.resolve(source, cfg))
            return {"kind": kind, "info": info,
                    "checks": {p: media.check(info, p) for p in ("youtube", "tiktok")}}
        if kind == "drive":
            meta = sources.drive_metadata(sources.drive_file_id(source), cfg)
            return {"kind": kind, "name": meta["name"],
                    "size_mb": round(int(meta.get("size", 0)) / 1e6, 1),
                    "note": "full quality checks run after download (or call inspect_video first)"}
        return {"kind": kind, "note": "checked after download"}
    except Exception as e:  # preview must still render
        return {"kind": kind, "error": str(e)}


def preview(group_id: str, file_report: dict | None = None) -> str:
    rows = store().group(group_id)
    if not rows:
        return f"No post group {group_id}"
    lines = [f"POST PREVIEW  (group {group_id}) - nothing has been uploaded yet", "",
             f"Source: {rows[0]['source']}"]
    if file_report:
        info = file_report.get("info")
        if info:
            lines.append(f"File: {info['width']}x{info['height']} {info['orientation']}, "
                         f"{info['fps']} fps, {info['video_codec']}/{info['audio_codec']}, "
                         f"{info['duration_s']}s, {info['size_mb']} MB")
        elif file_report.get("name"):
            lines.append(f"File: {file_report['name']} ({file_report['size_mb']} MB on Drive)")
        if file_report.get("error"):
            lines.append(f"File problem: {file_report['error']}")
        if file_report.get("note"):
            lines.append(f"Note: {file_report['note']}")
    for r in rows:
        o = r["options"]
        lines.append("")
        if r["platform"] == "youtube":
            lines += [
                f"[YouTube]  post id {r['id']}",
                f"  Title: {o.get('title')}",
                f"  Description: {_short(o.get('description'))}",
                f"  Tags: {', '.join(o.get('tags') or []) or '-'}",
                f"  Privacy: {o.get('youtube_privacy')}"
                + (f" -> auto-publishes {o['publish_at']} (YouTube-native schedule)"
                   if o.get("publish_at") else ""),
                f"  Made for kids: {o.get('made_for_kids')}   AI/synthetic disclosure: "
                f"{o.get('contains_synthetic_media')}   Category: {o.get('youtube_category_id')}",
                f"  Thumbnail: {o.get('thumbnail') or '-'}   Playlist: {o.get('playlist_id') or '-'}",
            ]
        else:
            mode = o.get("tiktok_mode")
            lines += [
                f"[TikTok]  post id {r['id']}",
                f"  Mode: {mode} " + ("(goes to your TikTok inbox as a draft; you add the caption "
                                       "and tap Post in the app)" if mode == "inbox"
                                       else f"(direct post, privacy {o.get('tiktok_privacy')})"),
                f"  Caption: {_short(o.get('tiktok_caption') or o.get('title'))}",
                f"  AI-generated label: {o.get('ai_generated')}   Format: {o.get('tiktok_format')}",
                f"  Comments: {o.get('allow_comments', True)}  Duet: {o.get('allow_duet', False)}"
                f"  Stitch: {o.get('allow_stitch', False)}",
                f"  When: {r['run_after'] or 'immediately after approval'}",
            ]
        checks = (file_report or {}).get("checks", {}).get(r["platform"])
        if checks:
            for m in checks["must_fix"]:
                lines.append(f"  Will auto-fix: {m}")
            for w in checks["warnings"]:
                if w.startswith("not vertical") and o.get("tiktok_format") == "vertical":
                    w = "will be converted to 1080x1920 vertical with a blurred background"
                    lines.append(f"  Will auto-fix: {w}")
                    continue
                lines.append(f"  Warning: {w}")
    lines += ["", "Reply to approve (approve_post) or ask for changes (update_draft)."]
    return "\n".join(lines)


def _short(text: str | None, n: int = 160) -> str:
    text = (text or "-").replace("\n", " / ")
    return text if len(text) <= n else text[:n] + "..."


def update_draft(ident: str, changes: dict) -> str:
    s = store()
    rows = [r for r in s.find(ident) if r["status"] == "draft"]
    if not rows:
        raise ValueError(f"No draft found for {ident} (only drafts can be edited)")
    for r in rows:
        o = {**r["options"], **{k: v for k, v in changes.items() if v is not None}}
        s.update(r["id"], options=o)
    return preview(rows[0]["group_id"])


def approve(group_id: str) -> int:
    rows = store().find(group_id)
    if not rows:
        raise ValueError(f"No post group {group_id}")
    n = store().approve_group(rows[0]["group_id"])
    kick()
    return n


# -- worker -------------------------------------------------------------------------
_kick = threading.Event()


def kick() -> None:
    _kick.set()


def start_background_worker() -> threading.Thread:
    """Run inside the MCP server: poll every 15 s, or immediately when kicked."""
    def loop():
        while True:
            try:
                run_due()
            except Exception:
                log.exception("worker loop error")
            _kick.wait(15)
            _kick.clear()
    t = threading.Thread(target=loop, name="tlm-worker", daemon=True)
    t.start()
    return t


def run_due(max_jobs: int = 50) -> int:
    s, owner, n = store(), worker_id(), 0
    cfg = load_config()
    while n < max_jobs:
        job = s.claim(owner)
        if not job:
            break
        n += 1
        try:
            process(job, s, owner, cfg)
        except Exception as e:  # last-resort guard; process() handles expected errors
            log.exception("job %s crashed", job["id"])
            s.release(job["id"], status="failed", detail=f"crashed: {e}")
    return n


def process(job: dict, s: Store, owner: str, cfg: Config) -> None:
    pid = job["id"]
    last = [0.0]

    def progress(frac: float, msg: str) -> None:
        if time.monotonic() - last[0] >= 3 or frac >= 1:
            last[0] = time.monotonic()
            s.update(pid, progress=round(frac, 4), detail=msg)
            s.heartbeat(pid, owner)

    if job["status"] == "processing":
        return _poll_tiktok(job, s, cfg)

    s.update(pid, status="working", attempts=job["attempts"] + 1, detail="starting")
    try:
        if job["platform"] == "youtube":
            _run_youtube(job, s, cfg, progress)
        else:
            _run_tiktok(job, s, cfg, progress)
    except AuthError as e:
        s.release(pid, status="failed", detail=str(e))
    except (ValueError, FileNotFoundError) as e:  # bad input: retrying won't help
        s.release(pid, status="failed", detail=str(e))
    except Exception as e:
        attempts = job["attempts"] + 1
        if attempts >= MAX_ATTEMPTS:
            s.release(pid, status="failed", detail=f"gave up after {attempts} tries: {e}")
        else:
            delay = RETRY_DELAYS_MIN[min(attempts - 1, len(RETRY_DELAYS_MIN) - 1)]
            s.release(pid, status="queued", run_after=iso(now() + timedelta(minutes=delay)),
                      detail=f"try {attempts} failed ({e}); retrying in {delay} min")


def _prepare(job: dict, s: Store, cfg: Config, progress, max_duration: int | None = None) -> Path:
    o = job["options"]
    src = sources.resolve(job["source"], cfg, progress)
    s.update(job["id"], detail="checking video")
    out, info, notes = media.optimize(src, job["platform"], o.get("tiktok_format", "auto"),
                                      max_duration, progress)
    s.update(job["id"], local_file=str(out), detail="; ".join(notes))
    return out


def _run_youtube(job: dict, s: Store, cfg: Config, progress) -> None:
    pid, o = job["id"], job["options"]
    google_token(cfg)  # fail fast if signed out
    path = Path(job["local_file"]) if job.get("local_file") and Path(job["local_file"]).exists() \
        else _prepare(job, s, cfg, progress)
    s.update(pid, detail="uploading to YouTube", progress=0)
    video = youtube.upload(path, o, lambda: google_token(cfg), job.get("resume"),
                           lambda st: s.update(pid, resume=st), progress)
    vid = video["id"]
    notes = []
    tok = google_token(cfg)
    if o.get("thumbnail"):
        try:
            youtube.set_thumbnail(vid, Path(o["thumbnail"]), tok)
        except Exception as e:
            notes.append(f"thumbnail not set: {e}")
    if o.get("playlist_id"):
        try:
            youtube.add_to_playlist(vid, o["playlist_id"], tok)
        except Exception as e:
            notes.append(f"playlist not updated: {e}")
    status = video.get("status", {})
    result = {"video_id": vid, "url": f"https://youtu.be/{vid}",
              "studio_url": f"https://studio.youtube.com/video/{vid}/edit",
              "privacy": status.get("privacyStatus"), "publish_at": status.get("publishAt"),
              "notes": notes}
    detail = "uploaded to YouTube"
    if o.get("publish_at"):
        detail += f"; scheduled to go public {o['publish_at']}"
    s.release(pid, status="done", progress=1, resume=None, result=result,
              detail=detail + ("; " + "; ".join(notes) if notes else ""))


def _run_tiktok(job: dict, s: Store, cfg: Config, progress) -> None:
    pid, o = job["id"], job["options"]
    tok = tiktok_token(cfg)
    mode = o.get("tiktok_mode", "inbox")
    creator, post_info = {}, None
    if mode == "direct":
        creator = tiktok.creator_info(tok)
        post_info = tiktok.build_post_info(o, creator)

    prefixes = cfg.tiktok.get("pull_from_url_prefixes") or []
    if any(job["source"].startswith(p) for p in prefixes if p):
        s.update(pid, detail="TikTok is pulling the file from your verified URL")
        data = tiktok.init_upload(tok, mode, {"source": "PULL_FROM_URL",
                                              "video_url": job["source"]}, post_info)
    else:
        path = _prepare(job, s, cfg, progress, creator.get("max_video_post_duration_sec"))
        size = path.stat().st_size
        chunk_size, count = tiktok.plan_chunks(size)
        data = tiktok.init_upload(tok, mode, {"source": "FILE_UPLOAD", "video_size": size,
                                              "chunk_size": chunk_size,
                                              "total_chunk_count": count}, post_info)
        s.update(pid, detail=f"uploading to TikTok in {count} chunk(s)", progress=0,
                 resume={"publish_id": data["publish_id"]})
        tiktok.upload_file(data["upload_url"], path, chunk_size, count, progress)

    result = {"publish_id": data["publish_id"], "mode": mode,
              "polling_since": iso(now())}
    if mode == "inbox":
        result["caption_to_paste"] = o.get("tiktok_caption") or o.get("title") or ""
    if post_info:
        result["privacy"] = post_info["privacy_level"]
    s.release(pid, status="processing", progress=1, result=result,
              run_after=iso(now() + timedelta(seconds=TIKTOK_POLL_S)),
              detail="uploaded; TikTok is processing")


def _poll_tiktok(job: dict, s: Store, cfg: Config) -> None:
    pid, result = job["id"], job["result"] or {}
    try:
        st = tiktok.fetch_status(tiktok_token(cfg), result["publish_id"])
    except Exception as e:
        s.release(pid, run_after=iso(now() + timedelta(minutes=1)), detail=f"status check: {e}")
        return
    state = st.get("status", "")
    result["tiktok_status"] = state
    if st.get("publicaly_available_post_id") or st.get("publicly_available_post_id"):
        result["post_ids"] = st.get("publicaly_available_post_id") or st.get("publicly_available_post_id")
    if state in tiktok.DONE_STATES:
        msg = ("in your TikTok inbox - open the TikTok app, add the caption, and post"
               if state == "SEND_TO_USER_INBOX" else "published on TikTok")
        s.release(pid, status="done", result=result, detail=msg)
    elif state in tiktok.FAILED_STATES:
        s.release(pid, status="failed", result=result,
                  detail=f"TikTok rejected it: {st.get('fail_reason')}")
    elif now() - datetime.fromisoformat(result["polling_since"]) > TIKTOK_POLL_LIMIT:
        s.release(pid, status="failed", result=result,
                  detail=f"TikTok still '{state}' after 2 hours; check the TikTok app")
    else:
        s.release(pid, result=result, run_after=iso(now() + timedelta(seconds=TIKTOK_POLL_S)),
                  detail=f"TikTok status: {state}")


# -- reporting ----------------------------------------------------------------------
def describe(row: dict) -> dict:
    keep = ("id", "group_id", "platform", "status", "detail", "progress", "run_after",
            "attempts", "created_at", "updated_at", "result", "source")
    d = {k: row.get(k) for k in keep}
    d["title"] = (row.get("options") or {}).get("title")
    return d
