#!/usr/bin/env python3
"""
GenTech Pals — Patch Notes Scanner
Scans for new game patches and flags changes relevant to a build.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Try to import hermes_tools for web search
try:
    from hermes_tools import web_search
    HAS_HERMES = True
except ImportError:
    HAS_HERMES = False

VAULT_BASE = Path("/root/vaults/gentech/15-Gaming")
BUILD_FILE = VAULT_BASE / "POE-2" / "Jordan Monk build.md"
PATCH_LOG = VAULT_BASE / "POE-2" / "patch-notes-log.json"


def load_patch_log() -> dict:
    """Load the patch notes log."""
    if PATCH_LOG.exists():
        return json.loads(PATCH_LOG.read_text())
    return {"last_scan": None, "known_patches": []}


def save_patch_log(log: dict):
    """Save the patch notes log."""
    PATCH_LOG.write_text(json.dumps(log, indent=2))


def extract_skills_from_build() -> list:
    """Extract skill names from the build file for relevance matching."""
    if not BUILD_FILE.exists():
        return []
    
    content = BUILD_FILE.read_text()
    skills = []
    
    for line in content.split("\n"):
        if line.strip().startswith("- **") and "skill" not in line.lower():
            import re
            match = re.search(r"\*\*(.+?)\*\*", line)
            if match:
                skills.append(match.group(1).lower())
    
    return skills


def check_relevance(patch_text: str, skills: list) -> list:
    """Check if patch changes are relevant to the build's skills."""
    relevant = []
    patch_lower = patch_text.lower()
    
    for skill in skills:
        if skill.lower() in patch_lower:
            relevant.append(skill)
    
    # Also check for general keywords
    general_keywords = ["monk", "lightning", "invoker", "quarterstaff", "mana", "elemental"]
    for kw in general_keywords:
        if kw in patch_lower and kw not in [r.lower() for r in relevant]:
            relevant.append(kw)
    
    return relevant


def format_scan_result(results: list, relevant_changes: list) -> str:
    """Format scan results into a readable report."""
    lines = []
    lines.append("🔍 **GenTech Pals — Patch Notes Scan**")
    lines.append(f"Scan time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    
    if not results:
        lines.append("No new patch notes found.")
        return "\n".join(lines)
    
    for r in results:
        lines.append(f"**{r.get('title', 'Unknown')}**")
        lines.append(f"  Source: {r.get('url', 'N/A')}")
        lines.append(f"  {r.get('description', 'No description')[:200]}")
        lines.append("")
    
    if relevant_changes:
        lines.append("**⚡ Relevant to your build:**")
        for change in relevant_changes:
            lines.append(f"  • {change}")
    else:
        lines.append("No changes directly relevant to your current build skills.")
    
    return "\n".join(lines)


def main():
    """Main entry point for patch notes scan."""
    if not HAS_HERMES:
        print("❌ hermes_tools not available. Run this as a Hermes skill or cron job.")
        sys.exit(1)
    
    skills = extract_skills_from_build()
    print(f"Building search queries for skills: {', '.join(skills[:5])}...")
    
    # Search for recent patch notes
    results = []
    queries = [
        "Path of Exile 2 patch notes 2026",
        "POE2 balance changes Monk Invoker",
        "Path of Exile 2 update May 2026"
    ]
    
    for query in queries:
        try:
            search_results = web_search(query, limit=3)
            if "data" in search_results and "web" in search_results["data"]:
                for r in search_results["data"]["web"]:
                    results.append({
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "description": r.get("description", "")
                    })
        except Exception as e:
            print(f"Search error: {e}")
    
    # Deduplicate by URL
    seen_urls = set()
    unique_results = []
    for r in results:
        if r["url"] not in seen_urls:
            seen_urls.add(r["url"])
            unique_results.append(r)
    
    # Check relevance
    all_text = " ".join([r.get("description", "") for r in unique_results])
    relevant = check_relevance(all_text, skills)
    
    # Format and output
    report = format_scan_result(unique_results[:5], relevant)
    print(report)
    
    # Update log
    log = load_patch_log()
    log["last_scan"] = datetime.now().isoformat()
    log["known_patches"] = [r["url"] for r in unique_results]
    save_patch_log(log)


if __name__ == "__main__":
    main()
