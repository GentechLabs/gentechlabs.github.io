#!/usr/bin/env python3
"""
Verify AAE config consistency between vault and Hermes profile runtime directories.

Checks that .lfj-aae-config.json milestones match across locations and reports
which profiles are in sync / out of sync.

Usage: python3 verify_aae_config_consistency.py
Exit codes: 0 = all sync, 1 = mismatch found, 2 = file missing
"""

import json
import os
import sys
from typing import Dict, Tuple

VAULT_CONFIG = "/root/vaults/gentech/03-Strategies/scripts/.lfj-aae-config.json"

PROFILES = ["yoyo", "dmob", "desmond", "gentech"]

RUNTIME_PATH_TEMPLATE = "/root/.hermes/profiles/{profile}/home/.hermes/scripts/.lfj-aae-config.json"


def load_config(path: str) -> Dict:
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON at {path}: {e}")
        sys.exit(2)


def extract_milestone_signature(cfg: Dict) -> Tuple:
    """Create hashable signature of milestone tiers/labels."""
    milestones = cfg.get("milestones", [])
    return tuple((m["tier"], m["label"], m["daily_fees"]) for m in milestones)


def main():
    vault_cfg = load_config(VAULT_CONFIG)
    if vault_cfg is None:
        print(f"ERROR: Vault config missing: {VAULT_CONFIG}")
        sys.exit(2)

    vault_sig = extract_milestone_signature(vault_cfg)
    print(f"Vault milestones: {vault_sig}\n")

    all_sync = True
    for profile in PROFILES:
        runtime_path = RUNTIME_PATH_TEMPLATE.format(profile=profile)
        runtime_cfg = load_config(runtime_path)
        if runtime_cfg is None:
            print(f"⚠️  {profile}: config missing at {runtime_path}")
            all_sync = False
            continue

        runtime_sig = extract_milestone_signature(runtime_cfg)
        if runtime_sig == vault_sig:
            print(f"✅ {profile}: in sync")
        else:
            print(f"❌ {profile}: OUT OF SYNC")
            print(f"   Vault:   {vault_sig}")
            print(f"   Runtime: {runtime_sig}")
            all_sync = False

    if all_sync:
        print("\n✅ All profiles synchronized.")
        sys.exit(0)
    else:
        print("\n❌ Mismatch detected. Run sync:")
        print("   cp " + VAULT_CONFIG + " /root/.hermes/profiles/yoyo/home/.hermes/scripts/")
        print("   cp " + VAULT_CONFIG + " /root/.hermes/profiles/dmob/home/.hermes/scripts/")
        sys.exit(1)


if __name__ == "__main__":
    main()
