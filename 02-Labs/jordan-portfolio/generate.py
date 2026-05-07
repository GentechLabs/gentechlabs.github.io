
#!/usr/bin/env python3
"""
Jordan Portfolio Generator — Sync projects.json → index.html
Replaces JSON block inside <script id="project-data"> with fresh data.
"""

import json
from pathlib import Path

PORTFOLIO = Path(__file__).parent
PROJECTS_JSON = PORTFOLIO / 'projects.json'
INDEX_HTML = PORTFOLIO / 'index.html'

if not PROJECTS_JSON.exists():
    print(f"❌ projects.json not found at {PROJECTS_JSON}")
    exit(1)

with open(PROJECTS_JSON) as f:
    data = json.load(f)
projects = data.get('projects', [])

html = INDEX_HTML.read_text()

start_tag = '<script id="project-data" type="application/json">'
end_tag = '</script>'

start_idx = html.find(start_tag)
if start_idx == -1:
    print("❌ Could not find start tag")
    exit(1)

content_start = start_idx + len(start_tag)
end_idx = html.find(end_tag, content_start)
if end_idx == -1:
    print("❌ Could not find end tag")
    exit(1)

# Prepare new JSON block (indented, then escape closing </script> to avoid early termination)
new_json = json.dumps(projects, indent=2)
# We don't need to escape </script> because the type is "application/json" not executed
# But to be safe, we could replace '<' with '\u003c', though not necessary
new_block = '\n' + new_json + '\n'

new_html = html[:content_start] + new_block + html[end_idx:]

INDEX_HTML.write_text(new_html)
print(f"✓ Portfolio regenerated — {len(projects)} projects embedded")
