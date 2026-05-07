---
name: vault-intelligence-recon
description: Systematic discovery of sensitive data, credentials, contacts, and operational intelligence across the Gentech Obsidian vault and Hermes agent infrastructure. NOT for external vulnerability scanning; this is internal asset mapping.
version: 1.0.0
author: DMOB (GenTech Labs)
tags: [recon, vault, intelligence, credentials, osint, gentech]
prerequisites:
  commands: [find, grep, jq, curl, cat]
  read: [/root/vaults/gentech, /root/.hermes]
---

# Vault Intelligence & Recon — Systematic Discovery Playbook

## When to Use

- "Where is the API key stored?" (ElevenLabs, CMC, OpenAI, etc.)
- "Find all wallet addresses used by AAE"
- "What are the voice talent contacts / inspirations?"
- "List active cron jobs across all agent profiles"
- "Pull the security researcher watchlist"
- "Where does the brain store collaborators?"
- Any task requiring **mapping of internal assets** across vault + Hermes

## What This Skill Covers

1. **Credentials discovery** — API keys, tokens, secrets (and their actual runtime locations vs documentation)
2. **Contact enumeration** — internal collaborators, external monitoring accounts, voice inspirations
3. **Operational mapping** — cron jobs, scripts, config files, agent profiles
4. **Asset correlation** — cross-referencing vault docs with Hermes runtime state

## The Multi-Layer Search Strategy

Gentech data lives in **three overlapping layers**:
- **Vault** (`/root/vaults/gentech/`) — Obsidian docs, markdown, structured configs
- **Hermes runtime** (`/root/.hermes/`) — agent profiles, `.env` files, secrets, scripts
- **System secrets** (`/root/vaults/gentech/00-System/`, `/root/vaults/gentech/00-HQ/Credentials/`) — sensitive configs

### General Approach

```
START: clear objective (e.g., "find ELEVENLABS_API_KEY")
│
├─ STEP 1: VAULT DOCUMENTATION GATHER
│  ├─ find vault for relevant files (name patterns: *key*, *cred*, *secret*, *env*, *.env*)
│  ├─ grep -r for the item name across vault (case-insensitive)
│  └─ check standard vault locations:
│     • 00-System/secrets.env
│     • 00-HQ/Credentials/
│     • 02-Labs/social-layer-poc/config.sh (for monitoring lists)
│     • 01-Agency/team-roster.md (internal collaborators)
│     • 01-Agents/voices/*.md (voice inspirations/clones)
│     • 00-HQ/Brainstorm/ (strategy brain docs)
│
├─ STEP 2: RUNTIME STATE CHECK
│  ├─ check /root/.hermes/.env (root agent env)
│  ├─ check each profile's .env: /root/.hermes/profiles/{dmob,yoyo,desmond,gentech}/.env
│  ├─ check for masked vs real: vault often shows `***` but profile .env has real value
│  └─ verify via: grep "ITEM_NAME" /root/.hermes/profiles/*/.env
│
├─ STEP 3: ACTIVE JOBS/SCHEDULES
│  ├─ check Hermes cron directories: /root/.hermes/profiles/*/cron/
│  ├─ read jobs.json for job definitions
│  └─ cross-reference with vault cron-jobs registry (if exists)
│
├─ STEP 4: SCRIPT / CONFIG TRACE
│  ├─ where is the item actually USED?
│  ├─ grep -r "ITEM_NAME" /root/.hermes/scripts/ /root/vaults/gentech/scripts/
│  └─ identify the canonical source of truth (often a config file like .lfj-aae-config.json)
│
└─ STEP 5: API VALIDATION (if appropriate)
   ├─ for API keys: curl -H "Authorization: Bearer $KEY" endpoint (safe read-only)
   ├─ check quota/status: e.g., ElevenLabs /v1/user, CMC /v1/key/info
   └─ do NOT send production audio or incur costs
```

## Key Directories & Their Purpose

| Path | Contents | For Finding |
|------|----------|------------|
| `/root/vaults/gentech/.env` | Vault-level env vars (often masked `***`) | Documented keys (not live values) |
| `/root/.hermes/.env` | Root Hermes agent env | Live keys used by Gentech agent |
| `/root/.hermes/profiles/*/.env` | Per-agent env | Runtime keys for each sub-agent |
| `/root/vaults/gentech/00-System/secrets.env` | Secrets (commented references) | Which keys exist + where stored |
| `/root/vaults/gentech/01-Agency/team-roster.md` | Internal collaborators | Names + Telegram IDs |
| `/root/vaults/gentech/02-Labs/social-layer-poc/config.sh` | Monitoring lists | Security researchers, DeFi protocols, hackathon accounts |
| `/root/vaults/gentech/01-Agents/voices/*.md` | Voice configs | Voice IDs, inspirations, clone targets |
| `/root/vaults/gentech/02-Labs/Agent-Voice-Assignments.md` | Voice assignment matrix | Agent → Voice mapping |
| `/root/.hermes/profiles/*/cron/` | Cron job definitions | Active scheduled jobs per agent |
| `/root/.hermes/scripts/` | Shared scripts | Config files (e.g., `cmc_config.json`, `.lfj-aae-config.json`) |

## Common Pitfalls

