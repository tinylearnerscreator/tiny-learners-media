"""Turn whatever the user gives us into a local file we can probe and upload.

Accepted sources:
  * a local path, including a Google Drive for desktop path such as
    G:\\My Drive\\Tiny Learners\\ep12.mp4 (Drive streams it on first read)
  * a Google Drive link or "drive:<fileId>" -> downloaded via the Drive API
    with HTTP Range resume and an md5 check, so multi-GB files survive drops
  * any other http(s) URL -> plain resumable download

Bytes never pass through Claude; only the path/link string does.
"""

from __future__ import annotations

import hashlib
import re
import time
import urllib.parse
from pathlib import Path
from typing import Callable

import httpx

from .auth import google_token
from .config import Config, paths

DRIVE_PATTERNS = [
    re.compile(r"drive\.google\.com/file/d/([A-Za-z0-9_-]{10,})"),
    re.compile(r"drive\.google\.com/(?:open|uc)\?(?:.*&)?id=([A-Za-z0-9_-]{10,})"),
    re.compile(r"docs\.google\.com/.*/d/([A-Za-z0-9_-]{10,})"),
    re.compile(r"^drive:([A-Za-z0-9_-]{10,})$"),
]
DRIVE_FOLDER = re.compile(r"drive\.google\.com/drive/(?:u/\d+/)?folders/([A-Za-z0-9_-]{10,})")
CHUNK = 8 * 1024 * 1024

Progress = Callable[[float, str], None]


def drive_file_id(source: str) -> str | None:
    s = source.strip()
    for pat in DRIVE_PATTERNS:
        m = pat.search(s)
        if m:
            return m.group(1)
    return None


def drive_folder_id(source: str) -> str:
    m = DRIVE_FOLDER.search(source)
    return m.group(1) if m else source.strip()


def classify(source: str) -> str:
    if drive_file_id(source):
        return "drive"
    if source.strip().lower().startswith(("http://", "https://")):
        return "url"
    return "local"


def resolve(source: str, cfg: Config, progress: Progress | None = None) -> Path:
    kind = classify(source)
    if kind == "local":
        p = Path(source.strip().strip('"')).expanduser()
        if not p.is_file():
            raise FileNotFoundError(f"Video not found: {p}")
        return p
    if kind == "drive":
        return download_drive(drive_file_id(source), cfg, progress)
    return download_url(source.strip(), progress)


# -- Google Drive -------------------------------------------------------------------
def drive_metadata(file_id: str, cfg: Config) -> dict:
    r = httpx.get(f"https://www.googleapis.com/drive/v3/files/{file_id}",
                  params={"fields": "id,name,size,mimeType,md5Checksum,modifiedTime",
                          "supportsAllDrives": "true"},
                  headers={"Authorization": f"Bearer {google_token(cfg)}"}, timeout=30)
    if r.status_code == 404:
        raise FileNotFoundError(f"Drive file {file_id} not found or not shared with your account.")
    r.raise_for_status()
    return r.json()


def list_drive_folder(folder: str, cfg: Config, name_contains: str = "") -> list[dict]:
    q = f"'{drive_folder_id(folder)}' in parents and trashed=false and mimeType contains 'video/'"
    if name_contains:
        q += " and name contains '" + name_contains.replace("'", "\\'") + "'"
    r = httpx.get("https://www.googleapis.com/drive/v3/files",
                  params={"q": q, "pageSize": 100, "orderBy": "modifiedTime desc",
                          "fields": "files(id,name,size,modifiedTime)",
                          "supportsAllDrives": "true", "includeItemsFromAllDrives": "true"},
                  headers={"Authorization": f"Bearer {google_token(cfg)}"}, timeout=30)
    r.raise_for_status()
    return [{**f, "link": f"https://drive.google.com/file/d/{f['id']}/view",
             "size_mb": round(int(f.get("size", 0)) / 1e6, 1)} for f in r.json().get("files", [])]


def download_drive(file_id: str, cfg: Config, progress: Progress | None = None) -> Path:
    meta = drive_metadata(file_id, cfg)
    safe = re.sub(r"[^\w.\- ]", "_", meta["name"])
    dest = paths().cache / "drive" / f"{file_id}_{safe}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    size = int(meta.get("size", 0))
    if dest.exists() and dest.stat().st_size == size and _md5_ok(dest, meta.get("md5Checksum")):
        return dest
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}"
    _ranged_download(url, dest, size, progress,
                     params={"alt": "media", "supportsAllDrives": "true"},
                     auth=lambda: {"Authorization": f"Bearer {google_token(cfg)}"})
    if not _md5_ok(dest, meta.get("md5Checksum")):
        dest.unlink(missing_ok=True)
        raise IOError(f"Downloaded file failed its md5 check: {meta['name']}. Try again.")
    return dest


def _md5_ok(path: Path, expected: str | None) -> bool:
    if not expected:
        return True
    h = hashlib.md5()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(CHUNK), b""):
            h.update(block)
    return h.hexdigest() == expected


# -- generic URL --------------------------------------------------------------------
def download_url(url: str, progress: Progress | None = None) -> Path:
    name = Path(urllib.parse.urlparse(url).path).name or "video.mp4"
    tag = hashlib.sha1(url.encode()).hexdigest()[:10]
    dest = paths().cache / "url" / f"{tag}_{name}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        return dest
    with httpx.Client(follow_redirects=True, timeout=30) as c:
        size = int(c.head(url).headers.get("content-length", 0))
    _ranged_download(url, dest, size, progress)
    return dest


def _ranged_download(url: str, dest: Path, size: int, progress: Progress | None,
                     params: dict | None = None, auth: Callable[[], dict] | None = None,
                     retries: int = 8) -> None:
    """Download to dest.part, resuming from its current length after any failure."""
    part = dest.with_name(dest.name + ".part")
    attempt = 0
    while True:
        have = part.stat().st_size if part.exists() else 0
        if size and have >= size:
            break
        headers = dict(auth() if auth else {})
        if have:
            headers["Range"] = f"bytes={have}-"
        try:
            with httpx.Client(follow_redirects=True, timeout=httpx.Timeout(60, read=120)) as c:
                with c.stream("GET", url, params=params, headers=headers) as r:
                    if r.status_code == 416:
                        break
                    if have and r.status_code == 200:  # server ignored Range: start over
                        have = 0
                        part.unlink(missing_ok=True)
                    r.raise_for_status()
                    with open(part, "ab") as f:
                        for block in r.iter_bytes(CHUNK):
                            f.write(block)
                            have += len(block)
                            if progress and size:
                                progress(have / size, f"downloading {have / 1e6:.0f}/{size / 1e6:.0f} MB")
            if not size or have >= size:
                break
        except (httpx.TransportError, httpx.HTTPStatusError) as e:
            attempt += 1
            if attempt > retries or (isinstance(e, httpx.HTTPStatusError)
                                     and e.response.status_code in (403, 404)):
                raise
            time.sleep(min(2 ** attempt, 60))
    part.replace(dest)
