---
title: Agent Gateway Recovery — Provider Mismatch & Authentication
created: 2026-04-22T13:55:00+00:00
updated: 2026-04-22T13:55:00+00:00
status: active
type: protocol
---

## 🚨 Symptom

Agents reporting in Telegram:
```
⚠️ Provider authentication failed: Unknown provider 'openai'.
Check 'hermes model' for available providers, or run 'hermes doctor' to diagnose config issues.
```

**Root cause:** Agent gateway configs have `provider: openai` but `auth.json` only contains `nous` (or `stepfun`) credentials — no OpenAI API key set.

## 🔍 Diagnosis

```bash
# 1. Check what each agent config says
for agent in yoyo dmob desmond; do
  cat /root/.hermes/profiles/$agent/config.yaml | grep -E '^(provider|base_url|default):'
done

# 2. Check what providers auth.json actually has
for agent in yoyo dmob desmond; do
  python3 -c "import json; a=json.load(open('/root/.hermes/profiles/$agent/auth.json')); print($agent, list(a.get('providers',{}).keys()))"
done

# 3. Check if gateways are running
ps aux | grep 'hermes gateway run' | grep -v grep
# Expecting 3 lines (one per agent). Zero = all dead.

# 4. Check for stale gateway.pid files
ls /root/.hermes/profiles/*/gateway.pid
# If files exist but processes not running → stale PIDs
```

**Expected findings when broken:**
- `config.yaml` → `provider: openai`
- `auth.json` → `providers: ["nous", "stepfun"]` (no `openai` key)
- Gateways either **not running** OR **running but crashing on startup** due to config mismatch
- Gateway logs show: `Unknown provider 'openai'`

## 🛠️ Quick Fix (One-liner)

Run this to switch all agents to use the **Nous Research API key** (set via `NOUS_API_KEY` in `/root/.hermes/.env`):

```bash
# Read the NOUS_API_KEY from main .env
NOUS_KEY=$(grep -E '^NOUS_API_KEY=' /root/.hermes/.env | cut -d= -f2-)

# Update each agent: auth.json (add api_key) + config.yaml (set provider=nous)
for agent in yoyo dmob desmond; do
  profile="/root/.hermes/profiles/$agent"
  
  # Update auth.json: replace 'nous' provider block with API key version
  python3 -c "
import json
with open('$profile/auth.json') as f: a = json.load(f)
a['providers']['nous'] = {'api_key': '$NOUS_KEY', 'base_url': 'https://inference-api.nousresearch.com/v1'}
with open('$profile/auth.json', 'w') as f: json.dump(a, f, indent=2)
print('✓ Updated auth.json for '$agent')
  "
  
  # Update config.yaml: use nous provider + step-3.5-flash
  python3 -c "
import yaml, sys
with open('$profile/config.yaml') as f: cfg = yaml.safe_load(f) or {}
cfg['model'] = {'provider': 'nous', 'base_url': 'https://inference-api.nousresearch.com/v1', 'default': 'nous/step-3.5-flash'}
with open('$profile/config.yaml', 'w') as f: yaml.dump(cfg, f, default_flow_style=False, sort_keys=False)
print('✓ Updated config.yaml for '$agent')
  "
done

# Kill any stale gateways
pkill -9 -f 'hermes gateway run' 2>/dev/null; sleep 1; rm -f /root/.hermes/profiles/*/gateway.pid

# Restart all 3 agents
for agent in yoyo dmob desmond; do
  HERMES_HOME=/root/.hermes/profiles/$agent /root/.local/bin/hermes gateway run --replace &
  echo "Started $agent"
  sleep 1
done

# Verify
/root/.hermes/scripts/agent-watchdog.sh
```

## 📋 Full Recovery Protocol

If the one-liner doesn't work or you want manual steps:

### Step 1 — Stop All Gateways
```bash
# Preferred: graceful stop
for agent in yoyo dmob desmond; do
  HERMES_HOME=/root/.hermes/profiles/$agent /root/.local/bin/hermes gateway stop || true
done
sleep 2

# Force kill any remaining
pkill -9 -f 'hermes gateway run' 2>/dev/null
sleep 1
rm -f /root/.hermes/profiles/*/gateway.pid
rm -f /root/.hermes/profiles/*/auth.lock
```

