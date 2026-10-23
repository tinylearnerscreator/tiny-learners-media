# Grid Guardians Module 1: Production Prompt Pack

Prompts and a shot list for building *"The Gremlin Wants the Lights Off"* with Google Flow (Veo 3.1), using the same pipeline as Tiny Learners. The narration comes from the script (`module-01-grid-guardians-script.md`). This file covers the visuals.

## How to use this pack

1. **Make the character references first** (Part 1). Generate each one as a still image in Flow, pick the best, and save it as an "ingredient." Attach the same ingredient images to every shot that character appears in. That is what keeps Hank and the Gremlin looking the same across 40 clips.
2. **Generate shots scene by scene** (Part 3). Each shot is one 8-second Veo clip. Paste the **Style block** (Part 2) at the start of every prompt.
3. **Record narration separately** (Kokoro or your own voice) and edit the clips under it. Turn off or mute Veo's generated audio, except where a shot asks for a sound effect.
4. **Add all on-screen text in the editor.** Veo garbles words. Prompts below say "blank screen" or "blank sign" wherever text will go, and you place captions, labels, and email text on top in editing.

**Budget:** about 40 Veo clips (5 minutes of footage). The rest of the 14 minutes is covered by holding, zooming, and reusing clips under narration, plus title and text cards made in the editor. Plan for roughly 1.5 generations per usable clip.

---

## Part 1 — Character and Location References (generate as still images)

### C1. Hank (narrator / host)

> Character reference sheet, 3D animated feature-film style, friendly American utility lineman in his late 50s, warm weathered face, short gray beard, kind crinkly eyes, slight smile, white hard hat covered in colorful round stickers, high-visibility lime-green safety vest over a navy work shirt, tan work pants, scuffed brown work boots, tool belt. Shown in four poses on a plain light-gray background: front view, three-quarter view, side view, and pointing toward the camera like he's explaining something. Soft studio lighting, consistent proportions, no text.

### C2. The Gremlin (comedic villain)

> Character reference sheet, 3D animated feature-film style, a small mischievous purple gremlin creature about knee-high, big round yellow eyes, oversized pointy ears, a toothy cheeky grin (cute, not scary), stubby arms and legs, wearing a tiny gray backpack with a single blank patch on the front. Shown in four poses on a plain light-gray background: front view, sneaking on tiptoes, laughing with hand over mouth, and pouting with arms crossed. Bright saturated colors, playful, family-friendly, no text.

*Add "TOTALLY NOT MALWARE" (as in the script) to the backpack patch in the editor, not in the prompt.*

### C3. Supporting cast (one sheet)

> Character lineup, 3D animated feature-film style, four friendly utility workers standing side by side on a plain light-gray background: (1) Dale, a burly lineman in his 40s with a reddish beard, hi-vis vest and climbing harness; (2) Maria, a technician in her 30s with a dark ponytail, safety glasses pushed up on her head, blue work jacket and badge on a lanyard; (3) a young relay technician with glasses carrying a laptop; (4) a dispatcher in a cardigan holding a coffee mug. Consistent style, soft lighting, no text.

### Locations (generate one establishing still each, reuse as ingredients)

- **L1 Control room at night:** *a cozy small-town utility control room at night, snow falling outside a window, desks with several monitors showing abstract blue line diagrams, warm desk lamp, 3D animated film style.*
- **L2 Rural substation at sunrise:** *a rural electric substation with transformers, steel lattice structures and a chain-link fence topped with barbed wire, golden sunrise, fields behind it, 3D animated film style.*
- **L3 Substation gate:** *close view of a substation's chain-link gate with a gray card reader on a post, gravel driveway, daytime, 3D animated film style.*
- **L4 Crew room / operations building:** *a utility crew room with lockers, a bulletin board, a coffee machine and a table, daytime, 3D animated film style.*

---

## Part 2 — Style Block (paste at the start of every shot prompt)

> 3D animated feature-film style, bright friendly colors, soft cinematic lighting, smooth gentle camera movement, family-friendly tone, workplace comedy, 16:9, no text, no words, no logos, no subtitles.

**Negative prompt / avoid:** text, letters, watermarks, real company logos, weapons shown clearly, injuries, scary faces, realistic news footage.

---

## Part 3 — Shot List by Scene

Format: **Shot ID · length · ingredients** → prompt (after the style block) → editor notes.

### Scene 0 — Cold Open (0:00–1:30), 5 shots

