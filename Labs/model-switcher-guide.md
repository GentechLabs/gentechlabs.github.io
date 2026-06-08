# Model Switching — Quick Reference

**Created:** Apr 21, 2026
**Context:** Hermes agents (YoYo, DMOB, Desmond, Gentech)

---

## Problem

After `hermes update`, the custom model block in `config.yaml` gets wiped, reverting to defaults. This breaks agents because:
1. Model becomes unspecified → provider auth fails
2. Cron jobs fail with "Refresh session has been revoked"

## Solution

### Option A — Use Telegram Skill (once built)
- `/model openrouter/qwen/qwen-3.6-chat` — switch models from chat
- `/models` — list what's available
- Requires: skill installed at `~/.hermes/skills/custom/telegram-model-switch/`
- Only Jordan can use it (user ID gate)

### Option B — Manual SSH (now)
```bash
# Edit each profile
nano /root/.hermes/profiles/yoyo/config.yaml

# Ensure model block looks like:
model:
  base_url: https://inference-api.nousresearch.com/v1
  default: xiaomi/mimo-v2-pro
  provider: nous

# Then restart gateway
HERMES_HOME=/root/.hermes/profiles/yoyo hermes gateway run &
```

### Option C — One-liner fix (bash)
```bash
for p in yoyo dmob desmond; do
  sed -i '/^model:/,/^[^ ]/c\model:\n  base_url: https://inference-api.nousresearch.com/v1\n  default: xiaomi/mimo-v2-pro\n  provider: nous' /root/.hermes/profiles/$p/config.yaml
done
```

## Known Good Configs (as of Apr 21)

### Nous MIMO v2-pro
```yaml
model:
  base_url: https://inference-api.nousresearch.com/v1
  default: xiaomi/mimo-v2-pro
  provider: nous
```

### Stepfun Step 3.6
```yaml
model:
  base_url: https://api.stepfun.com/v1
  default: step/step-3.6-chat
  provider: stepfun
```

### OpenRouter Qwen 3.6
```yaml
model:
  base_url: https://openrouter.ai/api/v1
  default: qwen/qwen-3.6-chat
  provider: openrouter
```

## Prevention

**After `hermes update`:**
- When prompted "Restore local changes?" → **ALWAYS ANSWER NO**
- Verify configs immediately: `grep -A3 '^model:' ~/.hermes/profiles/*/config.yaml`
- Restart gateways

## Fallback

If all else fails:
1. `pkill -f "hermes gateway run"`
2. Clear PIDs: `find ~/.hermes/profiles -name "*.pid" -delete`
3. Re-auth: `HERMES_HOME=<profile> hermes auth reset` (if needed)
4. Restart each: `HERMES_HOME=<profile> hermes gateway run &`

---

**Profiles affected:** `yoyo` (Strategies), `dmob` (Labs), `desmond` (Creative), `default` (Gentech HQ)
