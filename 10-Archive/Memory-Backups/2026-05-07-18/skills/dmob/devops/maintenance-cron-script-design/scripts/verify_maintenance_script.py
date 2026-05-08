#!/usr/bin/env python3
"""
Verify that a maintenance cron script follows the silent-failure pattern.

Checks:
  1. Docstring documents exit code semantics (0=expected states ok, 1=unexpected errors)
  2. Contains silent exit logic for needs_manual_action / needs_reauth flags
  3. Does NOT return non-zero for expected manual-action conditions

Usage:
  python verify_maintenance_script.py /path/to/script.py
  exit 0 = passes, exit 1 = fails check
"""

import sys
import re
from pathlib import Path


def check_script(path: Path) -> tuple[bool, list[str]]:
    """Return (pass, list of issues)."""
    issues = []
    content = path.read_text()

    # 1. Check docstring mentions exit codes
    doc_match = re.search(r'Exit codes:\s*\n\s+0\s*-\s*.*\n\s+1\s*-\s*.*', content, re.IGNORECASE)
    if not doc_match:
        issues.append("Missing or incomplete 'Exit codes:' documentation in docstring")

    # 2. Check for explicit silent-exit pattern
    silent_patterns = [
        r'if\s+status\.get\(["\']needs_manual_action["\']\):\s*\n\s*return\s+0',
        r'if\s+status\.get\(["\']needs_reauth["\']\):\s*\n\s*return\s+0',
    ]
    found_silent = any(re.search(p, content) for p in silent_patterns)
    if not found_silent:
        issues.append("Missing silent-exit guard for needs_manual_action / needs_reauth")

    # 3. Check final exit logic is not a blunt 'return 0 if success else 1' at toplevel
    # We want the silent-exit guard BEFORE the blunt return
    blunt_pattern = r'return\s+0\s+if\s+status\["success"\]\s+else\s+1'
    if re.search(blunt_pattern, content):
        # Check if it's preceded by the silent guard within reasonable proximity
        silent_before = any(
            re.search(p, content[:m.start()])
            for p in silent_patterns
            for m in re.finditer(blunt_pattern, content)
        )
        if not silent_before:
            issues.append(" blunt 'return 0 if success else 1' found without silent guard before it")

    # 4. Check exit code in main guard matches pattern
    exit_pattern = r'sys\.exit\(main\(\)\)'
    if not re.search(exit_pattern, content):
        issues.append("Script should end with 'sys.exit(main())'")

    return len(issues) == 0, issues


def main():
    if len(sys.argv) < 2:
        print("Usage: verify_maintenance_script.py <script.py>")
        sys.exit(1)

    script_path = Path(sys.argv[1])
    if not script_path.exists():
        print(f"Error: file not found: {script_path}")
        sys.exit(1)

    ok, issues = check_script(script_path)

    if ok:
        print(f"✅ {script_path.name}: passes maintenance-script pattern check")
        sys.exit(0)
    else:
        print(f"❌ {script_path.name}: FAILS checks")
        for issue in issues:
            print(f"   - {issue}")
        sys.exit(1)


if __name__ == "__main__":
    main()
