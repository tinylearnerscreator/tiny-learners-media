# Grid Guardians — Module 1: "The Gremlin Wants the Lights Off"

**Cyber Security Awareness Reinforcement for personnel with access to assets containing BES Cyber Systems**

| | |
|---|---|
| **Series** | Grid Guardians (annual security awareness for electric utilities) |
| **Module** | 1 of 1 for the annual cycle (with optional quarterly micro-reminders, see crosswalk) |
| **Runtime** | ~14 minutes video + 3-minute knowledge check + acknowledgment |
| **Audience** | Everyone with authorized electronic access or unescorted physical access to substations, generating plants, control centers, or other assets containing BES Cyber Systems: employees, contractors, and vendors |
| **Format** | AI-produced animated video (Flow/Veo visuals, Kokoro or recorded VO), hosted in an LMS or played in a safety meeting |
| **Version** | 1.0 — [MONTH YEAR] |
| **Compliance mapping** | See `module-01-compliance-crosswalk.md` |

---

## How to read this script

- **VISUAL** = what's on screen (written so it can be used as an AI video prompt).
- **HANK (VO)** = narrator lines. Hank is a 30-year grid veteran: calm, funny, a bit of a storyteller.
- **THE GREMLIN** = our cartoon villain, a small, sneaky, purple creature with a backpack labeled "TOTALLY NOT MALWARE." He stands in for every attacker: nation-state, criminal, or vandal. He is never scary, just annoyingly clever.
- **ON-SCREEN TEXT** = captions/key takeaways (also used for posters and the email recap).
- **[BRACKETS]** = items the utility customizes before rollout (names, phone numbers, site rules).
- 🟩 **COMPLIANCE TAG** boxes are for the utility and the auditor. They are *not* narrated.

Customize these placeholders once before rollout:

| Placeholder | Example |
|---|---|
| `[UTILITY NAME]` | Riverbend Electric Cooperative |
| `[SECURITY CONTACT]` | CIP Compliance Lead / On-call Security |
| `[REPORT PHONE]` | 555-0100 (24/7 dispatch) |
| `[REPORT EMAIL]` | security@utility.coop |
| `[SCAN STATION LOCATION]` | Operations building, room 104 |
| `[VENDOR ACCESS APPROVER]` | SCADA Supervisor |

---

## SCENE 0 — Cold Open: "The Day the Mouse Moved by Itself" (0:00–1:30)

**VISUAL:** A cozy small-town control room at night, snow outside, a coffee mug that says "#1 Dispatcher." An operator watches a SCADA screen. Suddenly the mouse cursor starts moving *on its own*, gliding over breaker icons.

**HANK (VO):**
> December 23rd, 2015. Western Ukraine. A dispatcher watches his mouse pointer move across the screen... and he's not the one moving it. One by one, breakers open. Substations go dark.

**VISUAL:** A map with three utility service areas. Lights blink out across towns, in winter.

**HANK (VO):**
> Around two hundred and twenty-five thousand people lost power in the cold. And here's the part that should make you sit up: it didn't start with some movie-hacker genius. It started months earlier... with an email. Somebody opened an attachment. Then the attackers used stolen logins and remote access tools, the same kind of doors we use every day, to walk right in.

**VISUAL:** Freeze frame. Record-scratch sound. The Gremlin pops up from behind the monitor, waves.

**THE GREMLIN:**
> Heh. Hi.

**HANK (VO):**
> This little guy is the Gremlin. He wants the lights off. Sometimes he works for a foreign government, sometimes for criminals, sometimes he's just a vandal with a rifle. Over the next fourteen minutes, I'll show you the seven doors he tries, and how *you* lock every one of them.

**ON-SCREEN TEXT:** *Grid Guardians: The Gremlin Wants the Lights Off*

---

## SCENE 1 — "Why Little Old Us?" (1:30–2:45)

**VISUAL:** Hank (an animated, friendly older lineman with a hard hat covered in stickers) stands in front of a rural substation at sunrise.