- **0.1 · 8s · L1** → Slow push-in on the dispatcher at a desk in the night control room, sipping coffee, snow outside the window, calm atmosphere. → *Editor: "December 23, 2015 — Western Ukraine" title card.*
- **0.2 · 8s · L1** → Close-up of a computer monitor showing an abstract blue electrical line diagram, a white mouse cursor begins gliding across the screen on its own, the dispatcher's hand is nowhere near the mouse. → *Editor: add a click sound each time an icon changes.*
- **0.3 · 8s · L1 + C3 dispatcher** → The dispatcher leans back in shock, eyes wide, as the red indicator lights on the monitors switch off one by one.
- **0.4 · 8s** → Aerial view of small snowy towns at night, clusters of house lights blink out section by section until whole areas go dark.
- **0.5 · 8s · L1 + C2** → The purple gremlin pops up from behind a monitor in the control room, waves cheerfully at the camera, then ducks back down. Comedic timing. → *Editor: record-scratch sound right before this shot, freeze-frame on the wave.*

### Scene 1 — "Why Little Old Us?" (1:30–2:45), 4 shots

- **1.1 · 8s · C1 + L2** → Hank stands in front of the rural substation at sunrise, gestures toward it with an open hand and smiles at the camera.
- **1.2 · 8s** → Night map-style aerial shot of North America, hundreds of tiny glowing substations appear and connect with glowing lines into one huge web. → *Editor: animated text "Small sites + coordinated attack = big outage."*
- **1.3 · 8s** → Quick friendly montage: a hospital with lit windows, a water treatment plant, a dairy barn, a child's room with a star-shaped nightlight, each glowing warmly at night.
- **1.4 · 8s · C1 + L2** → Hank taps the brim of his sticker-covered hard hat confidently, nods, and points at the camera.

### Scene 2 — The Inbox (2:45–4:45), 5 shots

- **2.1 · 8s · C3 Dale** → Dale sits in the cab of a utility bucket truck at lunchtime, eating a big sandwich and scrolling on his phone, relaxed.
- **2.2 · 8s · C3 Dale** → Over-the-shoulder close-up of Dale's phone showing a blank email screen with a bright button, his thumb slowly hovering over it in slow motion. → *Editor: overlay the fake "URGENT: Storm Overtime" email and the misspelled sender.*
- **2.3 · 8s · C2** → Inside a giant stylized phone screen, the tiny purple gremlin dangles from a fishing pole, a shiny gold coin on the hook as bait, grinning and wiggling it.
- **2.4 · 8s** → Reuse 2.2 as a still. → *Editor: three red circles pop on one at a time with a "ding" (sender, urgency, link). No Veo shot needed.*
- **2.5 · 8s · C3 Dale + C2** → Dale makes a skeptical "nope" face and taps a button on his phone, confetti bursts, and the gremlin falls off his fishing pole, landing face-first in Dale's sandwich.

### Scene 3 — The Fence (4:45–6:30), 5 shots

- **3.1 · 8s · C3 Maria + L3** → Maria walks up to the substation gate and taps her badge on the card reader, the gate begins to open.
- **3.2 · 8s · L3** → A man in a baggy hi-vis vest carrying a cardboard box hurries up behind Maria with a big friendly smile, nodding toward the gate. → *Keep his face partly hidden by the box; this is the Gremlin in disguise.*
- **3.3 · 8s** → Respectful news-style shot: a quiet rural road at dusk with distant substation lights going dark, no people, calm and serious mood. → *Editor: map pin "Moore County, NC — December 2022," then "Metcalf, CA — 2013."*
- **3.4 · 8s · C3 Maria + C2 + L3** → Maria smiles politely, shakes her head and points at the card reader, the man in the vest turns around and it's the purple gremlin wearing a vest that's comically too big, his shoulders slump.
- **3.5 · 8s · L3** → The substation gate swings closed and latches firmly, camera holds on the latch. → *Editor: checklist animation "Badge ✓ Escort ✓ Latch ✓ Report ✓."*

### Scene 4 — The Login (6:30–8:00), 4 shots

- **4.1 · 8s · C3 relay tech + L2** → Inside a substation control house, the young relay technician opens a laptop next to a rack of equipment, a yellow sticky note is stuck on the laptop lid. → *Editor: write "admin / admin" on the sticky note.*
- **4.2 · 8s · C3 relay tech + C2** → The gremlin peeks over the technician's shoulder, scribbling notes with a giant purple crayon, tongue sticking out in concentration.
- **4.3 · 8s · C2 + L4** → In the crew room, the gremlin sneakily reaches for a toothbrush in a cup by the sink, two workers turn and recoil in disgust, comedic reaction.
- **4.4 · 8s · C2** → A burly cartoon bouncer with a clipboard stands at a glowing doorway, the gremlin wearing a fake mustache tries to walk in, the bouncer shakes his head and points away. → *Editor: label the doorway "NETWORK."*

### Scene 5 — The Pocket (8:00–9:45), 4 shots

