#!/usr/bin/env python3
"""
Batch verify and fix model ID misconfiguration across Hermes agent fleet.

Detects the common error: using 'nousresearch/trinity-large-thinking'
instead of the correct 'arcee-ai/trinity-large-thinking' on OpenRouter.

Usage:
  python3 verify_model_config.py --check      # Only report, don't modify
  python3 verify_model_config.py --fix        # Update config.yaml files
  python3 verify_model_config.py --catalog    # Show current OpenRouter catalog

Exit codes: 0=all correct, 1=mismatch found, 2=error
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

AGENTS = ['yoyo', 'dmob', 'desmond', 'gentech']
CONFIG_PATH_TEMPLATE = Path('/root/.hermes/profiles/{agent}/config.yaml')
WRONG_MODEL = 'nousresearch/trinity-large-thinking'
CORRECT_MODEL = 'arcee-ai/trinity-large-thinking'

def read_config(agent: str) -> str | None:
    path = CONFIG_PATH_TEMPLATE.format(agent=agent)
    if not path.exists():
        return None
    content = path.read_text()
    # Simple extraction of model.default line
    for line in content.splitlines():
        if 'default:' in line and not line.strip().startswith('#'):
            return line.split('default:')[-1].strip().strip('"\'')
    return None

def write_config(agent: str, new_model: str) -> bool:
    path = CONFIG_PATH_TEMPLATE.format(agent=agent)
    content = path.read_text()
    new_lines = []
    for line in content.splitlines():
        if 'default:' in line and not line.strip().startswith('#'):
            # Preserve indentation
            indent = len(line) - len(line.lstrip())
            new_line = ' ' * indent + f'default: {new_model}'
            new_lines.append(new_line)
        else:
            new_lines.append(line)
    path.write_text('\n'.join(new_lines) + '\n')
    return True

def check_openrouter_catalog(api_key_env: str = 'OPENROUTER_API_KEY') -> list[str]:
    """Query OpenRouter models API and return list of available model IDs."""
    import os
    api_key = os.environ.get(api_key_env)
    if not api_key:
        print(f"WARNING: {api_key_env} not set; skipping catalog check")
        return []
    try:
        result = subprocess.run(
            ['curl', '-s',
             '-H', f'Authorization: Bearer {api_key}',
             'https://openrouter.ai/api/v1/models'],
            capture_output=True, text=True, timeout=10
        )
        data = json.loads(result.stdout)
        return [m['id'] for m in data.get('data', [])]
    except Exception as e:
        print(f"ERROR querying catalog: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(description='Verify/fix model ID misconfiguration')
    parser.add_argument('--check', action='store_true', default=True, help='Check mode (default)')
    parser.add_argument('--fix', action='store_true', help='Write corrected configs')
    parser.add_argument('--catalog', action='store_true', help='Show OpenRouter catalog trinity entries')
    args = parser.parse_args()

    if args.fix:
        args.check = False

    if args.catalog:
        print("Querying OpenRouter catalog for 'trinity' models...")
        models = check_openrouter_catalog()
        trinity = [m for m in models if 'trinity' in m.lower()]
        for m in trinity:
            print(f"  {m}")
        return 0

    print(f"{'AGENT':<10} {'CONFIGURED':<35} {'STATUS'}")
    print("-" * 80)

    mismatches = []
    all_ok = True

    for agent in AGENTS:
        configured = read_config(agent)
        if configured is None:
            print(f"{agent:<10} {'(config not found)':<35} SKIP")
            continue

        if configured.lower() == WRONG_MODEL.lower():
            status = "MISMATCH"
            all_ok = False
            mismatches.append(agent)
            print(f"{agent:<10} {configured:<35} ❌ {status}")
        elif configured.lower() == CORRECT_MODEL.lower():
            status = "OK"
            print(f"{agent:<10} {configured:<35} ✓ {status}")
        else:
            status = "UNKNOWN"
            print(f"{agent:<10} {configured:<35} ⚠ {status} (neither wrong nor known-good)")

    print("-" * 80)
    if all_ok:
        print("All agents have correct model configuration.")
        return 0

    print(f"\nMismatched agents: {', '.join(mismatches)}")
    print(f"Expected model: {CORRECT_MODEL}")
    print(f"Wrong model detected: {WRONG_MODEL}")

    if args.fix:
        print("\nApplying fixes...")
        for agent in mismatches:
            if write_config(agent, CORRECT_MODEL):
                print(f"  ✓ Updated {agent} config.yaml")
            else:
                print(f"  ✗ Failed to update {agent}")
        print("\nRestart all gateways to apply changes:")
        print("  pkill -f hermes.*gateway")
        print("  for a in yoyo dmob desmond gentech; do")
        print("    /usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main --profile $a gateway run --replace &")
        print("  done")
        return 0
    else:
        print("\nRun with --fix to update config.yaml files, then restart all gateways.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
