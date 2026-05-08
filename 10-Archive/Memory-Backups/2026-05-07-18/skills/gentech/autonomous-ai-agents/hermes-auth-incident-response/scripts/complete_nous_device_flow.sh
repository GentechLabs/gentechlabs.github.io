#!/bin/bash
# Nous Device Flow Completion Script
#
# Run this AFTER visiting the verification URL and completing login in your browser.
# This script polls for the token using the saved device_code and saves the credentials.
#
# Usage: /root/.hermes/profiles/gentech/scripts/complete_nous_device_flow.sh
#
# Exit codes:
#   0 - Success (tokens saved)
#   1 - Device flow not found or expired
#   2 - Auth failed or was denied

set -euo pipefail

HERMES_HOME="${HERMES_HOME:-/root/.hermes/profiles/gentech}"
FLOW_FILE="$HERMES_HOME/scripts/pending_nous_device_flow_latest.json"
AUTH_FILE="$HERMES_HOME/auth.json"

if [[ ! -f "$FLOW_FILE" ]]; then
    echo "ERROR: No pending device flow found at $FLOW_FILE"
    echo "Run the OAuth initiation first or check if the code expired."
    exit 1
fi

# Load device flow data
device_code=$(jq -r '.device_code' "$FLOW_FILE")
verification_url=$(jq -r '.verification_uri' "$FLOW_FILE")
expires_at=$(jq -r '.expires_at' "$FLOW_FILE")
initiated_at=$(jq -r '.initiated_at' "$FLOW_FILE")

echo "Nous OAuth Device Flow Completion"
echo "=================================="
echo "Verification URL: $verification_url"
echo "Initiated: $initiated_at"
echo "Expires: $expires_at"
echo

# Check expiry
now=$(date -u +%s)
expires_ts=$(date -d "$expires_at" +%s 2>/dev/null || echo 0)
if [[ $now -gt $expires_ts ]]; then
    echo "ERROR: Device code has EXPIRED. Please re-initiate the OAuth flow."
    rm -f "$FLOW_FILE"
    exit 1
fi

echo "Polling for token completion..."
echo "If you haven't visited the URL yet, do that now."
echo "Press Ctrl+C to abort."
echo

# Run the Python poller
python3 - "$HERMES_HOME" "$device_code" <<'PYEOF'
import sys
import json
import os
import time
import httpx
from datetime import datetime, timezone, timedelta

hermes_home = sys.argv[1]
device_code = sys.argv[2]
FLOW_FILE = os.path.join(hermes_home, "scripts", "pending_nous_device_flow_latest.json")
AUTH_FILE = os.path.join(hermes_home, "auth.json")

with open(FLOW_FILE) as f:
    flow = json.load(f)

portal_url = flow["verification_uri"].replace("/manage-subscription", "")
client_id = flow.get("client_id", "nous")
scope = flow.get("scope", "inference:mint_agent_key")
interval = flow.get("interval", 5)
expires_in = flow.get("expires_in", 600)
expires_at_str = flow.get("expires_at")
if expires_at_str:
    expires_at = datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))
    deadline = time.time() + max(0, (expires_at - datetime.now(timezone.utc)).total_seconds())
else:
    deadline = time.time() + expires_in

client = httpx.Client(verify=True)

try:
    while time.time() < deadline:
        resp = client.post(
            f"{portal_url}/api/oauth/token",
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "client_id": client_id,
                "device_code": device_code,
            },
        )
        if resp.status_code == 200:
            payload = resp.json()
            if "access_token" not in payload:
                raise RuntimeError("Token response missing access_token")

            # Save tokens
            with open(AUTH_FILE) as f:
                auth = json.load(f)
            now = datetime.now(timezone.utc)
            exp = now + timedelta(seconds=payload.get("expires_in", 2592000))
            nous = auth.setdefault("providers", {}).setdefault("nous", {})
            tous = payload.get("token_type", "Bearer").lower()
            nous.update({
                "access_token": payload["access_token"],
                "refresh_token": payload.get("refresh_token", nous.get("refresh_token")),
                "token_type": tous.capitalize(),
                "scope": payload.get("scope", scope),
                "obtained_at": now.isoformat(),
                "expires_at": exp.isoformat(),
                "client_id": client_id,
                "portal_base_url": portal_url,
            })
            with open(AUTH_FILE, 'w') as f:
                json.dump(auth, f, indent=2)

            # Clean up flow files
            for p in [FLOW_FILE, os.path.join(hermes_home, "scripts", "auth_pending_device_flow.json")]:
                try:
                    os.remove(p)
                except OSError:
                    pass

            print()
            print("✅ Success — tokens saved.")
            print(f"   Auth file: {AUTH_FILE}")
            sys.exit(0)

        try:
            err = resp.json()
            error_code = err.get("error", "")
        except Exception:
            error_code = ""

        if error_code == "authorization_pending":
            for _ in range(interval):
                time.sleep(1)
                print(".", end="", flush=True)
            continue
        elif error_code == "slow_down":
            interval = min(interval + 1, 30)
            time.sleep(interval)
            continue
        else:
            print()
            print(f"error {resp.status_code}: {resp.text}")
            sys.exit(2)

    print()
    print("ERROR: Timed out waiting for authorization.")
    sys.exit(1)

except KeyboardInterrupt:
    print("\n\nCancelled by user.")
    sys.exit(130)
except Exception as exc:
    print(f"\nERROR: {exc}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    client.close()
PYEOF
