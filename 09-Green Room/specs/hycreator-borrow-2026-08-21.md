# HyCreator — Borrow Spec (Agent Harness for Long Video Generation)

**Date:** 2026-08-21
**Source:** Tencent AI tweet (@TencentAI_News, status 2090720848756007372)
**Frame:** borrow-the-mechanism — "eat the meat, spit out the bones" (Jordan confirmed)

---

## What it is (the bones — we do NOT adopt)
Tencent **HyCreator** — a research agent harness for long video generation. End-to-end
production loop with mid-generation "cut in" rather than prompt re-rolling. Likely tied to
the HunyuanVideo stack, proprietary, not a drop-in for our Seedance/BlockRun MCP rail.
**SPIT OUT:** the tool, its stack, its dependencies.

## The mechanism worth borrowing (the meat)
Two primitives that map 1:1 onto our `seedance-cinematic-film-workflow` pain:

1. **Stateful continuity harness** — an agent holds the storyboard state across the whole
   production and feeds each clip's start-state → next clip's start-state automatically,
   instead of re-deriving the 6-part prompt + locked character + end-state on every call.
   We do this BY HAND today ("lock clip → feed end-state → next clip").

2. **Inspectable / cut-in at any point** — intervene mid-sequence instead of re-rolling.
   We hit this as "regenerate keyframe" / "skip frame" — decisions that cost real money
   ($1.28–3.19 per bad clip).

## Where it wires into our stack (BORROW)
Build a **per-production state file** that the film agent writes + reads on every clip:

```
productions/{name}/state.json
  - locked_character  (coating + seed + palette, from character sheet)
  - style_anchor      (single director/anime anchor)
  - sequence          [{clip, shot, end_state, prompt_used}]
  - last_end_state    (feeds next clip's start)
  - rejected          [{clip, reason, cost}]   # for cut-in / skip decisions
  - wallet_state      # for budget guardrails
```

That makes continuity *stateful* — fewer re-rolls, budget saved, and the
clip-by-clip Vanito-review loop stays (we are NOT removing the human).

## Deliberate NOT-borrow (honest)
Vanito explicitly wants one-clip-at-a-time, review-each. So the harness is NOT
"automate the whole film" — it's "make the agent's continuity stateful so fewer
clips need re-rolling." Keep the human gate; remove the re-derivation waste.

## Verdict
**Borrow:** stateful production harness (per-project state file over the Seedance workflow).
**Spit out:** Tencent's tool + Hunyuan stack.

## Status
Captured as a Green Room idea → candidate to fold into `seedance-cinematic-film-workflow`
when the next Vanito film starts (a `state.json` scaffold + read/write helpers). Not a build
now — next film is the natural test bed.
