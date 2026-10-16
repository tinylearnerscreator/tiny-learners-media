"""Optional fallback: hand a large local file to TikTok Studio in a real browser.

Why this works for big files: Playwright gives the browser the file *path*
(set_input_files), so the browser streams it from disk exactly as if you had
picked it in the file dialog. There is no 10/30 MB ceiling like when a file
has to be passed through Claude in Chrome.

Uses Microsoft Edge (always present on Windows, so no browser download) with
a dedicated persistent profile: log in to TikTok once and it stays logged in.
It fills the caption best-effort and then STOPS - you review and click Post.

Install the extra first:  uv tool install --with playwright ...  (setup.ps1 -WithBrowser)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from .config import paths

TIKTOK_STUDIO_UPLOAD = "https://www.tiktok.com/tiktokstudio/upload"


def launch_detached(video: Path, caption: str) -> None:
    """Start the browser helper as its own process so it outlives this tool call."""
    args = [sys.executable, "-m", "tlmedia.cli", "browser-upload", str(video), "--caption", caption]
    kwargs = {}
    if sys.platform == "win32":
        kwargs["creationflags"] = 0x00000008 | 0x00000200  # DETACHED_PROCESS | NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True
    subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL, **kwargs)


def run_upload(video: Path, caption: str) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        raise RuntimeError("Playwright is not installed. Re-run setup.ps1 -WithBrowser") from e

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            str(paths().browser_profile),
            channel="msedge" if sys.platform == "win32" else None,
            headless=False, no_viewport=True, accept_downloads=False,
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(TIKTOK_STUDIO_UPLOAD, wait_until="domcontentloaded")
        # If you're not logged in yet, log in in this window; we wait up to 10 minutes.
        file_input = page.locator('input[type="file"]').first
        file_input.wait_for(state="attached", timeout=10 * 60 * 1000)
        file_input.set_input_files(str(video))
        if caption:
            try:
                editor = page.locator('div[contenteditable="true"]').first
                editor.wait_for(state="visible", timeout=180_000)
                editor.click()
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                page.keyboard.insert_text(caption)
            except Exception:
                pass  # caption box changed; the user can paste it
        # Leave the window open for the human to review and click Post.
        ctx.wait_for_event("close", timeout=0)
