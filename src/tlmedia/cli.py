"""`tlm` command line.

  tlm setup                guided first-time setup (recommended)
  tlm init                 create config.toml and open it
  tlm config ...           show/set config, import Google key file, save TikTok keys
  tlm auth google|tiktok   one-time browser sign-in
  tlm doctor               check ffmpeg, credentials, sign-ins
  tlm serve                run the MCP server (Claude Desktop starts this)
  tlm worker [--loop]      run due uploads (the scheduled task runs this)
  tlm post FILE ...        post without Claude (shows preview, asks y/N)
  tlm status [ID]          show recent posts or one post/group
  tlm claude-config        add this server to Claude Desktop's config
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from . import jobs, media
from .auth import google_login, tiktok_login, token_status
from .config import ensure_config_file, load_config, paths


def _print(obj) -> None:
    print(json.dumps(obj, indent=2, default=str) if not isinstance(obj, str) else obj)


def cmd_init(_):
    p = ensure_config_file()
    print(f"Config: {p}")
    if sys.platform == "win32":
        subprocess.Popen(["notepad.exe", str(p)])


def cmd_auth(a):
    cfg = load_config()
    tok = google_login(cfg) if a.provider == "google" else tiktok_login(cfg)
    print(f"Signed in to {a.provider}" + (f" as {tok.get('account')}" if tok.get("account") else ""))
    if a.provider == "tiktok" and "video.publish" not in tok.get("scope", ""):
        print("Note: video.publish scope not granted -> use tiktok_mode='inbox' (the default).")


def cmd_doctor(_):
    cfg = load_config()
    _print({"ffmpeg": media.have_ffmpeg(), "config": str(paths().config_file),
            "google_client": bool(cfg.google.get("client_id")),
            "tiktok_client": bool(cfg.tiktok.get("client_key")),
            "accounts": token_status()})


def cmd_serve(_):
    from .server import main
    main()


def cmd_worker(a):
    logging.basicConfig(filename=paths().log_file, level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    while True:
        n = jobs.run_due()
        if n:
            logging.info("worker processed %d job(s)", n)
        if not a.loop:
            # keep going while something is still processing (e.g. TikTok status polling)
            pending = [r for r in jobs.store().recent(50) if r["status"] in ("processing", "working")]
            if not pending:
                break
        time.sleep(15)


def cmd_post(a):
    opts = {"title": a.title, "description": a.description, "tags": a.tags,
            "tiktok_caption": a.caption, "youtube_privacy": a.privacy,
            "tiktok_mode": a.tiktok_mode, "tiktok_format": a.tiktok_format}
    d = jobs.create_draft(a.source, a.platforms, opts, a.at)
    print(d["preview"])
    if input("\nPublish this? [y/N] ").strip().lower() != "y":
        jobs.store().cancel(d["group_id"])
        print("Cancelled.")
        return
    jobs.store().approve_group(d["group_id"])
    print("Uploading... (Ctrl+C is safe: the scheduled task resumes it later)")
    while True:
        jobs.run_due()
        rows = jobs.store().group(d["group_id"])
        for r in rows:
            print(f"  {r['platform']:8} {r['status']:10} {r['progress'] * 100:5.1f}%  {r['detail']}")
        if all(r["status"] in ("done", "failed", "cancelled") or
               (r["status"] == "queued" and r["run_after"]) for r in rows):
            break
        time.sleep(10)
    _print([jobs.describe(r) for r in rows])


def cmd_status(a):
    rows = jobs.store().find(a.id) if a.id else jobs.store().recent(a.limit)
    _print([jobs.describe(r) for r in rows])


def cmd_setup(_):
    from .setup_wizard import wizard
    wizard()


def _clipboard() -> str:
    if sys.platform == "win32":
        out = subprocess.run(["powershell", "-NoProfile", "-Command", "Get-Clipboard"],
                             capture_output=True, text=True, creationflags=0x08000000)
    elif sys.platform == "darwin":
        out = subprocess.run(["pbpaste"], capture_output=True, text=True)
    else:
        out = subprocess.run(["xclip", "-o", "-selection", "clipboard"], capture_output=True, text=True)
    return out.stdout.strip()


def cmd_config(a):
    from . import setup_wizard as sw
    if a.action == "show":
        _print(sw.show_config())
    elif a.action == "set":
        section, _, key = a.key.partition(".")
        if not key:
            sys.exit("Use SECTION.KEY, e.g. tiktok.default_mode")
        sw.set_value(section, key, sw._coerce(a.value))
        print(f"Saved {a.key}")
    elif a.action == "import-google":
        _print(sw.import_google_json(Path(a.key) if a.key else None))
    elif a.action == "tiktok-keys":
        # Secret comes from the clipboard so it never shows up in a chat transcript.
        key = a.key
        secret = _clipboard() if a.value in (None, "-") else a.value
        if not key or not secret:
            sys.exit("Usage: tlm config tiktok-keys CLIENT_KEY   (with the secret copied to clipboard)")
        ok, msg = sw.check_tiktok_keys(key, secret)
        print(msg)
        if not ok:
            sys.exit(1)
        sw.set_value("tiktok", "client_key", key)
        sw.set_value("tiktok", "client_secret", secret)
        print("Saved TikTok client key and secret.")


def cmd_browser_upload(a):
    from .browser import run_upload
    run_upload(Path(a.video), a.caption)


def claude_desktop_config_path() -> Path:
    if sys.platform == "win32":
        return Path(os.environ["APPDATA"]) / "Claude" / "claude_desktop_config.json"
    if sys.platform == "darwin":
        return Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
    return Path.home() / ".config/Claude/claude_desktop_config.json"


def cmd_claude_config(a):
    exe = str(Path(shutil.which("tlm") or sys.argv[0]).resolve())
    entry = {"command": exe, "args": ["serve"]}
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        entry["env"] = {"TLM_FFMPEG_DIR": str(Path(ffmpeg).parent)}
    cfg_path = claude_desktop_config_path()
    data = json.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.exists() else {}
    data.setdefault("mcpServers", {})["tiny-learners-media"] = entry
    if a.print_only:
        _print(data)
        return
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    if cfg_path.exists():
        shutil.copy2(cfg_path, cfg_path.with_suffix(".json.bak"))
    cfg_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Added tiny-learners-media to {cfg_path}. Restart Claude Desktop.")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="tlm", description="Tiny Learners Media uploader")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("setup").set_defaults(fn=cmd_setup)
    sub.add_parser("init").set_defaults(fn=cmd_init)
    p = sub.add_parser("config")
    p.add_argument("action", choices=["show", "set", "import-google", "tiktok-keys"])
    p.add_argument("key", nargs="?", help="set: SECTION.KEY | tiktok-keys: CLIENT_KEY | "
                                           "import-google: path to client_secret JSON")
    p.add_argument("value", nargs="?")
    p.set_defaults(fn=cmd_config)
    p = sub.add_parser("auth")
    p.add_argument("provider", choices=["google", "tiktok"])
    p.set_defaults(fn=cmd_auth)
    sub.add_parser("doctor").set_defaults(fn=cmd_doctor)
    sub.add_parser("serve").set_defaults(fn=cmd_serve)
    p = sub.add_parser("worker")
    p.add_argument("--loop", action="store_true", help="run forever instead of exiting when idle")
    p.set_defaults(fn=cmd_worker)
    p = sub.add_parser("post")
    p.add_argument("source")
    p.add_argument("--platforms", nargs="+", default=["youtube", "tiktok"])
    p.add_argument("--title", required=True)
    p.add_argument("--description", default="")
    p.add_argument("--tags", nargs="*")
    p.add_argument("--caption")
    p.add_argument("--privacy", choices=["private", "unlisted", "public"])
    p.add_argument("--tiktok-mode", choices=["inbox", "direct"])
    p.add_argument("--tiktok-format", choices=["auto", "vertical"])
    p.add_argument("--at", help="schedule, e.g. 2026-10-18T09:00")
    p.set_defaults(fn=cmd_post)
    p = sub.add_parser("status")
    p.add_argument("id", nargs="?")
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(fn=cmd_status)
    p = sub.add_parser("browser-upload")
    p.add_argument("video")
    p.add_argument("--caption", default="")
    p.set_defaults(fn=cmd_browser_upload)
    p = sub.add_parser("claude-config")
    p.add_argument("--print-only", action="store_true")
    p.set_defaults(fn=cmd_claude_config)
    a = ap.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