**HANK:**
> Now, you might be thinking: "Hank, we're a small utility. We're 'low impact.' Why would anybody bother with us?"

**VISUAL:** Zoom out. One small substation becomes a constellation of hundreds of small substations and plants, all lit up and connected by glowing lines across a map of North America.

**HANK (VO):**
> Because the grid is one big machine. The Gremlin doesn't need to break into one giant plant if he can quietly get into a *hundred* small ones and flip them all at the same time. That's exactly why the regulators keep adding protections for "low impact" sites: a coordinated attack on lots of small places can add up to something very big.

**VISUAL:** Quick montage: a hospital, a water treatment plant, a farm milking parlor, a kid's nightlight. Each one is powered by the lines from that little substation.

**HANK (VO):**
> And in our country, U.S. agencies have publicly warned that nation-state hackers, like the group nicknamed "Volt Typhoon," have been pre-positioning inside American critical infrastructure. Not to steal data. To be ready to turn things off.

**HANK:**
> So no: there's no such thing as "too small to matter." You're a Grid Guardian. Let's go.

**ON-SCREEN TEXT:** *Small sites + coordinated attack = big outage. Every site matters.*

> 🟩 **COMPLIANCE TAG — Scene 1**
> Reinforces the purpose of the entity's cyber security practices for low impact BES Cyber Systems. Supports CIP-003-9 Attachment 1, Section 1 (cyber security awareness).

---

## SCENE 2 — Door #1: The Inbox ("The Lineman's Lunch") (2:45–4:45)

*Topic: phishing and social engineering*

**VISUAL:** A crew truck at lunchtime. A lineman named Dale eats a sandwich and checks his phone. An email slides in: **"URGENT: Updated Storm Overtime Pay Rates — Sign In to View."** The sender: `payroll@[utllity-name]-hr.com` (note the misspelling).

**HANK (VO):**
> Door number one is the inbox. The Gremlin knows exactly what you care about: overtime, storm schedules, your benefits, a package delivery. So that's what his bait looks like.

**VISUAL:** Dale's thumb hovers over "Sign In." Slow-motion. The Gremlin, tiny, is dangling from a fishing pole *inside* the phone screen, hook baited with a dollar sign.

**HANK (VO):**
> Let's play "Spot the Gremlin." Pause the video if you want, and find three clues.

**VISUAL:** Three red circles pop on, one at a time, with a "ding" each:
1. The sender's address is misspelled and from outside the company.
2. "URGENT" pressure to act right now.
3. The link, when hovered, goes to a weird web address.

**HANK (VO):**
> Misspelled sender. Fake urgency. A link that goes somewhere strange. Phone calls and texts work the same way. If somebody calls saying they're "from IT" and needs your password or wants you to approve a login prompt you didn't start... that's the Gremlin with a phone.

**VISUAL:** Dale puts the phone down, makes a "nope" face, and taps the **Report Phish** button. Confetti. The Gremlin falls off his fishing pole into a sandwich.

**HANK:**
> What do you do? Don't click, don't reply, don't forward it to your buddies to ask "is this real?" Report it to [SECURITY CONTACT] using [REPORT EMAIL / Report button]. And if you already clicked? Report it *anyway*, right away. Nobody gets in trouble for reporting fast. The only mistake is staying quiet.

**ON-SCREEN TEXT:**
- *Slow down: urgency is a trick.*
- *Never give your password or approve a login you didn't start.*
- *Clicked by accident? Report it immediately: [REPORT PHONE].*

> 🟩 **COMPLIANCE TAG — Scene 2**
> Reinforces cyber security practices (phishing, social engineering, credential protection). CIP-003-9 Attachment 1, Section 1. Relates to policy topic R1.2.1 (cyber security awareness).

---

## SCENE 3 — Door #2: The Fence ("Hold the Gate, Not the Door") (4:45–6:30)

*Topic: physical security of assets containing BES Cyber Systems*

