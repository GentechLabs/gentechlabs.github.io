# Build Queue Audit — Completion/Routing Gaps (2026-08-17)

**From:** Entertainment (Pixel) — running the new save/handoff rules
**To:** HQ / Gentech — build list accuracy review
**Why:** Jordan flagged the queue keeps inflating (50→60→70) despite projects shipping.
Audit confirms the problem: **completions aren't being logged, so "shipped" has no trace
of the "why" (what was actually done).** This is the exact gap the new rules fix.

---

## Queue state (as of 2026-08-17)

| Status | Count |
|--------|-------|
| shipped | 37 |
| pending | 15 |
| cancelled | 3 |
| blocked | 2 |
| **total** | **57** |

---

## The core problem — completions aren't recorded

**37 items marked "shipped", but the completion trace is missing on most:**

- **7 shipped items have NO `shipped_date`** — no record of WHEN or WHO shipped them:
  #20 FrameForge, #29 awesome-selfhosted, #30 Hippocratic AI, #34 Yield.xyz,
  #35 Paperclip Control Plane, #36 API Audit Fix, #53 GenTech Hub PWA
- **36 of 37 shipped items have NO `shipped_note`** — no "what was actually built + why".
  Only #34 has one. So when Jordan (or the digest) looks at a shipped item, there's
  nothing explaining what shipped, just a status flag.
- **2 items lack a `group` field** (not routed to any group): #36 API Audit Fix (gentech),
  #49 NOT THE GHOST (forge).

**Result:** The queue *looks* like 57 items (inflated, "we're always at 50-70"), but
~36 of the 37 "done" items can't be verified — no completion note, no date, no trace.
This is why it feels like nothing's being pushed out: the completions aren't visible.

---

## Pending (15) — mostly greenlit Aug 3, aging silently

All pending items were greenlit "Aug 3" but have **no age/priority signal** — no
last_updated, no target date, no "stale if not started by X." They sit as an undifferentiated
list. Not duplicates (verified), but **no way to tell what's active vs. stalled.**

- #2–#5, #8, #10, #15: `[Jordan GO Aug 3]` — greenlit, should be actionable
- #6, #7, #13, #17: `[jordan]` — gated on Jordan (DeFi model, ComfyUI, Superteam, Multica)
- #9: `[forge]` — ACE-Step UI, moved to Forge (RTX 3070), still pending
- #16: `[gentech]` Great Agent Hackathon — needs Jordan to register
- #18: Vault Git Divergence — maintenance

---

## Blocked (2) — legitimately stuck

- #1 Super Arcade Tennis — game LIVE, only x402 payments remain (Jordan-gated) ✅ correct
- #11 AI Job Search — blocked since 08-09, needs Jordan

---

## What the new rules fix going forward

The new save/handoff rules (now live on all 4 profiles) require:
1. **Completion must show done + hand off to origin group** — every ship writes a
   `shipped_note` (what + why) + `shipped_date` + `shipped_by`, and a completion file
   in the lane that did the work.
2. **Route, don't dump** — items go to Labs/Forge/Treasury/queue at the stopping point.

**This audit is the baseline.** Going forward the queue should never inflate with
untraceable "shipped" items.

---

## RECOMMENDED ACTIONS for HQ/Gentech review

1. **Backfill the 7 shipped-without-date + 36 without-note items** with completion
   metadata (what shipped, when, by whom) OR downgrade to a lower-confidence status if
   it can't be verified. This alone de-clutters the queue.
2. **Add age/priority to pending items** — a `last_updated` + a "stale threshold" so
   old pending items surface instead of sitting silently.
3. **Confirm #36 and #49's group** so they're routed to the right lane.

---

*Audited by Pixel (Entertainment) — 2026-08-17. Handoff for HQ/Gentech review.*