### 1. **Masked keys in vault vs real keys in Hermes**
**Symptom:** Vault shows `ELEVENLABS_API_KEY=***` but API calls fail.  
**Cause:** Vault stores masked values; real key lives in `/root/.hermes/.env` or profile `.env`.  
**Fix:** Always check both vault `.env` AND Hermes profile `.env`. The profile env is source of truth at runtime.

### 2. **Docs out of sync with runtime**
**Symptom:** Documentation says key is in one file; script reads another.  
**Cause:** Recent rotation/migration (e.g., CMC key moved to `cmc_config.json`).  
**Fix:** Trace the actual script: `grep -r "API_KEY" /root/.hermes/scripts/` to find the real config loader.

### 3. **Multiple brain/contact locations**
**Symptom:** Cannot find "brain contacts" because they're not in a single file.  
**Cause:** Gentech splits brain data:  
  - Internal collaborators → `01-Agency/team-roster.md`  
  - External monitoring → `02-Labs/social-layer-poc/config.sh`  
  - Voice inspirations → `01-Agents/voices/*.md`  
  - Strategy brain → `00-HQ/Brainstorm/` and `02-Labs/AAE-Brain-Layer.md`  
**Fix:** Search by intent, not filename. Use `grep -r "contact\|@[a-zA-Z0-9_]"` across vault.

### 4. **Assuming one directory holds everything**
**Symptom:** Searched only `02-Labs/` and missed `01-Agency/`.  
**Cause:** Domain routing (brain for ops vs brain for strategy vs brain for creative).  
**Fix:** Query all top-level vault folders when unsure: `00-HQ`, `01-Agency`, `02-Labs`, `03-Strategies`, `04-Entertainment`, `06-Security`.

## Trigger Phrases (when user says…)

- "Check the brain for…" → Search **vault** (`00-HQ/Brainstorm/`, `02-Labs/AAE-Brain-Layer.md`, `01-Agency/team-roster.md`) **AND** **GitHub repos** (`~/repos/`, `~/workspace/`) using `git grep`
- "Is the key in EMV?" → Check environment variables in `.env` files (Hermes + vault)
- "Where do we store…?" → Run multi-location discovery (vault → Hermes → scripts)
- "List all contacts for…" → Enumerate relevant config arrays (social-layer-poc, voice assignments, team roster)
- "Audit the vault / vault health check" → Use `vault-audit` (comprehensive structural + security audit)

---

### Brain Scope: Vault + GitHub

The "brain" consists of **two overlapping surfaces**:

1. **Obsidian vault** (`/root/vaults/gentech/`) — structured notes, decisions, handoffs, specs
2. **GitHub repos + local clones** (`~/repos/`, `~/workspace/`) — active codebases, build artifacts, commit history

When asked to "check the brain" for something code-related, query BOTH:
- Vault first (high-level intent, architecture, decisions)
- Repos second (implementation details, current state, recent changes)

Example: "How does agent-escrow handle validation?"  
→ Vault: `02-Labs/Hackathons/Active/agent-escrow/ARCHITECTURE.md` (if exists)  
→ Repo: `~/workspace/agent-escrow/src/Validator.sol` + latest commit diff

## Output Structure

When reporting findings, structure clearly:

```
## Found: [Item Name]

**Status:** [active | deprecated | pending | masked]

**Locations:**
- *Documentation:* `path/to/doc.md` (shows placeholder/context)
- *Runtime:* `/root/.hermes/profiles/agent/.env` (actual value used)
- *Config:* `/root/.hermes/scripts/config.json` (canonical source)
- *Related:* `optional-links.md` (context, history)

**Notes:** [usage, rotation schedule, dependencies]

**Actionable:** [what to do next if incomplete]
```

## Cross-Skill References

- `vault-audit` — for comprehensive vault health, structural integrity, and security posture audits (**different class**: audit vs recon)
- `security-contest-monitoring` — for external platform recon (HackenProof, Cantina)
- `github-auth` — for credential rotation/revocation workflows
- `email-redaction-checklist` — when sharing contact lists externally
- `obsidian` — for vault search/sync operations

## Quick Reference Commands

```bash
# 1. Find any API key variable across all env files
grep -r "ELEVENLABS_API_KEY" /root/.hermes/profiles/*/.env /root/vaults/gentech/.env

# 2. Dump all masked keys from vault (shows which keys exist)
grep -r "_API_KEY=.*\*\*\*" /root/vaults/gentech/.env 00-System/secrets.env

# 3. List all cron jobs across agents
find /root/.hermes/profiles/*/cron -name "jobs.json" -exec cat {} \;

# 4. Extract voice contacts (IDs + inspirations)
grep -r "Voice ID:" /root/vaults/gentech/01-Agents/voices/*.md

# 5. Get security researcher watchlist
cat /root/vaults/gentech/02-Labs/social-layer-poc/config.sh | grep -A20 "SECURITY_RESEARCHERS"

# 6. Find ALL files mentioning a keyword (cross-vault)
grep -r "KEYWORD" /root/vaults/gentech --include="*.md" --include="*.env" --include="*.yaml"
```

## Session Log Reference

For examples of recent recon sessions, see:
- `references/2026-05-02-elevenlabs-key-brain-contacts-discovery.md` — full walkthrough of multi-layer search for ELEVENLABS_API_KEY and brain contacts
