# Gentech (Labs) → Jintek (HQ) — 2026-08-12 — Work Routing Convention

## Context
Jordan asked how services/APIs work should be split between HQ and Labs. Agreed convention below. This is the standing rule for where work happens so nothing lands in the wrong group.

## The Rule: split on DECISION vs BUILD, not on project
- **Builds → Labs.** Writing code, wiring SDKs, deploying APIs, fixing bugs, running tests, shipping. Dev work stays in Labs no matter which project it feeds.
- **Decisions → HQ.** Pricing a service, choosing what to launch, positioning in the agent economy, greenlighting a new API, deciding whether a feature ships this week. Jordan's calls live in HQ.
- **Interlocked projects:** don't move projects, move conversations. Thread starts where the PRIMARY work is; only the deep-dive routes to the specialist group.
  - API strategy discussion starts in HQ → implementation moves to Labs.
  - Smart-contract build starts in Labs → surfaces to HQ only for a decision or blocker.

## Operating loop (what Jordan confirmed)
- When it's time to actually do the work, HQ hands it off to Labs (gizmo) → Labs builds → hands it back to HQ → done in the correct place.
- Gentech (Labs) does the routing so nothing gets lost between groups.

## Why
Keeps Labs focused on shipping, HQ focused on steering. Minimal disruption to existing flow.

---
changed:   Established decision-vs-build routing convention between HQ and Labs.
validated: Jordan confirmed the loop (handoff to Labs → build → handoff back).
next-todo: Apply this convention to all future service/API work. Labs owns builds, HQ owns decisions.
