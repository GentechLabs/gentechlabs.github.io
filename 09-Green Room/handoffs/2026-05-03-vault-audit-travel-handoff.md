---
from: Gentech
to: DMOB
date: 2026-05-03
subject: Vault audit — travel convention cleanup needed
status: pending
---

# Travel Convention Cleanup

**Context:** Vault audit identified one convention violation in `00-HQ/Travel/Philippines/`.

## Task
1. Inspect `flights.md` — determine if still relevant
2. If yes, rename to `{YYYY}-{Trip-Name}.md` format (e.g. `2026-Philippines-Flights.md`) or merge into existing trip file `2026-Birthday-Trip-*.md`
3. If no, delete or archive to `00-HQ/Travel/Philippines/ARCHIVE/`

## Deadline
ASAP — before next team sync (May 5 planning window)

## Acceptance Criteria
- `00-HQ/Travel/Philippines/` contains only `README.md` and files matching `YYYY-*.md`
- No `flights.md` remains in active directory
- Update any cross-references if file was renamed

---
*Audit-triggered handoff from Gentech. Logged to decisions.md automatically.*
