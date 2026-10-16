# Tiny Learners Media

Post large, high-quality videos to **YouTube** and **TikTok** from a Windows PC. You do it by talking to Claude Desktop, which connects to this app over MCP.

> "Post `G:\My Drive\Tiny Learners\Episode 12.mp4` to YouTube and TikTok, titled *Counting to 10 with Tiny Learners*. Make a vertical version for TikTok and schedule it for Saturday 9am."

Claude drafts the post and shows you a preview. Nothing uploads until you say yes. Then the app streams the file straight from your disk or Google Drive to the platforms in resumable chunks: up to **4 GB on TikTok** and **256 GB on YouTube**, with no 30 MB limit and no quality-killing compression.

Why this works, and every alternative that was considered: [docs/large-file-strategies.md](docs/large-file-strategies.md).

## Features

- **Large files.** Chunked, resumable uploads. A dropped connection, sleep or reboot resumes where it stopped.
- **Google Drive.** Use a *Drive for desktop* path (`G:\My Drive\...`) or paste a Drive link. Links download with resume and are md5-verified.
- **Quality first.** Files that already meet the platform's requirements upload untouched. Otherwise the app re-encodes at near-lossless settings. It can also turn a 16:9 episode into a 1080×1920 TikTok with a blurred background.
- **Safe defaults.** YouTube posts go up private, marked *made for kids* with the *AI/synthetic content* disclosure. TikTok posts carry the *AI-generated* label.
- **Approval required.** Every post is a draft first, and Claude must show you the preview before approving.
- **Scheduling.** YouTube uses its own scheduler (fires even if the PC is off). TikTok is posted by a Windows background task.
- **TikTok without waiting for approval.** *Inbox* mode puts the full-quality video in your TikTok app's inbox; you tap Post. Optional *TikTok Studio* browser handoff for direct web posting.
- **Extras.** YouTube tags, custom thumbnails, playlists and categories.

## Install (Windows 10/11)

1. Download or clone this repo, e.g. to `C:\tiny-learners-media`.
2. In PowerShell:
   ```powershell
   cd C:\tiny-learners-media
   powershell -ExecutionPolicy Bypass -File scripts\setup.ps1            # add -WithBrowser for the TikTok Studio fallback
   ```
   This installs uv, ffmpeg and the `tlm` app, opens `config.toml` for your credentials, registers the server with Claude Desktop, and adds a scheduled task.
3. Do the one-time platform setup below, paste the keys into `config.toml`, then run:
   ```powershell
   tlm auth google
   tlm auth tiktok
   tlm doctor
   ```
4. Restart Claude Desktop. You should see the **tiny-learners-media** tools.

## One-time platform setup

### Google (YouTube + Drive)
1. Go to <https://console.cloud.google.com> → create a project (e.g. "Tiny Learners Media").
2. **APIs & Services → Library:** enable **YouTube Data API v3** and **Google Drive API**.
3. **OAuth consent screen:** choose External, fill in the app name and your email, and add yourself as a user. Then **Publish app** to *In production*. In *Testing*, sign-ins expire every 7 days. You'll click through an "unverified app" warning; that's expected for a personal app.
4. **Credentials → Create credentials → OAuth client ID → Desktop app.** Copy the client ID and secret into `[google]` in `config.toml`.
5. Optional: apply for the YouTube API audit so uploads can be public. Until then, YouTube keeps API uploads private and you publish them in Studio.

### TikTok
1. Go to <https://developers.tiktok.com> → **Manage apps → Connect an app**. Choose platform **Desktop**.
2. Add the **Login Kit** and **Content Posting API** products. Turn on **Direct Post** if you want it later.
3. Set the redirect URI to `http://localhost:3455/callback/`. It must match `redirect_uri` in config.
4. Request the scopes `user.info.basic`, `video.upload` and `video.publish`.
5. While the app is unreviewed, use **Sandbox** and add your TikTok account as a target user. Copy the client key and secret into `[tiktok]` in `config.toml`.
6. Submit the app for review when ready. Direct posts stay "Only me" until TikTok audits the app; **inbox mode works either way**.

## Using it with Claude

Things to say:
- "What videos are in my Drive folder `https://drive.google.com/drive/folders/...`?"
- "Check `G:\My Drive\Tiny Learners\ep12.mp4` for YouTube and TikTok."
- "Post it to both. Title: … Description: … Tags: counting, numbers, kids songs. Put it in my *Counting* playlist with thumbnail `G:\...\ep12-thumb.png`."
- "Make the TikTok version vertical and schedule both for Saturday 9am."
- "How's the upload going?" / "Show my last 10 posts." / "Retry the failed one."

MCP tools: `check_setup`, `inspect_video`, `list_drive_videos`, `draft_post`, `update_draft`, `approve_post`, `post_status`, `list_posts`, `cancel_post`, `retry_post`, `tiktok_account_info`, `youtube_playlists`, `open_in_tiktok_studio`.

## Without Claude

```powershell
tlm post "G:\My Drive\Tiny Learners\ep12.mp4" --title "Counting to 10" --platforms youtube tiktok --tiktok-format vertical
tlm status
```

## Where things live

| What | Where |
|---|---|
| Config, sign-in tokens, post history, log | `%APPDATA%\TinyLearnersMedia\` (keep this folder private) |
| Downloaded and optimized video cache | `%LOCALAPPDATA%\TinyLearnersMedia\cache\` (safe to delete) |
| Background worker | Task Scheduler → *TinyLearnersMedia Worker* |

## Development

```bash
uv venv && uv pip install -e ".[dev]"
.venv/bin/python -m pytest      # needs ffmpeg for the media tests
```

Uninstall: `scripts\uninstall.ps1`.
