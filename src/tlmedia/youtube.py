"""YouTube Data API v3 resumable upload.

Large-file strategy:
  * resumable protocol: one session URI, file sent in 32 MiB chunks
    (must be a multiple of 256 KiB), so memory stays flat even for 50 GB
  * the session URI and byte offset are persisted after every chunk; if the
    PC sleeps, Wi-Fi drops, or Claude is closed, the next worker run asks
    YouTube "how much do you have?" and continues from there (sessions stay
    valid for about a week)
  * transient errors (5xx, timeouts, resets) retry with exponential backoff
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Callable

import httpx

UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"
API = "https://www.googleapis.com/youtube/v3"
CHUNK = 32 * 1024 * 1024  # multiple of 256 KiB
RETRY_STATUS = {500, 502, 503, 504}
MAX_RETRIES = 10


class YouTubeError(RuntimeError):
    pass


def _clean(text: str, limit: int) -> str:
    # YouTube rejects angle brackets in titles and descriptions.
    text = (text or "").replace("<", "‹").replace(">", "›")
    data = text.encode("utf-8")[:limit]
    return data.decode("utf-8", errors="ignore")


def build_body(opts: dict) -> dict:
    tags, total = [], 0
    for t in opts.get("tags") or []:
        t = t.replace("<", "").replace(">", "").strip()
        cost = len(t) + (2 if " " in t else 0) + 1
        if t and total + cost <= 500:
            tags.append(t)
            total += cost
    status = {
        "privacyStatus": opts.get("youtube_privacy", "private"),
        "selfDeclaredMadeForKids": bool(opts.get("made_for_kids", True)),
        "containsSyntheticMedia": bool(opts.get("contains_synthetic_media", True)),
        "embeddable": True,
    }
    if opts.get("publish_at"):
        status["privacyStatus"] = "private"  # required for scheduled publishing
        status["publishAt"] = opts["publish_at"]
    snippet = {
        "title": _clean(opts.get("title") or "Untitled", 100),
        "description": _clean(opts.get("description") or "", 5000),
        "categoryId": str(opts.get("youtube_category_id") or "27"),
    }
    if tags:
        snippet["tags"] = tags
    if opts.get("language"):
        snippet["defaultLanguage"] = snippet["defaultAudioLanguage"] = opts["language"]
    return {"snippet": snippet, "status": status}


def upload(path: Path, opts: dict, token: Callable[[], str], resume: dict | None,
           save_resume: Callable[[dict], None],
           progress: Callable[[float, str], None] | None = None,
           chunk_size: int = CHUNK, client: httpx.Client | None = None) -> dict:
    size = path.stat().st_size
    own = client is None
    client = client or httpx.Client(timeout=httpx.Timeout(60, write=300, read=300))
    try:
        session, offset = None, 0
        if resume and resume.get("session") and resume.get("size") == size:
            session = resume["session"]
            state = _query(client, session, size, token)
            if isinstance(state, dict):
                return state
            if state is None:
                session = None
            else:
                offset = state
        if session is None:
            session = _start(client, opts, size, token)
            offset = 0
            save_resume({"session": session, "size": size, "offset": 0})

        retries = 0
        with open(path, "rb") as f:
            while True:
                f.seek(offset)
                data = f.read(chunk_size)
                end = offset + len(data) - 1
                try:
                    r = client.put(session, content=data, headers={
                        "Authorization": f"Bearer {token()}",
                        "Content-Length": str(len(data)),
                        "Content-Range": f"bytes {offset}-{end}/{size}",
                    })
                except httpx.TransportError as e:
                    r, err = None, str(e)
                if r is not None and r.status_code in (200, 201):
                    if progress:
                        progress(1.0, "upload complete")
                    return r.json()
                if r is not None and r.status_code == 308:
                    offset = _range_end(r)
                    retries = 0
                    save_resume({"session": session, "size": size, "offset": offset})
                    if progress:
                        progress(offset / size, f"uploaded {offset / 1e6:.0f}/{size / 1e6:.0f} MB")
                    continue
                if r is not None and r.status_code not in RETRY_STATUS and r.status_code != 401:
                    if r.status_code in (404, 410):  # session expired: start over cleanly
                        save_resume({})
                    raise YouTubeError(f"Upload failed ({r.status_code}): {_reason(r)}")
                retries += 1
                if retries > MAX_RETRIES:
                    raise YouTubeError(f"Upload kept failing: {err if r is None else _reason(r)}")
                time.sleep(min(2 ** retries, 64))
                state = _query(client, session, size, token)
                if isinstance(state, dict):
                    return state
                if state is None:
                    save_resume({})
                    raise YouTubeError("Upload session expired; it will restart on retry.")
                offset = state
    finally:
        if own:
            client.close()


def _start(client: httpx.Client, opts: dict, size: int, token: Callable[[], str]) -> str:
    params = {"uploadType": "resumable", "part": "snippet,status",
              "notifySubscribers": "true" if opts.get("notify_subscribers", True) else "false"}
    r = client.post(UPLOAD_URL, params=params, json=build_body(opts), headers={
        "Authorization": f"Bearer {token()}",
        "X-Upload-Content-Length": str(size),
        "X-Upload-Content-Type": "video/*",
    })
    if r.status_code != 200 or "location" not in r.headers:
        raise YouTubeError(f"Could not start upload ({r.status_code}): {_reason(r)}")
    return r.headers["location"]


def _query(client: httpx.Client, session: str, size: int, token: Callable[[], str]):
    """Ask YouTube how many bytes it has. Returns offset, final video dict, or None if expired."""
    for attempt in range(MAX_RETRIES):
        try:
            r = client.put(session, headers={"Authorization": f"Bearer {token()}",
                                             "Content-Length": "0",
                                             "Content-Range": f"bytes */{size}"})
        except httpx.TransportError:
            time.sleep(min(2 ** (attempt + 1), 64))
            continue
        if r.status_code in (200, 201):
            return r.json()
        if r.status_code == 308:
            return _range_end(r)
        if r.status_code in (404, 410):
            return None
        time.sleep(min(2 ** (attempt + 1), 64))
    raise YouTubeError("Could not reach YouTube to resume the upload.")


def _range_end(r: httpx.Response) -> int:
    rng = r.headers.get("range")  # "bytes=0-12345"
    return int(rng.rsplit("-", 1)[1]) + 1 if rng else 0


def _reason(r: httpx.Response) -> str:
    try:
        err = r.json()["error"]
        reasons = ",".join(e.get("reason", "") for e in err.get("errors", []))
        return f"{err.get('message')} [{reasons}]"
    except Exception:
        return r.text[:300]


# -- after upload -------------------------------------------------------------------
def set_thumbnail(video_id: str, image: Path, token: str) -> None:
    mime = "image/png" if image.suffix.lower() == ".png" else "image/jpeg"
    r = httpx.post("https://www.googleapis.com/upload/youtube/v3/thumbnails/set",
                   params={"videoId": video_id}, content=image.read_bytes(),
                   headers={"Authorization": f"Bearer {token}", "Content-Type": mime}, timeout=120)
    if r.status_code != 200:
        raise YouTubeError(f"Thumbnail failed ({r.status_code}): {_reason(r)}")


def add_to_playlist(video_id: str, playlist_id: str, token: str) -> None:
    r = httpx.post(f"{API}/playlistItems", params={"part": "snippet"}, json={
        "snippet": {"playlistId": playlist_id,
                    "resourceId": {"kind": "youtube#video", "videoId": video_id}}},
        headers={"Authorization": f"Bearer {token}"}, timeout=60)
    if r.status_code != 200:
        raise YouTubeError(f"Playlist add failed ({r.status_code}): {_reason(r)}")


def video_status(video_id: str, token: str) -> dict:
    r = httpx.get(f"{API}/videos", params={"part": "status,processingDetails", "id": video_id},
                  headers={"Authorization": f"Bearer {token}"}, timeout=60)
    r.raise_for_status()
    items = r.json().get("items", [])
    return items[0] if items else {}


def list_playlists(token: str) -> list[dict]:
    r = httpx.get(f"{API}/playlists", params={"part": "snippet", "mine": "true", "maxResults": 50},
                  headers={"Authorization": f"Bearer {token}"}, timeout=60)
    r.raise_for_status()
    return [{"id": p["id"], "title": p["snippet"]["title"]} for p in r.json().get("items", [])]


def find_playlist(name: str, token: str) -> str | None:
    """Playlist id for a title like 'Space for Little Ones' (case-insensitive)."""
    want = name.strip().lower()
    for p in list_playlists(token):
        if p["title"].strip().lower() == want:
            return p["id"]
    return None


def set_privacy(video_id: str, privacy: str, token: str) -> dict:
    """Change visibility (private | unlisted | public) without touching other settings."""
    if privacy not in ("private", "unlisted", "public"):
        raise ValueError("privacy must be private, unlisted or public")
    current = video_status(video_id, token)
    if not current:
        raise YouTubeError(f"Video {video_id} not found on this channel")
    status = {k: v for k, v in current.get("status", {}).items()
              if k in ("privacyStatus", "embeddable", "license", "publicStatsViewable",
                       "selfDeclaredMadeForKids", "containsSyntheticMedia", "publishAt")}
    status["privacyStatus"] = privacy
    if privacy != "private":
        status.pop("publishAt", None)
    r = httpx.put(f"{API}/videos", params={"part": "status"},
                  json={"id": video_id, "status": status},
                  headers={"Authorization": f"Bearer {token}"}, timeout=60)
    if r.status_code != 200:
        raise YouTubeError(f"Visibility change failed ({r.status_code}): {_reason(r)}")
    new = r.json().get("status", {}).get("privacyStatus")
    if new != privacy:
        raise YouTubeError(f"YouTube kept the video {new}. If the API project is not yet "
                           "audited, YouTube locks API uploads to private; change it in Studio.")
    return {"video_id": video_id, "privacy": new}
