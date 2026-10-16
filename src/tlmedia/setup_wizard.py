"""Guided first-time setup: `tlm setup`.

Does everything a program can do on its own (installing nothing by hand,
finding the downloaded Google key file, writing config, registering with
Claude Desktop) and only stops for the steps that need a human: signing in,
clicking Allow, and accepting Google's / TikTok's terms.

The non-interactive building blocks (set_value, import_google_json, ...) are
also exposed as `tlm config ...` so Claude can run them for you.
"""

from __future__ import annotations

import getpass
import json
import re
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path

import httpx

from . import media
from .auth import TIKTOK_TOKEN_URL, google_login, tiktok_login, token_status
from .config import ensure_config_file, load_config

SECRET_KEYS = {"client_secret"}

GOOGLE_PAGES = {
    "create_project": "https://console.cloud.google.com/projectcreate",
    "youtube_api": "https://console.cloud.google.com/apis/library/youtube.googleapis.com",
    "drive_api": "https://console.cloud.google.com/apis/library/drive.googleapis.com",
    "branding": "https://console.cloud.google.com/auth/branding",
    "audience": "https://console.cloud.google.com/auth/audience",
    "create_client": "https://console.cloud.google.com/auth/clients/create",
}
TIKTOK_PAGES = {
    "apps": "https://developers.tiktok.com/apps/",
}


