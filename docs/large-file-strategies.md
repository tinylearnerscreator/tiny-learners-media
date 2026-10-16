# Getting large videos to YouTube and TikTok

## Where the 30 MB wall actually comes from

YouTube and TikTok aren't the problem:

| Platform | Max file | How big files go up |
|---|---|---|
| YouTube Data API v3 | 256 GB / 12 h | Resumable upload session, chunks in multiples of 256 KiB, resumable for about a week |
| TikTok Content Posting API | 4 GB | Sequential chunks of 5–64 MB (final chunk up to 128 MB, at most 1000 chunks), or `PULL_FROM_URL` |

The wall comes from moving the video's bytes through Claude:

- **Chat attachments are capped** at roughly 30 MB.
- **Claude in Chrome passes files as data.** It has to hand the file to the page through the extension, which is why the current `tiktok-cross-post` skill shrinks videos to under 10 MB and loses quality.
- **Hosted MCP connectors and relays** usually want a public URL, or they proxy the bytes themselves.

**The core idea is to send Claude the file's path, never its bytes.** Claude passes a string like `G:\My Drive\Tiny Learners\ep12.mp4` or a Drive link to a local MCP server. That server streams the file from disk straight to Google's or TikTok's upload endpoint. File size stops mattering to Claude.

## Every approach considered

| # | Idea | Status | Notes |
|---|---|---|---|
| 1 | **Local MCP server that takes a path, not bytes** | ✅ built | Core of the app. Claude Desktop launches `tlm serve` over stdio. |
| 2 | **Resumable, chunked uploads** | ✅ built | YouTube: 32 MiB chunks, so memory stays flat even at 50 GB. TikTok: 20 MB chunks, valid whether "MB" means 10^6 or 2^20. |
| 3 | **Crash-proof resume** | ✅ built | The YouTube session URI and byte offset are saved to SQLite after every chunk. If the PC sleeps, Wi-Fi drops or Claude closes, the next run asks YouTube how much it already has and continues from there. |
| 4 | **Background worker as a Windows scheduled task** | ✅ built | Runs every 5 min, independent of Claude. Finishes interrupted uploads and posts scheduled TikToks. A lease system prevents double uploads. |
| 5 | **Google Drive without the size limit** | ✅ built | *Drive for desktop:* a `G:\My Drive\...` path is just a local file. *Drive link:* downloaded with the Drive API using HTTP Range resume, then md5-verified against Drive's checksum. |
| 6 | **TikTok inbox (draft) mode** | ✅ built (default) | Uses the `video.upload` scope. Full-quality upload to your TikTok inbox works before TikTok approves your app; you tap Post in the app. |
| 7 | **TikTok `PULL_FROM_URL`** | ✅ built (opt-in) | If videos also live on a domain you verified with TikTok (e.g. a Cloudflare R2 bucket on your own subdomain), TikTok's servers fetch the file and your PC uploads nothing. Add the prefix to `pull_from_url_prefixes`. |
| 8 | **Browser handoff with Playwright** | ✅ built (optional) | `open_in_tiktok_studio` opens TikTok Studio in Microsoft Edge with a saved login and attaches the file by path, so the browser streams it from disk. No API approval needed; you click Post. |
| 9 | **Re-encode only when necessary** | ✅ built | A valid file uploads untouched. Otherwise x264 CRF 18 / slow / AAC 192k / faststart. Optional 1080×1920 blurred-background vertical version for TikTok. |
| 10 | YouTube native scheduling (`publishAt`) | ✅ built | Uploads now, private, and YouTube flips it public on time even if the PC is off. |
| 11 | Compress to fit under 30 MB | ❌ rejected | This is what the old skill did. It destroys quality. |
| 12 | Cloud relay (worker runs on a small VM / Cloud Run, Drive → YouTube server to server) | 🔜 possible later | Same code works anywhere that has the token file. Lets the PC sleep. Costs a few dollars a month. |
| 13 | Paid relay (Blotato / Metricool) | ➖ alternative | Both take a public media URL and post for you. No developer app approvals, but a subscription and less control (e.g. Blotato's API doesn't support YouTube tags). Metricool is already connected to your Claude account. |
| 14 | Split long videos into parts | ➖ not needed | TikTok's 4 GB / account duration limit is checked up front. Longer episodes go to YouTube only, or as a Short cut. |

## Platform gates to know about

- **YouTube.** Uploads through an *unverified* Google Cloud project created after 28 Jul 2020 are locked to **private** until the project passes Google's API compliance audit. That matches your "post private first" default. Apply for the audit when you want the app to publish publicly by itself. Until then, flip videos public in YouTube Studio.
- **YouTube quota.** The default is 10,000 units/day. Sources disagree on how much one upload costs (100 vs 1,600 units), so check in Cloud Console.
- **YouTube consent screen.** Keep the Google OAuth consent screen in **Production**, not Testing; Testing refresh tokens expire after 7 days.
- **TikTok.** Direct posting needs the `video.publish` scope, and until your app passes TikTok's audit, posts are forced to `SELF_ONLY` (only you). The inbox mode (`video.upload`) avoids this entirely.
- **TikTok sign-in.** TikTok's desktop PKCE uses a **hex** SHA-256 code challenge, not base64url. The redirect URI must be `localhost`/`127.0.0.1` with a port.
- **Disclosures** are on by default: YouTube `selfDeclaredMadeForKids` and `containsSyntheticMedia`, and TikTok `is_aigc`.
