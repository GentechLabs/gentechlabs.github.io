#!/usr/bin/env python3
"""
Portfolio HTML Generator
Reads projects.json and embeds project data into index.html
"""
import json
import os
import sys

VAULT_ROOT = "/root/vaults/gentech"
PROJECTS_JSON = os.path.join(VAULT_ROOT, "projects.json")
INDEX_HTML = os.path.join(VAULT_ROOT, "index.html")

def load_projects():
    with open(PROJECTS_JSON, "r") as f:
        return json.load(f)

def embed_projects(html, projects_json_str):
    """Replace the <script id="project-data"> block with fresh data."""
    start_tag = '<script id="project-data" type="application/json">'
    end_tag = '</script>'
    start_idx = html.find(start_tag)
    if start_idx == -1:
        print("ERROR: Could not find <script id=\"project-data\"> block in index.html")
        sys.exit(1)
    # Find the closing </script> after the start tag
    end_idx = html.find(end_tag, start_idx + len(start_tag))
    if end_idx == -1:
        print("ERROR: Could not find closing </script> for project-data block")
        sys.exit(1)
    end_idx += len(end_tag)
    replacement = f'{start_tag}\n{projects_json_str}\n{end_tag}'
    return html[:start_idx] + replacement + html[end_idx:]

def main():
    data = load_projects()
    projects = data.get("projects", [])
    projects_json_str = json.dumps(projects, indent=2)

    with open(INDEX_HTML, "r") as f:
        html = f.read()

    new_html = embed_projects(html, projects_json_str)

    with open(INDEX_HTML, "w") as f:
        f.write(new_html)

    count = len(projects)
    statuses = {}
    for p in projects:
        s = p.get("status", "unknown")
        statuses[s] = statuses.get(s, 0) + 1

    status_summary = ", ".join(f"{s}: {c}" for s, c in sorted(statuses.items()))
    print(f"✓ Portfolio regenerated — {count} projects embedded")
    print(f"  Statuses: {status_summary}")

if __name__ == "__main__":
    main()
