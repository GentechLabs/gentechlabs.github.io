---
type: health-report
date: 2026-06-07
ai-first: true
tags: [vault, health, maintenance]
---

## For future Claude
This is an automated vault health check. Run weekly by cron.

## Vault Health — 2026-06-07

### Note Counts (top-level folders)
| Folder | Notes |
|--------|-------|
| 02-Labs | 727 |
| 03-Strategies | 163 |
| 09-Green Room | 144 |
| 03-Projects | 80 |
| 06-Content | 69 |
| 00-HQ | 49 |
| 04-Entertainment | 44 |
| 11-Mess Hall | 39 |
| 12-Skills | 31 |
| 05-Learning | 19 |
| 06-Audits | 15 |
| 02-Agent-Arena | 10 |
| Daily | 5 |
| 15-Gaming | 4 |
| 12-Archive / 10-Archive | 6 |
| **Total** | **~1,400** |

### Stale Notes (>14 days)
- **725 of ~964** non-CCGS/lib notes are stale — **75%** have not been touched in 2+ weeks.
- Only **18** of those stale notes contain wikilinks to other notes.

### Orphan Risk (no [[wikilinks]])
- **930 of ~964** notes contain zero wikilinks — **96% orphan rate**.
- Most notes are self-contained with no cross-references.

### Recommendations
1. **Archive aggressively.** Move completed hackathons, old daily digests, and resolved issues to `10-Archive/`. The `02-Labs/` folder is 727 notes — likely many are finished or abandoned.
2. **CCGS needs cleanup.** The `Claude-Code-Game-Studios/` subtree contributes ~300+ notes. Consider whether it belongs in the vault or as a separate repo.
3. **Link or archive stale notes.** 725 stale notes with zero cross-references are dead weight. Either add `[[wikilinks]]` to relevant notes, or archive them.
4. **Green Room is bloated.** 144 ideas/designs/build-logs — review and graduate or cull.
5. **Daily notes gap.** Only 5 daily notes exist for June. If daily capture isn't happening, the pipeline is broken.

### Health Score: 3/10
The vault is functional but heavily overloaded with unlinked, stale content. A focused 2-hour cleanup session would dramatically improve signal-to-noise.