# -- config editing -------------------------------------------------------------------
def _toml_value(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(_toml_value(v) for v in value) + "]"
    return json.dumps(str(value), ensure_ascii=False)  # valid TOML basic string


def _coerce(raw: str):
    low = raw.strip().lower()
    if low in ("true", "false"):
        return low == "true"
    if raw.strip().startswith("["):
        return json.loads(raw)
    return raw


def set_value(section: str, key: str, value) -> Path:
    """Set [section] key = value in config.toml, keeping comments and layout."""
    path = ensure_config_file()
    lines = path.read_text(encoding="utf-8").splitlines()
    line_out = f"{key} = {_toml_value(value)}"
    in_section, header_idx = False, None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_section = stripped[1:-1].strip() == section
            if in_section:
                header_idx = i
            continue
        if in_section and re.match(rf"^\s*{re.escape(key)}\s*=", line):
            lines[i] = line_out
            break
    else:
        if header_idx is None:
            lines += ["", f"[{section}]", line_out]
        else:
            lines.insert(header_idx + 1, line_out)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    load_config()  # raises if we somehow produced invalid TOML
    return path


def show_config() -> dict:
    cfg = load_config()
    out = {}
    for section in ("google", "tiktok", "defaults"):
        out[section] = {k: ("****" + str(v)[-4:] if k in SECRET_KEYS and v else v)
                        for k, v in getattr(cfg, section).items()}
    return out


# -- Google key file ------------------------------------------------------------------
def downloads_dir() -> Path:
    return Path.home() / "Downloads"


def find_google_client_json() -> Path | None:
    d = downloads_dir()
    if not d.is_dir():
        return None
    files = sorted(d.glob("client_secret*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def import_google_json(path: Path | None = None) -> dict:
    path = path or find_google_client_json()
    if not path or not Path(path).is_file():
        raise FileNotFoundError(
            f"No client_secret*.json found in {downloads_dir()}. Download it from "
            f"{GOOGLE_PAGES['create_client']} (type: Desktop app) and try again.")
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if "web" in data:
        raise ValueError("That key file is for a 'Web application' client. Create a new OAuth "
                         "client of type 'Desktop app' instead.")
    info = data.get("installed")
    if not info or not info.get("client_id") or not info.get("client_secret"):
        raise ValueError(f"{path} is not a Google OAuth client file.")
    set_value("google", "client_id", info["client_id"])
    set_value("google", "client_secret", info["client_secret"])
    return {"imported_from": str(path), "client_id": info["client_id"],
            "project_id": info.get("project_id", "")}


# -- TikTok key check -------------------------------------------------------------------
def check_tiktok_keys(client_key: str, client_secret: str) -> tuple[bool, str]:
    """Best-effort: ask TikTok for an app-only token, which only works with a valid pair."""
    try:
        r = httpx.post(TIKTOK_TOKEN_URL, data={"client_key": client_key,
                                               "client_secret": client_secret,
                                               "grant_type": "client_credentials"},
                       headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=30)
        body = r.json()
    except Exception as e:
        return True, f"could not verify right now ({e}); continuing"
    if "access_token" in body:
        return True, "TikTok accepted the client key and secret"
    err = str(body.get("error") or body)
    if "invalid_client" in err or "client_key" in err:
        return False, f"TikTok rejected these keys: {body.get('error_description') or err}"
    return True, "keys look valid"


# -- interactive wizard -----------------------------------------------------------------
def _step(title: str) -> None:
    print(f"\n=== {title} ===")


def _open(url: str) -> None:
    print(f"  Opening: {url}")
    webbrowser.open(url)


def _ask(prompt: str, default_yes: bool = True) -> bool:
    suffix = " [Y/n] " if default_yes else " [y/N] "
    ans = input(prompt + suffix).strip().lower()
    return default_yes if not ans else ans.startswith("y")


def _wait(msg: str = "Press Enter when done (or type s to skip)") -> bool:
    return input(f"  {msg}: ").strip().lower() != "s"


def wizard() -> None:
    ensure_config_file()
    print("Tiny Learners Media setup. I'll do the parts I can and tell you exactly what to\n"
          "click for the parts only you can do (signing in and accepting terms).")

    # 1. ffmpeg
    _step("1/5  ffmpeg")
    if media.have_ffmpeg():
        print("  ffmpeg found.")
    elif sys.platform == "win32" and shutil.which("winget") and _ask("  Install ffmpeg now?"):
        subprocess.run(["winget", "install", "--id", "Gyan.FFmpeg", "-e",
                        "--accept-source-agreements", "--accept-package-agreements"])
        print("  Installed. It will be on PATH in new windows.")
    else:
        print("  Install ffmpeg from https://www.gyan.dev/ffmpeg/builds/ and add it to PATH.")

    # 2. Google
    _step("2/5  Google (YouTube + Drive)")
    cfg = load_config()
    if cfg.google.get("client_id") and not _ask("  Google keys already saved. Replace them?", False):
        pass
    elif (found := find_google_client_json()) and _ask(f"  Found {found.name} in Downloads. Use it?"):
        print("  " + json.dumps(import_google_json(found)))
    else:
        print("  I'll open each Google Cloud page; do the one thing listed, then press Enter.")
        _open(GOOGLE_PAGES["create_project"])
        print("  -> Project name: Tiny Learners Media  -> Create. (Make sure it's selected after.)")
        if _wait():
            _open(GOOGLE_PAGES["youtube_api"])
            print("  -> Click Enable.")
            _wait()
            _open(GOOGLE_PAGES["drive_api"])
            print("  -> Click Enable.")
            _wait()
            _open(GOOGLE_PAGES["branding"])
            print("  -> Get started: App name 'Tiny Learners Media', your email as support email,\n"
                  "     Audience: External, contact email: yours -> agree -> Create.")
            _wait()
            _open(GOOGLE_PAGES["audience"])
            print("  -> Click 'Publish app' -> Confirm  (otherwise sign-ins expire every 7 days).")
            _wait()
            _open(GOOGLE_PAGES["create_client"])
            print("  -> Application type: Desktop app, name: tlm -> Create -> Download JSON.")
            _wait("Press Enter once the JSON is in your Downloads folder")
            print("  " + json.dumps(import_google_json()))
    if load_config().google.get("client_id") and not token_status()["google"]["signed_in"]:
        print("  Now sign in. In the browser: pick the account that owns the YouTube channel.\n"
              "  If you see 'Google hasn't verified this app': Advanced -> Go to Tiny Learners\n"
              "  Media (unsafe) -> tick all boxes -> Continue. (It's your own app.)")
        if _wait("Press Enter to open the sign-in page"):
            tok = google_login(load_config())
            print(f"  Signed in to Google{' as ' + tok['account'] if tok.get('account') else ''}.")

    # 3. TikTok
    _step("3/5  TikTok")
    cfg = load_config()
    if cfg.tiktok.get("client_key") and not _ask("  TikTok keys already saved. Replace them?", False):
        pass
    elif _ask("  Set up TikTok now?"):
        _open(TIKTOK_PAGES["apps"])
        print("  -> Log in, then 'Connect an app' (individual developer is fine), name it\n"
              "     'Tiny Learners Media', platform: Desktop.\n"
              "  -> Add products: Login Kit + Content Posting API (Direct Post optional).\n"
              "  -> Login Kit redirect URI:  " + cfg.tiktok["redirect_uri"] + "\n"
              "  -> Scopes: user.info.basic, video.upload, video.publish\n"
              "  -> Sandbox tab: create a sandbox, add your TikTok account as a target user.\n"
              "  -> Copy the Client key and Client secret (sandbox ones while in sandbox).")
        key = input("  Paste Client key: ").strip()
        secret = getpass.getpass("  Paste Client secret (hidden): ").strip()
        ok, msg = check_tiktok_keys(key, secret)
        print(f"  {msg}")
        if ok:
            set_value("tiktok", "client_key", key)
            set_value("tiktok", "client_secret", secret)
    if load_config().tiktok.get("client_key") and not token_status()["tiktok"]["signed_in"]:
        if _wait("Press Enter to sign in to TikTok (approve the permissions in the browser)"):
            tok = tiktok_login(load_config())
            print(f"  Signed in to TikTok{' as ' + tok['account'] if tok.get('account') else ''}.")

    # 4. Claude Desktop
    _step("4/5  Claude Desktop")
    from .cli import cmd_claude_config

    class _A:
        print_only = False
    cmd_claude_config(_A())

    # 5. summary
    _step("5/5  Check")
    status = token_status()
    print(json.dumps({"ffmpeg": media.have_ffmpeg(), "accounts": status}, indent=2))
    print("\nDone. Restart Claude Desktop and ask: 'check my video posting setup'.")
