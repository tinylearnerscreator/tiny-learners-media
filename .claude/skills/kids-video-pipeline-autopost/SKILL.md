---
name: "kids-video-pipeline-autopost"
description: "TEST COPY of kids-video-pipeline that publishes through the Tiny Learners Media posting app: full-quality YouTube and TikTok uploads straight from the PC archive, no Studio clicking and no under-10 MB copies. Use only when the user names kids-video-pipeline-autopost or asks to make a video with the posting app (autopost). Add /report after the skill name for the production and credit report."
---

# Kids Video Pipeline, Autopost (Script → Flow → Narration → Review → Assembly → QA → Package → Publish via posting app → Short → Retrospective)

> **Autopost test copy, maintained separately from `kids-video-pipeline`.** Forked 2026-10-17 from the 2026-10-17 version of `kids-video-pipeline`. Everything is identical except publishing: Step 9 (YouTube upload), 9e (Public flip), 10d (Short upload) and the TikTok cross-post use the Tiny Learners Media posting app (9-route). The retrospective updates **this** skill (`kids-video-pipeline-autopost`), never the original. Lessons that are not about posting can be copied to the original by hand when the user asks.

Cost-conscious, mostly automated pipeline for short kids' education videos (ages 2–6) for the Tiny Learners channel, plus a companion YouTube Short. Tools: **Google Flow (Veo 3.1)** (meta.ai as fallback), **Kokoro TTS** for narration, **ffmpeg** for review frames, assembly and QA, **Claude in Chrome** for generation, TTS and YouTube Studio. (Condensed rebuild 2026-10-12, updated 2026-10-13 and 2026-10-14 with the PC archive layout and the Video 65 and 66 lessons, and 2026-10-17 with native 9:16 Shorts as the standard, from the Video 64 to 71 Short regeneration. The full prior text is in `claude/kids_video_pipeline_SKILL_v63_proposed_2026-10-12.md` and `claude/kids_video_pipeline_skill_backup_2026-10-12_0921.md`.)

## Report mode: `/report` (added 2026-10-15)

When the user invokes the skill with `/report` after its name (for example "/kids-video-pipeline /report", "kids video pipeline /report" or "run the video report"), do not start a video. Build a read-only view of what has been produced, when, and what it cost. No Flow generation, no uploads, no registry claims, no credit spending, no questions.

**Source of truth:** `claude/flow_credit_ledger.md` (read it with `project_read`).
- Part 1: account balances, refresh times, "Read at" and "Notes" (a "not re-read" note means the balance is an estimate).
- Part 2: the video production log (one row per video asset: Video, Name, Type Long or Short, Date created, Credits used, Accounts used, Scenes and retries, Notes).
- Part 3: the TikTok post log (Video, Name, Type, Date posted, File, Status, Notes) and its post count line.
Also read the totals line under Part 2. Use `claude/channel_registry.md` only to fill a missing video name or to count published videos, and only when the user asks for channel-wide numbers (it is very large).

**What the report shows (build all of it from the ledger rows, never from memory):**
1. Headline numbers: videos logged (long and Short counts), total credits recorded, average credits per long video that has a number, newest video, date range covered.
2. Production table: one row per Part 2 row, newest first, with Video, Name, Type, Date created, Credits, Accounts, Scenes and retries, and Notes.
3. Credits by day (sum of recorded numbers per Date created) and credits by account where the Accounts column names a split (for example "sanull.pass (S1 to S5, 50)"). Sum only numbers that are written down.
4. Credits by video as a simple bar view, longest first.
5. Account balances and next refresh times from Part 1, with the "Read at" time and a flag on any row whose Notes say "not re-read" or whose Read at time is older than its refresh time (stale, read live before relying on it).
6. TikTok posts: total from the count line, rows by Type, and how many are still "Content under review" or "review status not yet re-checked".
7. Gaps: list every row that says "not recorded" so the user can see what is missing. Never estimate or fill a gap. Say plainly that "not recorded" credits are excluded from the totals and averages, and that the ledger only starts at Video 62 (earlier videos are in the registry, without credits).

**Format:** build a self-contained HTML page and publish it as an artifact (a Dashboard artifact type if Artifact lists one, otherwise a hand-built page that follows the artifact design rules: light and dark theme tokens, readable at phone width). Put the headline numbers and the tables first. Add a one-paragraph plain-language summary in the reply with the artifact card, and keep the reply short. If the user asks for a different view (one video, one account, a date range such as "last 7 days", or "credits only"), filter the same rows and say what filter was used. A request for a file ("give me a csv") gets a csv or xlsx from the same rows instead of a page.

**Rules:** the ledger is append-only history, so the report never edits it. If a Part 2 row is missing for a video the registry says exists after Video 62, say so in the Gaps list. If the ledger doc cannot be read, say that and stop. Re-running the report always re-reads the ledger, because rows are added at the end of each run. A report run may be asked mid-pipeline: answer it, then continue the pipeline where it stopped.

## Rules that apply to every run

0a. **Registry first:** read the registry, claim the next video number, check the topic for duplicates (1-pre).
0b. **Host:** Ellie the Elephant (animals; archaeologist-hat variant for history/dinosaurs; plain Ellie for earth science) or Stella the Star (space). Use the locked character bible (1a).
0c. **Style:** use the locked style phrase from `claude/channel_visual_style_bible.md` (1b).
0d. **Autonomy.** Once the user starts the skill on a topic, run Steps 1–10 end to end with no questions and no pauses. Only three human gates: (a) **The posting OK**: one question per video showing the posting app's previews for the main video and Short (9-drafts). (b) **Public visibility** needs explicit per-video authorization in chat (9e). (c) **The 10f question** once the main video and Short are both Private. Everything else is decided by Claude and logged in the package or progress doc.
0e. **Pre-authorized, never ask:**
   - Topic: if none given, take the next unused topic from the category rotation (registry duplicate check) and say which in one line.
   - Accounts: any logged-in Google account may spend Flow credits (including sanull@gmail.com), highest balance first after a fresh sweep (start from the ledger, 3a-pre item 0). Never type passwords, buy credits, or create accounts. **Always move on to the next account by yourself** when the current one is out of credits, rejects a submission, or does not deliver downloads. Never stop to ask or report "out of credits" while any connected browser's account is still untried (standing user instruction, 2026-10-13). Stop only after a fresh sweep of every account still reads zero (3a-pre item 6).
   - Browsers: pick by deviceId, confirm the account by content.
   - Retries: up to 3 per scene. Accept and log known quirks (eyelash drift, faint Sun marks, small ring defects).
   - All credits at 0: schedule a resume with `send_later` (3a-pre) and keep going.
   - Packaging and drafting: title, description, tags, thumbnail, playlist, Made for Kids Yes, AI disclosure No, paid promotion No, Private. The upload itself waits for the one posting OK (9-drafts), because the posting app never uploads without the user's OK on its preview. On Route C (Chrome fallback) the upload stays pre-authorized as in the original skill.
   - Flow downloads, uploads of the pipeline's own files, registry and project docs, and the Step 11/12 retrospective.
   Still ask only for: Public visibility, passwords or payment details, new accounts, permanent deletes, anything not covered here.
0f. **Archive every deliverable on the PC as you go (required, added 2026-10-14).** See "PC archive layout" below. A video is not done until its folder holds the raw clips, narration, master, Short and upload copies. Finished files that live only in the cloud workspace are lost when the session ends (this is how the full-quality Shorts for Videos 62 and 63 were lost, so TikTok had to get 360p copies).

Steps: 1 Script, 2 Prompts, 3 Generate (3d ends with the credit ledger and production log), 4 Frame review, 5 Retry, 6 Assemble, 7 QA, 8 Package, 9 Publish Private, 10 Short, 11 Retrospective, 12 Backup and log.

## PC archive layout (required for every video)

One folder per video on the linked PC, never loose files in Downloads root:

```
Downloads\TinyLearners\videoNN\
  raw\      Flow clips s1.mp4 … s10.mp4 (720p originals, renamed from Flow's captions at once)
  audio\    Kokoro narration pieces n1.wav … (plus n9a.wav-style recap pieces)
  master\   the full video at full quality (final_vNN.mp4 or videoNN_main.mp4)
  short\    the 1080x1920 Short at full quality (short_final.mp4 or videoNN_short.mp4)
  upload\   thumb_vNN.jpg, plus under-10 MB copies (upload_main.mp4, upload_short.mp4, ttNN.mp4) only when posting falls back to Chrome (Route C)
  MANIFEST.txt   what is in each folder and what is missing
```

