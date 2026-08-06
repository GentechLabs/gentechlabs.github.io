# Group Return-Loop — End-of-Day Report Instruction (Aug 6)

**Goal:** Make the Morning Digest actually surface real group reports (not placeholders).

## What was done
Added an **"End-of-Day Report (REQUIRED)"** section to the SOUL.md of all 5 group agents so they write their returns to the vault each session:

| Agent | Profile | SOUL.md |
|---|---|---|
| Gentech (HQ/Labs/Ent/Strategies) | gizmo | `/root/.hermes/profiles/gizmo/SOUL.md` |
| Treasury (Finance) | gentech-treasury | `/root/.hermes/profiles/gentech-treasury/SOUL.md` |
| (Labs) | desmond | `/root/.hermes/profiles/desmond/SOUL.md` |
| (Entertainment) | dmob | `/root/.hermes/profiles/dmob/SOUL.md` |
| (Strategies) | yoyo | `/root/.hermes/profiles/yoyo/SOUL.md` |

## The instruction each agent now follows
At end of session, write a dated note to:
- `01-HANDOFFS/<group>-to-gentech/YYYY-MM-DD.md` (completed / blocked / notes)
- Append shipped item IDs to `01-HANDOFFS/<group>-completions.md`
- Then `git add -A && git commit` to push it

## Why
- The return-loop plumbing already existed (`group-returns-scanner.py` reads these files nightly)
- But only Forge was writing real completions; labs/entertainment/finance/hq were placeholders
- This instruction makes every group agent actually write its report so the Morning Digest works as intended

## Note
- SOUL.md files live in each profile dir (NOT the vault), so they're not in git — but they're saved on disk and take effect on the agent's next session.
- The `<your-group>` placeholder should be replaced with the agent's actual group (labs/entertainment/finance/hq) — worth confirming per-agent on next session.
