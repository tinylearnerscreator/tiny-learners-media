# Posting videos to YouTube and TikTok

How to upload a Tiny Learners video once setup is done (`tlm doctor` shows everything `true`).

Nothing is ever uploaded without your approval. Every post starts as a **preview**; it only goes
out after you say yes.

## What happens right now (before the platform reviews)

| Platform | What you get today | What unlocks more |
|---|---|---|
| YouTube | Uploads are **private**. Make them public yourself in YouTube Studio. | Google's YouTube API audit lets uploads go public directly. |
| TikTok | The video lands in your **TikTok inbox as a draft**. You finish it in the app. | TikTok app review lets the tool post straight to your profile. |

## Option 1: Ask Claude (easiest)

1. Open **Claude Desktop**. If you just installed or updated, quit it from the tray icon and reopen it first.
2. Tell Claude which video, where to post it, and the details. Examples:
   - "Post `G:\My Drive\Tiny Learners\ep12.mp4` to YouTube and TikTok. Title: Counting to 10. Description: … Tags: counting, numbers, kids songs."
   - "What videos are in my Drive folder `https://drive.google.com/drive/folders/...`?" then "Post the newest one."
   - "Put it in my *Counting* playlist and use `G:\My Drive\Tiny Learners\ep12-thumb.png` as the thumbnail."
   - "Make the TikTok version vertical." (adds a blurred background to a horizontal episode)
   - "Schedule both for Saturday 9am."
3. Claude shows a **preview**: title, description, privacy, kids/AI settings, TikTok mode. Check it.
   - Want changes? Say so ("change the title to …"). Claude updates the preview.
   - Happy with it? Say **"approve"** or **"post it"**.
4. Ask "How's the upload going?" to see progress. When it is done, Claude gives you the YouTube link.

Other things you can say: "Show my last 10 posts", "Retry the failed one", "Cancel that post",
"What playlists do I have?".

## Option 2: Command line (no Claude)

Open PowerShell and run:

```powershell
tlm post "G:\My Drive\Tiny Learners\ep12.mp4" --platforms youtube tiktok --title "Counting to 10" --description "..." --tags counting numbers "kids songs"
```

It prints the preview and asks `Publish this? [y/N]`. Type `y` and press Enter.

Useful options:

| Option | What it does |
|---|---|
| `--platforms youtube` / `tiktok` / `youtube tiktok` | Where to post |
| `--privacy private` / `unlisted` / `public` | YouTube visibility (public only works after the audit) |
| `--caption "..."` | TikTok caption (defaults to the title) |
| `--tiktok-format vertical` | Make a 9:16 version for TikTok from a horizontal video |
| `--at 2026-10-18T09:00` | Schedule (PC local time) |

Check on posts with `tlm status` (last 10) or `tlm status <id>`.

## Finishing on each platform

**YouTube** (while uploads are private)
1. Open [YouTube Studio](https://studio.youtube.com) → **Content**. Short vertical videos (3 minutes or less) are under the **Shorts** tab.
2. Open the video, check it, then set **Visibility** to **Public** (or schedule it) and save.

**TikTok** (inbox mode)
1. On your phone, open TikTok. You get a notification that a video is ready; it is also in your **Inbox** / drafts.
2. Open it, paste the caption (Claude or `tlm status` shows `caption_to_paste`), add sounds or effects if you like, and tap **Post**.

## Where videos can come from

- A file on this PC, including Google Drive for desktop paths like `G:\My Drive\...`
- A Google Drive share link or folder link
- A direct video URL

The tool converts the video for each platform if needed. Downloaded copies are cached in
`%LOCALAPPDATA%\TinyLearnersMedia\cache\` (safe to delete).

## Defaults that are already set

- YouTube: **Made for kids = yes**, **altered/synthetic content disclosure = yes**, category Education.
- TikTok: **AI-generated label = yes**, comments on, duet and stitch off.

Change any of these per post by asking Claude ("turn off the AI label for this one") or in
`%APPDATA%\TinyLearnersMedia\config.toml`.

## Scheduling

- **YouTube** schedules are handled by YouTube itself, so the PC can be off at post time.
- **TikTok** scheduled posts are sent by the background worker (Task Scheduler →
  *TinyLearnersMedia Worker*), so **the PC must be on and signed in** at the scheduled time.

## If something goes wrong

| Problem | Fix |
|---|---|
| Claude doesn't know about posting | Fully quit Claude Desktop from the tray icon and reopen it. |
| "Not signed in" to Google or TikTok | Run `tlm auth google` or `tlm auth tiktok` and sign in again. |
| A post failed | Ask Claude to retry it, or check `tlm status` for the error. |
| Not sure what's wrong | Run `tlm doctor`; every item should be `true`. |
| TikTok inbox draft never arrives | Make sure you're logged in to the **Tiny Learners** TikTok account in the app. |

## Accounts this PC is set up with

- YouTube channel: **Tiny Learners** (tinylearnerscreator@gmail.com)
- TikTok account: **Tiny Learners** (sandbox app "Tiny Learners Media", until TikTok approves the app)
- Policy pages used by both apps: <https://tinylearnerscreator.github.io>
