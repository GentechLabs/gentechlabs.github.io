#!/bin/bash
# Agent Gateway Quick Recovery — Provider Mismatch Fix
# Usage: ./agent-gateway-fix.sh [nous|stepfun|auto]
# Auto-detects which API key is available in /root/.hermes/.env

set -e

HERMES_HOME="/root/.hermes"
AGENTS=("yoyo" "dmob" "desmond")

echo "=== Agent Gateway Quick Fix ==="
echo ""

# 1. Determine which provider to use
PROVIDER=""
BASE_URL=""
DEFAULT_MODEL=""
API_KEY=""

if [[ "$1" == "nous" ]] || [[ "$1" == "auto" ]]; then
    NOUS_KEY=$(grep -E '^NOUS_API_KEY=' "$HERMES_HOME/.env" | cut -d= -f2- | tr -d '"' | tr -d "'")
    if [[ -n "$NOUS_KEY" && "$NOUS_KEY" != "***" ]]; then
        PROVIDER="nous"
        BASE_URL="https://inference-api.nousresearch.com/v1"
        DEFAULT_MODEL="nous/step-3.5-flash"
        API_KEY="$NOUS_KEY"
        echo "✓ Using Nous Research (NOUS_API_KEY found)"
    fi
fi

if [[ -z "$PROVIDER" ]] && { [[ "$1" == "stepfun" ]] || [[ "$1" == "auto" ]]; }; then
    STEPFUN_KEY=$(grep -E '^STEPFUN_API_KEY=' "$HERMES_HOME/.env" | cut -d= -f2- | tr -d '"' | tr -d "'")
    if [[ -n "$STEPFUN_KEY" && "$STEPFUN_KEY" != "***" ]]; then
        PROVIDER="stepfun"
        BASE_URL="https://api.stepfun.ai/step_plan/v1"
        DEFAULT_MODEL="stepfun/step-3.5-flash"
        API_KEY="$STEPFUN_KEY"
        echo "✓ Using StepFun (STEPFUN_API_KEY found)"
    fi
fi

if [[ -z "$PROVIDER" ]]; then
    echo "❌ No usable API key found in $HERMES_HOME/.env"
    echo "   Set either NOUS_API_KEY or STEPFUN_API_KEY and re-run."
    exit 1
fi

echo "Provider: $PROVIDER"
echo "Model: $DEFAULT_MODEL"
echo ""

# 2. Stop all gateways
echo "--- Stopping existing gateways ---"
for agent in "${AGENTS[@]}"; do
    HERMES_HOME="$HERMES_HOME/profiles/$agent" /root/.local/bin/hermes gateway stop 2>/dev/null || true
done
sleep 2
pkill -9 -f 'hermes gateway run' 2>/dev/null || true
rm -f "$HERMES_HOME/profiles/"*/gateway.pid
echo "✓ All gateways stopped"
echo ""

# 3. Update auth.json + config.yaml for each agent
echo "--- Updating agent configs ---"
for agent in "${AGENTS[@]}"; do
    profile="$HERMES_HOME/profiles/$agent"
    auth_file="$profile/auth.json"
    config_file="$profile/config.yaml"
    
    echo "  [$agent]"
    
    # Update auth.json
    python3 << 'PYEOF'
import json, sys
agent = "'$agent'"
profile = "'$profile'"
auth_file = "'$auth_file'"
provider = "'$PROVIDER'"
base_url = "'$BASE_URL'"
api_key = "'$API_KEY'"

with open(auth_file) as f:
    auth = json.load(f)

# Set/overwrite the chosen provider with API key auth
auth['providers'][provider] = {
    'api_key': api_key,
    'base_url': base_url
}

with open(auth_file, 'w') as f:
    json.dump(auth, f, indent=2)
print(f"    ✓ auth.json: {provider} provider set with API key")
PYEOF
    
    # Update config.yaml
    python3 << 'PYEOF'
import yaml, sys
agent = "'$agent'"
profile = "'$profile'"
config_file = "'$config_file'"
provider = "'$PROVIDER'"
base_url = "'$BASE_URL'"
default_model = "'$DEFAULT_MODEL'"

with open(config_file) as f:
    config = yaml.safe_load(f) or {}

config['model'] = {
    'provider': provider,
    'base_url': base_url,
    'default': default_model
}

with open(config_file, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)
print(f"    ✓ config.yaml: provider={provider}, default={default_model}")
PYEOF
    
    # Clean TERMINAL_CWD from .env if present
    if [[ -f "$profile/.env" ]]; then
        sed -i '/^TERMINAL_CWD=/d' "$profile/.env" 2>/dev/null || true
        # Ensure config has terminal.cwd
        python3 -c "
import yaml
with open('$config_file') as f: cfg = yaml.safe_load(f) or {}
if 'terminal' not in cfg: cfg['terminal'] = {}
cfg['terminal']['cwd'] = '/root'
with open('$config_file', 'w') as f: yaml.dump(cfg, f, default_flow_style=False)
        "
    fi
done

echo ""
echo "--- All agent configs updated ---"
echo ""

# 4. Restart gateways
echo "--- Starting gateways ---"
for agent in "${AGENTS[@]}"; do
    profile="$HERMES_HOME/profiles/$agent"
    HERMES_HOME="$profile" /root/.local/bin/hermes gateway run --replace &
    echo "  Started $agent"
    sleep 1
done

sleep 3

# 5. Verify
echo ""
echo "=== Verification ==="
echo ""

# Check processes
running=$(ps aux | grep 'hermes gateway run' | grep -v grep | wc -l)
echo "Gateway processes running: $running (expected: 3)"

# Run watchdog
echo ""
echo "Watchdog output:"
/root/.hermes/scripts/agent-watchdog.sh || true

echo ""
echo "=== Done ==="
echo "If all agents show ✅, they're fixed."
echo "Check logs if any still failing: tail -30 /root/.hermes/profiles/<agent>/logs/gateway.out"
