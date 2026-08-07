# Group Return-Loop — End-of-Day Report Instruction (Aug 6)

**Goal:** Make the Morning Digest actually surface real group reports (not placeholders).

## Active agents (Jordan confirmed Aug 6)
Only these 3 profiles are in use. desmond/dmob/yoyo are NOT used — reverted.

| Agent | Profile | SOUL.md | Group |
|---|---|---|---|
| Gentech (main) | gizmo | `/root/.hermes/profiles/gizmo/SOUL.md` | HQ/Labs/Strategies |
| Treasury (Finance) | gentech-treasury | `/root/.hermes/profiles/gentech-treasury/SOUL.md` | Finance |
| Gentech (Entertainment) | gentech (this profile) | `/root/.hermes/profiles/gentech/SOUL.md` | Entertainment |

## The instruction each active agent now follows
At end of session, write a dated note to:
- `01-HANDOFFS/<group>-to-gentech/YYYY-MM-DD.md` (completed / blocked / notes)
- Append shipped item IDs to `01-HANDOFFS/<group>-completions.md`
- Then `git add -A && git commit` to push it

## Why
- The return-loop plumbing already existed (`group-returns-scanner.py` reads these files nightly)
- But only Forge was writing real completions; labs/entertainment/finance/hq were placeholders
- This instruction makes each active agent actually write its report so the Morning Digest works as intended

## Note
- SOUL.md files live in each profile dir (NOT the vault), so they're not in git — but they're saved on disk and take effect on the agent's next session.
- desmond/dmob/yoyo were reverted to their original generic Hermes SOUL.md (unused profiles).
