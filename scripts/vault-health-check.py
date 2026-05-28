#!/usr/bin/env python3
"""
Vault Health Check — Security & Organization Audit
Runs as a cron job. Checks for:
1. Secrets/keys left in plain text
2. Personal info that shouldn't be committed
3. Naming inconsistencies
4. Files in wrong locations
5. Stale files needing archive
6. Missing required files
"""

import os
import re
import json
from datetime import datetime, timedelta
from pathlib import Path

VAULT = os.environ.get("OBSIDIAN_VAULT_PATH", "/root/vaults/gentech")
BRAIN = "/root/repos/hermes-brain"

# === SECURITY CHECKS ===

SECRET_PATTERNS = [
    (r'(?i)(api[_-]?key|secret[_-]?key|private[_-]?key|password|token)\s*[=:]\s*["\'][A-Za-z0-9]{16,}["\']', "Potential secret/key in plain text"),
    (r'(?i)bearer\s+[A-Za-z0-9\-._~+/]+=*', "Bearer token exposed"),
    (r'sk-[A-Za-z0-9]{20,}', "OpenAI-style API key"),
    (r'ghp_[A-Za-z0-9]{36}', "GitHub personal access token"),
    (r'xox[bpsa]-[A-Za-z0-9\-]+', "Slack token"),
    (r'(?i)-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----', "Private key block"),
    (r'0x[a-fA-F0-9]{64}', "Potential private key (64-byte hex)"),
    (r'(?i)(mnemonic|seed\s*phrase)\s*[=:]\s*["\'].+["\']', "Seed phrase/mnemonic exposed"),
]

PERSONAL_PATTERNS = [
    (r'\b\d{3}-\d{2}-\d{4}\b', "SSN pattern"),
    (r'\b\d{16}\b', "Potential credit card number"),
    (r'jordanjones0902@gmail\.com', "Personal email (consider if this should be in vault)"),
]

def check_secrets(filepath):
    """Scan file for secrets and personal info."""
    issues = []
    # Skip known false-positive directories
    skip_dirs = ['06-Audits', 'lib/', 'forge-std', 'node_modules', '__pycache__', '10-Archive']
    skip_files = ['SKILL.md', 'README.md', '.py.tmp', '.bak']
    if any(sd in filepath for sd in skip_dirs):
        return issues
    if any(sf in filepath for sf in skip_files):
        return issues
    try:
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
        for pattern, desc in SECRET_PATTERNS:
            matches = re.findall(pattern, content)
            if matches:
                issues.append(("🔴 SECRET", desc, filepath))
        for pattern, desc in PERSONAL_PATTERNS:
            matches = re.findall(pattern, content)
            if matches:
                issues.append(("🟡 PERSONAL", desc, filepath))
    except:
        pass
    return issues

# === ORGANIZATION CHECKS ===

def check_naming(vault_path):
    """Check for naming inconsistencies."""
    issues = []
    for root, dirs, files in os.walk(vault_path):
        # Skip .git, node_modules, etc.
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', '.obsidian']]
        for f in files:
            if f.startswith('.'):
                continue
            filepath = os.path.join(root, f)
            relpath = os.path.relpath(filepath, vault_path)
            
            # Check for spaces in filenames (Obsidian handles, but inconsistent)
            if ' ' in f and '-' in f:
                issues.append(("🟡 NAMING", f"Mixed spaces/hyphens: {relpath}", relpath))
            
            # Check for uppercase files (should be lowercase with hyphens)
            if f[0].isupper() and '-' in f:
                issues.append(("🟡 NAMING", f"Capitalized with hyphens: {relpath}", relpath))
            
            # Check for files at vault root that should be in a folder
            if os.path.dirname(relpath) == '' and f.endswith('.md'):
                if f not in ['INDEX.md', 'README.md', 'Gentech-HQ.md', '00-Working-Memory.md']:
                    issues.append(("🟡 ORGANIZATION", f"Loose file at root: {relpath}", relpath))
    return issues

def check_stale_files(vault_path, days_threshold=14):
    """Find files older than threshold that aren't archived."""
    issues = []
    now = datetime.now()
    archive_folders = ['10-Archive', '12-Archive', '.git', 'node_modules', '__pycache__']
    
    for root, dirs, files in os.walk(vault_path):
        # Skip archive and system folders
        dirs[:] = [d for d in dirs if d not in archive_folders + ['.obsidian']]
        relroot = os.path.relpath(root, vault_path)
        
        # Skip archive folders
        if any(af in relroot for af in archive_folders):
            continue
            
        for f in files:
            if f.startswith('.') or f.endswith(('.json', '.pyc', '.log')):
                continue
            filepath = os.path.join(root, f)
            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                age_days = (now - mtime).days
                if age_days > days_threshold:
                    relpath = os.path.relpath(filepath, vault_path)
                    issues.append(("🟡 STALE", f"{age_days} days old: {relpath}", relpath))
            except:
                pass
    return issues

