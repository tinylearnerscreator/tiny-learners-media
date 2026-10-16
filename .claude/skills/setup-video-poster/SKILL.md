---
name: setup-video-poster
description: Set up the Tiny Learners Media video poster on Shawn's Windows PC end to end - install it, create the Google Cloud OAuth app and TikTok developer app in the browser, save the keys, and sign in - pausing only for sign-ins, consent clicks and legal acceptances. Use when asked to "set up the video posting app", "do the setup steps for me", or when `tlm doctor` shows missing keys or sign-ins.
---

# Set up the video poster for the user

Goal: the user only **signs in, clicks Allow, and approves** things. You do the rest.
This must run on the user's Windows PC: a Claude Code session there (Claude Desktop's
Code tab, or `claude remote-control` controlled from their phone). It needs a browser
tool: Claude in Chrome (`mcp__claude-in-chrome__*`) or computer use. Load the browser
skill and tools with ToolSearch first. Without a browser tool, run `tlm setup` in a
terminal for the user and guide them through it instead.

## Ground rules
- **Never type the user's passwords or 2FA codes.** At any login page, stop and ask the
  user to sign in in that tab, then continue when they say done.
- **Ask before accepting any terms of service, developer agreement or audit/review
  submission.** Show the user what you're about to agree to, and wait for a yes.
- **Never print, read back or paste secrets into the chat.** Google's key arrives as a
  downloaded JSON file, which `tlm config import-google` reads directly. For TikTok, click
  TikTok's copy button next to the Client secret, then run
  `tlm config tiktok-keys <CLIENT_KEY>`, which reads the secret from the clipboard.
- Use one checklist (TaskCreate) with the phases below, and update it as you go.
- Console UIs change. If a button isn't where this says, look for the equivalent
  and tell the user what you did differently.

## Phase 0 - Install (no approval needed)
1. If the repo isn't on the PC yet: `git clone https://github.com/tinylearnerscreator/tiny-learners-media C:\tiny-learners-media`
   and check out the branch that has `scripts/setup.ps1`.
2. `powershell -ExecutionPolicy Bypass -File scripts\setup.ps1 -Unattended -WithBrowser`
   This installs uv, ffmpeg, the `tlm` app and the scheduled task, and registers the
   server in Claude Desktop. If winget asks for a UAC prompt, tell the user to click **Yes**.
3. `tlm doctor` shows what's left.

## Phase 1 - Google Cloud (YouTube + Drive)
Skip if `tlm doctor` shows `google_client: true`.
1. Open https://console.cloud.google.com/projectcreate. **Checkpoint:** the user signs in
   with the Google account that owns the Tiny Learners YouTube channel.
   First-time Cloud users get a Terms of Service dialog: **ask before accepting.**
2. Create the project "Tiny Learners Media" and make sure it's selected in the top bar.
3. Enable the APIs: open
   https://console.cloud.google.com/apis/library/youtube.googleapis.com and click Enable,
   then https://console.cloud.google.com/apis/library/drive.googleapis.com and click Enable.
4. Consent screen: https://console.cloud.google.com/auth/branding → Get started.
   App name "Tiny Learners Media", user support email = the user's email,
   Audience **External**, contact email = the user's email. **Ask before ticking the
   Google API Services User Data Policy agreement,** then Create.
5. https://console.cloud.google.com/auth/audience → **Publish app** → Confirm. This is
   required, because in "Testing" sign-ins expire every 7 days. No Google review is
   needed for a personal app; ignore any "verification" prompts.
6. https://console.cloud.google.com/auth/clients/create → Application type **Desktop app**,
   name `tlm` → Create → **Download JSON**. It lands in Downloads as `client_secret_*.json`.
7. Run `tlm config import-google`, which finds the newest file in Downloads, checks it and saves it.

## Phase 2 - Sign in to Google
1. Run `tlm auth google` (it waits up to 5 minutes and opens the browser).
2. **Checkpoint:** tell the user: "Pick the account that owns the YouTube channel. You'll
   see 'Google hasn't verified this app'; click **Advanced → Go to Tiny Learners Media
   (unsafe)**, tick all the boxes and click **Continue**. It's your own app." If the
   account has several channels, they pick the Tiny Learners one.
3. The command prints `Signed in to google as <channel>`. Confirm the channel name with the user.

## Phase 3 - TikTok developer app
Skip if `tlm doctor` shows `tiktok_client: true`.
1. Open https://developers.tiktok.com/apps/. **Checkpoint:** the user logs in with the
   TikTok account that posts the videos. If TikTok asks to register as a developer or
   accept the **TikTok Developer Terms**, show them and **ask before accepting.**
2. **Connect an app**: owner = individual (or their organization), app name "Tiny Learners
   Media", category Education/Entertainment, description "Posts our own kids' videos from
   our PC to our TikTok account", platform **Desktop**. Upload an app icon if required
   (ask the user which image to use).
3. Add products: **Login Kit** and **Content Posting API**. Under Content Posting API,
   enable **Direct Post** too, so it's ready after the audit.
4. Login Kit → Redirect URI: `http://localhost:3455/callback/` (exactly that, with the trailing slash).
5. Scopes: `user.info.basic`, `video.upload`, `video.publish`.
6. **Sandbox** (works immediately, no review): create a sandbox, then under Target Users
   add the user's TikTok account. **Checkpoint:** the user may need to accept an
   invite inside the TikTok app on their phone.
7. Open the sandbox's credentials. Read the **Client key** (not secret) from the page.
   Click the **copy** button next to the **Client secret**, then run
   `tlm config tiktok-keys <CLIENT_KEY>`, which validates and saves both.
8. Do NOT click "Submit for review" without asking. Explain: review is only needed for
   *direct public* posting; inbox mode works now. Offer to prepare the review
   submission later (it needs a demo video of the app flow).

## Phase 4 - Sign in to TikTok
1. Run `tlm auth tiktok`. **Checkpoint:** the user logs in if needed and clicks **Authorize**.
2. It prints `Signed in to tiktok as <name>`. Confirm it with the user.

## Phase 5 - Verify
1. `tlm doctor` should show everything true and both accounts signed in.
2. Tell the user to restart Claude Desktop (fully quit from the tray icon) so it loads the
   `tiny-learners-media` tools.
3. Offer a safe test: post a short local clip to YouTube as **private** and to TikTok
   in **inbox** mode, then `tlm status` it. Use `draft_post`, show the preview, and wait
   for the user's approval like any other post.

## Summary to give the user at the end
What was created (project name, OAuth client, TikTok app and sandbox), what's
signed in, and the two optional follow-ups: the YouTube API audit (lets the app post
publicly by itself) and TikTok app review (lets direct posts be public). Until those are
done, YouTube uploads stay private and TikTok goes to the inbox.
