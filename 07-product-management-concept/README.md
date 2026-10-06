# Project 7: Product Management Case: A Team Hub for Volunteer-Run Youth Sports (Concept)

A product discovery and planning case: define the problem, form hypotheses about users, prioritize features with **RICE**, scope an **MVP**, set success metrics, and plan how to test the idea cheaply before building anything.

> **Honesty note:** This is a **concept case study**. The personas are **hypotheses I would validate**, not findings from real interviews. Reach, impact, and effort numbers are **estimates**. I haven't done a competitive analysis here, and the plan lists it as a step to do before building. I'm not claiming facts about existing products.

**Skills shown:** problem framing, user personas and jobs-to-be-done, hypothesis-driven discovery, RICE prioritization, MVP scoping, PRD writing, user stories with acceptance criteria, product metrics, experiment design, roadmapping.

---

## 1. Problem statement
Volunteer-run youth sports organizations juggle registration, payments, schedules, and parent updates across group chats, spreadsheets, and e-transfers. Volunteers lose hours to admin and parents miss changes. **Hypothesis:** a single simple hub that handles sign-up, payment, and schedule updates would save organizers time and reduce missed games and no-shows.

## 2. Users (hypotheses to validate)
| Persona | Job to be done | Pain (hypothesized) |
|---|---|---|
| **Organizer / volunteer admin** | "Get every kid registered and paid with minimal chasing" | Manual data entry, unclear payment status, last-minute schedule changes |
| **Parent / guardian** | "Know where my kid needs to be and when, without digging through messages" | Missed updates, multiple channels, paying and signing forms separately |
| **Coach** | "Know who's coming and tell the team quickly" | No reliable attendance list, updates by text |

## 3. Discovery plan
- **Interviews:** 8-10 conversations (3 organizers, 5 parents, 2 coaches). Questions focus on past behavior ("Tell me about the last time a game time changed. What happened?"), not opinions about my idea.
- **Hypotheses to test:**
  - H1: Organizers spend more than 3 hours per season on registration admin.
  - H2: At least 1 in 5 families misses or is confused by a schedule change each season.
  - H3: Parents will pay online if it takes under 5 minutes.
  - H4: Organizers would switch tools if setup takes under 30 minutes.
- **Competitive scan (to do):** list what organizers use today (including spreadsheets and group chats as the "competitor"), what they pay, and what they dislike.

## 4. Prioritization (RICE)
Full table: [`rice_prioritization.md`](rice_prioritization.md)

| Rank | Feature | RICE |
|---|---|---|
| 1 | Online registration + payment | 160 |
| 2 | Automatic schedule + reminders | 160 |
| 3 | Parent-facing team page | 107 |
| 4-8 | Attendance, volunteer sign-up, live scores, photos, player stats | 20 and below |

The top 3 features total **13 person-weeks** of estimated effort and also address the biggest hypothesized pains. They form the MVP. Confidence on the lower items is low (30-50%), which is itself a signal to research before building them.

## 5. MVP scope
**In:** online registration with payment, automatic schedule with email/text reminders, one simple team page for parents.
**Out (for now):** live scores, photos, player stats, volunteer scheduling, mobile app (web only).

## 6. PRD summary
**Goal:** cut organizer admin time and reduce schedule confusion in one season.
**Non-goals:** replacing league management software, video, social features.

**User stories**
- *As a parent, I want to register and pay in one flow so I'm done in under 5 minutes.*
  Acceptance: required fields validated; payment confirmation + receipt emailed instantly; child is placed in the right age group automatically.
- *As an organizer, I want payment status per player so I don't chase anyone manually.*
  Acceptance: dashboard shows paid / pending; pending over 3 days is highlighted.
- *As a parent, I want a reminder before each game so I don't miss it.*
  Acceptance: reminder sent 24 hours before; schedule changes trigger an immediate notification.

**Requirements:** works on mobile browsers; data on minors stored securely with access limited to authorized volunteers; compliance with applicable privacy rules to be confirmed before launch.

## 7. Success metrics
| Type | Metric | Target (assumption) |
|---|---|---|
| North star | % of registered families who complete registration and payment online | 80% in first season |
| Adoption | Time for an organizer to set up a season | < 30 minutes |
| Quality | Registration completion time | < 5 minutes |
| Outcome | Organizer admin hours per season | -50% vs. baseline (measure baseline first) |
| Guardrail | Support requests per 100 families | < 5 |

## 8. Test before building (experiments)
1. **Smoke test:** a one-page landing page describing the product with a "Get early access" sign-up. Success = 20 organizer sign-ups from direct outreach.
2. **Concierge MVP:** run one real season for one organization using a form + spreadsheet + manual reminders, doing by hand what the product would automate. Measure admin hours and missed-game rate versus the old way.
3. **Decision rule:** build only if organizers confirm the pain (H1, H2) and at least 3 would commit to using it next season.

## 9. Roadmap (now / next / later)
- **Now (0-3 months):** discovery, concierge MVP, competitive scan
- **Next (3-6 months):** build registration + payment, schedule + reminders, team page
- **Later (6+ months):** attendance, volunteer scheduling, live scores (only if research supports it)

## 10. Key risks
| Risk | Mitigation |
|---|---|
| Free tools (spreadsheets, group chats) are "good enough" | Test willingness to switch early; make setup under 30 minutes |
| Privacy of minors' data | Collect only what's needed; review legal requirements before launch |
| Low willingness to pay | Test pricing in the smoke test; consider charging per season rather than per user |
| Seasonal demand | Plan launch ahead of registration season |
