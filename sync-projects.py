#!/usr/bin/env python3
"""
Portfolio Sync Script
=====================
Single source of truth: data/projects.json
Generates: projects.json (root) + inline JS array in index.html

Usage: python3 sync-projects.py [--dry-run]
"""
import json
import sys
import re
import os

PORTFOLIO_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_FILE = os.path.join(PORTFOLIO_DIR, "data", "projects.json")
ROOT_FILE = os.path.join(PORTFOLIO_DIR, "projects.json")
HTML_FILE = os.path.join(PORTFOLIO_DIR, "index.html")

DRY_RUN = "--dry-run" in sys.argv


def load_source():
    with open(SRC_FILE) as f:
        data = json.load(f)
    return data["projects"]


def sync_projects_json(projects):
    """Write projects.json root file."""
    data = {
        "count": len(projects),
        "generated": "Auto-generated from data/projects.json",
        "projects": projects
    }
    if DRY_RUN:
        print(f"  [dry-run] Would write {ROOT_FILE} with {len(projects)} projects")
        return
    with open(ROOT_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  ✅ projects.json — {len(projects)} projects")


def build_js_entry(p):
    """Build a JS object entry for a project."""
    tech_str = json.dumps(p.get("tech", []))
    lines = [f"    {{"]
    lines.append(f"      id: '{p['id']}',")
    lines.append(f"      title: '{p['title']}',")
    desc = p.get("description", "").replace("'", "\\'")
    lines.append(f"      description: '{desc}',")
    lines.append(f"      tech: {tech_str},")
    lines.append(f"      status: '{p.get('status', 'building')}',")
    deadline = p.get("deadline")
    lines.append(f"      deadline: {json.dumps(deadline)},")
    lines.append(f"      timeline: '{p.get('timeline', '')}',")
    lines.append(f"      highlight: {json.dumps(p.get('highlight', False))},")
    if p.get("demo_url"):
        lines.append(f"      demo_url: '{p['demo_url']}',")
    if p.get("github"):
        lines.append(f"      github: '{p['github']}',")
    if p.get("vault_path"):
        lines.append(f"      vault_path: '{p['vault_path']}',")
    lines.append(f"    }}")
    return "\n".join(lines)


def sync_index_html(projects):
    """Replace the inline JS project array in index.html."""
    with open(HTML_FILE) as f:
        content = f.read()

    # Build the new JS array
    js_entries = [build_js_entry(p) for p in projects]
    new_array = "[\n" + ",\n".join(js_entries) + "\n]"

    # Match the JS projects array: starts with 'const projects = [' or similar
    # Look for the pattern: projects that ends with ]
    pattern = r'(const\s+projects\s*=\s*)\[.*?\n\]'
    replacement = f"\\1{new_array}"

    new_content, count = re.subn(pattern, replacement, content, count=1, flags=re.DOTALL)

    if count == 0:
        # Try alternative pattern (just the array)
        pattern2 = r'(\[\s*\n\s*\{\s*\n\s*id:\s*[\'"])'
        print("  ⚠️  Could not find JS projects array in index.html")
        print("     May need manual sync")
        return

    if DRY_RUN:
        print(f"  [dry-run] Would update JS array in index.html")
        return

    with open(HTML_FILE, "w") as f:
        f.write(new_content)
    print(f"  ✅ index.html JS array — {len(projects)} projects")


def main():
    print("🔄 Portfolio Sync")
    print(f"   Source: {SRC_FILE}")
    print()

    projects = load_source()
    print(f"   Found {len(projects)} projects in data/projects.json")
    print()

    print("Syncing...")
    sync_projects_json(projects)
    sync_index_html(projects)

    print()
    print("✅ Done. All sources aligned.")


if __name__ == "__main__":
    main()