- **5.1 · 8s** → A shiny USB drive lying on the asphalt of a utility parking lot, sunlight glinting off it, a worker's boots stop next to it. → *Editor: label "BONUS LIST — CONFIDENTIAL."*
- **5.2 · 8s** → Stylized history-book shot: an animated industrial centrifuge spinning faster and faster, sepia-toned, like an illustrated documentary. → *Editor: "2010: Stuxnet."*
- **5.3 · 8s · L4 + C2** → The worker drops the USB drive into a metal turn-in bin, camera follows it inside where the gremlin is hopelessly tangled in a pile of cables.
- **5.4 · 8s · L4** → A worker plugs a USB drive into a dedicated scanning computer on a desk, a progress bar fills and a green light comes on. → *Editor: label "SCAN STATION."*

### Scene 6 — The Vendor Door (9:45–11:15), 4 shots

- **6.1 · 8s · C2** → Night shot of a cozy house: the front door has several locks and a camera, the camera pans around to the back door which is wide open, the gremlin tiptoes toward it. → *Editor: sign on the back door "Vendor support — be right back."*
- **6.2 · 8s · C1 + L1** → Hank sits on the edge of a desk in the control room, speaks to the camera seriously but kindly, one finger raised to make a point. → *This is the shot for Hank's personal "our process, every time" line.*
- **6.3 · 8s** → A large wall-mounted light switch glows, a worker's hand flips it firmly from on to off. → *Editor: label "VENDOR ACCESS" and the three panels "KNOW IT'S ON → WATCH IT → SHUT IT OFF."*
- **6.4 · 8s · C2** → The back door of the house slams shut just as the gremlin reaches it, he bonks his nose on it and staggers backward, cartoon stars circle his head.

### Scene 7 — The Silence (11:15–12:30), 3 shots

- **7.1 · 8s · C1** → A bright, colorful game-show set with flashing lights, Hank in a sparkly blazer over his hi-vis vest stands at a host podium holding cue cards, grinning.
- **7.2 · 8s · C3** → Three utility workers stand behind contestant podiums, the middle one slams a big buzzer, lights flash and confetti falls. → *Editor: big letter "C" lights up, applause sound.*
- **7.3 · 8s · C3 dispatcher + L1** → The dispatcher calmly picks up a desk phone and makes a call while looking at a monitor, serious and focused. → *Editor: "[REPORT PHONE] — 24/7."*

### Scene 8 — The Storm (12:30–13:15), 3 shots

- **8.1 · 8s** → Dramatic thunderstorm at night, utility bucket trucks with flashing amber lights driving down a rainy road, crews in rain gear working on a power line.
- **8.2 · 8s · C2** → The gremlin stands in the pouring rain wearing a tiny hard hat, holding a blank cardboard sign hopefully over his head. → *Editor: sign "ANY HELP NEEDED? I'M A CONTRACTOR!"*
- **8.3 · 8s · C3 Dale + C2** → Dale kindly hands the gremlin a bottle of water and firmly points him toward a lit tent in the distance, the gremlin trudges off.

### Scene 9 — The Wrap (13:15–14:00), 3 shots

- **9.1 · reuse** → Fast montage of shots 2.5, 3.4, 4.4, 5.3, 6.4 and 7.2 (no new generation).
- **9.2 · 8s · C2** → The gremlin sits alone on a curb under a streetlight, sulking and eating a sandwich, while the substation behind him glows brightly.
- **9.3 · 8s · C1 + L2** → Hank at the substation at sunset, tips his hard hat to the camera with a warm smile, camera slowly pulls back as the substation lights glow. → *Editor: end card "The 7 Doors" list, then contact info.*

**Total new Veo clips: 40** (2.4 and 9.1 reuse existing footage).

---

## Part 4 — Editing Checklist

- [ ] Narration track laid first, then clips cut to it.
- [ ] Every text overlay from the script's **ON-SCREEN TEXT** lines added in the editor.
- [ ] Title card with module name, version (v1.0) and release date. This is part of the auditor evidence (E1).
- [ ] Burned-in captions plus an exported caption file (.srt).
- [ ] Chapter markers at each scene so the LMS and the quarterly reminders can use them.
- [ ] Real-incident shots (0.4, 3.3, 5.2) stay calm and non-graphic.
- [ ] Watch once at full length for character consistency, and regenerate any shot where Hank or the Gremlin drift off-model.
- [ ] Export 1080p MP4 for the LMS, plus individual scene files for the quarterly reminder kit.
- [ ] Fill in a copy with the sample placeholders (e.g. "Riverbend Electric Cooperative") for the sales demo, and keep a clean `[BRACKETS]` master for customers.
