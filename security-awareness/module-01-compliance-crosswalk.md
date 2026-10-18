# Grid Guardians Module 1: Compliance Crosswalk and Utility Toolkit

This document has three parts:

1. **Auditor Crosswalk:** shows, requirement by requirement, how the module and its evidence package meet NERC CIP security awareness obligations.
2. **Utility Rollout Kit:** a step-by-step checklist so a small utility can deploy it in under an hour.
3. **Evidence Package Templates:** the records an auditor will ask for.

> **Status of standards as of October 2026.** Please confirm against the current NERC "US Effective Date Status" page before each audit.
> - **CIP-003-9** has been the enforceable low impact standard in the U.S. since **April 1, 2026**.
> - **CIP-003-11** was approved by FERC in **Order No. 918** (March 2026). It moves the vendor remote access controls into Attachment 1, Section 3 and adds authentication, credential protection, and malicious communications detection. Its effective date is in the future, with the Section 3.1.2 detection obligation not required before April 1, 2029. **It does not change the Section 1 cyber security awareness requirement.**
> - **CIP-004-7 R1** (high and medium impact) requires security awareness reinforcement **at least once each calendar quarter**.

---

## Part 1 — Auditor Crosswalk

### 1A. CIP-003-9, Requirement R2, Attachment 1, Section 1 (Low Impact)

**Requirement text:**
> *Section 1. Cyber Security Awareness: Each Responsible Entity shall reinforce, at least once every 15 calendar months, cyber security practices (which may include associated physical security practices).*

