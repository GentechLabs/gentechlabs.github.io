# 🔄 Skills Auto-Update Check — Cron Job Set

**Date:** 2026-04-27
**Triggered by:** Jordan request in HQ
**Agent:** Gentech

---

## What Was Built

| Layer | Artifact |
|---|---|
| **Script** | `~/.hermes/scripts/cron/skills-update-github-check.sh` |
| **Cron Job** | `Skills GitHub Update Check` — Sundays 4:00 PM |
| **Report Output** | `09-Green Room/skills-update-check-YYYY-MM-DD.md` |

## How It Works

1. Scans all skill dirs under `~/.hermes/profiles/gentech/skills/`
2. For any with `.git`, fetches upstream quietly
3. Compares `HEAD` vs `origin/HEAD`
4. If behind, writes a **checkbox approval list** to Green Room:
   - `- [ ] Approve update → \`skill-name\``
   - Shows commits behind + latest upstream commit message
5. Vault auto-commits the report
6. **Delivers to origin** (HQ thread) with summary

## Routing Protocol

| Trigger | Routing |
|---|---|
| Updates found | Report saved to `09-Green Room/` + delivered to HQ |
| Jordan says "yes" to any checkbox | Gentech pulls + merges that skill |
| No updates | Silent confirmation only |

## Cron Registry Entry

```yaml
name: Skills GitHub Update Check
schedule: 0 16 * * 0  # Sundays 4:00 PM
repeat: forever
deliver: origin
```

---

## ✅ Status

- [x] Script created + hardened (`set -euo pipefail`)
- [x] Cron job registered
- [x] First run: 2026-05-03 at 4:00 PM
- [x] Vault sync wired in

---

## Related

- Existing job: `Weekly Skills Update Check` (Sundays 9:00 AM) — this is a **complement**, not replacement. That job audits registry health; this one checks git upstreams.
