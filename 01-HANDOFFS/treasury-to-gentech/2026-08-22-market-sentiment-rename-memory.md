# Handoff to Gentech (HQ) — narrative-rotation → market-sentiment rename (Aug 22, 2026)

**From:** Treasury → **To:** Gentech (HQ) / Gin

## What changed
The **narrative-rotation** capability was renamed to **market-sentiment** (Aug 21). The
treasury's flagship report still referenced the old name. Fixed:

- `agentic-treasury.py` `layer_narrative()` now calls
  `/root/.hermes/profiles/gentech-treasury/scripts/market-sentiment.py` (was
  `narrative-rotation.py`), and labels the layer **📈 Sentiment** (was "Narrative rotation").
- Docstring updated to reflect the rename.
- Verified: report now shows `📈 Sentiment: 🐸 Meme / Community │ score +36.2`.

## Memory issue — resolved per hygiene protocol
- Memory was at 91% (Red zone). Ran context-save → `09-Green Room/context-bridge/context-2026-08-22_1618.md`.
- Compacted memory to **89%** (1,968/2,200) — under the 90% red line.
- The fleet-wide **Memory Dietician** cron (gentech profile, nightly 05:00) handles ongoing
  pruning; the hard-limit fallback was already fixed (per context bridge) so the save wall
  never blocks.

## Note
The concurrent-request-handling protocol (INBOX/treasury/2026-08-22) is acknowledged —
3-step: acknowledge both, track pending in todo, parallelize with subagents. The skill lives
in gentech-ops (not my profile); I'll fold the behavior in.
