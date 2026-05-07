---
name: vault-script-execution
description: "Run and troubleshoot scripts from the Obsidian vault — path resolution, pre-flight dependency checks, credential verification, and structured error reporting with actionable recovery steps. Covers common failure modes for monitoring scripts (social layer, crypto watchlists, cron jobs) and vault navigation patterns."
tags: [devops, execution, vault, troubleshooting, monitoring, cron]
trigger: "When executing any script or tool from the vault (bash/Python/Node) — especially cron jobs, monitoring scripts, social media feeds, DeFi trackers, or periodic briefings — and need to handle missing paths, authentication failures, or dependency issues with clear actionable reporting."
related_skills:
  - system-health     # for post-failure diagnostics and fleet health
  - agent-coordination # for delegation and handoff protocols
version: 1.0.0
author: Gentech
---

# Vault Script Execution (Umbrella)

Unified framework for running, debugging, and reporting on scripts stored in the Obsidian vault. Covers path discovery when given wrong location, pre-flight dependency checks (credentials, services, env vars), structured failure reporting with actionable recovery steps, and vault navigation conventions for finding scripts.

> **Why this exists:** Scripts live across multiple vault locations (`03-Strategies/`, `02-Labs/`, `10-Archive/`, skill-specific `scripts/` dirs). Users often reference a path that doesn't exist yet. This skill ensures graceful handling: find the real script, verify readiness, execute, and report clearly — not just "file not found" or opaque 401s.

## Quick Decision Table