def check_required_files(vault_path):
    """Check that required files exist."""
    required = [
        "00-Working-Memory.md",
        "INDEX.md",
        "Gentech-HQ.md",
        "00-HQ/hackathon-tracker.md",
        "09-Green Room/ideas.md",
    ]
    missing = []
    for f in required:
        if not os.path.exists(os.path.join(vault_path, f)):
            missing.append(("🔴 MISSING", f"Required file missing: {f}", f))
    return missing

def check_duplicate_folders(vault_path):
    """Check for duplicate or confusing folder names."""
    issues = []
    # Check for "09-Green Room" vs "09-Green Room" variants
    root_items = os.listdir(vault_path)
    green_room = [d for d in root_items if 'green' in d.lower() and 'room' in d.lower()]
    if len(green_room) > 1:
        issues.append(("🔴 DUPLICATE", f"Multiple Green Room folders: {green_room}", str(green_room)))
    
    archive = [d for d in root_items if 'archive' in d.lower()]
    if len(archive) > 1:
        issues.append(("🟡 DUPLICATE", f"Multiple archive folders: {archive}", str(archive)))
    return issues

def check_env_files(vault_path):
    """Check for .env files that shouldn't be committed."""
    issues = []
    for root, dirs, files in os.walk(vault_path):
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules']]
        for f in files:
            if f == '.env' or f == 'secrets.env':
                filepath = os.path.relpath(os.path.join(root, f), vault_path)
                issues.append(("🔴 ENV", f"Env file in vault: {filepath}", filepath))
            if f == '.git-credentials':
                filepath = os.path.relpath(os.path.join(root, f), vault_path)
                issues.append(("🔴 CREDENTIALS", f"Git credentials in vault: {filepath}", filepath))
    return issues

# === MAIN ===

def run_audit():
    """Run full vault audit."""
    all_issues = []
    
    # 1. Security scan
    print("🔍 Scanning for secrets...")
    for root, dirs, files in os.walk(VAULT):
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', '.obsidian']]
        for f in files:
            if f.startswith('.') or f.endswith(('.json', '.pyc', '.png', '.jpg', '.svg')):
                continue
            filepath = os.path.join(root, f)
            all_issues.extend(check_secrets(filepath))
    
    # 2. Organization checks
    print("📁 Checking organization...")
    all_issues.extend(check_naming(VAULT))
    all_issues.extend(check_duplicate_folders(VAULT))
    all_issues.extend(check_env_files(VAULT))
    all_issues.extend(check_required_files(VAULT))
    
    # 3. Stale files
    print("⏰ Finding stale files...")
    all_issues.extend(check_stale_files(VAULT, days_threshold=14))
    
    # 4. Brain backup check
    print("🧠 Checking brain backup...")
    brain_files = [
        "memories/MEMORY.md",
        "config.yaml",
    ]
    for f in brain_files:
        if not os.path.exists(os.path.join(BRAIN, f)):
            all_issues.append(("🟡 BRAIN", f"Brain backup missing: {f}", f))
    
    # 5. Git status
    print("📊 Checking git status...")
    import subprocess
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=VAULT, capture_output=True, text=True, timeout=10
        )
        untracked = [l for l in result.stdout.strip().split('\n') if l.startswith('??')]
        modified = [l for l in result.stdout.strip().split('\n') if l.startswith(' M') or l.startswith('M ')]
        if len(untracked) > 10:
            all_issues.append(("🟡 GIT", f"{len(untracked)} untracked files — consider committing or gitignoring", ""))
        if len(modified) > 10:
            all_issues.append(("🟡 GIT", f"{len(modified)} modified but uncommitted files", ""))
    except:
        pass
    
    return all_issues

def format_report(issues):
    """Format issues into a readable report."""
    if not issues:
        return "✅ Vault is clean! No issues found."
    
    # Group by severity
    secrets = [i for i in issues if i[0].startswith("🔴")]
    warnings = [i for i in issues if i[0].startswith("🟡")]
    
    lines = []
    lines.append(f"# 🔍 Vault Health Check — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Issues found:** {len(issues)} ({len(secrets)} critical, {len(warnings)} warnings)")
    lines.append("")
    
    if secrets:
        lines.append("## 🔴 Critical (Fix Immediately)")
        for severity, desc, path in secrets:
            lines.append(f"- **{desc}** — `{path}`")
        lines.append("")
    
    if warnings:
        lines.append("## 🟡 Warnings (Review)")
        for severity, desc, path in warnings:
            lines.append(f"- {desc} — `{path}`")
        lines.append("")
    
    # Health score
    score = max(0, 100 - (len(secrets) * 15) - (len(warnings) * 3))
    if score >= 90:
        grade = "A"
    elif score >= 75:
        grade = "B"
    elif score >= 60:
        grade = "C"
    else:
        grade = "D"
    
    lines.append(f"## Health Score: {score}/100 ({grade})")
    
    return "\n".join(lines)

if __name__ == "__main__":
    issues = run_audit()
    report = format_report(issues)
    print(report)