| Element of the requirement | How this module satisfies it | Evidence the auditor sees |
|---|---|---|
| "**reinforce** ... cyber security practices" | Scenes 1–9 reinforce specific cyber security practices: phishing reporting, credential protection, authentication, approved connections, removable media scanning, vendor remote access, and incident reporting. | Dated copy of the script and video (version 1.0, release date on title card) — Evidence Item E1 |
| "(which may include associated **physical security practices**)" | Scene 3 covers badging, escorts, tailgating, gate latching, and reporting physical threats. | Same as above |
| "at least once every **15 calendar months**" | Delivered as an **annual** module (every 12 months), which leaves a 3-month buffer. The utility's tracker records each delivery date and the next due date. | Delivery date log and 15-month tracker — E3, E5 |
| Scope: personnel with access to assets containing low impact BES Cyber Systems (as defined in the entity's plan) | The audience statement covers employees, contractors, and vendors with electronic or unescorted physical access. The roster comes from the entity's access list. | Roster-to-completion reconciliation — E4 |
| Entity has discretion over topics and method | Topics align with the seven policy subjects in CIP-003-9 R1.2, so the program visibly ties back to the entity's own documented policy. | Topic mapping table (1C below) |

**Attachment 2, Section 1 (examples of evidence):** "Documentation that the reinforcement of cyber security practices occurred at least once every 15 calendar months. The evidence could be documentation through one or more of the following methods":

| Attachment 2 method | Module component that produces it |
|---|---|
| **Direct communications** (for example, emails, memos, computer-based training) | LMS completion records for the video, plus the recap email (Template T2) |
| **Indirect communications** (for example, posters, intranet, brochures) | "7 Doors" poster and intranet page built from the end card (Template T3) |
| **Management support and reinforcement** (for example, presentations, meetings) | Optional safety-meeting showing with a sign-in sheet (Template T4) |

**Recommendation:** use **at least two** methods each cycle, for example the LMS module plus the poster. If one record is incomplete, the other still proves the reinforcement happened.

### 1B. CIP-004-7, Requirement R1, Part 1.1 (High and Medium Impact) — if applicable

**Requirement:** Security awareness that, **at least once each calendar quarter**, reinforces cyber security practices (which may include associated physical security practices) for personnel who have authorized electronic or authorized unescorted physical access to BES Cyber Systems.

How to use this module for quarterly coverage:

| Calendar quarter | Delivery | Evidence |
|---|---|---|
| Q1 | Full Module 1 video and knowledge check | LMS records, acknowledgments |
| Q2 | Email recap: Scenes 2 and 4 (Inbox and Login) | Dated email and distribution list |
| Q3 | Poster rotation: Scenes 3 and 5 (Fence and Pocket) | Dated photo of posted locations, intranet screenshot |
| Q4 | Safety meeting clip: Scenes 6 and 7 (Vendor door and Silence) | Agenda and sign-in sheet |

> ⚠️ **Scope note:** This module is a **security awareness** program. It is **not** the CIP-004-7 R2 **cyber security training** program, which has role-based training content requirements (Parts 2.1.1–2.1.9) and a 15-month cadence. A separate R2 training module can be built later.

### 1C. Topic Mapping to the Entity's CIP-003-9 R1.2 Policy Subjects

Auditors often check that the awareness content matches the entity's documented policies. This table makes that check fast.

| R1.2 policy subject | Attachment 1 section | Module scene |
|---|---|---|
| 1.2.1 Cyber security awareness | Section 1 | Scenes 1, 2 (and the module as a whole) |
| 1.2.2 Physical security controls | Section 2 | Scene 3 — "Hold the Gate" |
| 1.2.3 Electronic access controls | Section 3 | Scene 4 — "Passwords Are Like Toothbrushes" |
| 1.2.4 Cyber Security Incident response | Section 4 | Scene 7 — "See Something, Say Something... FAST" |
| 1.2.5 Transient Cyber Asset and Removable Media malicious code risk mitigation | Section 5 | Scene 5 — "The Free USB Stick" |
| 1.2.6 Declaring and responding to CIP Exceptional Circumstances | (R1.2.6) | Scene 8 — "Emergencies Don't Erase the Rules" |
| 1.2.7 Vendor electronic remote access security controls | Section 6 (moves to Section 3 under CIP-003-11) | Scene 6 — "Who Left the Back Door Open?" |

**Result:** every R1.2 policy subject is reinforced at least once.

### 1D. Forward Compatibility with CIP-003-11

| CIP-003-11 change | Module readiness |
|---|---|
| Vendor remote access provisions move from Section 6 into Section 3 | Scene 6 content is unchanged. Only the citation in the compliance tag needs updating. |
| Authentication before network access and protection of user authentication information | Scene 4 already reinforces using your own account, never sharing credentials, protecting passwords, and denying unexpected MFA prompts. |
| Detection of known or suspected malicious inbound and outbound communications | Scenes 6 and 7 reinforce monitoring and fast reporting of suspicious traffic and sessions. |
| Section 1 awareness requirement | Unchanged; the 15-month cadence remains. |

---

## Part 2 — Utility Rollout Kit (about 1 hour of setup)

**Before rollout:**
- [ ] Fill in all placeholders in the script: `[UTILITY NAME]`, `[SECURITY CONTACT]`, `[REPORT PHONE]`, `[REPORT EMAIL]`, `[SCAN STATION LOCATION]`, `[VENDOR ACCESS APPROVER]`.
- [ ] Have the CIP Senior Manager or delegate approve the module version (Template T1). This is not required by Section 1, but it shows management ownership.
- [ ] Pull the roster of everyone with electronic or unescorted physical access to low impact assets, **including contractors and vendors**.
- [ ] Update your cyber security plan to reference this module as a reinforcement method (sample language in T6).

**Rollout (pick at least two methods):**
- [ ] **Direct:** assign the video and knowledge check in the LMS, or play it and collect paper acknowledgments.
- [ ] **Direct:** send the recap email (T2) to the full roster on the same day.
- [ ] **Indirect:** print the "7 Doors" poster (T3) for control rooms, crew rooms, and substation control houses. Take dated photos.
- [ ] **Management:** show the video at a safety or tailgate meeting with a sign-in sheet (T4).

**After rollout:**
- [ ] Reconcile the roster against completions (T5). Follow up with anyone missing.
- [ ] People who gain access mid-cycle: give them the module during onboarding.
- [ ] Record the delivery date and set the next due date to **12 months out** (hard deadline: 15 calendar months).
- [ ] Save everything into one dated evidence folder (E1–E6 below).

**Employee experience:** one link, 14-minute video in chapters, a 10-question check, and a one-click acknowledgment. It works on a phone, in a truck, or at a safety meeting.

---

## Part 3 — Evidence Package Templates

### Evidence folder index (what the auditor asks for)

| ID | Evidence | Source |
|---|---|---|
| E1 | Dated copy of awareness content (script PDF and video file/link, version 1.0) | This package |
| E2 | Approval record (T1) | CIP Senior Manager or delegate |
| E3 | Delivery records: LMS completion export, dated recap email with distribution list, sign-in sheets, poster photos | T2–T4 |
| E4 | Roster-to-completion reconciliation | T5 |
| E5 | 15-month tracker showing prior and next delivery dates | T5 |
| E6 | Cyber security plan excerpt referencing the module | T6 |

### T1 — Content Approval Record

| Field | Entry |
|---|---|
| Content | Grid Guardians Module 1: The Gremlin Wants the Lights Off, v1.0 |
| Purpose | Cyber security awareness reinforcement per CIP-003-9 Att. 1 §1 (and CIP-004-7 R1.1 if applicable) |
| Reviewed by | |
| Approved by (CIP Senior Manager / delegate) | |
| Approval date | |
| Planned delivery window | |

### T2 — Recap Email (direct communication)

> **Subject:** Grid Guardians: The 7 Doors That Keep the Lights On
>
> Team,
>
> As part of [UTILITY NAME]'s cyber security awareness program, please watch *Grid Guardians Module 1* (14 min) here: [LINK] by [DATE].
>
> The 7 doors the Gremlin tries, and how we lock them:
> 1. **Inbox:** don't click, report phishing to [REPORT EMAIL].
> 2. **Fence:** badge every time, escort every visitor, watch the gate latch.
> 3. **Login:** use your own account, never share it, deny surprise MFA prompts.
> 4. **Pocket:** turn in found devices; scan approved media at [SCAN STATION LOCATION] before use.
> 5. **Vendor door:** vendor remote access only through [VENDOR ACCESS APPROVER]. Never "just click allow."
> 6. **Silence:** anything weird? Call [REPORT PHONE], 24/7. You don't have to be sure.
> 7. **Storm:** emergencies are formally declared; security still matters.
>
> Thank you for keeping the lights on.
> [SECURITY CONTACT]

*Evidence: save the sent email with date, sender, and full distribution list.*

### T3 — "7 Doors" Poster (indirect communication)

Use the end card from Scene 9 as an 11×17 poster with the Gremlin artwork and `[REPORT PHONE]` in large type. Record the date posted and the locations, and take a dated photo of each.

### T4 — Meeting Sign-In Sheet (management support and reinforcement)

| Date | Location | Presenter | Content shown |
|---|---|---|---|
| | | | Grid Guardians Module 1 (full / Scenes __) |

| Name | Company | Signature |
|---|---|---|
| | | |

### T5 — Roster Reconciliation and 15-Month Tracker

| Name | Employee / Contractor | Access type (physical / electronic / both) | Completion date | Method | Next due (12 mo.) | Hard deadline (15 mo.) |
|---|---|---|---|---|---|---|
| | | | | | | |

**Program-level tracker:**

| Cycle | Delivery start | Delivery complete | Next target (12 mo.) | 15-month deadline |
|---|---|---|---|---|
| 2026–27 | | | | |

### T6 — Sample Cyber Security Plan Language

> **Cyber Security Awareness (CIP-003-9 Attachment 1, Section 1).** [UTILITY NAME] reinforces cyber security practices, including associated physical security practices, at least once every 15 calendar months for personnel with authorized electronic access or unescorted physical access to assets containing low impact BES Cyber Systems. Reinforcement is delivered annually using the Grid Guardians awareness module through direct communications (computer-based training and email) and at least one additional method (posters/intranet or management-led meetings). The [SECURITY CONTACT] maintains dated copies of content, delivery records, and a tracker of delivery dates to show compliance with the 15-calendar-month interval.

---

## Source References

- NERC Reliability Standard CIP-003-9, Requirement R1.2 and Attachments 1 and 2
- NERC CIP-003-9 Technical Rationale (entity discretion over awareness topics and methods)
- FERC Order No. 918 approving CIP-003-11 (Federal Register, March 24, 2026) and the NERC Project 2023-04 implementation plan
- NERC Reliability Standard CIP-004-7, Requirement R1, Part 1.1
- ReliabilityFirst, "The Lighthouse: CIP low impact from the ground up," Part 8.1 (security awareness plan)

*Have your CIP compliance lead or legal counsel review this crosswalk before relying on it for an audit. Regional entities may have additional expectations.*
