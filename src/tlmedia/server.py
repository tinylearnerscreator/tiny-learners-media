"""MCP server (stdio) for Claude Desktop.

Claude only ever passes *paths and links* to these tools. The video bytes
move directly from disk/Drive to YouTube/TikTok inside this process, which
is what removes the ~30 MB limit of attaching files to a chat or pushing
them through a browser extension.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

try:  # mcp >= 2
    from mcp.server.mcpserver import MCPServer as _Server
except ImportError:  # mcp 1.x
    from mcp.server.fastmcp import FastMCP as _Server

from . import browser, jobs, media, sources, tiktok, youtube
from .auth import google_token, tiktok_token, token_status
from .config import load_config, paths

INSTRUCTIONS = """\
Tiny Learners Media posts videos (any size, up to 4 GB on TikTok / 256 GB on YouTube)
from this Windows PC to YouTube and TikTok.

Rules:
1. Never read or attach the video file yourself. Pass its path (e.g. G:\\My Drive\\...\\ep12.mp4),
   a Google Drive link, or a URL as `source`. This server moves the bytes.
2. Always call draft_post first, show the user the returned preview VERBATIM, and only call
   approve_post after the user explicitly says to publish/approve. Never approve on your own.
3. After approving, use post_status to report progress. Uploads continue in the background,
   and also resume via the Windows scheduled task if Claude is closed.
4. TikTok "inbox" mode puts the video in the user's TikTok app inbox; remind them to paste the
   caption (post_status returns caption_to_paste) and tap Post.
"""

mcp = _Server("tiny-learners-media", instructions=INSTRUCTIONS)


async def _bg(fn, *args, **kwargs):
    return await asyncio.to_thread(fn, *args, **kwargs)


@mcp.tool()
async def check_setup() -> dict:
    """Check that ffmpeg is installed, credentials are configured, and which accounts are
    signed in. Run this first if anything fails."""
    cfg = load_config()
    p = paths()
    return {
        "ffmpeg_installed": media.have_ffmpeg(),
        "google_client_configured": bool(cfg.google.get("client_id")),
        "tiktok_client_configured": bool(cfg.tiktok.get("client_key")),
        "accounts": token_status(),
        "tiktok_default_mode": cfg.tiktok.get("default_mode"),
        "config_file": str(p.config_file),
        "cache_dir": str(p.cache),
        "how_to_sign_in": "Run in PowerShell:  tlm auth google   and   tlm auth tiktok",
    }


@mcp.tool()
async def inspect_video(source: str, download: bool = True) -> dict:
    """Probe a video (local path, Google Drive link, or URL) and check it against YouTube and
    TikTok requirements. Drive files are downloaded to the local cache first (resumable,
    md5-verified) unless download=False, in which case only Drive metadata is returned."""
    cfg = load_config()
    if not download and sources.classify(source) == "drive":
        return await _bg(sources.drive_metadata, sources.drive_file_id(source), cfg)
    path = await _bg(sources.resolve, source, cfg)
    info = await _bg(media.probe, path)
    return {"info": info, "youtube": media.check(info, "youtube"),
            "tiktok": media.check(info, "tiktok"), "local_file": str(path)}


@mcp.tool()
async def list_drive_videos(folder: str, name_contains: str = "") -> list[dict]:
    """List video files in a Google Drive folder (folder link or folder ID), newest first.
    Each result includes a `link` usable as draft_post's source."""
    return await _bg(sources.list_drive_folder, folder, load_config(), name_contains)


@mcp.tool()
async def draft_post(
    source: str,
    platforms: list[str],
    title: str,
    description: str = "",
    tags: list[str] | None = None,
    tiktok_caption: str | None = None,
    scheduled_at: str | None = None,
    youtube_privacy: str | None = None,
    made_for_kids: bool | None = None,
    contains_synthetic_media: bool | None = None,
    thumbnail: str | None = None,
    playlist_id: str | None = None,
    youtube_category_id: str | None = None,
    notify_subscribers: bool | None = None,
    tiktok_mode: str | None = None,
    tiktok_privacy: str | None = None,
    tiktok_format: str | None = None,
    ai_generated: bool | None = None,
    allow_comments: bool | None = None,
    allow_duet: bool | None = None,
    allow_stitch: bool | None = None,
    cover_timestamp_ms: int | None = None,
) -> dict:
    """Create a post draft (uploads NOTHING) and return a preview to show the user.

    source: local path (Drive for desktop paths work), Google Drive link, or URL.
    platforms: ["youtube"], ["tiktok"], or ["youtube", "tiktok"].
    title: YouTube title (max 100 chars); also the TikTok caption if tiktok_caption is unset.
    description: YouTube description. tags: YouTube tags.
    scheduled_at: ISO time, e.g. "2026-10-18T09:00" (PC local time) or with offset/Z.
      YouTube uses its native scheduler; TikTok is posted by the background worker then.
    youtube_privacy: private | unlisted | public (default from config: private).
    made_for_kids / contains_synthetic_media: YouTube disclosures (defaults true).
    thumbnail: local .jpg/.png path (<2 MB). playlist_id: YouTube playlist id.
    tiktok_mode: inbox (draft in TikTok app; default) | direct (needs video.publish).
    tiktok_privacy (direct mode): PUBLIC_TO_EVERYONE | MUTUAL_FOLLOW_FRIENDS | FOLLOWER_OF_CREATOR
      | SELF_ONLY. Unaudited TikTok apps can only use SELF_ONLY.
    tiktok_format: auto (keep as-is when valid) | vertical (make a 1080x1920 version with a
      blurred background from a horizontal episode).
    ai_generated: TikTok AI-generated content label (default true).
    """
    opts: dict[str, Any] = {
        "title": title, "description": description, "tags": tags,
        "tiktok_caption": tiktok_caption, "youtube_privacy": youtube_privacy,
        "made_for_kids": made_for_kids, "contains_synthetic_media": contains_synthetic_media,
        "thumbnail": thumbnail, "playlist_id": playlist_id,
        "youtube_category_id": youtube_category_id, "notify_subscribers": notify_subscribers,
        "tiktok_mode": tiktok_mode, "tiktok_privacy": tiktok_privacy,
        "tiktok_format": tiktok_format, "ai_generated": ai_generated,
        "allow_comments": allow_comments, "allow_duet": allow_duet, "allow_stitch": allow_stitch,
        "cover_timestamp_ms": cover_timestamp_ms,
    }
    if thumbnail and not Path(thumbnail).is_file():
        raise ValueError(f"thumbnail not found: {thumbnail}")
    return await _bg(jobs.create_draft, source, platforms, opts, scheduled_at)


