# Memory-Backups Intentional Duplicate Pattern

**Date identified:** 2026-05-03  
**Pattern:** Agent-prefixed DR snapshot duplicates  
**Status:** Whitelisted — DO NOT DELETE

---

## Pattern Location
```
10-Archive/Memory-Backups/<timestamp>/
├── desmond-skills-*.md
├── dmob-skills-*.md
├── yoyo-skills-*.md
└── gentech-skills-*.md
```

## Why It Exists
Each agent (Desmond, DMOB, YoYo, Gentech) receives a **full isolated backup** of shared skill knowledge for disaster recovery. The content is bit-identical across prefixes; the duplication is intentional for:
- **Isolation:** Each agent's backup is self-contained
- **Recovery:** Any agent can be restored from any snapshot
- **Namespace clarity:** Prefix identifies ownership

## Whitelist Rule

**Regex pattern:**
```
^10-Archive/Memory-Backups/[^/]+/(yoyo|dmob|desmond|gentech)-skills-.*\.md$
```

**Hash-based exemption:** If all files in a duplicate set share common prefixes matching `^(yoyo|dmob|desmond|gentech)-` AND live under the same Memory-Backups timestamp directory → classify as **intentional DR copies**.

## Detection signature

```bash
# Find sets where same skill appears across 3+ agent prefixes
find 10-Archive/Memory-Backups/ -name "*-skills-*.md" \
  -exec sha256sum {} \; | sort | uniq -w 64 -d
```

Expected output: hash collisions across files named like:
- `desmond-skills-server.md`
- `dmob-skills-server.md`
- `yoyo-skills-server.md`
- `gentech-skills-server.md`

All four have **identical content** → whitelist.

## Action in vault-maintenance-audit

When duplicate detection flags these:
1. Count agent prefixes in set
2. If ≥3 prefixes AND location is `Memory-Backups/*/` → skip deletion
3. Log in report as "Intentional Duplicates (DR)" with count, not file list

---

## Related

See also: `10-Archive/Memory-Backups/` README if present; agent backup cron jobs in `00-System/agent-profiles/*/cron/`
