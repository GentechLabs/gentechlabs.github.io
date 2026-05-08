#!/usr/bin/env python3
"""
Pre-flight dependency checker for vault scripts.
Scans a script for external commands, env vars, and common blockers.
Usage: verify-script-deps.py /path/to/script.sh
"""
import sys
import os
import re
import subprocess
from pathlib import Path

def check_file(path):
    if not os.path.isfile(path):
        print(f"❌ Not found: {path}")
        return False
    if not os.access(path, os.X_OK):
        print(f"⚠️  Not executable: {path} (chmod +x recommended)")
    return True

def extract_commands(script_content):
    """Find external command calls (simple heuristic)."""
    # Match $CMD patterns at start of line or after && || ;
    pattern = r'(?:^|[\s;&|])([a-zA-Z0-9_-]+)(?=\s|$|\))'
    candidates = re.findall(pattern, script_content)
    # Filter to known-common commands (expand as needed)
    common = {'curl','wget','jq','python3','python','node','npm','xurl','hermes',
              'systemctl','service','git','apt','yum','brew','sqlite3','ps','find',
              'grep','sed','awk','cat','head','tail','ls','df','du','nc','netcat',
              'kill','pkill','pgrep','sqlite3','yamllint','yq'}
    return sorted({c for c in candidates if c in common})

def extract_env_vars(script_content):
    """Find $VAR patterns."""
    pattern = r'\$([A-Z_][A-Z0-9_]*)'
    return sorted(set(re.findall(pattern, script_content)))

def check_commands_exist(commands):
    missing = []
    for cmd in commands:
        if subprocess.run(['which', cmd], capture_output=True).returncode != 0:
            missing.append(cmd)
    return missing

def check_env_vars_exist(vars_list):
    missing = []
    for var in vars_list:
        if var not in os.environ:
            missing.append(var)
    return missing

def main():
    if len(sys.argv) < 2:
        print("Usage: verify-script-deps.py <script_path>")
        sys.exit(1)

    script_path = sys.argv[1]
    print(f"🔍 Checking: {script_path}\n")

    if not check_file(script_path):
        sys.exit(1)

    with open(script_path, 'r') as f:
        content = f.read()

    # Extract dependencies
    cmds = extract_commands(content)
    envs = extract_env_vars(content)

    print("📦 External commands detected:")
    if cmds:
        for c in cmds:
            print(f"   • {c}")
    else:
        print("   (none identified)")

    print("\n🔐 Environment variables referenced:")
    if envs:
        for v in envs:
            present = "✅" if v in os.environ else "❌"
            print(f"   {present} {v}")
    else:
        print("   (none identified)")

    print("\n✅ Command availability check:")
    missing_cmds = check_commands_exist(cmds)
    if missing_cmds:
        print(f"   Missing: {', '.join(missing_cmds)}")
    else:
        print("   All commands available")

    print("\n📝 Summary:")
    issues = []
    if missing_cmds:
        issues.append(f"Install missing commands: {', '.join(missing_cmds)}")
    if not os.access(script_path, os.X_OK):
        issues.append("Make script executable: chmod +x")
    if 'Unauthorized' in content or '401' in content:
        issues.append("Script contains 'Unauthorized' — likely auth blocked (see x-api-auth-setup.md)")

    if issues:
        print("   Actions needed:")
        for issue in issues:
            print(f"   • {issue}")
    else:
        print("   ✅ No obvious blockers detected")

    return 0 if not issues else 2

if __name__ == "__main__":
    sys.exit(main())
