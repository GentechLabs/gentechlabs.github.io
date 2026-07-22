#!/usr/bin/env python3
"""
GenTech Vault Audit — Find Unfinished, Misplaced, and Incomplete Notes
Runs daily at 6 PM to flag issues before they get lost
"""

import os
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

VAULT_PATH = Path("/root/vaults/gentech")
OUTPUT_PATH = VAULT_PATH / "11-Mess Hall" / "vault-audits"

# Keywords that indicate unfinished work
UNFINISHED_KEYWORDS = [
    "TODO", "WIP", "Draft", "In Progress", "FIXME", "PLACEHOLDER",
    "TBD", "Coming Soon", "Not Started", "Paused", "Blocked"
]

# Keywords that indicate completed work
COMPLETED_KEYWORDS = [
    "Done", "Complete", "Completed", "Shipped", "Deployed", "Live"
]

# Folder structure for proper organization
FOLDER_STRUCTURE = {
    "decisions": ["00-HQ"],
    "ideas": ["11-Mess Hall"],
    "strategies": ["03-Strategies", "Strategies"],
    "labs": ["02-Labs", "Labs"],
    "projects": ["03-Projects", "Projects"],
    "content": ["06-Content", "Content", "Entertainment"],
    "gaming": ["15-Gaming", "Gaming"],
    "daily": ["Daily"],
    "archive": ["Archive"]
}

def scan_vault():
    """Scan vault for issues"""
    issues = {
        "unfinished": [],
        "misplaced": [],
        "incomplete": [],
        "stale": [],
        "duplicates": []
    }
    
    # Track all files for duplicate detection
    all_files = defaultdict(list)
    
    for md_file in VAULT_PATH.rglob("*.md"):
        if ".git" in str(md_file) or "node_modules" in str(md_file):
            continue
        
        try:
            content = md_file.read_text()
            relative_path = md_file.relative_to(VAULT_PATH)
            
            # Check for unfinished work
            for keyword in UNFINISHED_KEYWORDS:
                if keyword.lower() in content.lower():
                    issues["unfinished"].append({
                        "file": str(relative_path),
                        "keyword": keyword,
                        "line": find_line_with_keyword(content, keyword)
                    })
                    break
            
            # Check for incomplete files (very short content)
            if len(content.strip()) < 100 and not str(relative_path).endswith("README.md"):
                issues["incomplete"].append({
                    "file": str(relative_path),
                    "size": len(content.strip())
                })
            
            # Check for stale files (not updated in 14+ days)
            mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
            if datetime.now() - mtime > timedelta(days=14):
                issues["stale"].append({
                    "file": str(relative_path),
                    "last_modified": mtime.strftime("%Y-%m-%d")
                })
            
            # Track for duplicate detection
            all_files[md_file.name].append(str(relative_path))
            
        except Exception as e:
            print(f"Error reading {md_file}: {e}")
    
    # Find duplicates
    for filename, paths in all_files.items():
        if len(paths) > 1:
            issues["duplicates"].append({
                "filename": filename,
                "locations": paths
            })
    
    return issues

def find_line_with_keyword(content, keyword):
    """Find line number with keyword"""
    for i, line in enumerate(content.split("\n"), 1):
        if keyword.lower() in line.lower():
            return i
    return 1

def generate_report(issues):
    """Generate audit report"""
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    
    report_file = OUTPUT_PATH / f"vault-audit-{datetime.now().strftime('%Y%m%d')}.md"
    
    report = f"""# Vault Audit Report — {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Summary
- **Unfinished notes:** {len(issues["unfinished"])}
- **Incomplete files:** {len(issues["incomplete"])}
- **Stale files (14+ days):** {len(issues["stale"])}
- **Duplicate filenames:** {len(issues["duplicates"])}

---

## Unfinished Notes
These files contain TODO, WIP, Draft, or other unfinished markers:

| File | Keyword | Line |
|------|---------|------|
"""
    
    for item in issues["unfinished"][:20]:  # Limit to 20
        report += f"| `{item['file']}` | {item['keyword']} | {item['line']} |\n"
    
    report += f"""
---

## Incomplete Files
These files are very small (< 100 chars) and may be placeholders:

| File | Size |
|------|------|
"""
    
    for item in issues["incomplete"][:20]:
        report += f"| `{item['file']}` | {item['size']} chars |\n"
    
    report += f"""
---

## Stale Files (14+ days)
These files haven't been updated in 2+ weeks:

| File | Last Modified |
|------|---------------|
"""
    
    for item in issues["stale"][:20]:
        report += f"| `{item['file']}` | {item['last_modified']} |\n"
    
    report += f"""
---

## Duplicate Filenames
These filenames exist in multiple locations:

| Filename | Locations |
|----------|-----------|
"""
    
    for item in issues["duplicates"][:10]:
        locations = ", ".join([f"`{loc}`" for loc in item["locations"]])
        report += f"| `{item['filename']}` | {locations} |\n"
    
    report += """
---

## Recommended Actions

1. **Unfinished notes:** Review and either complete or archive
2. **Incomplete files:** Fill in content or delete if no longer needed
3. **Stale files:** Update or move to Archive
4. **Duplicates:** Consolidate into single location

---

*Gentech Vault Audit — Auto-generated*
"""
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    return report_file

if __name__ == "__main__":
    print("Scanning vault for issues...")
    issues = scan_vault()
    
    print(f"\nAudit Results:")
    print(f"  Unfinished notes: {len(issues['unfinished'])}")
    print(f"  Incomplete files: {len(issues['incomplete'])}")
    print(f"  Stale files: {len(issues['stale'])}")
    print(f"  Duplicates: {len(issues['duplicates'])}")
    
    report_file = generate_report(issues)
    print(f"\nReport saved to: {report_file}")
