"""OAuth sign-in for Google (YouTube + Drive) and TikTok.

Both use the "installed app" pattern: open the system browser, catch the
redirect on a loopback port, exchange the code (with PKCE) for tokens, and
store a refresh token so later runs are silent.

TikTok quirk: its desktop PKCE expects the code_challenge to be the *hex*
SHA-256 of the verifier, not the base64url form the OAuth spec uses.
"""

from __future__ import annotations

import base64
import hashlib
import http.server
import json
import secrets
import threading
import time
import urllib.parse
import webbrowser
from pathlib import Path

import httpx

from .config import Config, paths

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",           # thumbnails, playlists, status
    "https://www.googleapis.com/auth/drive.readonly",    # fetch videos by Drive link
]

TIKTOK_AUTH_URL = "https://www.tiktok.com/v2/auth/authorize/"
TIKTOK_TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
TIKTOK_SCOPES = ["user.info.basic", "video.upload", "video.publish"]


class AuthError(RuntimeError):
    pass


# -- token file -------------------------------------------------------------------
def _load_tokens() -> dict:
    f = paths().tokens_file
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def _save_tokens(provider: str, data: dict) -> None:
    f: Path = paths().tokens_file
    tokens = _load_tokens()
    tokens[provider] = data
    f.write_text(json.dumps(tokens, indent=2), encoding="utf-8")


def token_status() -> dict:
    tokens = _load_tokens()
    out = {}
    for provider in ("google", "tiktok"):
        t = tokens.get(provider)
        out[provider] = (
            {"signed_in": True, "scopes": t.get("scope", ""), "account": t.get("account", "")}
            if t and t.get("refresh_token") else {"signed_in": False}
        )
    return out


# -- PKCE + loopback ----------------------------------------------------------------
def pkce_pair(hex_challenge: bool = False) -> tuple[str, str]:
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~"
    verifier = "".join(secrets.choice(alphabet) for _ in range(64))
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    if hex_challenge:
        challenge = digest.hex()
    else:
        challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return verifier, challenge


