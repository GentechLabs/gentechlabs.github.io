#!/usr/bin/env python3
"""
Portfolio Data Generator — reads canonical source and writes data/projects.json
Source: 02-Labs/jordan-portfolio/projects.json
"""

import json
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).parent.parent
SOURCE = REPO_ROOT / '02-Labs' / 'jordan-portfolio' / 'projects.json'
OUTPUT = REPO_ROOT / 'data' / 'projects.json'

if not SOURCE.exists():
    print(f"Source not found: {SOURCE}")
    exit(1)

with open(SOURCE) as f:
    data = json.load(f)

# Ensure count field
data['count'] = len(data.get('projects', []))
data['generated'] = datetime.now().strftime("%Y-%m-%d %H:%M")
data['source'] = "02-Labs/jordan-portfolio/projects.json"

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(data, indent=2))
print(f"Generated {data['count']} projects → {OUTPUT}")