@mcp.tool()
async def update_draft(post_or_group_id: str, changes: dict) -> str:
    """Edit a draft before approval. `changes` uses the same keys as draft_post
    (e.g. {"title": "...", "tiktok_format": "vertical"}). Returns the new preview."""
    if "scheduled_at" in changes:
        raise ValueError("To change the schedule, cancel_post this draft and draft it again.")
    return await _bg(jobs.update_draft, post_or_group_id, changes)


@mcp.tool()
async def approve_post(group_id: str) -> dict:
    """Publish an approved draft group. ONLY call after the user has seen the preview and
    explicitly approved it. Uploads run in the background; follow with post_status."""
    n = await _bg(jobs.approve, group_id)
    rows = jobs.store().find(group_id)
    return {"approved": n, "posts": [jobs.describe(r) for r in rows],
            "next": "Call post_status in a minute to report progress."}


@mcp.tool()
async def post_status(post_or_group_id: str) -> list[dict]:
    """Current status, progress (0-1), and results (video URLs, TikTok publish state)."""
    rows = jobs.store().find(post_or_group_id)
    if not rows:
        raise ValueError(f"Nothing found for {post_or_group_id}")
    return [jobs.describe(r) for r in rows]


@mcp.tool()
async def list_posts(limit: int = 20, status: str | None = None) -> list[dict]:
    """Recent posts, newest first. Optional status filter: draft, queued, working,
    processing, done, failed, cancelled."""
    return [jobs.describe(r) for r in jobs.store().recent(limit, status)]


@mcp.tool()
async def cancel_post(post_or_group_id: str) -> dict:
    """Cancel a draft or queued (e.g. scheduled TikTok) post that has not started uploading.
    Note: a YouTube video already uploaded with a schedule must be changed in YouTube Studio."""
    return {"cancelled": jobs.store().cancel(post_or_group_id)}


@mcp.tool()
async def retry_post(post_or_group_id: str) -> dict:
    """Re-queue failed posts (e.g. after signing in again or fixing a file)."""
    n = jobs.store().retry(post_or_group_id)
    jobs.kick()
    return {"requeued": n}


@mcp.tool()
async def tiktok_account_info() -> dict:
    """TikTok creator info for direct posting: allowed privacy levels, max video length,
    and whether comments/duet/stitch are disabled on the account."""
    cfg = load_config()
    return await _bg(lambda: tiktok.creator_info(tiktok_token(cfg)))


@mcp.tool()
async def youtube_playlists() -> list[dict]:
    """List the signed-in channel's playlists (id + title) for draft_post's playlist_id."""
    cfg = load_config()
    return await _bg(lambda: youtube.list_playlists(google_token(cfg)))


@mcp.tool()
async def open_in_tiktok_studio(source: str, caption: str = "",
                                tiktok_format: str = "auto") -> dict:
    """Fallback that needs no TikTok API approval: opens TikTok Studio in Microsoft Edge (saved
    login) with the video already attached and the caption filled in. The USER reviews and
    clicks Post. Handles large files because the browser reads the file straight from disk."""
    cfg = load_config()

    def prep():
        src = sources.resolve(source, cfg)
        out, _, notes = media.optimize(src, "tiktok", tiktok_format)
        browser.launch_detached(out, caption)
        return {"opened": str(out), "notes": notes,
                "next": "Log in if asked, check the post in the Edge window, then click Post."}
    return await _bg(prep)


def main() -> None:
    logging.basicConfig(filename=paths().log_file, level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    jobs.start_background_worker()
    mcp.run()  # stdio


if __name__ == "__main__":
    main()