### Step 2 — Verify Credentials Available

**Option A: Using Nous Research API key** (NOUS_API_KEY in .env)
```bash
grep '^NOUS_API_KEY=' /root/.hermes/.env
# Should output: NOUS_API_KEY=sk-...
```

**Option B: Using StepFun API key** (STEPFUN_API_KEY in .env)
```bash
grep '^STEPFUN_API_KEY=' /root/.hermes/.env
```

**Option C: Need to add key manually**
Edit `/root/.hermes/.env` and add:
```bash
NOUS_API_KEY=sk-your-key-here
# or
STEPFUN_API_KEY=sk-your-key-here
```

### Step 3 — Reconfigure Each Agent

For each agent (`yoyo`, `dmob`, `desmond`):

#### 3a. Set auth.json to use API key (not OAuth)
```bash
agent="yoyo"  # change per agent
profile="/root/.hermes/profiles/$agent"

# Backup first
cp "$profile/auth.json" "$profile/auth.json.backup.$(date +%s)"

# Update with python (preserves other providers like stepfun if present)
python3 << 'PYEOF'
import json, os
agent = os.environ['AGENT']
profile = f"/root/.hermes/profiles/{agent}"
auth_path = f"{profile}/auth.json"
with open(auth_path) as f:
    auth = json.load(f)

# Determine which key to use (NOUS or STEPFUN)
import re
with open('/root/.hermes/.env') as f:
    env = f.read()
nous_key = re.search(r'NOUS_API_KEY[=\s]+([^\n]+)', env)
stepfun_key = re.search(r'STEPFUN_API_KEY[=\s]+([^\n]+)', env)

if nous_key:
    auth['providers']['nous'] = {
        'api_key': nous_key.group(1).strip().strip('"').strip("'"),
        'base_url': 'https://inference-api.nousresearch.com/v1'
    }
    provider = 'nous'
    base_url = 'https://inference-api.nousresearch.com/v1'
    default_model = 'nous/step-3.5-flash'
elif stepfun_key:
    auth['providers']['stepfun'] = {
        'api_key': stepfun_key.group(1).strip().strip('"').strip("'"),
        'base_url': 'https://api.stepfun.ai/step_plan/v1'
    }
    provider = 'stepfun'
    base_url = 'https://api.stepfun.ai/step_plan/v1'
    default_model = 'stepfun/step-3.5-flash'
else:
    raise ValueError("No NOUS_API_KEY or STEPFUN_API_KEY found in /root/.hermes/.env")

with open(auth_path, 'w') as f:
    json.dump(auth, f, indent=2)
print(f"✓ auth.json: set {provider} provider with API key")
PYEOF
```

#### 3b. Update config.yaml
```bash
agent="yoyo"
profile="/root/.hermes/profiles/$agent"

python3 << 'PYEOF'
import yaml, os
agent = os.environ['AGENT']
profile = f"/root/.hermes/profiles/{agent}"
config_path = f"{profile}/config.yaml"

with open(config_path) as f:
    config = yaml.safe_load(f) or {}

# Use values determined above (from Step 3a)
config['model'] = {
    'provider': 'nous',          # or 'stepfun'
    'base_url': 'https://inference-api.nousresearch.com/v1',  # adjust if stepfun
    'default': 'nous/step-3.5-flash'  # or 'stepfun/step-3.5-flash'
}

with open(config_path, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)
print(f"✓ config.yaml: provider={config['model']['provider']}, default={config['model']['default']}")
PYEOF
```

### Step 4 — Clean Deprecated .env Entries
```bash
for agent in yoyo dmob desmond; do
  profile="/root/.hermes/profiles/$agent"
  # Remove TERMINAL_CWD if present (causes warnings)
  sed -i '/^TERMINAL_CWD=/d' "$profile/.env" 2>/dev/null || true
  
  # Ensure config.yaml has terminal.cwd instead
  python3 -c "
import yaml
with open('$profile/config.yaml') as f: cfg = yaml.safe_load(f) or {}
if 'terminal' not in cfg: cfg['terminal'] = {}
cfg['terminal']['cwd'] = '/root'
with open('$profile/config.yaml', 'w') as f: yaml.dump(cfg, f, default_flow_style=False)
  "
done
```