def _catch_redirect(host: str, port: int, path: str, auth_url: str, timeout: int = 300) -> dict:
    """Serve one request on the loopback address and return its query params."""
    result: dict = {}
    done = threading.Event()

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path.rstrip("/") != path.rstrip("/"):
                self.send_response(404)
                self.end_headers()
                return
            result.update({k: v[0] for k, v in urllib.parse.parse_qs(parsed.query).items()})
            ok = "code" in result
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            msg = ("Signed in. You can close this tab and return to Claude." if ok
                   else f"Sign-in failed: {result.get('error_description') or result.get('error')}")
            self.wfile.write(f"<html><body style='font-family:sans-serif'><h2>{msg}</h2>"
                             "</body></html>".encode())
            done.set()

        def log_message(self, *args):
            pass

    server = http.server.HTTPServer((host, port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        print(f"Opening browser for sign-in. If it does not open, visit:\n{auth_url}\n")
        webbrowser.open(auth_url)
        if not done.wait(timeout):
            raise AuthError("Timed out waiting for the browser sign-in.")
    finally:
        server.shutdown()
    return result


def _free_port() -> int:
    import socket
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


# -- Google -------------------------------------------------------------------------
def google_login(cfg: Config) -> dict:
    cid, secret = cfg.google.get("client_id"), cfg.google.get("client_secret")
    if not cid:
        raise AuthError("Set [google] client_id/client_secret in config.toml first.")
    port = _free_port()
    redirect = f"http://127.0.0.1:{port}/"
    verifier, challenge = pkce_pair()
    state = secrets.token_urlsafe(16)
    url = GOOGLE_AUTH_URL + "?" + urllib.parse.urlencode({
        "client_id": cid, "redirect_uri": redirect, "response_type": "code",
        "scope": " ".join(GOOGLE_SCOPES), "access_type": "offline", "prompt": "consent",
        "code_challenge": challenge, "code_challenge_method": "S256", "state": state,
    })
    q = _catch_redirect("127.0.0.1", port, "/", url)
    if q.get("state") != state or "code" not in q:
        raise AuthError(f"Google sign-in failed: {q}")
    r = httpx.post(GOOGLE_TOKEN_URL, data={
        "client_id": cid, "client_secret": secret, "code": q["code"], "code_verifier": verifier,
        "grant_type": "authorization_code", "redirect_uri": redirect,
    }, timeout=30)
    if r.status_code != 200:
        raise AuthError(f"Google token exchange failed: {r.text}")
    tok = r.json()
    tok["expires_at"] = time.time() + tok.get("expires_in", 3600) - 60
    try:
        me = httpx.get("https://www.googleapis.com/youtube/v3/channels",
                       params={"part": "snippet", "mine": "true"},
                       headers={"Authorization": f"Bearer {tok['access_token']}"}, timeout=30).json()
        tok["account"] = me["items"][0]["snippet"]["title"]
    except Exception:  # channel lookup is cosmetic
        tok["account"] = ""
    _save_tokens("google", tok)
    return tok


def google_token(cfg: Config) -> str:
    tok = _load_tokens().get("google")
    if not tok or not tok.get("refresh_token"):
        raise AuthError("Not signed in to Google. Run:  tlm auth google")
    if tok.get("expires_at", 0) > time.time():
        return tok["access_token"]
    r = httpx.post(GOOGLE_TOKEN_URL, data={
        "client_id": cfg.google["client_id"], "client_secret": cfg.google["client_secret"],
        "refresh_token": tok["refresh_token"], "grant_type": "refresh_token",
    }, timeout=30)
    if r.status_code != 200:
        raise AuthError(f"Google token refresh failed ({r.text}). Run:  tlm auth google")
    new = r.json()
    tok.update(access_token=new["access_token"],
               expires_at=time.time() + new.get("expires_in", 3600) - 60)
    _save_tokens("google", tok)
    return tok["access_token"]


# -- TikTok -------------------------------------------------------------------------
def tiktok_login(cfg: Config) -> dict:
    key, secret = cfg.tiktok.get("client_key"), cfg.tiktok.get("client_secret")
    if not key:
        raise AuthError("Set [tiktok] client_key/client_secret in config.toml first.")
    redirect = cfg.tiktok["redirect_uri"]
    parsed = urllib.parse.urlparse(redirect)
    verifier, challenge = pkce_pair(hex_challenge=True)
    state = secrets.token_urlsafe(16)
    url = TIKTOK_AUTH_URL + "?" + urllib.parse.urlencode({
        "client_key": key, "scope": ",".join(TIKTOK_SCOPES), "response_type": "code",
        "redirect_uri": redirect, "state": state,
        "code_challenge": challenge, "code_challenge_method": "S256",
    })
    host = "127.0.0.1" if parsed.hostname in ("localhost", "127.0.0.1") else parsed.hostname
    q = _catch_redirect(host, parsed.port or 80, parsed.path or "/", url)
    if q.get("state") != state or "code" not in q:
        raise AuthError(f"TikTok sign-in failed: {q}")
    r = httpx.post(TIKTOK_TOKEN_URL, data={
        "client_key": key, "client_secret": secret, "code": q["code"],
        "grant_type": "authorization_code", "redirect_uri": redirect, "code_verifier": verifier,
    }, headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=30)
    tok = r.json()
    if r.status_code != 200 or "access_token" not in tok:
        raise AuthError(f"TikTok token exchange failed: {r.text}")
    tok["expires_at"] = time.time() + tok.get("expires_in", 86400) - 60
    try:
        info = httpx.get("https://open.tiktokapis.com/v2/user/info/",
                         params={"fields": "display_name"},
                         headers={"Authorization": f"Bearer {tok['access_token']}"}, timeout=30).json()
        tok["account"] = info["data"]["user"]["display_name"]
    except Exception:
        tok["account"] = ""
    _save_tokens("tiktok", tok)
    return tok


def tiktok_token(cfg: Config) -> str:
    tok = _load_tokens().get("tiktok")
    if not tok or not tok.get("refresh_token"):
        raise AuthError("Not signed in to TikTok. Run:  tlm auth tiktok")
    if tok.get("expires_at", 0) > time.time():
        return tok["access_token"]
    r = httpx.post(TIKTOK_TOKEN_URL, data={
        "client_key": cfg.tiktok["client_key"], "client_secret": cfg.tiktok["client_secret"],
        "grant_type": "refresh_token", "refresh_token": tok["refresh_token"],
    }, headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=30)
    new = r.json()
    if r.status_code != 200 or "access_token" not in new:
        raise AuthError(f"TikTok token refresh failed ({r.text}). Run:  tlm auth tiktok")
    tok.update(new)
    tok["expires_at"] = time.time() + new.get("expires_in", 86400) - 60
    _save_tokens("tiktok", tok)
    return tok["access_token"]
