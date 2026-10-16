"""TikTok Content Posting API.

Two ways in, both taking files up to 4 GB:
  * FILE_UPLOAD: we PUT the file to TikTok in sequential chunks
    (5-64 MB each, final chunk may run to 128 MB, at most 1000 chunks)
  * PULL_FROM_URL: TikTok's servers fetch the file from a URL prefix you
    verified in the developer portal, so nothing leaves this PC at all

Two destinations:
  * inbox  (scope video.upload)  -> lands in the TikTok app's inbox as a draft;
    works before your app passes TikTok's audit, at full quality
  * direct (scope video.publish) -> posts to the profile; until the app is
    audited TikTok only allows privacy SELF_ONLY
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Callable

import httpx

API = "https://open.tiktokapis.com/v2"
MB = 1_000_000
SINGLE_CHUNK_MAX = 64 * MB   # files up to this size go in one PUT
CHUNK = 20 * MB              # safely inside 5-64 MB whether "MB" means 10^6 or 2^20
MIME = {".mp4": "video/mp4", ".mov": "video/quicktime", ".webm": "video/webm"}


class TikTokError(RuntimeError):
    pass


def plan_chunks(size: int, chunk: int = CHUNK) -> tuple[int, int]:
    """Return (chunk_size, total_chunk_count) per TikTok's media transfer rules.

    total_chunk_count = floor(size / chunk_size); trailing bytes ride along in
    the final chunk, which stays well under the 128 MB final-chunk ceiling.
    """
    if size <= 0:
        raise ValueError("empty file")
    if size <= SINGLE_CHUNK_MAX:
        return size, 1
    count = size // chunk
    if count > 1000:
        raise TikTokError("file too large for TikTok chunked upload")
    return chunk, count


def chunk_ranges(size: int, chunk_size: int, count: int) -> list[tuple[int, int]]:
    ranges = []
    for i in range(count):
        start = i * chunk_size
        end = size - 1 if i == count - 1 else start + chunk_size - 1
        ranges.append((start, end))
    return ranges


def _call(path: str, token: str, body: dict | None = None,
          client: httpx.Client | None = None) -> dict:
    c = client or httpx
    r = c.post(f"{API}{path}", json=body or {}, timeout=60, headers={
        "Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=UTF-8"})
    try:
        data = r.json()
    except ValueError:
        raise TikTokError(f"{path} returned {r.status_code}: {r.text[:300]}") from None
    err = data.get("error") or {}
    if r.status_code != 200 or err.get("code") not in (None, "ok"):
        raise TikTokError(f"{path}: {err.get('code')} - {err.get('message')} "
                          f"(log_id {err.get('log_id')})")
    return data.get("data") or {}


def creator_info(token: str, client: httpx.Client | None = None) -> dict:
    return _call("/post/publish/creator_info/query/", token, client=client)


def init_upload(token: str, mode: str, source_info: dict, post_info: dict | None = None,
                client: httpx.Client | None = None) -> dict:
    if mode == "inbox":
        return _call("/post/publish/inbox/video/init/", token, {"source_info": source_info}, client)
    return _call("/post/publish/video/init/", token,
                 {"post_info": post_info or {}, "source_info": source_info}, client)


def build_post_info(opts: dict, creator: dict) -> dict:
    allowed = creator.get("privacy_level_options") or ["SELF_ONLY"]
    privacy = opts.get("tiktok_privacy") or "SELF_ONLY"
    if privacy not in allowed:
        privacy = "SELF_ONLY" if "SELF_ONLY" in allowed else allowed[0]
    info = {
        "title": (opts.get("tiktok_caption") or opts.get("title") or "")[:2200],
        "privacy_level": privacy,
        "disable_comment": not opts.get("allow_comments", True) or bool(creator.get("comment_disabled")),
        "disable_duet": not opts.get("allow_duet", False) or bool(creator.get("duet_disabled")),
        "disable_stitch": not opts.get("allow_stitch", False) or bool(creator.get("stitch_disabled")),
        "is_aigc": bool(opts.get("ai_generated", True)),
        "brand_content_toggle": False,
        "brand_organic_toggle": False,
    }
    if opts.get("cover_timestamp_ms") is not None:
        info["video_cover_timestamp_ms"] = int(opts["cover_timestamp_ms"])
    return info


def upload_file(upload_url: str, path: Path, chunk_size: int, count: int,
                progress: Callable[[float, str], None] | None = None,
                client: httpx.Client | None = None, retries: int = 6) -> None:
    size = path.stat().st_size
    mime = MIME.get(path.suffix.lower(), "video/mp4")
    own = client is None
    client = client or httpx.Client(timeout=httpx.Timeout(60, write=600, read=300))
    try:
        with open(path, "rb") as f:
            for idx, (start, end) in enumerate(chunk_ranges(size, chunk_size, count)):
                f.seek(start)
                data = f.read(end - start + 1)
                for attempt in range(retries + 1):
                    try:
                        r = client.put(upload_url, content=data, headers={
                            "Content-Type": mime, "Content-Length": str(len(data)),
                            "Content-Range": f"bytes {start}-{end}/{size}"})
                        if r.status_code in (200, 201, 206):
                            break
                        if r.status_code < 500 and r.status_code != 429:
                            raise TikTokError(f"chunk {idx + 1}/{count} rejected "
                                              f"({r.status_code}): {r.text[:300]}")
                    except httpx.TransportError:
                        pass
                    if attempt == retries:
                        raise TikTokError(f"chunk {idx + 1}/{count} kept failing")
                    time.sleep(min(2 ** (attempt + 1), 60))
                if progress:
                    progress((end + 1) / size, f"uploaded {(end + 1) / 1e6:.0f}/{size / 1e6:.0f} MB")
    finally:
        if own:
            client.close()


def fetch_status(token: str, publish_id: str, client: httpx.Client | None = None) -> dict:
    return _call("/post/publish/status/fetch/", token, {"publish_id": publish_id}, client)


# Final states reported by status/fetch
DONE_STATES = {"PUBLISH_COMPLETE", "SEND_TO_USER_INBOX"}
FAILED_STATES = {"FAILED"}
