#!/usr/bin/env python3
"""
Extract travel-relevant APIs from public-apis/README.md

Usage:
  python extract-public-apis.py /path/to/public-apis/README.md travel > travel-apis.json

Outputs structured JSON:
{
  "Transportation": [{ "name": "...", "url": "...", "description": "...", "auth": "...", "https": "...", "cors": "..." }],
  "Geocoding": [...],
  ...
}
"""

import sys
import re
import json


def parse_public_apis(readme_path: str, semantic_keywords: list) -> dict:
    """
    Parse public-apis README.md and extract categories matching semantic_keywords.

    Args:
        readme_path: Path to public-apis/README.md
        semantic_keywords: List of lowercase keywords to match in category names

    Returns:
        dict: {category_name: [api_records, ...]}
    """
    with open(readme_path, 'r') as f:
        lines = f.read().split('\n')

    # Find Index section boundaries
    index_start = None
    index_end = None
    for i, line in enumerate(lines):
        if line.startswith('## ') and 'Index' in line:
            index_start = i
        elif index_start and line.startswith('## ') and i > index_start:
            index_end = i
            break
    if index_end is None:
        index_end = len(lines)

    # Find all ### subsections within Index (these are API categories)
    subsections = []
    for i in range(index_start, index_end):
        if lines[i].startswith('### '):
            name = lines[i][4:].strip()
            # Find table start (after separator line)
            table_start = None
            for j in range(i + 1, min(i + 10, index_end)):
                if re.match(r'^\|:?---\|:?---\|:?---\|', lines[j]):
                    table_start = j + 1
                    break
            if table_start:
                subsections.append({'name': name, 'table_start': table_start})

    # Filter by semantic keywords
    matching_subsections = [
        s for s in subsections
        if any(kw in s['name'].lower() for kw in semantic_keywords)
    ]

    # Parse API entries for each matching category
    results = {}
    for subsec in matching_subsections:
        apis = []
        for i in range(subsec['table_start'], index_end):
            line = lines[i]
            if not line.strip().startswith('|'):
                break  # End of table for this category
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 6:
                name_match = re.search(r'\[(.*?)\]\(', parts[1])
                url_match = re.search(r'\((https?://[^)]+)\)', parts[1])
                api = {
                    'name': name_match.group(1) if name_match else parts[1],
                    'url': url_match.group(1) if url_match else '',
                    'description': parts[2],
                    'auth': parts[3],
                    'https': parts[4],
                    'cors': parts[5]
                }
                apis.append(api)
        results[subsec['name']] = apis

    return results


def main():
    if len(sys.argv) < 3:
        print("Usage: extract-public-apis.py <readme.md> <project-keyword> [additional-keywords...]")
        print("Example: extract-public-apis.py README.md travel transport weather")
        sys.exit(1)

    readme_path = sys.argv[1]
    keywords = [kw.lower() for kw in sys.argv[2:]]

    results = parse_public_apis(readme_path, keywords)

    # Output JSON to stdout
    json.dump(results, sys.stdout, indent=2)
    print()  # newline

    # Print summary to stderr
    total = sum(len(apis) for apis in results.values())
    print(f"\nExtracted {total} APIs across {len(results)} categories:", file=sys.stderr)
    for cat, apis in results.items():
        free = sum(1 for a in apis if a['auth'] == 'No')
        print(f"  {cat}: {len(apis)} total, {free} free (no auth)", file=sys.stderr)


if __name__ == '__main__':
    main()
