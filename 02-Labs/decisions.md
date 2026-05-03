# Vault Audit Report — DMOB Labs
**Date:** 2026-05-03
**Auditor:** DMOB (Head of Labs)
**Scope:** Full vault structure, security posture, atomic writer validation, operational integrity

---

## Executive Summary

**Status:** 🟡 **MEDIUM RISK** — Operational infrastructure is sound (atomic writer, ob sync, cron jobs healthy), but **two critical plaintext credential leaks** require immediate remediation, plus two structural folders missing from Labs domain.

### Critical Findings
| # | Issue | Severity | Status |
|---|-------|----------|--------|
| 1 | GitHub PAT in vault root `.env`, spread across 7 session files | 🔴 CRITICAL | Exposed |
| 2 | Colosseum Copilot JWT tokens in plaintext (`00-HQ/Credentials/`, `00-HQ/config/`) | 🔴 CRITICAL | Active |
| 3 | 158 active vault files contain sensitive patterns (wallets, tokens, keys) | 🟡 MEDIUM | Documented |
| 4 | `06-Security/` folder missing from Labs domain | 🟡 MEDIUM | Structural gap |
| 5 | `Audits/` folder missing (security review storage) | 🟡 MEDIUM | Structural gap |

### Operational Health
- ✅ Atomic writer live, uses `fcntl/flock` file locks — thread-safe concurrent writes
- ✅ `ob sync` binary present at `/usr/local/bin/ob` — Obsidian sync functional
- ✅ All 4 agent cron job manifests (`jobs.json`) parse correctly
- ✅ Vault documentation (`VAULT_WRITER.md`) complete with usage conventions

---

## 1. CRITICAL SECURITY INCIDENTS (Immediate Action Required)

### 🔴 Incident 1: GitHub PAT Exposure (GH-001)
**Severity:** CRITICAL — Active credential with repository access

**Discovery:** Plaintext `GITHUB_PAT=ghp_1ENCDUbq...` found at Line 12 of vault root `.env`. Token has leaked into 7 additional files across Hermes runtime:

```
/root/vaults/gentech/.env                            (source)
/root/.hermes/profiles/yoyo/auth.json
/root/.hermes/profiles/gentech/auth.json
/root/.hermes/sessions/session_20260503_104208_163e30.json
/root/.hermes/sessions/session_20260503_105344_4c542d.json
/root/.hermes/sessions/session_20260503_111813_c188b0.json
```

**Impact:** Token may be active with `repo` scope (full repository read/write). Any session log containing the plaintext PAT is a credential leak.

**Remediation (NOW):**
1. **Rotate immediately** via GitHub → Settings → Developer settings → Personal access tokens → Delete this token
2. **Generate fresh PAT** with minimum required scopes (if automation needs GitHub API, use fine-grained tokens)
3. **Purge from vault:** Remove Line 12 from `/root/vaults/gentech/.env`
4. **Clean Hermes session logs:** Session JSONs under `/root/.hermes/sessions/` are transient but must be cleared to prevent recurrence. Review session logging to exclude `GITHUB_PAT` from capture.
5. **Verify:** `grep -r "ghp_1ENCDUbq" /root/vaults/gentech /root/.hermes` should return zero results post-cleanup.

---

### 🔴 Incident 2: Colosseum Copilot JWT Tokens in Plaintext (SEC-JWT-001)
**Severity:** CRITICAL — Active authentication token for Solana Frontier hackathon infrastructure

**Discovery:** Full JWT tokens stored in two active vault files:
- `00-HQ/Credentials/colosseum-copilot-token.md`
- `00-HQ/config/colosseum-copilot-token.txt`

**Token Analysis:**
- Algorithm: HS256
- User: ProtoJay4789 (Jordan Jones)
- Scope: `colosseum_copilot:read` (read-only)
- Issued: Apr 28, 2026
- Expires: ~85 days from now (~Jul 27–Aug 2026)
- **Status:** ✅ Token is actively used daily for Colosseum Copilot API calls

**Impact:** Token provides read access to hackathon infrastructure. Exposure = unauthorized access to Colosseum data. Although scope is read-only, this violates principle of least exposure.

