---
name: vault-audit
description: System vault health and security audits — structural integrity, sensitive data inventory, operational infrastructure validation, and governance compliance. Distinguish from vault-intelligence-recon (which discovers credential locations) — audit focuses on completeness, exposure, and policy adherence.
version: 1.0.0
author: DMOB (GenTech Labs)
tags: [audit, vault, security, governance, compliance]
prerequisites:
  commands: [find, grep, jq, python3]
  files_read: [/root/vaults/gentech, /root/.hermes]
---

# Vault Audit — Class-Level Skill

## When to Use

- "Audit the vault" or "run vault health check"
- "Review vault structure and completeness"
- "Find plaintext secrets / credential exposures"
- "Validate atomic writer / ob sync / cron health"
- Periodic compliance review (weekly / monthly)

## What This Skill Covers

1. **Structural audit** — verify expected folders per agent identity are present
2. **Sensitive data inventory** — scan active vault (exclude archives) for exposed secrets patterns
3. **Operational validation** — verify atomic writer, ob sync, cron manifests
4. **Governance review** — check archive filtering, secret lifecycle policies
5. **Incident triage** — classify findings by severity (CRITICAL/MEDIUM/LOW)

## What This Skill Does NOT Cover

- 🔍 **Credential hunting for a specific key** → use `vault-intelligence-recon`
- ✏️ **Writing to the vault** → use `vault-writer`
- 📁 **Obsidian sync troubleshooting** → use `hermes-operations`

## Audit Methodology

### Phase 1: Structure Scan
```bash
# Expected folder mapping per identity
- Labs:           02-Labs/, 02-AAE/, 06-Security/, Audits/
- HQ:             00-HQ/, 00-System/, 00-Inbox/
- Agency:         01-Agency/, 01-Agents/
- Strategies:     03-Strategies/, 03-Projects/
- Entertainment:  04-Entertainment/, 04-Content/
- Learning:       05-Learning/
- Coordination:   09-Green Room/, 09-Templates/, 11-Mess Hall/
- Skills:         12-Skills/
```
Calculate completion percentage; flag missing folders.

### Phase 2: Sensitive Data Scan (Active Vault Only)
Scan patterns: API keys (masked/unmasked), private keys, wallet addresses, JWT, AWS keys, tokens, emails, IPs.
**Exclude:** `10-Archive/`, `memories/`, `.git/`.
Classify by folder and severity.

### Phase 3: Operational Health
- Atomic writer present + lock mechanism + docs
- `ob sync` binary location + executable
- Cron job manifests parseable per profile

### Phase 4: Governance & Leak Analysis
- Archive ingestion filtering (pre-ingestion secret exclude patterns)
- Secret storage policy (runtime .env vs vault)
- Token exposure chain (if found: session logs, usage traces)
- Rotation recommendations per incident

## Severity Classifications

| Level | Criteria | Response |
|-------|----------|----------|
| 🔴 CRITICAL | Plaintext active credential (PAT, JWT, API key) used in production | Fix TODAY — rotate + purge |
| 🟡 MEDIUM | Plaintext sensitive data in inactive file OR masked key in active vault | Fix this week — migrate/delete |
- 🟢 LOW | Wallet addresses, historical data, non-sensitive PII | Document, monitor |

## Audit Report Format

1. Executive Summary (health score, critical incidents table)
2. Critical Incidents (rem: rotate, migrate, delete, verify)
3. Structural Gaps (folder creation checklist)
4. Active Sensitive Data Inventory (by vault area)
5. Operational Infrastructure Health (atomic writer, ob sync, cron)
6. Governance Gaps (archive filtering, policies)
7. Action Items (immediate → this week → next sprint)
8. Verification Checklist (post-remediation bash one-liners)

## Quick Reference Commands

```bash
# Full vault scan (active areas only)
vault_scan.py --full --exclude-archives

# Verify atomic writer
python3 02-Labs/scripts/vault_writer.py read 02-Labs/decisions.md --tail 1

# Check git history for missing folders
git log --oneline --follow -- 06-Security

# JWT decode (safe: header+payload only)
python3 -c "import base64,json; p='<JWT>'.split('.')[1]+'=='; print(json.loads(base64.urlsafe_b64decode(p)))"

# Purge token from Hermes session logs
grep -rl 'PAT_VALUE' /root/.hermes/sessions/ | xargs rm
```

## Common Pitfalls

### 1. Archive vs Active Vault Confusion
**Symptom:** False positives from `10-Archive/` memory backups.
**Fix:** Always pass `--exclude-archives` flag to sensitive scanners. Archive is for historical preservation, not hot secret storage.

### 2. Masked vs Real Key Detection
**Symptom:** Vault `.env` shows `***` but session files contain real value.
**Fix:** Check both vault docs AND Hermes runtime (`/root/.hermes/profiles/*/.env`, `sessions/`). The profile `.env` is source of truth at runtime; vault docs show *which keys exist* not their values.

### 3. Wallet Address Over-flagging
**Symptom:** Hundreds of wallet hits drown out real secrets.
**Fix:** Filter to keys/tokens/jwt patterns only. Wallet addresses are expected in crypto context; only flag if paired with private key or labeled as secret.

### 4. Missing Cron Error Diagnosis
**Symptom:** `jobs.json parse error` reported.
**Fix:** Check file is valid JSON (`cat jobs.json | python3 -m json.tool`). If empty or corrupted, restore from agent profile template.

## Post-Audit Workflow

1. **Save report** → `02-Labs/vault-audit-YYYY-MM-DD.md`
2. **Append decision log** → use atomic writer on `02-Labs/decisions.md`
3. **Notify HQ** → summary in `telegram:Gentech HQ` topic
4. **Create remediation tickets** → if using Linear/Kanban, open issues for critical incidents
5. **Schedule follow-up** → re-run audit 48h after remediation to verify closure

## Integration with Other Skills

- `vault-intelligence-recon` → drill down on a specific secret's location/usage after audit finds it
- `email-redaction-checklist` → if sharing audit report externally, apply PII redaction
- `skill-audit-operations` → parallel pattern for skill version audit (same methodology applies)

---

## Session Notes — 2026-05-03 (DMOB)

Initial run surfaced:
- 2 critical plaintext leaks (GitHub PAT + Colosseum JWT)
- Missing `06-Security/` and `Audits/` folders (Labs identity requirement)
- 158 active files with sensitive patterns (mostly expected wallet context)
- Operational infrastructure healthy (atomic writer, ob sync, cron)

Remediation created:
- `02-Labs/vault-audit-2026-05-03.md` (full report)
- `02-Labs/decisions.md` entry (atomic append)

Key insight: **Audit != Recon**. Recon finds *where X is stored*; audit answers *is everything where it should be and are any secrets exposed?*. Two different skill classes.
