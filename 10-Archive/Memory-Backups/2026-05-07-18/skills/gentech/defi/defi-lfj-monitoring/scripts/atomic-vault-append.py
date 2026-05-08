#!/usr/bin/env python3
"""
Atomic vault append — prevents duplicate date entries and ensures clean file writes.
Usage: python3 atomic-vault-append.py --vault /path/to/file.md --entry "$(cat new_entry.txt)"
"""

import re
import sys
import tempfile
import shutil
from pathlib import Path

def parse_entries(content):
    """Split vault into blocks by date header, return OrderedDict {date: entry_text}"""
    pattern = r'(## 2026-\d{2}-\d{2} Update.*?)(?=\n## 2026-|\Z)'
    matches = re.findall(pattern, content, re.DOTALL)
    entries = {}
    for block in matches:
        m = re.search(r'## (2026-\d{2}-\d{2}) Update', block)
        if m:
            date = m.group(1)
            entries[date] = block.strip()
    return entries

def merge_entry(vault_path, new_entry_text):
    """Merge new entry into vault, replacing same-date if exists, then write atomically"""
    vault = Path(vault_path)
    if not vault.exists():
        vault.write_text(new_entry_text + '\n')
        return

    content = vault.read_text()
    entries = parse_entries(content)

    # Extract date from new entry
    m = re.search(r'## (2026-\d{2}-\d{2}) Update', new_entry_text)
    if not m:
        raise ValueError("New entry must have ## YYYY-MM-DD Update header")
    new_date = m.group(1)

    # Merge: new entry replaces any existing same-date block
    entries[new_date] = new_entry_text.strip()

    # Rebuild file: keep header, then entries sorted by date, then footer
    header_match = re.search(r'^.*?(?=\n## 2026-)', content, re.DOTALL)
    if not header_match:
        raise ValueError("Vault missing standard header")
    header = header_match.group(0).strip()

    footer_match = re.search(r'\*Next check:.*?\n---\s*$', content, re.DOTALL)
    footer = footer_match.group(0).strip() if footer_match else "*Next check: 4× daily (08:15 / 12:15 / 16:15 / 20:15 UTC).*\n---"

    sorted_dates = sorted(entries.keys())
    new_body = '\n\n'.join([entries[d] for d in sorted_dates])

    new_content = f"{header}\n\n---\n\n{new_body}\n\n{footer}\n"

    # Atomic write: temp file + mv
    fd, tmp_path = tempfile.mkstemp(dir=vault.parent, text=True, prefix='.vault-tmp-')
    with os.fdopen(fd, 'w') as f:
        f.write(new_content)
    shutil.move(tmp_path, vault_path)

    print(f"✅ Vault updated: {vault_path} | Entry date: {new_date} | Total entries: {len(sorted_dates)}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--vault', required=True, help='Path to vault markdown file')
    parser.add_argument('--entry', required=True, help='New entry text (with header)')
    parser.add_argument('--dry-run', action='store_true', help='Show diff without writing')
    args = parser.parse_args()

    if args.dry_run:
        # Preview merge result
        vault = Path(args.vault)
        content = vault.read_text()
        entries = parse_entries(content)
        m = re.search(r'## (2026-\d{2}-\d{2}) Update', args.entry)
        new_date = m.group(1) if m else 'UNKNOWN'
        entries[new_date] = args.entry.strip()
        sorted_dates = sorted(entries.keys())
        print(f"[DRY RUN] Would update vault {args.vault}")
        print(f"  New date: {new_date}")
        print(f"  Total entries after merge: {len(sorted_dates)}")
        print(f"  Entry order: {sorted_dates}")
    else:
        merge_entry(args.vault, args.entry)
