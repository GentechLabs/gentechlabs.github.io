#!/usr/bin/env python3
"""
Vault Audit Runner — DMOB Labs
Generates a standardized vault health report.
Usage: python3 vault_audit.py > vault-audit-YYYY-MM-DD.md
"""

import subprocess, json, os, re
from pathlib import Path
from datetime import datetime, timezone

VAULT = Path('/root/vaults/gentech')
HERMES = Path('/root/.hermes')
NOW = datetime.now(timezone.utc)

def section(title, icon="📋"):
    print(f"\n## {icon} {title}\n")

def find_dirs():
    return [p for p in VAULT.iterdir() if p.is_dir()]

def check_folder(folder_name):
    p = VAULT / folder_name
    return p.exists(), len(list(p.rglob('*'))) if p.exists() else 0

def scan_sensitive(active_only=True):
    patterns = [
        ('API keys (masked)', r'\w+_API_KEY=\*\*\*'),
        ('Private keys', r'(0x)?[a-fA-F0-9]{64,}'),
        ('Wallet addresses', r'0x[a-fA-F0-9]{40}'),
        ('JWT tokens', r'eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*'),
        ('GitHub tokens', r'ghp_[a-zA-Z0-9]{36}'),
        ('Email addresses', r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'),
    ]
    results = {}
    for label, pat in patterns:
        cmd = ['grep', '-rPl', pat, str(VAULT),
               '--include=*.md', '--include=*.env', '--include=*.yaml', '--include=*.yml',
               '--include=*.json', '--include=*.txt', '--include=*.sh']
        if active_only:
            cmd += ['--exclude-dir=10-Archive', '--exclude-dir=memories']
        r = subprocess.run(cmd, capture_output=True, text=True)
        files = [f for f in r.stdout.strip().split('\n') if f]
        results[label] = files
    return results

def check_cron_health():
    profiles_dir = HERMES / 'profiles'
    if not profiles_dir.exists():
        return []
    result = []
    for pdir in profiles_dir.iterdir():
        if pdir.is_dir():
            jf = pdir / 'cron' / 'jobs.json'
            if jf.exists():
                try:
                    data = json.loads(jf.read_text())
                    result.append((pdir.name, '✅', len(data)))
                except Exception as e:
                    result.append((pdir.name, '❌', str(e)))
    return result

def main():
    print(f"# Vault Audit Report — {NOW.date()} ({NOW.isoformat()})")
    print(f"**Auditor:** DMOB (Head of Labs)")
    print(f"**Vault:** {VAULT}")

    # 1. Structure
    section("1. Structural Completeness", "🏗️")
    expected = {
        'Labs Core': ['02-Labs', '02-AAE'],
        'Labs Security': ['06-Security', 'Audits'],
        'HQ': ['00-HQ', '00-System', '00-Inbox'],
        'Agency': ['01-Agency', '01-Agents'],
        'Strategies': ['03-Strategies', '03-Projects'],
        'Creative': ['04-Entertainment', '04-Content'],
        'Learning': ['05-Learning'],
        'Coordination': ['09-Green Room', '09-Templates', '11-Mess Hall'],
        'Skills': ['12-Skills'],
    }
    missing = []
    for cat, folders in expected.items():
        print(f"**{cat}:**")
        for f in folders:
            exists, count = check_folder(f)
            stat = "✅" if exists else f"❌ MISSING"
            print(f"  {stat} {f}/" + (f" ({count} files)" if exists else ""))
            if not exists:
                missing.append(f)
        print()

    # 2. Sensitive data
    section("2. Active Sensitive Data Inventory", "🔐")
    sensitive = scan_sensitive(active_only=True)
    total_active = sum(len(v) for v in sensitive.values())
    print(f"Files in active vault with sensitive patterns: **{total_active}**")
    for label, files in sensitive.items():
        if files:
            print(f"\n- **{label}:** {len(files)} file(s)")
            for f in files[:3]:
                print(f"    - {f}")
            if len(files) > 3:
                print(f"    ... +{len(files)-3} more")

    # 3. Operational health
    section("3. Operational Infrastructure Health", "⚙️")
    # Atomic writer
    vw = VAULT / '02-Labs' / 'scripts' / 'vault_writer.py'
    print(f"**Atomic writer:** {'✅ Found' if vw.exists() else '❌ Missing'}")
    # ob sync
    ob = subprocess.run(['which', 'ob'], capture_output=True, text=True)
    print(f"**ob sync:** {'✅ ' + ob.stdout.strip() if ob.returncode==0 else '❌ Not in PATH'}")
    # Cron
    cron_stats = check_cron_health()
    print("**Cron jobs:**")
    for profile, status, detail in cron_stats:
        print(f"  {profile}: {status} {detail}")

    # 4. Governance gaps
    section("4. Governance & Policy Gaps", "🛡️")
    archive_dir = VAULT / '10-Archive'
    if archive_dir.exists():
        count = sum(1 for _ in archive_dir.rglob('*') if _.is_file())
        print(f"**Archive ingestion:** 10-Archive/ contains {count} files — verify secret-exclusion filter is active")
    print("**Policy recommendations:**")
    print("  - Add `vault-writer` secret-storage rule: NEVER write active secrets to vault")
    print("  - Implement pre-ingestion filter: exclude `*.env`, `*token*`, `*key*` from archives")
    print("  - Define secret lifecycle: tokens in vault ≤ 24h grace period before deletion")

    # Summary
    section("Executive Summary", "📊")
    health = "🟡 MEDIUM RISK"
    if missing:
        health += f" — {len(missing)} structural gaps"
    if total_active > 0:
        health += f", {total_active} sensitive files in active vault"
    print(f"**Vault health:** {health}")
    print(f"\n**Immediate actions:**")
    print("1. 🔴 Rotate GitHub PAT + purge from vault root `.env` and Hermes sessions")
    print("2. 🔴 Move Colosseum JWT to Hermes profile `.env` only, delete from vault")
    print("3. 🟡 Create missing `06-Security/` and `Audits/` folders")
    print("\n---")
    print("Generated by `vault-audit` skill | Method: structural + sensitive scan + operational health")

if __name__ == '__main__':
    main()