From the cloud shell the same place is `$HOME/mnt/Downloads/TinyLearners/videoNN` inside `device_bash`, and `C:\Users\Dad\Downloads\TinyLearners\videoNN` for `device_stage_files`. Rules:
- **Create the five folders at Step 3, before the first download**, and copy each step's output there before moving on: raw clips after 3a (rename to sN.mp4), narration after 3c, master after Step 7 passes, Short after 10c/10d, upload copies and thumbnail after Step 8 and 10d. Work in the cloud, but the PC folder is the system of record.
- Copy with `device_stage_files` / `device_commit_files`. Never commit a raw binary by `stagedPath` (Video 65's files came out 5,875 bytes too large). Send the file with `SendUserFile` (30 MiB per file) and commit it by `fileUuid`, then check `md5sum`. Re-encode a bigger master at crf 23 for the archive copy and note it in MANIFEST. Or build directly on the PC with `device_bash` ffmpeg when a file is already there. Verify each copy with `ls -l` or `ffprobe`.
- Never leave a Short only on YouTube. Re-downloading from YouTube gives 360p at best, and Studio's Download button produced no file. TikTok and any other cross-post must come from `short\`.
- Keep files that are known-bad (OLD, stale, first-pass) out of these five folders. Park them in a `_old` folder inside the video folder if they are worth keeping.
- At the end of the run write `MANIFEST.txt` (file names and sizes per folder, plus a `MISSING:` line) and list any gap in the progress doc. Videos 50–64 were sorted into this layout on 2026-10-14 by copy (originals untouched). Video 59 has no master or Short file on the PC, 61 has no master or audio, 62 has raw clips only (no master, Short or audio), 63 has raw clips only, 64 has no raw clips or audio. Rebuild a missing piece from the raw clips only when the user asks.
- Older videos 1–49 are not in this layout. Do not retrofit unless asked.

---

## Step 1: Script

- ~3 minutes, INTRO / 2–3 SECTIONS / OUTRO. Ages 2–6: simple words, short sentences, repetition. Confirm nothing with the user: default to the registry's next topic (0e).
- **Open on the hook, not the host.** Intro under 3 seconds, opening mid-fact or mid-question. Put the single most surprising of the planned "5 fun facts" in the first 5 seconds of narration (the closer recaps it). Host greeting comes right after the hook. Put a 3–6 word on-screen hook line in Scene 1's `[SCENE: ...]` direction. It is burned in at Step 6, never generated.
- `[SCENE: ...]` directions go in brackets and are not read aloud. VOICEOVER is split into short pieces, about one per scene (Kokoro limit ~500 characters).
- Close with a "5 fun facts" recap and a subscribe CTA.
- Alphabet/phonics videos use the ABC format (letter, sound, word, "Grow the Scene", milestone mascot every 5 letters, sections A–E/F–J/K–O/P–T/U–Z).
- **Onomatopoeia screen (before 3c):** Kokoro spells out written sounds ("Shh" becomes "ess aitch aitch"). Reword "Shh", "Sss", "Grr", "Zzz", "Psst" into descriptive sentences.

### 1-pre. Shared channel registry

- Lives in project doc `claude/channel_registry.md` (a Drive Google Doc "Tiny Learners - Channel Registry" may also exist, find it with `search_files`. Trust whichever has the higher Video Log number and tell the user if they disagree). Also read any `claude/channel_registry_videoNN_row_pending.md` docs: those videos are taken and their rows are not merged yet.
- Next number = 1 + highest Video Log number, skipping numbers under an open Claim you don't own. Flag topic duplicates. For a near-duplicate, lead the title and thumbnail with the differentiating angle and note the overlap in the package doc.
- Claim before generating: re-read right before writing, add a Claims row (number, topic, category, claimant, time), write the whole doc back (full replace only). A recent Claim without a Video Log row means the number is taken. A stale-looking Claim is surfaced to the user, not reclaimed.
- Status can drift (videos were found Public while the registry said Private): verify live state in Studio before any batch visibility change.
- Release the claim in 10e.

### 1a. Channel hosts (new videos only, never retrofit)

- **Ellie the Elephant**, voice **af_bella**: animal facts. Archaeologist-hat variant for history, ancient history, dinosaurs. Plain Ellie for current earth science. **Stella the Star**, voice **af_sky**: space (and space-driven atmospheric topics such as the Northern Lights).
- The host is written into the script (greeting after the hook, transitions, outro CTA), not a logo bumper. Before scripting read `claude/host_ellie_character_bible.md`, `claude/host_ellie_history_character_bible.md` or `claude/host_stella_character_bible.md` and reuse the locked description verbatim in every scene prompt. If none exists, this video establishes it (3a-char). Only change it on an explicit redesign request.
- Known: Stella renders often show eyelashes despite the bible. Stronger wording does not fix it, so don't spend retries on it.
- The recurring character's establishing scene is Scene 1 (or the first generated).
- Relative positioning of two subjects (head-to-tail, back-to-back) resists prompts. Accept a simpler face-to-face composition if wholesome.

**Generic-default risks.** Name the real form and negate the look-alike:
- A solo named planet or landmark renders as its nearest look-alike (Uranus became Earth until the prompt said "no continents, landmasses, oceans, clouds").
- Technology described generically ("a friendly satellite") renders as a UFO. Describe the real form ("boxy metallic body, two flat solar panel wings, no dome, no flying-saucer shape").
- Objects topped with animal heads (canopic jars) become characters: negate body, arms, legs, paws, fur, feathers.
- **The Sun** defaults to a cartoon face. Use "a big realistic photographic-style plain textured ball of fire, a blazing star surface with swirling flames, absolutely no face, no eyes, no mouth, no smile". Budget up to three takes. Prefer the Sun plus two or three planets per scene and let narration list the rest.
- A "spinning planet" or day/night scene triggers ring/halo defects: describe the planet as static and let narration carry the rotation.
- Plants: "glowing lily pads" became lotus flowers. Say "flat round green lily pad leaves lying on the water, no flowers, no petals".
- A species must stay consistent across scenes: name its color and type in every prompt and negate the common alternative ("small brown owl with a tan face, not a white snowy owl").

### 1b. Channel visual style

Locked phrases: **"3D Pixar-style animation, bright vibrant colors, cute friendly characters, dreamy cosmic lighting"** (space) and **"...macro cinematic lighting"** (other categories). Check `claude/channel_visual_style_bible.md` before writing prompts and reuse verbatim. Never infer the style from a prior video's prompts (Videos 25/26 drifted to "flat vector illustration" that way). Change only on an explicit user request.

## Step 2: Prompts

- One short prompt per `[SCENE: ...]` (subject, setting, style, mood), the locked style phrase in every prompt, numbered in generation order. Hosts use their bible text verbatim. A non-host recurring character uses a placeholder until Scene 1 is locked.
- **Never ask Flow or meta.ai to render text** (hook text, numerals, labels) or UI graphics (subscribe button, bell, like icon, even "soft"). Both are composited in Step 6.
- A numbered board with "blank" slots needs an explicit negative ("no numbers, numerals, digits, or any text or symbols visible on the board anywhere") and a retry budget.

## Step 3: Generation

Create the video's PC archive folders now (see PC archive layout).

### 3a-pre. Inventory accounts and credits (no questions)

0. **Read the ledger first: `claude/flow_credit_ledger.md`** (added 2026-10-14). It holds every account's last balance, its daily refresh time, when it was read and which browser held it. Use it to decide the order to poll and to skip waiting: an account whose refresh time has passed since its "Read at" time has probably refilled. The ledger is a hint, never a balance: always confirm with a live read before spending (credits refresh and get spent by other sessions).
1. `list_connected_browsers`, then `select_browser` on each deviceId from Browser 1 numerically. Open a Flow project in that browser (credits show only inside an open project, not on the Flow home grid), click the avatar at the top right (about 1517,30 on a 1568 frame), **do not take a screenshot afterwards** (the tab freezes, so use `find`), then `find` "Google Flow credits number and account email in account popup" and `find` "Credits refresh daily at". Read the email and refresh time as well as the number (Video 66 and the 2026-10-14 poll). Never infer identity from the "Browser N" label. An account out of credits shows "You're out of Google Flow credits" and may show no refresh time.
2. Record `email → balance → refresh time → deviceId` in `accounts.md` and key everything by email, because labels and deviceIds drift. The live inventory is session-scoped. Carry forward only the refresh times and the ledger as hints.
3. Spend the highest balances first. Veo 3.1 Lite costs 10 credits per scene (Fast costs 20). Log which account made which scene.
4. **Test downloads early.** Only some browsers deliver files to the user's PC (Video 63: Browsers 1, 5, 13 did. 2, 3 and the channel owner's 4 did not, which wasted about 40 credits). Download one clip per browser right after its first generation, check the PC's Downloads with `device_list_dir` (sort by `mtimeMs`) and `device_stage_files`, and generate on a browser that lands files.
5. **Fallback, no pause, no question.** Always move to the next account yourself (0e). If an account can't afford the next scene or a submission returns 0% after a "Not enough credits" toast (the toast can appear and still succeed, so check All Media), move to the next account by balance, re-set the model and project settings there, and keep the prompt identical.
6. **Before declaring every account exhausted, re-sweep every balance, every time** (credits refresh mid-session). If a fresh sweep still reads near zero: read each account's refresh time from its panel, record them in the progress doc, do all credit-free work (narration, downloads, 3a-verify, registry, docs), then `send_later` a resume shortly after the earliest refresh time in the ledger (or the panel) naming the progress doc and saying to re-sweep first. Never use the local cron tools (they die with the session). Tell the user the refresh and resume times.
7. Never close the first tab of a browser's tab group (it kills the group). Recreate with `tabs_context_mcp{createIfEmpty:true}`.

### 3a. Google Flow (Veo 3.1) — preferred