**VISUAL:** A substation gate with a badge reader. A friendly technician, Maria, badges in. A man in a hi-vis vest carrying a box walks up behind her, smiling: *"Hey, can you get the gate? My hands are full."*

**HANK (VO):**
> Door number two is the fence. Hackers aren't the only threat to the grid. Some attacks are about bolt cutters and bullets.

**VISUAL:** Respectful, non-graphic: a news-style map pin on Moore County, North Carolina. Text: *December 2022.*

**HANK (VO):**
> In December 2022, someone shot up two substations in Moore County, North Carolina, and tens of thousands of customers lost power, some for days. Back in 2013, attackers fired on transformers at the Metcalf substation in California. Physical security *is* grid security.

**VISUAL:** Back to Maria at the gate. She smiles, points to the badge reader, and says: *"Sorry, everybody badges. I'll call it in and someone will meet you."* The "vest guy" turns around... he's the Gremlin in a vest that's way too big.

**HANK:**
> We call that tailgating, and Maria did it right. At our sites:
> - Everyone uses their *own* badge or key, every time.
> - Visitors are escorted the whole time they're inside, and logged.
> - Gates and doors close behind you. Watch them latch.
> - Cut fence, broken lock, strange drone, somebody photographing equipment? Don't confront. Back off, note what you saw, and call [REPORT PHONE].

**VISUAL:** Quick checklist animation with check marks: Badge ✓, Escort ✓, Latch ✓, Report ✓.

**ON-SCREEN TEXT:** *Your badge is yours. Escort every visitor. Watch the gate latch. See something weird? Call [REPORT PHONE].*

> 🟩 **COMPLIANCE TAG — Scene 3**
> Reinforces associated physical security practices, as expressly permitted by CIP-003-9 Attachment 1, Section 1 ("which may include associated physical security practices"). Supports policy topic R1.2.2 / Attachment 1, Section 2 (physical security controls).

---

## SCENE 4 — Door #3: The Login ("Passwords Are Like Toothbrushes") (6:30–8:00)

*Topic: electronic access controls, authentication, and protecting credentials*

**VISUAL:** A relay technician opens a laptop to connect to a relay at a substation. A sticky note on the laptop reads: `admin / admin`. The Gremlin is peeking over the technician's shoulder, taking notes with a crayon.

**HANK (VO):**
> Door number three is the login. Passwords are like toothbrushes: pick a good one, don't share it, and never leave it lying on the counter.

**VISUAL:** Toothbrush gag: the Gremlin tries to "borrow" someone's toothbrush. Everyone recoils. *"Ewww."*

**HANK (VO):**
> Default passwords on field equipment are the Gremlin's favorite snack. Shared team logins mean nobody knows who did what. And a password on a sticky note is just a password with extra steps.

**HANK:**
> So:
> - Use your *own* account. Never share it, never borrow one.
> - Change default passwords, and if you find a device still using one, report it.
> - Got a multi-factor prompt you didn't ask for? Deny it and report it. That's somebody trying your password.
> - Only connect to our control systems using the approved paths, the ones [UTILITY NAME] set up. No "quick shortcuts," no personal hotspots, no new wireless gadgets plugged into anything at a site.

**VISUAL:** A cartoon "bouncer" stands at a network door with a clipboard: **"If you're not on the list, you're not getting in."** The Gremlin, wearing a fake mustache, gets turned away.

**ON-SCREEN TEXT:** *Your login = your signature. Don't share it. Deny surprise MFA prompts. Approved connections only.*

> 🟩 **COMPLIANCE TAG — Scene 4**
> Reinforces cyber security practices for electronic access. Supports policy topic R1.2.3 / Attachment 1, Section 3 (electronic access controls). Also previews the authentication and credential-protection controls added to Section 3 by CIP-003-11 (FERC Order No. 918), so personnel are prepared before that version takes effect.

---

## SCENE 5 — Door #4: The Pocket ("The Free USB Stick") (8:00–9:45)

*Topic: transient cyber assets and removable media*

