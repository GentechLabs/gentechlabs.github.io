# 🔒 GitHub Token Security Audit — 2026-04-24

**Auditor:** Desmond (Creative)  
**Scope:** Full `.hermes/` filesystem + vault + brain backup repo  
**Token audited:** `ghp_Hr...xlo3` (classic PAT, active)

---

## ✅ GOOD NEWS

### 1. Token IS in `.env` (correct location)
- `/root/.hermes/.env` line 371: `GITHUB_TOKEN=***`
- All 4 profile `.env` files also contain it (different md5sums, likely synced)
- Files are `chmod 600` (rw-------) — proper permissions

### 2. Brain backup repo is CLEAN
- `/root/repos/hermes-brain/.gitignore` excludes: `.env`, `auth.json`, `sessions/`, `logs/`
- Verified `git ls-files`: **zero** session files, env files, or `hosts.yml` committed
- Backup script (`scripts/backup.sh`) only copies: memories, skills, config.yaml, SOUL.md, cron/jobs.json, vault highlights

### 3. `auth.json` redaction works
- API keys are stored as `***` in auth.json files across all profiles
- Nous tokens (access_token, refresh_token) are present but that's expected for Nous auth

### 4. Vault is clean
- No live tokens in vault markdown files
- Only placeholder examples (`ghp_...`, `ghp_xx...xxxx`) found in skill docs and memory backups

---

## 🚨 CRITICAL FINDINGS

### Finding 1: Session archives contain raw tokens
**Location:** `.hermes/profiles/{dmob,desmond,yoyo,gentech}/sessions_archive_*/`
**Count:** 113 files across all profiles contain `ghp_` references
**Risk:** HIGH — these are persistent JSON/JSONL conversation logs

**Details:**
- dmob: 423 archive files, 27 contain token data
- desmond: 451 archive files, 8 contain token data  
- yoyo: 1,442 archive files, 37 contain token data
- gentech: 1,447 archive files, 41 contain token data

The archives contain not just GitHub tokens but also:
- Telegram bot tokens (all 4 agents)
- ElevenLabs API key
- OpenCode Go API key
- Nous API key, Ollama API key
- Brave API key, CoinMarketCap API key, Groq API key
- Collaborator phone numbers (Vanito, Dadrian)

### Finding 2: `.hermes_history` contains raw tokens
**Location:** `/root/.hermes/.hermes_history`
**Lines:** 2 occurrences of `ghp_` tokens
**Risk:** MEDIUM — shell command history with pasted tokens

**Exposed in history:**
- `ghp_Gv...zbTU` (older token)
- `ghp_Fc...QQ4f` (older token, noted as "we lost some during update")
- `ghp_Hr...xlo3` (current active token)

### Finding 3: `hosts.yml` stores token in plaintext
**Location:** `.hermes/profiles/{dmob,gentech,yoyo}/home/.config/gh/hosts.yml`
**Risk:** LOW-MEDIUM — required for `gh` CLI operation, but still plaintext on disk

All 3 profiles share the same token:
```yaml
github.com:
    users:
        ProtoJay4789:
            oauth_token: ghp_Hr...xlo3
    oauth_token: ghp_Hr...xlo3
    user: ProtoJay4789
```

### Finding 4: Current active session contains token
**Location:** `.hermes/profiles/desmond/sessions/session_20260424_*.json`
**Risk:** HIGH — live session files are being written right now with token data in tool outputs and reasoning content

The xxd hex dump of `hosts.yml` was captured in the current session JSON, including the full token bytes.

### Finding 5: Logs contain token validation errors
**Location:** `.hermes/logs/errors.log`, `.hermes/logs/agent.log`
**Risk:** LOW — logs show the token prefix/suffix in error messages

Error pattern:
```
Token from `gh auth token` is a classic PAT (ghp_*).
Classic Personal Access Tokens (ghp_*) are not supported by the Copilot API.
```

---

## 📊 TOKEN INVENTORY

| Token | Location | Status |
|-------|----------|--------|
| `ghp_Hr...xlo3` | `.env` (all profiles), `hosts.yml`, session archives, current session, logs | **ACTIVE — EXPOSED** |
| `ghp_Gv...zbTU` | `.hermes_history` only | Historical |
| `ghp_Fc...QQ4f` | `.hermes_history` only | Historical |

---

## 🛠️ REMEDIATION PLAN

### Immediate (Do Today)
1. **Rotate the GitHub token**
   - Revoke `ghp_Hr...xlo3` at https://github.com/settings/tokens
   - Generate a new **fine-grained PAT** (classic PATs are deprecated)
   - Update `/root/.hermes/.env` with new token
   - Re-authenticate `gh` CLI: `gh auth login` or `gh auth refresh`

2. **Sanitize `.hermes_history`**
   ```bash
   sed -i 's/ghp_[A-Za-z0-9]\{20,\}/ghp_REDACTED/g' /root/.hermes/.hermes_history
   ```

3. **Purge current session token leak**
   - Current session files contain the hex dump of `hosts.yml`
   - These will be archived on session end
   - Consider manually sanitizing `.hermes/profiles/desmond/sessions/session_20260424_131832_aaee552b.json`

### Short-term (This Week)
4. **Add session archive sanitization to backup script**
   - The backup script doesn't copy sessions (good)
   - But sessions accumulate indefinitely on disk
   - Consider a cron job that scrubs `sessions_archive_*` for `ghp_*` and replaces with `ghp_REDACTED`

5. **Switch all agents to fine-grained PAT**
   - Fine-grained PATs use `github_pat_*` prefix
   - Required for Copilot API access (logs confirm classic PAT is rejected)
   - Scope needed: `repo`, `workflow`, `copilot_requests` (if using Copilot)

6. **Review `.env` sync strategy**
   - All 4 profile `.env` files have different md5sums
   - Are they manually synced? Consider a single source of truth
   - Root `.env` at `/root/.hermes/.env` is the canonical location

### Policy (Ongoing)
7. **Never paste tokens in chat**
   - The `.hermes_history` leak came from pasting tokens into Telegram/chat
   - Use `hermes setup` or direct file editing instead
   - If a token must be shared in chat, revoke it immediately after use

8. **Enable Hermes secret redaction**
   - Hermes already has secret redaction in logs (`***` substitution)
   - But session JSON files bypass this (they store full tool output)
   - Consider enabling `HERMES_REDACT_SESSIONS=true` if available

---

## 🎯 VERIFICATION CHECKLIST

- [ ] Token rotated on GitHub
- [ ] `.env` updated with new token
- [ ] `gh auth status` shows new token
- [ ] `.hermes_history` sanitized
- [ ] Current session JSON scrubbed (or accepted as transient)
- [ ] Backup script verified to NOT copy sessions
- [ ] All agents tested with `gh api user` to confirm auth

---

**Audit completed by Desmond at 2026-04-24 13:20 UTC**
