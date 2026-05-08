# Vault Audit — Session Reference: 2026-05-03 (DMOB)

**Skill:** vault-audit
**Context:** First full vault health audit after atomic writer went live.

---

## Incident Taxonomy Defined

| Level | Criteria | Example | Response Time |
|-------|----------|---------|--------------|
| 🔴 CRITICAL | Plaintext active credential (PAT, JWT, API key) used in production | GitHub PAT in root `.env` + Hermes sessions; Colosseum JWT in `00-HQ/` | TODAY — rotate + purge |
| 🟡 MEDIUM | Plaintext sensitive data in inactive OR masked key in active vault | API key in outdated doc, wallet addresses in historical notes | THIS WEEK — migrate/delete |
| 🟢 LOW | Non-sensitive PII, expected crypto context (wallet addresses in LP tracking), archival data | LP positions, historical wallet logs | — |

**Rationale:** Wallet addresses are endemic in crypto vaults and not secrets by themselves. Only flag when paired with private key material or labeled as secret.

---

## Secret Pattern Regex Library

Used in `scan_sensitive()` (vault_audit.py):

```python
patterns = [
    ('API keys (masked)',   r'\w+_API_KEY=\*\*\*'),          # masked placeholders
    ('Private keys',        r'(0x)?[a-fA-F0-9]{64,}'),     # 64+ hex chars (eth key)
    ('Wallet addresses',    r'0x[a-fA-Z0-9]{40}'),          # standard ETH-style addr
    ('JWT tokens',          r'eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*'),
    ('GitHub tokens',       r'ghp_[a-zA-Z0-9]{36}'),
    ('Email addresses',     r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'),
]
```

**Scan scope:** Active vault only (`--exclude-dir=10-Archive,memories`), file types `.md .env .yaml .yml .json .txt .sh`.

---

## Structural Completeness Matrix

Per DMOB identity (`02-Labs/`, `02-AAE/`, `06-Security/`, `Audits/` required as Labs domain):

| Folder | Present? | Files | Notes |
|--------|----------|-------|-------|
| 02-Labs | ✅ | ~6k | Core labs work |
| 02-AAE | ✅ | 2 | Autonomous agents |
| 06-Security | ❌ | — | MISSING — create |
| Audits | ❌ | — | MISSING — create |
| 00-HQ | ✅ | 48 | HQ ops |
| ... | ... | ... | ... |

---

## Operational Checklist Implemented

- ✅ `vault_writer.py` present at `02-Labs/scripts/` — lock `fcntl.flock`
- ✅ `ob` binary at `/usr/local/bin/ob` — Obsidian sync functional
- ✅ All `cron/jobs.json` parse (dmob, desmond, yoyo, gentech)

---

## Governance Gaps Identified

1. **Archive filtering absent** — `10-Archive/Memory-Backups/` ingests everything unfiltered (19.6k files), including secrets.
   - *Fix:* Pre-ingestion filter excluding `*.env`, `*token*`, `*key*`, and credential directories.
2. **Vault-writer policy missing** — No explicit prohibition on writing secrets to active vault.
   - *Fix:* Patch `VAULT_WRITER.md` with: "NEVER store active secrets (API keys, tokens, private keys) in active vault. Use Hermes profile `.env` only."
3. **Secret lifecycle undefined** — No TTL for tokens in vault.
   - *Fix:* Adopt 24h grace period: secrets in vault must be migrated/deleted within one day.

---

## Remediation Command Library

### GitHub PAT Purge
```bash
# 1. Rotate at github.com/settings/tokens
# 2. Remove from vault
sed -i '/GITHUB_PAT/d' /root/vaults/gentech/.env
# 3. Purge from Hermes sessions
grep -rl 'ghp_1ENCDUbq' /root/.hermes/sessions/ | xargs -r rm
# 4. Verify
grep -r "ghp_1ENCDUbq" /root/vaults/gentech /root/.hermes || echo "✅ Clean"
```

### Colosseum JWT Migration
```bash
# 1. Rotate at arena.colosseum.org/copilot
# 2. Add to Hermes profile .env (which profile uses Colosseum? check scripts)
echo "COLOSSEUM_TOKEN=<NEW_JWT>" >> /root/.hermes/profiles/gentech/.env
# 3. Delete vault files
rm /root/vaults/gentech/00-HQ/Credentials/colosseum-copilot-token.md
rm /root/vaults/gentech/00-Hq/config/colosseum-copilot-token.txt
# 4. Update any scripts reading from vault paths to use env var
```

### Create Missing Folders
```bash
mkdir -p /root/vaults/gentech/06-Security/{audits,reports,findings,checklists,tools}
mkdir -p /root/vaults/gentech/Audits
# Or create symlink: ln -s 06-Security/audits Audits
```

---

## Output Structure Standard

Full audit report → `02-Labs/vault-audit-YYYY-MM-DD.md`  
Decision log entry → atomic append to `02-Labs/decisions.md`  
HQ summary → Telegram topic `Gentech HQ / topic <current>`

---

**Next audit:** Weekly health check recommended. Run `vault_audit.py` and compare structural diff.