**VISUAL:** A parking lot. A shiny USB stick lies on the asphalt with a label: **"BONUS LIST — CONFIDENTIAL."** A worker picks it up, intrigued.

**HANK (VO):**
> Door number four fits in your pocket. USB drives, vendor laptops, a phone you plug in "just to charge."

**VISUAL:** Flashback, history-book style: a centrifuge spinning, labeled "2010: Stuxnet."

**HANK (VO):**
> The most famous industrial cyberattack in history, Stuxnet, crossed into a facility that wasn't even connected to the internet. How? Most likely on removable media. Somebody carried it in.

**VISUAL:** The worker drops the USB stick into a bin labeled **"SECURITY: TURN IN HERE"** and walks away. Inside the bin, the Gremlin is tangled in USB cables.

**HANK:**
> Rules of the pocket:
> - Never plug a found or unknown device into *anything*. Turn it in to [SECURITY CONTACT].
> - Only use [UTILITY NAME]-approved USB drives and laptops on control equipment, and scan them first at [SCAN STATION LOCATION] before every use.
> - Vendor showing up with their own laptop or drive? It gets checked under our process *before* it connects. Every time, even for nice vendors with donuts.
> - Don't charge your phone from a relay, an HMI, or any control system port. Ever.

**ON-SCREEN TEXT:** *Found it? Turn it in. Scan before you plug in. No phone charging on control equipment.*

> 🟩 **COMPLIANCE TAG — Scene 5**
> Reinforces cyber security practices for Transient Cyber Assets and Removable Media. Supports policy topic R1.2.5 / Attachment 1, Section 5 (TCA and Removable Media malicious code risk mitigation).

---

## SCENE 6 — Door #5: The Vendor Door ("Who Left the Back Door Open?") (9:45–11:15)

*Topic: vendor electronic remote access*

**VISUAL:** A house at night. Front door: deadbolt, chain, camera. The back door is wide open, with a sign: *"Vendor support — be right back."* The Gremlin tiptoes in.

**HANK (VO):**
> Door number five is the one most people forget: the vendor door. Vendors help us. They support our relays, our SCADA, our software. But every remote connection a vendor uses is a door into our system, and in Ukraine, remote access tools are how the attackers took control.

**HANK:**
> I'll tell you something from experience. I've seen people with no business on a critical network ask for access, because it's "faster" or "the contract says so." The right answer is: our process, every time. If the access isn't approved and it isn't necessary, it doesn't happen.

**VISUAL:** A big light switch labeled **VENDOR ACCESS** with three panels next to it: **KNOW IT'S ON → WATCH IT → SHUT IT OFF.**

**HANK (VO):**
> Here's how [UTILITY NAME] handles it:
> - **Know it's on.** Vendor remote sessions are approved by [VENDOR ACCESS APPROVER] and we know when they're active.
> - **Watch it.** Sessions are monitored for anything suspicious, coming in or going out.
> - **Shut it off.** We can kill a vendor session fast, and we turn it off when the work is done.

**HANK:**
> Your part? Never set up, share, or "leave open" remote access for anyone outside our process. If a vendor asks you to install a remote tool, give them a login, or "just click allow," stop and call [VENDOR ACCESS APPROVER]. And if you ever see a vendor session on that shouldn't be? Report it like it's smoke.

**VISUAL:** Someone flips the switch to OFF. The back door slams. The Gremlin bonks his nose on it.

**ON-SCREEN TEXT:** *Vendor access: approved, monitored, and turned off when the work is done. Never "just click allow."*

> 🟩 **COMPLIANCE TAG — Scene 6**
> Reinforces cyber security practices for vendor electronic remote access. Supports policy topic R1.2.7 and CIP-003-9 Attachment 1, Section 6 (methods to determine, disable, and detect malicious communications for vendor electronic remote access). Under CIP-003-11 these provisions move into Section 3; the content stays valid.

---

## SCENE 7 — Door #6: The Silence ("See Something, Say Something... FAST") (11:15–12:30)

*Topic: recognizing and reporting Cyber Security Incidents*

