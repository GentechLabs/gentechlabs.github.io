#!/usr/bin/env python3
"""
Safe vault appender — preserves history when prepending new entry.

Usage: vault_append.py /path/to/vault.md "## 2026-05-03 Update\n**Content**…"
"""

import sys
import os

SEPARATOR = "---"  # vault footer marker to preserve

def vault_append(vault_path, new_entry):
    with open(vault_path, 'r') as f:
        content = f.read()

    # Split at separator; preserve header+body before separator
    if SEPARATOR in content:
        header_body, separator, footer = content.partition(SEPARATOR)
        separator_line = SEPARATOR + "\n"
    else:
        # No separator found → vault may be malformed; append at end
        header_body = content
        separator_line = "\n" + SEPARATOR + "\n"
        footer = ""

    # Prepend new entry to history section (before separator)
    # Ensure new entry ends with double newline for spacing
    if not new_entry.endswith('\n'):
        new_entry += '\n'
    updated = new_entry + header_body + separator_line + footer

    with open(vault_path, 'w') as f:
        f.write(updated)
    print(f"✅ Vault updated: {vault_path} (prepended new entry)")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: vault_append.py <vault_path> <new_entry_markdown>")
        sys.exit(1)
    vault_append(sys.argv[1], sys.argv[2])