- Credits are per account per day. Flow auth is separate from the browser's Google account: to switch, sign out of Flow and pick the account in Google's chooser. Project URLs are account-scoped ("Application error" usually means account mismatch: go to the Flow root and click in).
- **Check the model before every submission and retry** (screenshot the composer): it must read a Veo 3.1 variant. Some accounts default to "Omni 1.1 Flash", which renders photorealistic.
- Some accounts only offer an "Agent" composer: prefix "Generate an 8-second video (not an image):" and check the Agent toggle before submitting. Agent accounts can hit a separate daily quota (switch accounts or wait). On the 1568x726 frame (an account with a shorter page, jhancock.spam in Video 70) the composer sits higher: text box about (700,641), send (1001,679), settings chip (925,678). Screenshot the composer once on every new browser before the first click instead of reusing the 772-high coordinates.
- Confirm a click landed on the bottom composer bar, not an existing tile's edit panel, before typing.
- Resolution varies by account (640x360 or 1280x720). `ffprobe` every raw clip.
- **Download:** right-click the tile in the grid, Download, **720p / Original Size** (never the 270p GIF or credit-costing upgrades). The file lands named from Flow's caption with a timestamp, so `mv -n` it to `sN.mp4` at once **and into `videoNN\raw`** (PC archive layout). Tiles are newest-first and captions are not scene numbers, so map tiles to scenes by looking. Alternatives: the row's "Download batch" icon (a zip, unzip and delete it. On the Video 66 run the row icon made zips on one browser while right-click Download landed named files on another) or the toolbar icon on a selected clip. **The context menu moves as tiles finish rendering: screenshot right before the Download click** (a stale position once hit the wrong item in Video 66). Verify with a broad `find -newermt` sweep.
- **Content filter** ("third-party content") rejects at no charge: reword and resubmit. Avoid "No text/letters/numbers" phrasing. Examples that failed then passed: "friendly cartoon owl perched" → "small cute brown owl sitting on a tree branch". "waves goodbye happily" beside Stella → "cheerfully waves one little hand". Also passed: "dark round spots" → "darker patches", "cheerfully waves" → "lifting one little hand in a gentle hello". A counted-row scene (Video 66 S9, five snowballs beside the host) was rejected once: reword the host's action, keep the exact-count wording.
- **Never type two prompts back to back.** Confirm the first prompt's submit (a tile appears) before the next. In Video 65 two prompts merged in the box and the merged prompt failed. Clear the box with ctrl+a before retyping.
- A stuck black player is not proof the render is corrupt (check Downloads). A frozen tab ("renderer may be frozen", also seen on Studio edit pages right after a click): open a fresh tab at the Flow or Studio URL, or use `read_page` + `find` + ref clicks instead of screenshots.
- A downloaded clip can be byte-identical to another scene's: checksum against neighbors and regenerate on a different account.
- If Flow is unavailable use meta.ai (3b).

### 3a-verify. Content check on every raw clip before assembly

Pull one frame per scene (`ffmpeg -ss <t> -i f.mp4 -frames:v 1 -update 1 out.png`) and compare it to that scene's own prompt. A correctly named, correctly sized file can hold the wrong footage (Video 36 shipped an unrelated fox and robot). A checksum does not catch this.

**Countable-details check (mandatory, added after Video 64).** Any number written in the script, narration or prompt is a fact the picture must match: "five fun facts" with five lights or stars, "three planets", "two moons". For every scene whose prompt or narration states a count, extract at least 5 frames across the whole 8 seconds (`-ss 0.5,2,3.5,5,6.5,7.7`), tile them into one contact sheet, **count the objects in each frame out loud in the progress doc** ("S9: 5,5,5,5,5,5, script says 5"), and compare to the script. A count that differs in any frame fails the scene. A glance that decides "looks like a row of stars" is not a count: Video 57 S9 and Video 64 S9 both shipped four stars where the narration said five, and Video 64's miss reached Public because the review checked style and character but never counted. Prompt wording that gave a stable five: "exactly five small softly glowing yellow stars arranged in one neat horizontal row beside her, evenly spaced, five separate stars side by side, exactly five and not four, no other stars in the row". Add the count to the Step 7 final pass too: pull a frame from the assembled master at each counted scene and recount.

### 3a-char. Locking a recurring character

