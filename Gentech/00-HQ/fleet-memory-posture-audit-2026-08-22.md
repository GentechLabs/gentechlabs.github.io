# Fleet Memory Posture Audit — 2026-08-22

Trigger: Jordan "everybody should start working on their memory we want to start pruning." Watchdog (a1069d08e993) flagged 5 files ≥85%.

Caps: MEMORY.md = 2200 chars, USER.md = 1375 chars.

## Measured (evidence-first)

| Profile | File | Chars | Cap | Posture |
|---------|------|-------|-----|---------|
| gentech (self) | MEMORY.md | 1854 | 2200 | ✅ 84% (pruned this session) |
| gentech-treasury | MEMORY.md | 2084 | 2200 | ⚠️ 95% |
| gentech-treasury | USER.md | 1020 | 1375 | ✅ 74% |
| pixel | MEMORY.md | 2133 | 2200 | ⚠️ 97% |
| pixel | USER.md | 1353 | 1375 | ⚠️ 98% |
| gentech | USER.md | 1346 | 1375 | ⚠️ 98% |

## Interpretation
- **gentech (self)**: MEMORY pruned 2121→1854 (84%). USER.md still 98% — needs a pass.
- **gentech-treasury**: MEMORY 95% (red-ish, near cap). USER fine.
- **pixel**: both MEMORY (97%) and USER (98%) near cap — most urgent.

## Routed handoffs
- `01-HANDOFFS/gentech-to-treasury/2026-08-22-memory-posture.md`
- `01-HANDOFFS/gentech-to-pixel/2026-08-22-memory-posture.md`
- gentech USER.md handled by self (this session).

## Fix each lane needs (verbatim)
1. Save to brain EARLY at 80/85% — dated file to 09-Green Room/context-bridge/, route, load fresh.
2. Let dietician cron archive low-priority to 11-Mess Hall/memory-archive/.
3. Never run 95%+ — consolidate in ONE atomic batch (remove stale + add new).
4. Save at natural stopping points.