**VISUAL:** A game-show set: **"WHAT WOULD YOU DO?"** Hank is the host. Contestants are utility workers. Each one sees something odd on a screen.

**HANK (as host):**
> Contestant one, your HMI screen is acting weird: values jumping, settings you didn't change. Do you (A) reboot and hope, (B) ignore it, or (C) call it in?

**VISUAL:** Buzzer. A big **C** lights up. Applause.

**HANK (VO):**
> The Gremlin's best friend is silence. Every minute nobody reports, he gets further in. Things worth reporting right away:
> - Equipment or screens behaving strangely, or settings changing on their own.
> - Accounts locked out, or logins you didn't make.
> - Suspicious emails, calls, devices, or people at a site.
> - Anything that just feels *off*.

**HANK:**
> Call [REPORT PHONE], 24/7. Don't try to investigate it yourself, and don't wipe or reboot things unless operations requires it for safety. Our incident response plan kicks in from there, and the people trained to handle it take over. You don't have to be sure. You just have to say something.

**ON-SCREEN TEXT:** *Weird? Report it. Don't need to be sure. [REPORT PHONE], 24/7.*

> 🟩 **COMPLIANCE TAG — Scene 7**
> Reinforces personnel role in identifying and reporting suspected Cyber Security Incidents. Supports policy topic R1.2.4 / Attachment 1, Section 4 (Cyber Security Incident response).

---

## SCENE 8 — Door #7: The Storm ("Emergencies Don't Erase the Rules") (12:30–13:15)

*Topic: CIP Exceptional Circumstances*

**VISUAL:** A huge thunderstorm. Crews racing. Trucks everywhere. The Gremlin is standing in the rain holding a sign: **"ANY HELP NEEDED? I'M A CONTRACTOR!"**

**HANK (VO):**
> Door number seven is chaos. Storms, fires, and real emergencies are when the Gremlin loves to show up, because everybody's in a hurry.

**HANK:**
> During a true emergency, [UTILITY NAME] may formally declare what's called a "CIP Exceptional Circumstance." That lets certain security steps flex so we can protect people and restore power. But it's *declared* by the people authorized to do it, it's documented, and it ends. Being busy is not an exceptional circumstance. And even in a storm, a stranger asking for your badge or your login still gets a "no."

**VISUAL:** A lineman hands the Gremlin a bottle of water and points him firmly toward the escort desk.

**ON-SCREEN TEXT:** *Emergencies are declared, not assumed. Security still matters in a storm.*

> 🟩 **COMPLIANCE TAG — Scene 8**
> Reinforces awareness of the entity's process for declaring and responding to CIP Exceptional Circumstances. Supports policy topic R1.2.6.

---

## SCENE 9 — The Wrap: "Lights Stay On" (13:15–14:00)

**VISUAL:** Montage of everyone from the episode: Dale reporting the phish, Maria at the gate, the tech with no sticky note, the USB in the bin, the vendor switch flipped off, the game show winner. The Gremlin sits on a curb, defeated, eating Dale's sandwich.

**HANK (VO):**
> Seven doors. The inbox, the fence, the login, the pocket, the vendor door, the silence, and the storm. The Gremlin only needs one of them open. *We* need all seven locked, and that's on all of us.

**HANK:**
> Thanks for being a Grid Guardian. I'll see you next time. Keep the lights on.

**ON-SCREEN TEXT (end card):**
> **The 7 Doors**
> 1. Inbox: report phish
> 2. Fence: badge, escort, latch
> 3. Login: your own, never shared
> 4. Pocket: scan before you plug
> 5. Vendor door: approved, watched, shut off
> 6. Silence: report fast, [REPORT PHONE]
> 7. Storm: emergencies are declared
>
> *Questions? [SECURITY CONTACT] · [REPORT EMAIL]*

---

## KNOWLEDGE CHECK (3 minutes, in the LMS or on paper)

Passing score: 8 of 10. Retakes allowed. *(CIP-003 does not require a test; the check strengthens learning and gives auditors evidence the reinforcement was received.)*