| User Intent | Go To Section |
|-------------|---------------|
| "Run script at `/path/to/script.sh`" | [1. Pre-Flight Execution Protocol](#1-pre-flight-execution-protocol) |
| "Script failed with 401/auth error" | [2. Credential Dependencies Check](#2-credential-dependencies-check) |
| "Given path doesn't exist — find it" | [3. Vault Path Resolution](#3-vault-path-resolution) |
| "Script runs but no output / silent failure" | [4. Silent-Failure Detection](#4-silent-failure-detection) |
| "What dependencies does this script need?" | [5. Dependency Mapping](#5-dependency-mapping) |

---

## 1. Pre-Flight Execution Protocol

**Standard flow for any vault script execution:**

### Step 1 — Verify Path Exists (immediate)
```bash
if [ ! -f "/root/vaults/gentech/03-Strategies/social-layer-poc/scripts/engagement-monitor.sh" ]; then
  echo "❌ Path not found"
  exit 1
fi
```

Red flag: User-provided path may be stale or mis-typed.

### Step 2 — Check Script is Executable
```bash
if [ ! -x "$SCRIPT" ]; then
  chmod +x "$SCRIPT"  # or report permission issue
fi
```

### Step 3 — Scan for Known Dependency Types
Read script header or known patterns to identify:
- External CLIs (`xurl`, `curl`, `jq`, `python3`, `hermes`)
- Env var requirements (`$TWITTER_BEARER`, `$ELEVENLABS_API_KEY`)
- Service dependencies (`systemctl`, Redis, PostgreSQL)
- Network access (API endpoints, URL targets)
- Vault/config file reads

### Step 4 — Quick Pre-Flight Checks (optional `--preflight` mode)
```bash
# Check required commands exist
for cmd in xurl jq python3; do
  command -v $cmd >/dev/null || echo "Missing: $cmd"
done

# Check env vars referenced in script
grep -E '\$[A-Z_]+' "$SCRIPT" | sort -u

# Check ports/services if needed
nc -z localhost 8080 2>/dev/null || echo "Service not listening"
```

### Step 5 — Execute with Output Wrapping
Always capture both stdout and stderr separately; preserve JSON integrity if applicable.

---

## 2. Credential Dependencies Check

When a script fails with 401/403 or "Unauthorized" errors:

### Pattern: X/Twitter API (`xurl` CLI)
**Error signature:** `{"title":"Unauthorized","status":401}` from any `xurl` call.

**Checklist:**
- [ ] `~/.xurlrc` exists? (`ls ~/.xurlrc` → should be present)
- [ ] `xurl whoami` returns user info (not 401)
- [ ] App registered: `xurl auth apps list` shows `gentech`
- [ ] OAuth flow completed: `xurl auth token` shows valid token

**Fix flow (for Jordan):**
```bash
# 1. Register app
xurl auth apps add gentech --client-id <ID> --client-secret <SECRET>

# 2. OAuth (opens browser)
xurl auth oauth2

# 3. Verify
xurl whoami
```

**Skill reference:** `system-health` §3f (Multi-Provider Credential Health Check) — systematic sweep across all agents for auth failures.

---

## 3. Vault Path Resolution

When given path doesn't exist, search known vault locations.

### Standard Search Order
1. **Exact path** — if `-f` fails, continue
2. **Sibling directory** — `03-Strategies/social-layer-poc/` vs `03-Strategies/social-layer/`
3. **Parallel project** — `02-Labs/social-layer-poc/`
4. **Archive** — `10-Archive/.../social-layer-poc/` (old backup)
5. **Skills** — agent-specific script dirs (e.g., `gentech/skills/.../scripts/`)
6. **Name-only search** — `find /root/vaults/gentech -name "engagement-monitor.*"`

### Convention: Social Layer Location Canonical
- **Primary:** `/root/vaults/gentech/03-Strategies/social-layer/`
- **POC backup:** `/root/vaults/gentech/03-Strategies/social-layer-poc/` (often contains briefing outputs but not scripts)
- **Archive:** `/root/vaults/gentech/10-Archive/.../social-layer-poc/` (old skill backups)

**Pattern observed (May 3, 2026):**
User path: `03-Strategies/social-layer-poc/scripts/engagement-monitor.sh` → Not found  
Real path: `03-Strategies/social-layer/scripts/engagement-monitor.sh` (off-by-one directory level).

### Path-Check Wrapper Function
```bash
resolve_vault_script() {
  local given="$1"
  if [ -f "$given" ]; then echo "$given"; return; fi

  # Try known variations
  local basename=$(basename "$given")
  local found=$(find /root/vaults/gentech -name "$basename" -type f 2>/dev/null | head -1)
  if [ -n "$found" ]; then echo "$found"; return; fi

  echo "ERROR: Cannot locate $basename in vault" >&2
  return 1
}
```

---

## 4. Silent-Failure Detection

Some scripts "succeed" (exit 0) but produce no actionable output due to blocked dependencies.

**Detection pattern:**
```bash
OUTPUT=$(bash "$SCRIPT" 2>&1)
if echo "$OUTPUT" | grep -qi 'unauthorized\|failed\|error'; then
  echo "🚨 Script completed but reported errors:"
  echo "$OUTPUT"
fi
```

**Social-layer specific:** Even with 401, the script writes a monitor JSON file with error objects embedded. Always parse output AND check side-effects (files written).

---

## 5. Dependency Mapping

Build a dependency catalog for frequently-run vault scripts so pre-flight can be proactive.

**Example: `social-layer/scripts/engagement-monitor.sh`**
- Dependencies: `xurl` CLI, X API credentials (`~/.xurlrc`), network egress
- Output: `03-Strategies/social-layer-poc/monitors/YYYY-MM-DD_HHMM.json`
- Frequency: Designed for cron (every 2h)
- Cost: ~$0.001 per call (owned reads)
- Blockers: X Developer app setup, OAuth completion

**Example: `social-layer/feed-monitor.py`**
- Dependencies: Python 3, `xurl` CLI, `~/.hermes/data/x-seen-posts.json` state file
- Keywords: x402, GenLayer, ARC hackathon, Solana hackathon, AI agents, multi-agent
- Output: stdout (digest) + state update
- Blockers: X API auth

---

## 6. Actionable Reporting Format

Always end with clear next steps. Structure:

```
✅ Script executed: [path]
📊 Output: [summary of findings]
🚨 Issues detected: [list if any]
🔧 Action required:
   • [ ] [Who] — [what to do] (priority: P0/P1/P2)
   • [ ] [Who] — [what to do]
⏭️ Next: [what happens after fix]
```

**Example from May 3 session:**
```
✅ Monitor data saved to: /root/vaults/gentech/03-Strategies/social-layer-poc/monitors/2026-05-03_1154.json
🚨 All X API calls returned 401 Unauthorized — social layer non-functional.
🔧 Action required:
   • [ ] Jordan — Complete X API setup (xurl auth apps add + oauth2) — P0
   • [ ] YoYo — Activate cron jobs after auth verified — P1
⏭️ After fix: Scripts deliver actionable intelligence at ~$0.60/month.
```

---

## 7. Post-Execution Verification

After running a monitoring/cron script:
1. Check exit code
2. Verify output file created (if applicable)
3. Parse output for error signatures
4. Cross-check with last successful run (if historical data exists)
5. If silent or error, run pre-flight dependency check

---

## 8. Common Failure Signatures

| Error pattern | Likely cause | Quick diagnostic | Fix |
|---------------|--------------|------------------|-----|
| `No such file or directory` | Wrong path | `ls $DIR` | Use vault search; update path |
| `401 Unauthorized` (xurl) | Missing X API creds | `xurl whoami` | Jordan: run `xurl auth apps add` + `xurl auth oauth2` |
| `command not found` | CLI not installed | `which <cmd>` | Install missing binary (apt/pip) |
| Exit 0 but empty output | Dependency blocked early | Check stderr; run with `-x` | Fix underlying auth/service |
| JSON parse error | Output truncated/invalid | `head -20 $OUTPUT` | Check disk space; script timeouts |
| Permission denied | Not executable | `ls -l $SCRIPT` | `chmod +x` or sudo |

---

## 9. Script Category Patterns

### Social Media Monitoring (X/Twitter)
- Primary CLI: `xurl`
- Auth: `~/.xurlrc` + OAuth token
- Costs: Post-price-drop ~$0.001/call for owned reads
- Common blocks: Developer app not created, OAuth not completed

### DeFi Position Trackers (LP, watchlist)
- Primary: Python scripts calling on-chain APIs (LFJ, DEX Screener, CoinGecko)
- Dependencies: `curl`/`requests`, API keys in `.env`
- Output: Markdown digests to `03-Strategies/` or Telegram delivery
- Common blocks: Rate limits, API key expired, network errors

### Cron Job Health
- Managed by `hermes cron`
- Registry: `/root/.hermes/cron/jobs.json`
- Per-agent: `/root/.hermes/profiles/<agent>/cron/`
- Use `system-health` skill when cron jobs misbehave

---

## 10. Delegation Boundaries

**When to route:**
- Script requires domain-specific config (e.g., "update DeFi dashboard token list") → **YoYo**
- Script needs security audit or new API integration → **DMOB**
- Script produces content for publishing → **Desmond**
- Script infrastructure broken (gateway, cron, systemd) → **Refer to `system-health`**

**When Gentech handles directly:**
- One-off execution with clear instructions
- Path resolution and dependency verification
- Reporting and handoff to fix blockers

---

## 11. References (Session-Specific Detail)

### X API Authentication Setup (from May 3, 2026 session)
**Observed failure:** All `xurl` calls returned 401 Unauthorized across `mentions`, `search`, and `whoami`.
**Root cause:** No X Developer app registered, OAuth not completed, `~/.xurlrc` absent.
**Fix sequence:**
1. Create X Developer app at https://developer.x.com with redirect URI `http://localhost:8080/callback`
2. `xurl auth apps add gentech --client-id <ID> --client-secret <SECRET>`
3. `xurl auth oauth2` (browser-based flow)
4. Verify: `xurl whoami` should return user JSON (not 401)
5. Cost post-auth: ~$0.001/call for owned reads; full daily monitoring ~$0.60/month

**Files involved:**
- Config: `~/.xurlrc`
- Tokens stored: `~/.config/xurl/` or similar (CLI-dependent)
- Test command: `xurl whoami` (must return JSON with user info)

### Social Layer Vault Layout (canonical)
```
/root/vaults/gentech/
├── 03-Strategies/
│   ├── social-layer/              ← canonical script home
│   │   ├── scripts/
│   │   │   ├── engagement-monitor.sh
│   │   │   ├── feed-monitor.py
│   │   │   ├── daily-briefing.sh
│   │   │   └── influencer-scout.sh
│   │   ├── SOCIAL-LAYER.md
│   │   └── README.md
│   └── social-layer-poc/          ← POC outputs, not scripts
│       ├── monitors/              ← JSON monitor outputs
│       ├── briefings/             ← Markdown digest outputs
│       └── influencers/           ← Scout outputs
└── 02-Labs/social-layer-poc/      ← alternate location (older)
```
**Pitfall:** Don't confuse `social-layer-poc` (outputs) with `social-layer` (scripts). Scripts live in `social-layer/scripts/`.

---

## 12. Pitfalls

- ❌ Assuming user-provided path is correct — always verify existence first
- ❌ Running scripts with obvious 401 errors without checking auth state → wasted execution
- ❌ Confusing output directories (`*-poc/`) with script directories
- ❌ Forgetting to make script executable (`chmod +x`)
- ❌ Not capturing stderr — errors often there, not stdout
- ❌ Assuming environment variables are loaded — they're read at process start
- ❌ Running social scripts before X API setup → every call fails identically
- ❌ Reporting raw JSON/dumps to user — synthesize actionable items only
- ❌ Ignoring exit codes — exit 0 ≠ success if output contains errors

---

## 13. Templates & Scripts

**Templates:**
- `templates/script-execution-report.md` — standardized output format with action items

**Support scripts:**
- `scripts/verify-script-deps.py` — pre-flight checker for common vault scripts
- `scripts/find-vault-script.py` — locate script by basename across vault

---

## 14. Related Skills

- **`system-health`** — Use when cron jobs fail to execute, gateways unhealthy, or systemic errors appear. Provides full diagnostic sweep and recovery procedures.
- **`agent-coordination`** — Use when script results require handoff to YoYo/DMOB/Desmond for follow-up actions.
- **`stateful-alert-monitoring`** — Relevant for monitoring scripts that need debounced/thresholded reporting.
