#!/usr/bin/env python3
"""
Sync maintenance scripts from vault to all Hermes profile runtime directories.

This ensures the runtime copies in ~/.hermes/profiles/<profile>/scripts/
match the vault's canonical versions in /root/vaults/gentech/00-System/agent-profiles/.

Usage:
  python3 sync_maintenance_scripts.py [--dry-run] [--profile <name>]

Options:
  --dry-run    Show what would change without copying
  --profile    Sync only the specified profile (default: all)
"""

import os
import sys
import argparse
import filecmp
import shutil

VAULT_BASE = '/root/vaults/gentech/00-System/agent-profiles'
RUNTIME_BASE = '/root/.hermes/profiles'

PROFILES = ['gentech', 'yoyo', 'dmob', 'desmond']

def sync_profile(profile, dry_run=False):
    vault_scripts = os.path.join(VAULT_BASE, profile, 'scripts')
    runtime_scripts = os.path.join(RUNTIME_BASE, profile, 'scripts')

    if not os.path.isdir(vault_scripts):
        print(f'⚠️  No vault scripts directory for {profile} at {vault_scripts}')
        return

    os.makedirs(runtime_scripts, exist_ok=True)

    changes = []
    for fname in sorted(os.listdir(vault_scripts)):
        if not fname.endswith('.py'):
            continue
        src = os.path.join(vault_scripts, fname)
        dst = os.path.join(runtime_scripts, fname)

        # Compare if destination exists
        copy_needed = True
        if os.path.exists(dst):
            if filecmp.cmp(src, dst, shallow=False):
                copy_needed = False
            else:
                # Show diff preview
                src_size = os.path.getsize(src)
                dst_size = os.path.getsize(dst)
                print(f'  DRIFT: {fname} (vault:{src_size} bytes vs runtime:{dst_size} bytes)')

        if copy_needed:
            changes.append(fname)
            if not dry_run:
                shutil.copy2(src, dst)
                os.chmod(dst, 0o755)
                print(f'  ✓ Synced: {fname}')
            else:
                print(f'  • Would sync: {fname}')

    if not changes:
        print(f'  ✓ {profile}: already in sync')


def main():
    parser = argparse.ArgumentParser(description='Sync Hermes maintenance scripts from vault to runtime')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without applying')
    parser.add_argument('--profile', choices=PROFILES, help='Sync only this profile')
    args = parser.parse_args()

    profiles = [args.profile] if args.profile else PROFILES

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Syncing maintenance scripts...")
    for profile in profiles:
        print(f'\n{profile.upper()}:')
        sync_profile(profile, dry_run=args.dry_run)

    print('\nDone.')


if __name__ == "__main__":
    main()