Each Flow account renders a short phrase differently, so: generate Scene 1 alone first, extract a clear front or 3/4 frame, write an exhaustive literal description as rendered (hair, skin, eyes, each garment and color, shoes, apparent age and gender) into `character_bible.md`, and use it word for word in every later scene on every account. If Scene 1 is retried and the look changes, update the lock first. Same on meta.ai.
- **Progressive drift** (clean frame 0, eyelashes later) does not respond to stronger wording. One reworded retry, then accept the clip or use reference-image locking.
- **Reference-image locking** (Flow's Characters panel) cannot be automated (no file input, native picker). It is a manual opt-in: ask the user to upload one clean reference frame per account, and keep the text lock as the baseline.

### 3d. End-of-generation credit ledger and video production log (required, added 2026-10-14)

`claude/flow_credit_ledger.md` has three parts: the account balances table, the video production log (YouTube videos) and the TikTok post log (the tiktok-cross-post skill fills that one). Update the first two at the end of generation. If the run ends late and a full re-poll of every browser is not practical, still rewrite Part 1 for the accounts you spent from (estimate = read balance minus scenes x 10), keep the other rows, and write "not re-read" in each row's Notes so the next run knows to read live. Never leave Part 1 stale without that note (Video 68).

Part 1, account balances. When the last scene is generated and downloaded (and again after any retries that spend credits), **re-poll every connected Flow account** with the 3a-pre item 1 method and rewrite the balances table (one row per email): balance, "Credits refresh daily at" time, read-at date and time (Eastern), browser label and deviceId, and a note (out of credits, delivers downloads or not, usage limit hit). Add the "next likely refresh order" line. The next video's 3a-pre starts from this file. Do this even when you stop early because credits ran out. Replace old balance values rather than appending a history.

Part 2, video production log (append only, never delete rows). One table with one row per video asset and these stable columns: Video, Name, Type (Long or Short), Date created, Credits used, Accounts used, Scenes and retries, Notes. Date created is the Eastern day generation finished. Add the row for the main video at the end of generation and the row for its Short at Step 10. Count credits from the balance drop per account (balance before the first scene minus balance at the 3d poll, adjusting for any refresh that happened mid-run), or from scenes times cost (10 for Veo 3.1 Lite, 20 for Fast) plus retries when a balance drop is not readable. Say which method you used in Notes. A Short built from the main video's footage uses 0 credits. A scene reused from another scene uses 0. Mark an unknown number "not recorded" and never guess. Keep the totals line under the table current (videos, long count, short count, total credits recorded). The user reports on this table, so keep column names stable. Write the file with `project_write` and `local_path` (full replace, so read it first and keep every existing row, including the TikTok post log).

### 3b. meta.ai fallback

Same locking rules. Confirm typed text landed before Send. Still image + Animate works without Flow credits but outputs 1080x720, so Step 6 must normalize resolution.

### 3c. Narration — Kokoro TTS

**Fresh-audio rule (Video 55).** Narration files must be generated in this video's session and carry this video's script. Before assembly run a speech check on every file (offline `pocketsphinx`, 16 kHz mono wav, `python3 -I`, compare to the script line, threshold 0.45), always including N1, because Video 55 shipped an old frog outro as the opening line ("thanks for joining") from a stale download, and an md5 check only compared files within the same video. Also listen to the first 3 seconds of every master and Short. **Copy the verified narration wavs into `videoNN\audio` on the PC** so a rebuild never needs new TTS.

Narration runs on `https://hexgrad-kokoro-tts.hf.space/` (the raw Space host, not the huggingface.co wrapper). Voices: **af_bella** (Ellie), **af_sky** (Stella). Pieces under ~500 characters, about one per scene, after the onomatopoeia screen.

**Fast path (Videos 58, 61, 63), use this first.** From one tab on the Space, run `javascript_tool` that POSTs `/gradio_api/queue/join` with `{data:[text,'af_sky',1,true],fn_index:4,session_hash:sh,event_data:null,trigger_id:2}` (`sh` a random string, `Content-Type: application/json`), then reads `fetch('/gradio_api/queue/data?session_hash='+sh)` and regexes the stream for `"url":"([^"]+audio\.wav)"`. Send 3–5 pieces per call with `Promise.all` (own `sh` each), about 15s per call, keeping every call under ~35s. Download from the cloud shell with `curl -sS -o nN.wav '<url>'` (test one curl first, hf.space is normally reachable). If a call returns no URL, reload the Space tab and retry once. md5 every file against its neighbors (a download can silently repeat the previous audio), `ffprobe` every duration, name files by scene number, and then **run the speech check below on every file**.

**Speech check (mandatory, added after Video 55).** Video 55's first narration file held the previous video's outro ("Thank you for visiting the pond with me, subscribe...") instead of the owl hook, so the main video and the Short both opened by thanking viewers as if the video had ended. Kokoro's download can return the last generation's file, and an md5 compared only within the same video cannot see a file left over from another session. Fix: transcribe every narration wav offline and compare it to its script text before any assembly. `pip install --break-system-packages pocketsphinx`, then per file: `ffmpeg -y -i nN.wav -ar 16000 -ac 1 /tmp/nN.wav` and `from pocketsphinx import Pocketsphinx; p=Pocketsphinx(); p.decode(audio_file='/tmp/nN.wav'); print(p.hypothesis())` (run with `python3 -I`). Score = share of the script's words found in the transcript. Below ~0.45 is a mismatch: regenerate that piece. Accuracy is rough ("Ellie" comes out as "alley"). Short fact-recap pieces (one sentence) throw false flags, so treat N1 and the outro as the hard gate and, for a recap piece under the threshold, check that its key nouns appear and listen to it before regenerating (Video 66). A piece whose transcript begins "thank you", "subscribe", "see you next time" or "bye bye" must be the outro and nothing else. Run the same check on N1 of every video as a hard gate, because N1 is the hook. If narration is generated from the cloud shell, the Kokoro API call (`/gradio_api/queue/join`, voice name in `data[1]`) also works from Python `urllib` with no browser (Video 64 and the Video 55 fix did this).

**UI fallback** if the API path fails: one generation tab (click input, `ctrl+a`, type, click Generate twice 2s apart, since the first click often only blurs the input) and one download tab that only navigates to the `gradio_api/file=/tmp/gradio/<hash>/audio.wav` URL from the DOM. Detect completion by a **new** `audio.wav` hash in the DOM, not the token counter. A freshly loaded page hydrates late, so redo early clicks. Keep the Kokoro tab in front (background tabs throttle and stall). On "ZeroGPU runs limit exceeded → Retrying with CPU" each piece takes 1–5 minutes, so overlap downloading with the next generation. For "Cannot access chrome-extension://" or "Detached while handling command" errors persisting after 2 retries, restart the tab (or the whole tab group). Keep each `browser_batch` to about 50 seconds of waits. "Completed" does not prove a file exists: confirm with `find -newermt` plus `ffprobe`.

## Step 4: Free frame-based review

Get the clip on disk, extract frames (`ffmpeg -i clip.mp4 -vf fps=0.5 frames_sceneN/frame_%03d.png`, `fps=1` for fast scenes, a single still needs `-update 1`), and view every frame. Frames miss motion and audio problems (Step 7). Check:
- Nothing frightening or intense. Clear subject focus. Age-appropriate pacing. Subject fills a reasonable share of the frame.
- Style matches the locked phrase (1b). Footage matches the scene direction (3a-verify). Hosts match their bible and recurring characters are consistent across the whole set (surface an outlier to the user: regenerate or accept).
- **Counts match the script (3a-verify countable-details check): written count per frame, not an impression.**
- Every fact in a "5 fun facts" recap has its own matching cutaway (6h).
- No garbled text, artifacts, broken limbs. Intrusions and drift can appear partway through any clip, so scrutinize the full clip.
- No pillarboxing or letterboxing in any frame.
- An alternate but wholesome composition is not a failure. Minor cross-account variance is fine, and is no license to change the style phrase.
- Treat a first-pass sign-off as provisional when anything looks ambiguous (a ring artifact and a literal subscribe button were once wrongly cleared). Re-check across several frames.

## Step 5: Retry loop

- Rewrite only the failing scene's prompt (a character mismatch resubmits the exact locked description). Cap at **3 attempts per scene** (2 for a relative-positioning miss with an acceptable alternate), then hand back the best version with a note.
- A defect that survives a wording-only retry may need a changed composition (explicit split-screen), not louder wording. Progressive host drift: see 3a-char.
- A clean early window can rescue a clip: trim to it and freeze-extend the last good frame.
- An unexplained generation error is best resolved by switching accounts within the same cap.
- A short download count needs diagnosis: a PIL contact sheet cross-referenced with the prompts shows what is missing.

## Step 6: Assemble

Core assembly is always required. 6a–6e are optional on request.

**One-script build (Videos 62, 63):** a single `build.py` or `build.sh` builds every segment, then concatenates. Per segment: `scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,fps=24,setsar=1` (**normalize every clip's resolution unconditionally**: a concat inherits the first clip's resolution silently), drop the clip's own audio (`-map` only the narration), then pad or trim to narration + ~0.25–0.3s. Compute durations in Python (`f"{v:.3f}"`), not `bc` (it drops the leading zero and breaks `tpad`). Use `-preset veryfast` for segment and master encodes: slower presets timed out the cloud shell call in Video 66 (use `timeout` near 600000 ms for a full build).

**Pad method by length:**
- **Under ~2s:** `tpad=stop_mode=clone:stop_duration=<extra>` plus `apad=whole_dur=<target>` on the audio and `-shortest`. `stop_duration` is the padding to add, not the total: `max(0, target - original + margin)`. If the clip is already longer than the narration, pad only the audio and trim. A gap under ~0.5s can make `tpad` fail ("Failed to inject frame"): use plain trim with `apad`.
- **Over ~2s:** Ken Burns zoom on a held frame, because a long freeze reads as a stall. Extract the held frame (`-sseof -0.1`), `zoompan=z='min(zoom+(<zoomend>-1)/<frames>,<zoomend>)':d=<frames>:s=1280x720:fps=30` for `<pad>` seconds, concat to the clip (video only), then mux the narration. `<zoomend>` ≈ 1.0 + 0.05*(pad/6), capped near 1.10, and **`<frames>` must equal that pad's own duration × fps** (a borrowed value left ~15s static once). **Pick the held frame, not the literal last one**: sample 3–5 frames from the last second and choose one with eyes open and a natural pose.
- **Slow stretch** for 1–3s pads on calm scenes: `setpts=<narr+0.3>/8*PTS,minterpolate=fps=24:mi_mode=blend`. Re-run the repeated-frame test afterwards.
- **Multi-shot or fast-cut scene:** loop with a continuous `zoompan` keyed to the output frame counter. A raw `-stream_loop` with no drift is a defect.
- After assembly check holds: `freezedetect=n=-30dB:d=1.5`. A literal `tpad` freeze over ~2s must become a zoom.

Then: concat demuxer for all segments. **Burn the Step 1 hook text into Scene 1 before concatenating** (`drawtext` with box or heavy stroke, e.g. Poppins-Bold at `/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf`, fontsize ~84, `enable='between(t,0.3,4.3)'`, `y=h-170`), visible by 1s and held 2–4s, clear of the host's face. Keep every `seg_N.mp4` for the Short (they carry pre-QA audio). Finish with `-c copy -movflags +faststart`.

ffmpeg gotchas: output flags placed after the output filename are ignored (verify with `ffprobe`, not the exit code). **`loudnorm` on a stereo master:** put `aformat=channel_layouts=stereo` before `loudnorm` and `aformat=sample_rates=48000:channel_layouts=stereo` after it (a trailing `aresample` raises "Cannot select channel layout"). Two-pass with `measured_*` values and `linear=true` hits -16.0 LUFS and the exact peak target. Combining `-t` with `tpad`+`drawtext` in one `-vf` chain can silently yield only the trimmed length: trim in pass 1, pad and overlay in pass 2. A `drawtext` expression mixing `iw` and `text_w` may fail to parse: use fixed pixel coordinates. Without delete permission on a connected folder, `rm`/`mv` fail: use `cp` and `-y`.

**Narration sync:** keep per-scene TTS files as the source of truth, never rebuild by splicing silence into a prior export. Find each piece's speech end with `silencedetect=noise=-35dB:d=0.1` (last `silence_start`), set clip length to at least `last_speech_end + 0.4–0.5s`, extend by freeze never by trimming narration, compute absolute starts as a cumulative sum in one script, and build master audio in one pass with `adelay` per file and `amix=inputs=N:normalize=0`.

**6h. Facts-recap scenes:** split each fact into its own narration piece (`scene12a`…`f`), join with short silence gaps, and drive numeral timing from the running sum of piece durations. **Every fact gets its own visual cutaway matching that fact**, trimmed to its narration with a numeral badge (start each cutaway ~3s into its clip so it differs from the main scene, and avoid a blink on its first frame). One static host shot for the whole recap is a content defect. Verify each cutaway's footage against its own fact text. Place numerals in a bottom band clear of the host's head. Numerals on a facts board: generate blank slots with an explicit negative and composite 1–5 with `drawtext`.

**Optional real-footage layer (6a–6e), on request only:** list every scene (including intro and outro) in a todo list first. Photos: `https://commons.wikimedia.org/wiki/Special:FilePath/<Exact_File_Name.ext>` (public-domain or CC0 only, JS anchor download in a fresh tab). Zooming animated scenes: no flat percentage crops, find the subject bounding box (largest dense component), pad 12–15%, verify visually, then `crop` and `scale`. Real-photo pan/zoom that can't crop the subject: blurred cover background plus foreground fit inside ~87.5%, `zoompan` capped at ≈1.143. Crossfades: `xfade` ~0.3s with `offset = first_clip_duration - crossfade_duration`, re-encoding inputs to one fps and timescale. A hard cut is valid.

## Step 7: Audio/video QA (every time)

1. **Clicks:** decode to PCM and flag `abs(diff) > 15000` jumps (clusters at splice points are artifacts, scattered ones are usually consonants). Every `silence_end` equals a computed scene start. Listen for spelled-out sound effects.
2. **Loudness:** `ffmpeg -i final.mp4 -af loudnorm=print_format=json -f null -`. Target ~-16 LUFS, true peak under ~-1.5 dBTP (at or above -0.5 dBTP is a hard blocker). Use `loudnorm=I=-16:TP=-2.0:LRA=11` on the master, because the later AAC re-encode raises the peak by ~0.7 dB. After any `loudnorm` re-encode `ffprobe` the sample rate and force `-ar 48000` (it has come out at 96 kHz). If a stereo second pass fails with "Cannot select channel layout", put `aformat=channel_layouts=stereo` ahead of `loudnorm`.
3. **Spec:** H.264, `yuv420p`, AAC, constant frame rate, faststart, and master resolution 1280x720 via `ffprobe` (backstop for the per-clip check).
4. **Repeated frames** (any scene over ~1.5x its source length, and every Short's final file): extract `fps=1` frames and hash them. An exact duplicate recurring at the source clip's length means a naive loop: rebuild with zoom-pad.
5. **Expression check** on every zoom-pad and recap cutaway: sample 2–3 frames and confirm eyes open and a natural pose (the hash test passes on a closed-eye hold). Fix by starting later in the source (`ss=5.0`) or choosing another frame.
6. **Retention check:** first spoken line and visuals within 3s, hook text legible by 1s, the opening fact is the most surprising one. A miss is a defect.
7. **Overlay overflow:** view a frame for every composited overlay (hook, badges, CTA) whose wording is new (a CTA once ran off the right edge at fontsize 64).
8. Boundary frames on a concatenated file need accurate seek (`-ss` after `-i`). Fast seek can show the next clip. (Cutting a Short uses `-ss` before `-i`, 10b.)
9. **Archive the passing master** to `videoNN\master` on the PC (full quality, not the compressed upload copy).

## Step 8: Package

- Look at 3–5 recent channel titles for the convention: **"[Topic]: [Hook]?! [emoji] Stella/Ellie the [Elephant/Star]'s Adventure | Tiny Learners"**. Draft title, description (hook sentence, numbered five facts, "Made for kids ages 2 to 6. Subscribe to Tiny Learners...", 4 hashtags), and tags (SEO list, one comma-separated string with a trailing comma).
- **Write the title's character count into the package doc** (e.g. "95/100 chars"). 101 has bitten twice.
- Thumbnail 1280x720: a strong extracted frame with one line of bold outlined text at the bottom, clear of the host's mouth (a design tool with a `youtube_thumbnail` type if available). Save it in the project folder **and as `videoNN\upload\thumb_vNN.jpg` on the PC**.
- Note the Made for Kids / COPPA setting. Stage the files.

## Step 9: Publish with the Tiny Learners Media posting app (YouTube + TikTok)

**What changed in this autopost copy:** Steps 9, 10d and the TikTok cross-post go through the
Tiny Learners Media posting app (repo `tinylearnerscreator/tiny-learners-media`, command `tlm`,
MCP server `tiny-learners-media`). The app reads the **full-quality files straight from the PC
archive** and uploads them to YouTube and TikTok in resumable chunks: no under-10 MB copies, no
staging, no Studio clicking, no 360p losses. The Chrome Studio steps from the original skill are
kept below as **9-fallback**, for when the app can't be reached.

### 9-route. Pick the posting route once, by evidence (no questions)

- **Route A, app tools:** the session has the tools `check_setup`, `draft_post`, `approve_post`,
  `post_status` and `set_youtube_visibility` (server `tiny-learners-media`; the names may carry a
  prefix). This happens when the pipeline runs in Claude Desktop on the PC, or in a Claude Code
  session on the PC (Remote Control). Call `check_setup` first: it needs `ffmpeg_installed`,
  both clients configured and both accounts signed in.
- **Route B, `tlm` command:** the session has a Windows shell on the PC where `tlm doctor` works.
  Use `tlm draft`, `tlm approve`, `tlm wait`, `tlm status` and `tlm visibility` (same behavior as
  Route A).
- **Route C, fallback:** neither, for example a cloud session that only reaches the PC through
  `device_*` tools. `device_bash` is a Linux VM and cannot run the Windows app. Use 9-fallback and
  the `tiktok-cross-post` skill exactly as in the original pipeline, and tell the user in one line:
  "Posting used the Chrome route; run the pipeline from a session on the PC to use the posting app."
- If `check_setup` or `tlm doctor` shows something missing (not signed in, no keys), do not try to
  fix it mid-run: use Route C for this video and tell the user to run the `setup-video-poster`
  skill (or `tlm setup`) afterwards.

Write the chosen route in the progress doc.

### 9-files. Which files (full quality, from the PC archive)

Pass **Windows paths as plain strings**. Never read, attach, stage or upload the video bytes
yourself; the app streams them from disk.
- Main video: `C:\Users\Dad\Downloads\TinyLearners\videoNN\master\<master file>` (the Step 7 master).
- Short: `C:\Users\Dad\Downloads\TinyLearners\videoNN\short\<short file>` (the Step 10 file).
- Thumbnail: `C:\Users\Dad\Downloads\TinyLearners\videoNN\upload\thumb_vNN.jpg` (under 2 MB).
- The `upload\` under-10 MB copies are not needed on Routes A and B. Make them only for Route C.

Run `inspect_video` (Route A) on the master and the Short before drafting. It checks codec, size,
fps and orientation per platform. The Short must read `vertical`.

### 9-drafts. Build both drafts, then ask once (the only new stop)

The posting app never uploads without the user's OK on its preview. Pre-authorization in 0e does
not replace this, so batch it into **one** question per video. Build two drafts first:

1. **Main group:** `draft_post` with
   - `source` = the master path, `platforms` = `["youtube", "tiktok"]`
   - `title`, `description`, `tags` (a list) from Step 8, and `thumbnail` = the thumb path
   - `playlist_name` = the category playlist (space: "Space for Little Ones")
   - `youtube_privacy` = "private", `made_for_kids` = true, **`contains_synthetic_media` = false**
     (this channel answers the altered-content question **No**, same as 9c), `youtube_category_id`
     = "27" unless the channel's recent videos use another category
   - TikTok long form: `tiktok_format` = "gradient" (the 9:16 blue-purple pad the channel uses),
     `tiktok_caption` = the long-form caption (tiktok-cross-post Step 3: hook first, about 5 tiered
     hashtags, TikTok-native CTA, different from the Short's), `ai_generated` = true,
     `tiktok_mode` = "inbox" until the user says the TikTok app passed its audit, then "direct"
     with `tiktok_privacy` = "PUBLIC_TO_EVERYONE"
2. **Short group:** `draft_post` with
   - `source` = the Short path, `platforms` = `["youtube", "tiktok"]`
   - Short title with `#Shorts`, description whose last line is
     `Watch the full adventure here: MAIN_VIDEO_LINK` (the literal placeholder text, replaced in
     9-upload), Made for Kids true, `contains_synthetic_media` false, **no playlist**
   - `tiktok_format` = "auto", the Short's own TikTok caption, `ai_generated` = true, same mode
3. Show the user both previews together, plus one line on TikTok inbox mode if it's used, and ask
   **once**: "Upload the main video and Short to YouTube as Private and send both to your TikTok
   inbox?" A yes approves both groups. Changes requested: `update_draft`, then show the new
   preview. Nothing else in the run waits on the user.

Route B: `tlm draft "<path>" --platforms youtube tiktok --title "..." --description "..." --tags a
b c --thumbnail "<path>" --playlist "Space for Little Ones" --privacy private --tiktok-format
gradient --caption "..."` prints the preview and the group id. Made for Kids and the AI flags come
from the app config: before the first Route B run, run
`tlm config set defaults.contains_synthetic_media false` once (the channel answers the
altered-content question No) and check `made_for_kids = true` and `tiktok_ai_generated = true`
with `tlm config show`.

### 9-upload. Upload, IDs, cross-link

1. After the yes: `approve_post` on the **main** group. Poll `post_status` about every 60 s (a
   500 MB master takes a few minutes; the upload resumes on its own after a drop, so never
   approve or upload again). Route B: `tlm approve <group>` then `tlm wait <group>`.
2. When the main YouTube post reads `done`, its `result` holds `video_id` and `url`. **IDs come from
   the app's result, not from a screenshot or the DOM**, so the l/I confusion of 9d cannot happen.
3. `update_draft` on the Short group: replace `MAIN_VIDEO_LINK` in its description with
   `https://youtu.be/<main video_id>`. Then `approve_post` on the Short group, which the user's
   yes in 9-drafts already covers. Poll until both platforms read `done`.
4. TikTok inbox mode: the post ends in the user's TikTok app inbox (status
   `SEND_TO_USER_INBOX`). Tell the user once, at the 10f checkpoint, to open TikTok, paste the
   caption (`caption_to_paste` in the result), switch on "AI-generated content" and post. In direct
   mode the app sets the AI label itself, and posts read "Only me" until TikTok's app audit passes.
5. A post that ends `failed` shows its reason in `detail`. Fix the cause (sign-in, file) and
   `retry_post`. If the same platform fails twice, use Route C for that platform only and say why.
6. Copy into the progress doc: main and Short video IDs and URLs, TikTok publish IDs and status,
   and the route used.

**YouTube API audit (trial note).** Until the user says Google approved the app's YouTube API
audit, YouTube may lock API uploads to Private. Uploading Private is what the pipeline wants
anyway. The Public step (9e) shows whether the lock applies: if `set_youtube_visibility` reports
the video was kept private, follow 9e's fallback and record "YouTube API lock" in the progress doc
and the retrospective.

### 9-fallback. Chrome Studio route (Route C only)

The original Chrome steps, unchanged.


On Route C, steps 3–9 run straight through to a **Private** upload (no "ready to publish?" question). Reaching Private never authorizes Public (9e). "Instant Premiere" adds nothing for made-for-kids content.

#### 9a. Account and channel

Check memory (`reference_tiny_learners_youtube.md`) for which Chrome profile owns the channel (tinylearnercreator). Re-verify by content after any pause (Studio dashboard: channel name, subscriber count, video list), since deviceIds and "Browser N" labels drift. Never ask which browser to use: narrow by evidence and `select_browser`. If a fresh tab group lands on the wrong Google account, the original group may be alive on another browser, so try other deviceIds from Browser 1 before rebuilding.

#### 9b. Upload the file

- **Get the file in place.** `file_upload` accepts a file copied into `/mnt/user-data/uploads/<subfolder>/` (e.g. `for_youtube`) directly (Videos 62, 63). Files under `/mnt/user-data/outputs/` are rejected ("only files this session is allowed to read"). A file only on the user's PC must be `device_stage_files`d first. A staged path that fails can work from the original cloud path, so try the other. 10 MB combined cap per call. `device_commit_files` can corrupt raw binary (base64 it and check `md5sum`).
- **Over 10 MB:** compress in the cloud with `Bash`, scale to 1280x720, `-b:v 640k -maxrate 760k` (95 s main ≈ 8.8 MB) or `-crf 27 -maxrate 620k`. A 1080x1920 Short is often larger: `-b:v 1100k -maxrate 1300k` (52 s ≈ 7.7 MB), or `-b:v 1500k -maxrate 1800k -bufsize 3000k` if still over. Check the Short's size too. On the PC run encodes in the foreground with `timeout_ms` near 175000 (a `nohup … &` is killed when the call returns, leaving truncated files: `ffprobe` every output, "moov atom not found" means truncated). **Save the under-10 MB copies to `videoNN\upload` on the PC.**
- **Open the dialog:** `find` the Create button, click its ref, click Upload videos. A coordinate click on Create sometimes opens nothing, and the first click can silently fail, so click again. Or open `https://studio.youtube.com/channel/<CHANNEL_ID>/videos/upload?d=ud`.
- **Never use the native picker.** `find` the *hidden* file input and `file_upload` to its ref (the visible button throws "Element is not a file input"). If every route fails, ask the user to pick the file.
- Wait for the Details step to fully load before typing (text typed while loading is lost). The dialog title defaults to the file name, so always overwrite it.
- **Studio layout shifts (Video 68).** After the title is typed an A/B Testing row appears and moves the description box down about 70 px, so use `find` refs or take a 0.5-scale screenshot before clicking the description. Typing `#Shorts` opens a hashtag autocomplete: click the description box to dismiss it, never press Escape (it can close the dialog). On a Short the preview shows a black spinner while it processes, so Private and Save still work before checks finish.
- **Recovery:** after a disconnect mid-upload the file is usually done: resume in the same open dialog, never upload again (it makes an orphan draft) and never force past "Leave site?". Read the video ID from the dialog first (`a[href*="youtu.be"]`). With the tab group lost: `list_connected_browsers` → `select_browser` → `tabs_context_mcp{createIfEmpty:true}` → `.../videos/upload` → **Edit draft**.
- The YouTube Data API (OAuth doc `youtube_oauth_credentials.md`) is blocked here (classifier and network allowlist), so use Studio and say why.

#### 9c. Details

Title and description are `contenteditable` divs (`form_input` fails). Reliable method: click the field, `ctrl+a`, `type`, then read `#textbox` `innerText` to confirm. `execCommand('selectAll')` + `insertText` worked on a first dialog but selected the whole page on the second, so don't rely on it.
- **Description is the most repeated failure.** A stale click or layout shift lands text in the Title. Take a fresh screenshot immediately before clicking Description and read back right after the first `type` (count moved off `0/5000`, Title unchanged). If misfired, clear Title, retype it, redo.
- The screenshot coordinate frame changes between captures. After any wait, reload or JS call take a fresh screenshot and compute clicks from it alone (a stale click once put the tab in fullscreen: recover with `document.exitFullscreen()`).
- Split large `type` calls (the classifier can block huge ones, and a batch with several big types can fail JSON parsing). Hashtags pop an autocomplete: type the whole title in one shot and dismiss by clicking inert dialog chrome. **`Escape` can close the entire dialog** (recover via Edit draft, the draft autosaves).
- **Playlist:** the Select button → check the box → Done. Main videos go in their category playlist (space: "Space for Little Ones"). Shorts get no playlist.
- **Show more** holds tags (`#tags-container input`, type the comma-separated string, confirm `ytcp-chip` texts), paid promotion and AI disclosure. If those radios are missing from the DOM, Show more did not open: click it by coordinates (`#toggle-button`) and re-run the JS.
- **Verify by DOM, not screenshots** (screenshots freeze while the dialog processes): `[...document.querySelectorAll('tp-yt-paper-radio-button')].map(r=>r.getAttribute('name')+':'+r.getAttribute('aria-checked'))` shows `VIDEO_MADE_FOR_KIDS_MFK`, `VIDEO_PAID_PRODUCT_PLACEMENT_NO`, `VIDEO_HAS_ALTERED_CONTENT_NO`, and visibility (`PRIVATE|UNLISTED|PUBLIC`). Required: Made for Kids **Yes**, paid promotion **No**, AI disclosure **No** (a Short's flow asks the same two questions under Show more).
- Visibility radios start with none checked: click **PRIVATE**, confirm `aria-checked`, then Save. `#next-button` ×3 (1.5s apart) reaches Visibility and `#done-button` is the dialog's Save. A "This video is only visible to you" toast confirms.
- **After Done, the dialog may show "We had trouble saving your video, retrying" and then close, and the Shorts list can read empty or blank for a minute.** The upload is usually fine. Never re-upload. Open the Shorts list in a different tab, wait, and read the new row's ID and visibility from the DOM (Video 66).
- **Thumbnail:** `file_upload` to its hidden `type=file` input. If "Unlock more on YouTube" appears, **never click Verify**: Cancel, use Select from video, and tell the user the custom thumbnail path. A classifier denial resolves with one identical retry.

#### 9d. IDs

Copy IDs from the DOM, never from a screenshot (lowercase l and uppercase I look identical). The main ID is in the dialog's `a[href*="youtu.be"]` or the Videos list row `a[href*="/video/"]`. **A Short never appears in the Videos list**: open `studio.youtube.com/channel/<CHANNEL_ID>/videos/short` and read `ytcp-video-row` hrefs and `[class*=visibility]`.

### 9e. Visibility, the non-negotiable checkpoint

The Visibility step defaults to Private with **Save** (it becomes Publish only if Public is picked). **Never select Public without the user explicitly choosing it in this session.** A mid-flow or after-the-fact instruction ("Make them public", "Make the videos public. and start retrospective") is valid authorization for the videos it names. "Publish now" naming one video covers its Short, otherwise ask again. Stop at the Visibility screen otherwise. "Publish anyway" on a still-running check is reasonable only after explicit Public authorization.

**Public flip via the posting app (Routes A and B, try first).** Only after the explicit authorization above, call `set_youtube_visibility(video_id, "public")` (Route B: `tlm visibility <ID> public`) for the main video and then its Short, using the IDs from the app's results. Success returns `privacy: public`. Then read `post_status`, or the Videos and Shorts lists, and update the registry (10e). If it reports that YouTube kept the video private (the API-upload lock before the API audit), or errors twice, use the Studio steps below for that video and log "YouTube API lock".

**Public flip in Studio (fallback, after-the-fact, no new upload).** Verify live state in Studio first (the registry can be stale), then for each video, main and Short:
1. Open `studio.youtube.com/video/<ID>/edit`, wait ~5s (the first click after a load often does nothing).
2. Open Visibility: JS `document.querySelector('ytcp-video-metadata-visibility #select-button').click()`, or `find` "Edit video visibility status" and click its ref, or a coordinate click on the box (screenshot first, it moves after scrolling).
3. Click `tp-yt-paper-radio-button[name="PUBLIC"]` (or the Public radio). The panel shifts, so screenshot before clicking Done. Click Done (`#save-button` inside the dialog), then the page **Save** (`#save`, top right).
4. **Success = the "Changes saved" toast** or `#save` becoming `disabled`. A Save button still active, or a "Leave site?" block on navigation, means it is unsaved. A Short often needs a second Save click (Video 66: the first Save did nothing, the second showed `#save` disabled). In Video 66 `document.querySelector('#visibility-text').click()` opened the dialog and the Done button sat near (1278,662) on a 1568x726 frame. If the tab freezes on a screenshot, open the edit page in another tab. **The auto-mode classifier can deny the Done click on a Public flip** (Video 65 Short, 2026-10-14, after the main saved Public fine). Do not retry or script around it: leave that video Private, finish the rest of the turn, and tell the user in one line to flip it by hand.
4b. **A ref-based Save click can fail silently on a Short** (Video 70: Visibility read Public but `#save` stayed active and navigation raised "Leave site?"). Screenshot after the first Save. If Save is still dark, click it by coordinate (about (1038,80) on a 1568x726 frame) and wait 4 s before navigating. A mid-turn "Make public" from the user, sent while another task is running, authorizes the main video and its Short for that video number.
5. Finish by reading both the Videos and Shorts lists (`[class*=visibility]` on each row) and confirming Public. Then update the registry status in a second, separate write (10e). A Short's Save can raise "We're still checking your video" with a Publish button: use it only under the explicit authorization.

### 9g. Replacing a published video after a defect is found (added after Videos 55 and 64)

When the user says to fix a published video, never edit the live file. Do this in order, no questions (the user's request authorizes Public for the replacements):

**Routes A and B:** do the same steps with the posting app. Upload the replacement main and Short with `draft_post` (show the previews, and the user's fix request is the OK for them), set them Public with `set_youtube_visibility` once uploaded, and set the old ones to `unlisted` the same way. Use Studio only for anything the app reports it cannot change.

1. Find the root cause first and fix it at the source (regenerate the bad clip or audio, rebuild main and Short). Run the full Step 4/7 checks on the new files, including the countable-details check and the speech check on the opening line.
2. Upload the new main with the old video's title, description, tags, playlist and thumbnail (read them from the old video's edit page: description via `ytcp-video-description #textbox`, tags via `#toggle-button` then `#tags-container` text). Wait for "Checks complete. No issues found." before clicking Publish, since publishing during checks raises a strike-warning dialog. Choose Public, Publish.
3. Read the new main ID from the DOM. Upload the new Short with the same metadata and `Watch the full video: https://youtu.be/<NEW main ID>` as the last line, hashtags first. Public after checks complete.
4. Set the OLD main and OLD Short to Unlisted (9e steps 1-4, radio `UNLISTED`). Never delete them.
5. Read the Videos and Shorts lists to confirm all four states, then update the registry (new IDs, old IDs marked Unlisted, reason) and write a project doc with root cause and new IDs.
6. Run the retrospective (Step 11). A fix after publish is always a lesson, so it ends in `propose_skills`.

**Studio notes:** set Studio text by `el.innerText=v` plus an `InputEvent('input',{bubbles:true,composed:true,inputType:'insertText',data:v})` on `ytcp-uploads-dialog #textbox`. Tags: `#toggle-button` (Show more), then set the `#tags-container input` value with comma-separated tags and blur; confirm the counter. Next is `#next-button` three times, then `tp-yt-paper-radio-button[name=PUBLIC]`, then `#done-button`. The Edit page shows description newlines collapsed, but the stored text keeps them. File uploads through `file_upload` are limited to about 10 MB, so keep upload copies under that.

**Permission mode:** when the user is remote (for example at a work PC with no desktop app or extension) and browser calls fail because the approval card demands an install, ask them to switch the permission mode from Manual to Auto. That fixed it on 2026-10-13.

**PC build path:** with a linked computer, `device_bash` is a Linux VM with ffmpeg, python3 and PIL, and the Downloads folder is `$HOME/mnt/Downloads`. Build and measure there without browser approval, then `device_stage_files` the upload copies to the cloud. Copying large folders is slow (about 1 to 2 minutes per 100 MB in the VM): run copy scripts in chunks that finish inside the 120 s call limit and make them skip files already copied.

### 9f. Browser problems

If a desktop screenshot shows the wrong window, `switch_display` through the monitors. If `navigate`/`tabs_context_mcp` work but every `computer`/`read_page`/`find` fails with "Couldn't determine which page this action targets": close all tabs and rebuild the group, test another browser, and if still failing tell the user the computer needs a reboot or Chrome restart (Studio autosaves).

## Step 10: Companion YouTube Short

A ≤60s vertical Short built from the video's audio. **Standard since 2026-10-17: generate the Short's scenes natively in 9:16 (10c-native, 10h).** The reuse-the-footage pillarbox cut (10c) is the fallback only when no Flow account has credits left, and it must be logged as a fallback in the production log. Part of every video.

**10a. Segments.** From the per-scene `seg_N.mp4` pick 3–6 (hook, striking highlights, outro CTA), 40–55s total, snapped to `silencedetect` boundaries. A self-contained section (the 5-facts recap) can be one continuous range. Never use fixed-length windows across unrelated clips. Verify each cut with a contact sheet (or word-level transcription with offline `pocketsphinx` for multi-source Shorts), and recheck every boundary if the user reports one glitch.

**10b. Cut and join.** Re-encode (not `-c copy`) with `-ss`/`-to` before `-i` and a 0.15s fade in/out. Verify each part before concatenating (pixel variance, not file size). Normalize every segment's audio to 48 kHz stereo AAC (`-af aresample=48000 -ac 2`) before concat (mixed rates caused DTS errors). Check the final length against 60s.

**10c. Vertical 9:16, never landscape** (a landscape "fix" once disqualified 23 Shorts): `ffprobe` height ≥ width before upload. A Short must fill the whole screen with nothing cut off, which is why native 9:16 generation (10c-native) is the standard and the options below are fallbacks.
- **Gradient pillarbox (fallback).** Full uncropped frame centered on a mood-colored gradient, no busy fill. Inline: `gradients=s=1080x1920:c0=0x1B1F5E:c1=0x7A2D9A:x0=0:y0=0:x1=0:y1=1920:d=<s>:r=30` as input 0, foreground `scale=1080:-2` overlaid centered (`y=656` for 16:9) with `format=yuv420p`. Or a pre-rendered PIL `gradient_bg.png` looped (never a live `geq`).
- **Center-crop-to-fill** keeps only ~31.6% of a 16:9 frame's width (`scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=25`). Use it only if a contact sheet shows the subject within the middle third. Skip anything with a solo wide subject, two subjects, or readable text.
- Blurred pillarbox (`gblur`) is a last resort (it produced a "3 windows" look on 23 videos) and needs a contact-sheet review.
- **Hook text goes on the padding area**, never the video content (a transparent PNG or `drawtext` in the gradient margin, ~fontsize 170 at y≈330, label fontsize 70 at y≈1380), timed to the hook window. If Scene 1 already carries the burned-in hook, leave the padding blank for that window (never show the hook twice).

**10c-native. Native 9:16 Short (standard, added 2026-10-17).** Cut the Short's audio from the finished main video (the hook, the 5-facts recap and the outro, 40 to 55 s, snapped to silence boundaries), then generate about 5 to 6 new 8-second scenes in Flow at 9:16 to cover it (10 credits each on Veo 3.1 Lite). Reuse one good scene mirrored (`hflip`) for a second fact to save 10 credits. Build with the audio mapped in. For a new video's own Short, continue straight to the Private upload (0d). **When replacing an existing published Short, send a preview in chat (`SendUserFile`) and wait for the user's approval before uploading.** Upload as Private, and set Public only with per-video authorization. For a replacement, the user's "do all three" answer covers: new Short Public, old Short Private (never delete), new Short posted to TikTok as a new post (AI label on, old TikTok left up). Details in 10h.

**10d. Upload.** On Routes A and B the Short is the Short group from 9-drafts: the same one-time OK covers it, its cross-link is filled in by 9-upload step 3, and the checks below still run on the Short's own file **before** the drafts are shown. TikTok gets the Short and the 9:16 gradient long form from the same two groups, so the separate `tiktok-cross-post` skill is only used on Route C. On Route C upload as in Step 9-fallback. Route C differences: title short with `#Shorts`, description cross-links `Watch the full adventure here: https://youtu.be/<ID>` (use the main video's ID read from the DOM), Made for Kids Yes, no playlist. **Before upload, on the Short's own file:** repeated-frame hash check, `ffprobe` vertical, and loudness (`loudnorm=I=-16:TP=-1.5:LRA=11` with `aformat=channel_layouts=stereo` ahead, confirm with `ebur128=peak=true`, because a flat concat once measured -19.5 LUFS with a 0.1 dBFS peak). **Archive the full-quality Short to `videoNN\short` on the PC (required, 0f)** and the under-10 MB copy to `videoNN\upload`. **Add the Short's row to the production log in `claude/flow_credit_ledger.md` (type Short, credits 0 when built from the main footage, otherwise 10 per native 9:16 scene with the accounts used, 3d).** **TikTok logging (Routes A and B):** when the TikTok posts finish, append one row per post (Short and Long) to the TikTok post log in `claude/flow_credit_ledger.md` (columns Video, Name, Type, Date posted, Credits used 0, File, Status, Notes) exactly as `tiktok-cross-post` Step 6 describes, with Status "In TikTok inbox (posting app)" or the direct-post state, and Notes naming the posting app and caption hook. Then the per-day TikTok log doc and the registry line, batched. **Cross-posting on Route C is the separate skill** (`tiktok-cross-post`) and always starts from `videoNN\short`, never from a YouTube download. It logs each TikTok post in the same ledger file. TikTok gets both the Short and a 9:16 padded long-form copy (Videos 65 and 66 onward, standing approval 2026-10-14), posted from under-10 MB copies via Chrome upload (see that skill).

**10h. Native 9:16 mechanics (Videos 64 to 71, 2026-10-16 and 17).**
- **Flow composer:** chip at the bottom right, choose Video, 9:16, x1 (new accounts default to Agent mode and x2, switch both). Frame height can be 726 or 772, so screenshot the composer once per browser (submit about (1001,679) or (1001,725), prompt box about (777,642) or (777,687)). The "Not enough credits" toast can appear even when the submission worked, so check the grid.
- **Prompt rule:** "A tall vertical wide-shot of <subject>, fully visible and small in the frame with wide empty margins on all sides, the camera stays far away and does not zoom in, nothing cut off by any edge. No text." plus the locked style phrase. Characters still drift toward the camera and grow over 8 s, so trim each clip where an edge is touched and check every clip on a contact sheet. "Hugging Earth" style prompts zoom in and cut the subject, avoid them. A Sun can show dark pits that read as a face, add "no dark holes".
- **Ellie and the content filter:** the full locked Ellie text, and variants with "tiny tusks" or "waves goodbye", can be rejected (refunded after a few minutes). This passes: "cute cartoon baby elephant with soft light gray skin, a big round head, big flappy ears, a short curly trunk, a round plump body and short sturdy legs, big friendly eyes, stands and waves hello with one front foot". Stella prompts passed with the locked text.
- **Download from the editor page:** click the tile (opens /edit/<id>), the download icon at the top right (about (1303,30) on a 1568-wide frame), then "720p Original size" (about (1322,108)). The filmstrip thumbnails at the top switch clips. Files land named from the caption: `mv -n` each into `videoNN\vt\fN_name.mp4` at once. Grid right-click menus are unreliable.
- **Read credits:** click the avatar (about (1517,30)), `find` "Google Flow credits number and account email in account popup", close with (1523,40).
- **Build (ffmpeg, foreground, under 170 s per call):** per segment `-ss s -t d -i clip -vf "[hflip,]setpts=F*PTS,scale=1080:1920:flags=lanczos,fps=30,format=yuv420p" -t D -an -c:v libx264 -preset veryfast -crf 19 seg/x.mp4`, concat with `-c copy` to cat.mp4, then one final pass: Poppins-Bold `drawtext` for the hook (`/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf`, borderw 6 to 8 black, placed on empty area checked on a frame), optional `tpad=stop_mode=clone:stop_duration=0.6` and `fade=t=out`, audio from the old Short (`-map "[v]" -map 1:a`), crf 20, `-t` the old Short's duration, faststart. Make the upload copy `-b:v 1400k -maxrate 1600k -bufsize 3200k` so it is under 10 MB. Archive both to `videoNN\short` and `videoNN\upload`.
- **YouTube upload (Short):** use the channel-scoped URL `https://studio.youtube.com/channel/UCVewof9gLI_8Oju2egagrQw/videos/upload?d=ud`. One connected browser can answer "no permission to view this page": try the next browser (the one that opens the upload dialog is the channel's). `find` the file input, `file_upload` the staged path (stage first with `device_stage_files` using the Windows path). **After typing the title, take a 0.5-scale screenshot (the hashtag suggestion row shifts the layout), then click the description box by its `find` ref and type.** A coordinate click on the old position put the description text into the title in Video 71 (fix: click the title, ctrl+a, retype it, then click the description by ref). Escape closed the suggestion list without closing the dialog that time, but 9b warns it can, so prefer the ref click. `find` "Yes, it's made for kids" and Next, click Next three times with 3 s waits, then Private (about (482,295)) and Save (about (1131,704)). Find the new ID from the Shorts list (`/videos/short`, first row href).
- **Visibility flips:** open `/video/<id>/edit`, click the visibility control (about (950,737)), Public radio (about (880,571)) or Private radio (about (880,509)), Done (about (1278,710)), wait 8 s, `find` Save and click it, then reload and verify in the Shorts list (the Visibility column).
- **TikTok:** `tiktokstudio/upload`, `find` the file input, wait about 18 s, triple-click the description (about (500,283)) and type the caption. **Press Escape, do not click blank space, while the hashtag suggestion list is open** (a stray click auto-selected "#fypシ゚viral" in Video 70, fix with Backspaces and retype). `find` "Show more", then the AI-generated content switch, click it, and verify with `read_page` that it reads "on" (screenshot the block too, the name can lie). `find` Post and click. The page redirects to `tiktokstudio/content` when posted, with the new post marked "Content under review" and visible to you only until review ends.

**10e. Registry (release the claim).** As soon as the main video is published (don't wait for the Short): read the registry fresh, replace the Claim row with a finished Video Log row (number, topic, category, host, status, links, date), delete the Claim, write the whole doc back. The registry is ~75k characters and every write is a full replace, so batch row, Short link, status and playlist moves into as few writes as possible. **Fallback:** if a full replace is unsafe, write `claude/channel_registry_videoNN_row_pending.md` (the exact row plus the new next number), tell the user once, and let the next session merge it. Propose an archive split (`claude/channel_registry_archive.md` for Videos 1–40) so the replace stays small. After an after-the-fact Public flip, update the status in a second write. Also confirm the video is in its category playlist.

**10f. Review checkpoint.** Once the main video and Short are both Private, stop and ask whether the user wants to review before the retrospective. In the same message, if TikTok used inbox mode, remind the user in one line to post the two TikTok inbox drafts (paste the caption, AI-generated label on). If they review, wait and touch nothing. Otherwise go to Step 11/12. **A single message like "Make them public. Do the retrospective" authorizes both**: flip the main video and Short Public (9e), verify in the lists, then run Step 11/12 in the same turn.

**10g. Mechanics learned on Video 67 (2026-10-14).**
- Build the Short from the finished segment files: concat the hook, recap and outro segments with `-c copy`, then one pass of the gradient pillarbox (`split`, blurred cover background with `eq=brightness=-0.15`, foreground scaled to 1080 wide, `overlay` centered, fps 30), then a two-pass loudnorm with `linear=true`. Takes under a minute.
- The 9:16 long form for TikTok (84 to 90 s) needs `-preset veryfast -b:v 800k` to fit under 10 MB. At 720x1280 with `-b:v 800k -maxrate 900k -bufsize 1800k` an 88 s master encoded in about 30 s and came out 9.7 MB (Video 68). `device_bash` allows 180 s per call at most, so `timeout: 540000` does nothing there. **Background jobs die when the call returns** (`nohup ... &` and `setsid` both left a 0.5 MB partial file in Video 68): run every encode in the foreground, and split it into parts only if one call would pass 170 s. A 97 s master (Video 70) fit at `-b:v 760k` (9.99 MB, just under the cap), so lower the bitrate by about 5 percent per extra 5 s over 90 s. On TikTok Studio the AI-generated toggle does not always stay on between uploads and its accessibility name can read "on" while it is off: screenshot the Settings block before Post and click the toggle only if it reads off. A long form over 60 s also loses the Reuse of content box, which is normal.
- Studio upload: after `file_upload` wait about 10 s before typing. A title typed too early is lost. Click the title, `ctrl+a`, type, then read both `#textbox` fields with JS to confirm. Read IDs from the DOM (`a[href*="/video/"]`) with the characters split by spaces, since plain ID strings are blocked in JS output. Verify a main ID by opening `studio.youtube.com/video/<ID>/edit`.
- Public flip from the edit page: open the visibility dialog, `find` the Public radio, Done and Save refs and click them in that order. Save once, check it is greyed out (or click it a second time), then confirm in the list.
- The extension can drop mid-run ("not connected"). Run `list_connected_browsers`, `select_browser` on the same deviceId and the tab group returns intact.
- Archive narration as one zip (SendUserFile, then `device_commit_files` by fileUuid) and unzip on the PC with python. The zip stays behind because `rm` is not permitted.
- A user message that repeats the start request mid-run is the same request. Keep going.

---

## Step 11: Post-publish retrospective

0. **A retrospective always ends in a skill proposal.** If the scan below finds even one lesson (a failure, a workaround, a user complaint, a check that would have caught a defect), the retrospective is not finished until `propose_skills` has been called with the complete revised skill in the same turn. Writing a retrospective doc alone does not count (Video 64's retrospective was written as a doc and no skill update was proposed). Do it without being asked: "Start retrospective" means scan, record, propose.
1. Scan the session for friction: retries, workarounds, anything needing the user's hands, any guidance here that was wrong or incomplete. Separate flukes from repeatable patterns. A failure the user says recurred, or an explicit standing instruction, is a mandatory fix on first occurrence.
2. Record what happened, why, and the fix. Prefer removing a manual step over a better workaround. Fold each lesson into the one step it belongs to, and **keep the file small**: replace an older, narrower note rather than appending a new one.
3. Apply via `propose_skills` (`kind: "improvement"`, `target: "kids-video-pipeline-autopost"`, complete revised Markdown as `skillMd`). **Never target `kids-video-pipeline` from this copy**: the two skills are maintained separately. If a lesson is not about posting, list it in the update notes as "also applies to kids-video-pipeline" so the user can carry it over. Editing the cached disk copy doesn't persist. Tell the user what changed in one or two sentences.
4. A durable channel-identity fact (which account owns which channel) goes in memory, not here. Skip the update and Step 12 only when the scan found no lesson at all, and say so in one line.

## Step 12: Backup and log

1. One timestamp for both files (`TZ=America/New_York date "+%Y-%m-%d_%H%M"`). Save the skill exactly as it stood at session start to `claude/kids_video_pipeline_autopost_skill_backup_<timestamp>.md` (write it with `local_path`). If the installed copy is broken (placeholder or pointer), back up the last known-good full version instead.
2. Write `claude/skill_update_info_autopost_<timestamp>.md`: the prompting session, each change and why, and a pointer to the backup.
3. **Build `skillMd` as a file on disk first** (Write in parts if needed), `wc -l` it against the expected size, `grep` for placeholder-shaped text (a bracketed marker, a pointer to a path, "see file") and confirm none, read it back in full, then transcribe it character for character into `propose_skills`. A success response is not proof: after the user saves it, re-read the synced SKILL.md in a later turn to confirm what landed.
4. If the tool or classifier refuses, don't loop: save the finished SKILL.md and notes as project docs (`claude/kids_video_pipeline_autopost_SKILL_<tag>_proposed_<date>.md`), tell the user in two sentences where they are, and carry on.
5. **Broken-skill check at session start:** if the loaded SKILL.md shows a placeholder or a pointer instead of real steps, stop, tell the user, and submit a corrected full proposal before any pipeline work.

---

## Session checklist

- [ ] Skill body is real content (Step 12 item 5). Registry read, number claimed, duplicates checked (1-pre). Host bible and style phrase read (1a, 1b).
- [ ] PC archive folders `TinyLearners\videoNN\{raw,audio,master,short,upload}` created at Step 3 and filled as each step finishes (0f). MANIFEST.txt written at the end with gaps listed.
- [ ] Ledger `claude/flow_credit_ledger.md` read first and rewritten with every account's balance and refresh time after the last scene, and the video production log has a row for the main video (and for the Short at Step 10) with credits used (3a-pre item 0, 3d). Accounts inventoried by content, one clip downloaded per browser to confirm files land (3a-pre). Model verified before every submission. Fallback and re-sweep rules followed (3a-pre items 5–6).
- [ ] Script hook-first with onomatopoeia screened. Character locked from Scene 1 (3a-char). Every raw clip content-checked and `ffprobe`d (3a-verify). Narration hashed, `ffprobe`d, listened to (3c).
- [ ] Recap has one matching cutaway per fact (6h). Step 6 normalization, pads, held frames, hook burn-in done. Step 7 items 1–9 all run.
- [ ] Title count written as a number (Step 8). Posting route chosen and logged (9-route). Routes A/B: `check_setup` passed, full-quality master and Short paths used, both drafts shown and one OK received, main uploaded first, Short cross-link filled from the app's video_id, IDs taken from the app's results. Route C: channel confirmed by content (9a), DOM radios verified, Private saved, IDs copied from the DOM (9c, 9d).
- [ ] TikTok: Short and gradient long form sent (inbox or direct), each with its own caption and the AI label. Every post logged in the ledger's TikTok post log. Inbox reminder given at 10f.
- [ ] Short: native 9:16 scenes (10c-native, 10h) or the gradient pillarbox fallback logged as such, vertical `ffprobe`, loudness, repeated-frame hash, hook on empty area, cross-link, no playlist (10c, 10d). Full-quality Short saved in `short\`.
- [ ] Registry row written or pending doc saved (10e). Both Private: 10f question asked. Nothing Public without explicit authorization.
- [ ] Countable-details check done and written per frame for every scene with a number (3a-verify). Speech check run on every narration file, N1 first (3c).