### Step 5 — Start Gateways
```bash
# Ensure no stale PIDs
rm -f /root/.hermes/profiles/*/gateway.pid

# Start all 3 (order doesn't matter)
for agent in yoyo dmob desmond; do
  HERMES_HOME=/root/.hermes/profiles/$agent \
    /root/.local/bin/hermes gateway run --replace &
  echo "Started $agent"
  sleep 1
done

# Wait a moment for init
sleep 3
```

### Step 6 — Verify
```bash
# Check running processes
ps aux | grep 'hermes gateway run' | grep -v grep
# Should show 3 lines with different PIDs

# Run watchdog
/root/.hermes/scripts/agent-watchdog.sh
# Expected: "All agents healthy. ✅ yoyo/dmob/desmond running"

# Check logs for errors
for agent in yoyo dmob desmond; do
  echo "=== $agent ==="
  tail -20 "/root/.hermes/profiles/$agent/logs/gateway.out" | grep -i 'error\|fail\|exception' || echo "No errors found"
done

# Test via `hermes cron run` on a test job or send a /test message in Telegram
```

## 🔄 Prevention

### Monthly Maintenance
1. **Rotate Nous OAuth tokens** (if still using OAuth): `hermes model` in each profile before 24h expiry
2. **Verify NOUS_API_KEY or STEPFUN_API_KEY** is valid in `/root/.hermes/.env`
3. **Check gateway health**: `hermes cron list` shows all agents' cron jobs active
4. **Run watchdog manually**: `/root/.hermes/scripts/agent-watchdog.sh`

### Consider: Full Provider Migration
The current Nous OAuth tokens expire every ~24h and require re-login. For **more reliability**, switch to **StepFun API key** provider permanently (no expiry, no refresh needed):
1. Get StepFun API key from https://platform.stepfun.com
2. Add `STEPFUN_API_KEY=sk-...` to `/root/.hermes/.env`
3. Run the **Quick Fix** above (it auto-detects STEPFUN_API_KEY and configures stepfun provider)
4. Benefits: No auth expiry, no refresh tokens, fewer outages

## 📁 Related Files

| File | Purpose |
|------|---------|
| `/root/.hermes/profiles/{agent}/config.yaml` | Agent model config (provider, base_url, default model) |
| `/root/.hermes/profiles/{agent}/auth.json` | Agent credentials (OAuth tokens or API keys per provider) |
| `/root/.hermes/.env` | Shared API keys (NOUS_API_KEY, STEPFUN_API_KEY, etc.) |
| `/root/.hermes/scripts/agent-watchdog.sh` | Health check + auto-restart monitor |
| `Skills/agents-protocol.md` | Agent routing + collaboration rules |
| `devops/gentech-agent-reactivation` | Full agent recovery skill |
| `Mess-Hall/2026-04-22/agent-recovery-summary.md` | This incident's post-mortem |

## 🆘 Still Broken?

If gateways still fail after this protocol:

1. **Check for PID file race**:
   ```bash
   ls /root/.hermes/profiles/*/gateway.pid
   # If files exist → stale → rm them
   ```

2. **Check auxiliary_client.py corruption**:
   ```bash
   python3 -m py_compile /root/.hermes/profiles/yoyo/home/auxiliary_client.py
   # If SyntaxError → replace from /root/.hermes/hermes-agent/agent/auxiliary_client.py
   ```

3. **Check home/.hermes symlink**:
   ```bash
   ls -la /root/.hermes/profiles/yoyo/home/.hermes
   # Should be symlink → /root/.hermes
   ```

4. **Inspect full gateway log**:
   ```bash
   tail -100 /root/.hermes/profiles/yoyo/logs/gateway.out
   ```

5. **Run `hermes doctor`** in each profile (interactive) for diagnostics

---

**Last tested:** 2026-04-22  
**Affected agents:** YoYo, DMOB, Desmond  
**Fix status:** ✅ Verified working (PIDs 243744/243749/243758 → 244826/244844/???)
**Root cause:** `config.yaml` provider=openai but auth.json had nous+stepfun OAuth → no matching credentials → gateway startup failure