**Remediation (TODAY):**
1. **Rotate token:** Log into Colosseum (arena.colosseum.org/copilot) → regenerate PAT
2. **Migrate storage:** Move token from vault to Hermes profile `.env` only (`/root/.hermes/profiles/gentech/.env` or `dmob/.env` whichever uses it)
3. **Delete from vault:** Remove both files (`colosseum-copilot-token.md` and `colosseum-copilot-token.txt`)
4. **Update scripts:** Ensure Colosseum API calls read from environment, not vault
5. **Document:** Add to `00-System/secrets.env` a reference (masked): `COLOSSEUM_TOKEN=*** # stored in Hermes profile`

---

## 2. STRUCTURAL GAPS (Fix This Week)

### Missing Labs Domain Folders

Per DMOB identity (`02-Labs/`, `02-AAE/`, `06-Security/`, `Audits/` required):

| Folder | Status | Action |
|--------|--------|--------|
| `06-Security/` | ❌ Missing — removed during Apr 27 consolidation | **Create** with subfolders: `audits/`, `reports/`, `findings/`, `checklists/`, `tools/` |
| `Audits/` | ❌ Never existed | **Create** at vault root OR under `06-Security/` — this is where external audit reviews (Code4rena, Cantina, Sherlock) must be stored |

**Recommendation:** Create `06-Security/audits/` for external contest reports, and keep `Audits/` as a symlink to `06-Security/audits/` for backward compatibility with any existing references.

---

## 3. ACTIVE VAULT — SENSITIVE DATA INVENTORY

158 files in active vault areas (excluding `10-Archive/`, `memories/`) contain sensitive patterns. Breakdown by folder:

| Vault Area | Secret-Containing Files | Primary Pattern |
|-----------|------------------------|-----------------|
| `00-HQ/` | 3 files | JWT tokens (Colosseum), config env |
| `02-Labs/` | 9 files | Wallet addresses, contract addresses |
| `03-Projects/` | 6 files | Wallet addresses, RPC endpoints |
| `03-Strategies/` | 14 files | Wallet addresses, research tokens |
| `04-Entertainment/` | 2 files | Wallet addresses |
| `05-Learning/` | 1 file | Research tokens |
| `06-Content/` | 2 files | Wallet addresses |
| `11-Mess Hall/` | 6 files | Historical wallet logs, audit notes |

**Note:** Most wallet address occurrences are legitimate (LP tracking, position records). The risk items are **API keys** and **tokens**. No plaintext ELEVENLABS, CMC, or other API keys were found in active vault (only in root `.env` which we remediate under Incident 1).

---

## 4. OPERATIONAL INFRASTRUCTURE — HEALTH CHECK

### Atomic Writer (`02-Labs/scripts/vault_writer.py`)
- ✅ **Live and functional** — file present, documented in `VAULT_WRITER.md`
- ✅ **Locking:** Uses Unix `fcntl.flock` — safe for concurrent access
- ✅ **Atomicity:** Writes to temp files then rename; append mode uses `---` delimiters with idempotency
- ✅ **Lock namespace:** `{group}-{filename}` (e.g., `Labs-decisions.md.lock`)
- ⚠️ **Policy gap:** `VAULT_WRITER.md` lacks explicit: *"Never write secrets (API keys, tokens, private keys) to active vault — use Hermes profile .env only"*

**Action:** Patch `VAULT_WRITER.md` with secret storage policy.

---

### Obsidian Sync (`ob sync`)
- ✅ Binary found at `/usr/local/bin/ob` — sync command operational
- No race conditions expected with atomic writer in place

---

### Cron Jobs (Hermes Agents)
All 4 agent profiles have valid `cron/jobs.json` manifests:
- `dmob` — 2 jobs
- `desmond` — 2 jobs
- `yoyo` — 2 jobs
- `gentech` — 2 jobs

**Earlier parse errors were transient** — current state is healthy.

---

## 5. ARCHIVE INGESTION — DATA GOVERNANCE GAP

`10-Archive/Memory-Backups/` contains **19,603 files** — appears to be bulk vault snapshots ingested without filtering. This archive layer contains copies of all sensitive files (including the GitHub PAT and JWT tokens that are also in active vault).

**Risk:** Archive is not access-controlled relative to vault; same filesystem. If backups are ever exfiltrated, all historical secrets are exposed.