1. An email says "URGENT: Sign in to see new storm overtime rates." The sender is `payroll@utilty-hr.com`. What should you do?
   a) Sign in quickly before the deadline
   b) Forward it to coworkers to ask if it's real
   c) **Report it using [REPORT EMAIL / Report button] and don't click** ✅
   d) Reply and ask for proof

2. You clicked a link and then realized it was a phish. What now?
   a) Wait and see if anything happens
   b) **Report it immediately to [REPORT PHONE]** ✅
   c) Delete the email so nobody knows
   d) Restart your computer

3. Someone in a hi-vis vest with full hands asks you to hold the substation gate. You:
   a) Hold it, they look like a contractor
   b) **Politely decline; everyone badges in or is escorted** ✅
   c) Give them your badge
   d) Leave the gate propped open for them

4. Why does a "low impact" site matter to grid security?
   a) It doesn't
   b) **Many small sites attacked at once can cause a large outage** ✅
   c) Only big plants are targeted
   d) Small sites aren't connected to anything

5. You get a multi-factor login prompt on your phone you didn't start. You:
   a) Approve it to make it go away
   b) **Deny it and report it** ✅
   c) Ignore it forever
   d) Turn off your phone

6. You find a USB drive labeled "BONUSES" in the parking lot. You:
   a) Plug it into an operations PC to find the owner
   b) Plug it into your home computer
   c) **Turn it in to [SECURITY CONTACT] without plugging it in** ✅
   d) Throw it away

7. Before using an approved USB drive or laptop on control equipment, you must:
   a) Ask a coworker if it's fine
   b) **Scan it at [SCAN STATION LOCATION] per our process** ✅
   c) Nothing, approved means always safe
   d) Charge your phone with it first

8. A vendor on the phone asks you to install a remote support tool on an HMI "to save time." You:
   a) Install it, they're our vendor
   b) Give them your login instead
   c) **Stop and contact [VENDOR ACCESS APPROVER]; vendor access only through our approved process** ✅
   d) Install it but uninstall it later

9. An HMI screen shows settings changing that nobody touched. You:
   a) Reboot it and move on
   b) Investigate yourself before telling anyone
   c) **Call [REPORT PHONE] right away and follow the incident process** ✅
   d) Wait until the end of shift

10. During a major storm, can you skip escorting a visitor because everyone is busy?
    a) Yes, storms suspend all security rules
    b) **No; only a formally declared CIP Exceptional Circumstance changes procedures, and stranger access is still controlled** ✅
    c) Yes, if they say they're a contractor
    d) Only at night

---

## ACKNOWLEDGMENT (captured electronically or on paper)

> I, ______________________, completed *Grid Guardians Module 1: The Gremlin Wants the Lights Off* on ____/____/______. I understand the cyber and physical security practices reinforced in this module and know how to report suspicious activity to [SECURITY CONTACT] at [REPORT PHONE].
>
> Signature: ______________________ Employee/Contractor ID: __________ Company (if contractor): ______________

---

## PRODUCTION NOTES (for the video build)

- **Tone:** Pixar-ish warmth, not fear. The Gremlin is a comedic villain; real-world incidents are presented factually and respectfully (no graphic imagery, no victim footage).
- **Characters:** Keep Hank and the Gremlin visually consistent across all future modules. Generate a character reference sheet first, then reuse it in every Veo prompt.
- **Accessibility:** Burned-in captions plus a separate caption file; reading level about 8th grade; 1.25× speed works for repeat viewers.
- **Chapters:** Export each scene as its own chapter so the LMS can show progress and the utility can reuse scenes as standalone quarterly reminders.
- **Fact check before release:** Re-confirm incident facts (Ukraine 2015, Metcalf 2013, Moore County 2022, Stuxnet, Volt Typhoon) against public government sources (CISA, DOE, FBI) and update the year references at each annual refresh.
- **Language:** A Spanish VO track is a strong add-on for crews and contractors.
