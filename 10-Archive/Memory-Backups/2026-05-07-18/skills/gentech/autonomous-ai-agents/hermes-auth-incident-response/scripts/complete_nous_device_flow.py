#!/usr/bin/env python3
"""Nous Device Flow Completion — poll for tokens after browser auth.

Usage:
  python3 complete_nous_device_flow.py

Requires: httpx (available in Hermes venv).
"""
import json
import os
import sys
import time
import httpx
from datetime import datetime, timezone, timedelta

HERMES_HOME = os.environ.get("HERMES_HOME", "/root/.hermes/profiles/gentech")
FLOW_FILE = os.path.join(HERMES_HOME, "scripts", "pending_nous_device_flow_latest.json")
AUTH_FILE = os.path.join(HERMES_HOME, "auth.json")

def main():
    if not os.path.exists(FLOW_FILE):
        print(f"ERROR: No pending device flow at {FLOW_FILE}")
        print("Re-initiate OAuth or check if code expired.")
        sys.exit(1)

    with open(FLOW_FILE) as f:
        flow = json.load(f)

    device_code = flow["device_code"]
    verification_url = flow["verification_uri"]
    expires_at_str = flow["expires_at"]
    interval = flow.get("interval", 5)
    expires_in = flow.get("expires_in", 600)

    expires_at = datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    if now > expires_at:
        print("ERROR: Device code has EXPIRED.")
        os.remove(FLOW_FILE)
        sys.exit(1)

    print("Nous OAuth Device Flow Completion")
    print("=" * 40)
    print(f"Verify at: {verification_url}")
    print(f"Expires: {expires_at.strftime('%Y-%m-%d %H:%M UTC')}")
    print()
    print("Polling... (visit URL in browser first)")
    print()

    portal_url = verification_url.replace("/manage-subscription", "")
    client_id = flow.get("client_id", "nous")
    scope = flow.get("scope", "inference:mint_agent_key")
    deadline = time.time() + expires_in

    with httpx.Client(verify=True) as client:
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
                save_tokens(payload, flow)
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

def save_tokens(payload: dict, flow: dict):
    with open(AUTH_FILE) as f:
        auth = json.load(f)

    now = datetime.now(timezone.utc)
    expires_in_seconds = payload.get("expires_in", 2592000)
    exp = now + timedelta(seconds=expires_in_seconds)

    nous = auth.setdefault("providers", {}).setdefault("nous", {})
    tous = payload.get("token_type", "Bearer").lower()
    nous.update({
        "access_token": payload["access_token"],
        "refresh_token": payload.get("refresh_token", nous.get("refresh_token")),
        "token_type": tous.capitalize(),
        "scope": payload.get("scope", flow.get("scope", "inference:mint_agent_key")),
        "obtained_at": now.isoformat(),
        "expires_at": exp.isoformat(),
        "client_id": flow.get("client_id", "nous"),
        "portal_base_url": flow["verification_uri"].replace("/manage-subscription", ""),
    })

    with open(AUTH_FILE, 'w') as f:
        json.dump(auth, f, indent=2)

    # Clean up flow files
    flow_dir = os.path.dirname(FLOW_FILE)
    for name in ["pending_nous_device_flow_latest.json", "auth_pending_device_flow.json"]:
        path = os.path.join(flow_dir, name)
        try:
            os.remove(path)
        except OSError:
            pass

if __name__ == "__main__":
    main()