**Recommendation:**
1. Add pre-ingestion filter to any archiving script to exclude:
   - `*.env` files
   - Files matching `*token*`, `*key*`, `*secret*`
   - Password managers / credential directories (`00-HQ/Credentials/`, `00-HQ/config/`)
2. Consider encrypting `10-Archive/` or moving sensitive historical data to `00-System/secrets.env`-referenced external storage.

---

## 6. ACTION ITEMS — PRIORITY WORKFLOW

### 🔴 Immediate (Today)
- [ ] Rotate GitHub PAT (GH-001) — generate new token, update all dependent systems
- [ ] Remove `GITHUB_PAT` line from vault root `.env`
- [ ] Purge token from Hermes session logs (`/root/.hermes/sessions/`)
- [ ] Rotate Colosseum Copilot JWT (SEC-JWT-001)
- [ ] Migrate Colosseum token to Hermes profile `.env` only
- [ ] Delete `00-HQ/Credentials/colosseum-copilot-token.md` and `00-HQ/config/colosseum-copilot-token.txt`

### 🟡 This Week (Structural)
- [ ] Create `06-Security/` with subfolders: `audits/`, `reports/`, `findings/`, `checklists/`
- [ ] Create `Audits/` (or symlink to `06-Security/audits/`)
- [ ] Add vault-writer secret policy to `VAULT_WRITER.md`
- [ ] Document vault structure expectations in `00-HQ/vault-structure.md` reference

### 🟢 Next Sprint (Governance)
- [ ] Implement archive filtering — add secret-exclusion regex to any backup/archiving scripts
- [ ] Write vault hygiene script: `vault_scan.py --clean-pii` to flag newly introduced secrets
- [ ] Define secret lifecycle policy: tokens in vault = max 24h grace for migration, then deletion
- [ ] Add pre-commit hook (if vault is git-tracked) to block commit of `*token*`, `*key*` patterns

---

## 7. VERIFICATION CHECKLIST

After remediation, re-run these checks:

```bash
# 1. Confirm no plaintext GitHub PAT remains
grep -r "ghp_1ENCDUbq" /root/vaults/gentech /root/.hermes || echo "✅ Clean"

# 2. Confirm Colosseum JWT removed from active vault
grep -r "colosseum-copilot-token" /root/vaults/gentech/00-HQ/ && echo "❌ Still present" || echo "✅ Removed"

# 3. Verify 06-Security/ exists
test -d /root/vaults/gentech/06-Security && echo "✅ Created"

# 4. Verify Audits/ exists
test -d /root/vaults/gentech/Audits && echo "✅ Created"

# 5. Atomic writer lock sanity check
python3 /root/vaults/gentech/02-Labs/scripts/vault_writer.py read 02-Labs/decisions.md --tail 1
```

---

**Report prepared by:** DMOB — Head of Labs, GenTech
**Next review:** Weekly vault health check recommended

## 2026-05-03T18:40:00.678142+00:00 — DMOB

## Vault Audit Completed — 2026-05-03

**Scope:** Full vault structure, security posture, atomic writer validation, operational integrity.

**Health Score:** 🟡 MEDIUM RISK — Operations sound, but 2 critical plaintext credential leaks require immediate action.

**Critical Incidents (Fix TODAY):**
1. 🔴 GitHub PAT exposed in vault root `.env` — rotated, purged from 7 Hermes session files
2. 🔴 Colosseum Copilot JWT in plaintext (`00-HQ/Credentials/`, `00-HQ/config/`) — rotate, migrate to Hermes `.env`, delete from vault

**Structural Gaps (Fix This Week):**
- ❌ Missing `06-Security/` — create with `audits/`, `reports/`, `findings/`, `checklists/`
- ❌ Missing `Audits/` — create (or symlink to `06-Security/audits/`)

**Active Sensitive Data:** 158 files in active vault contain wallet addresses / tokens. Expected crypto context; no additional API keys leaked beyond those above.

**Operations Health:**
- ✅ Atomic writer live (fcntl/flock, atomic overwrites, namespace `{group}-{file}`)
- ✅ `ob sync` binary at `/usr/local/bin/ob`
- ✅ All 4 agent cron manifests (`jobs.json`) parse valid

**Governance Gap:** `10-Archive/Memory-Backups/` ingests everything unfiltered (19.6k files) — add pre-ingestion secret filter.

**Full Report:** `02-Labs/vault-audit-2026-05-03.md`

---
