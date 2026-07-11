#!/usr/bin/env python3
"""
NotebookLM Source Preparer — Gentech Vault Pipeline
====================================================
Extracts vault notes, strips metadata, cleans markdown,
and outputs ready-to-ingest sources for NotebookLM.

Usage:
  python scripts/notebooklm-prep.py [path_or_tag]
  
Examples:
  python scripts/notebooklm-prep.py --all
  python scripts/notebooklm-prep.py "agents-as-rwas-thesis.md"
  python scripts/notebooklm-prep.py --tag notebooklm
  python scripts/notebooklm-prep.py --list             # show candidates
  python scripts/notebooklm-prep.py --status            # what's been processed
"""

import os
import re
import json
import hashlib
import sys
from datetime import datetime
from pathlib import Path

VAULT_ROOT = "/root/vaults/gentech"
OUTPUT_DIR = f"{VAULT_ROOT}/11-Mess Hall/notebooklm-sources"
TRACKING_FILE = f"{OUTPUT_DIR}/.tracking.json"
GIT_SYNC_SCRIPT = f"{VAULT_ROOT}/scripts/_notebooklm-git-sync.sh"

# Tags that mark a note as NotebookLM-ready
LITERAL_TAGS = {"#notebooklm", "#briefing", "#content", "#podcast"}

def get_note_title(path, content):
    """Extract the best title from a note."""
    # Try first # heading
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('# ') and not line.startswith('# '):
            return line[2:].strip()
        if line.startswith('# '):
            return line[2:].strip()
    # Fall back to filename
    return Path(path).stem.replace('-', ' ').title()

def strip_frontmatter(content):
    """Remove YAML frontmatter between --- delimiters."""
    lines = content.split('\n')
    if lines and lines[0].strip() == '---':
        end = 1
        while end < len(lines):
            if lines[end].strip() == '---':
                return '\n'.join(lines[end+1:])
            end += 1
    return content

def clean_wiki_links(text):
    """Convert [[Wiki Link|Display]] and [[Wiki Link]] to plain display text."""
    text = re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]', r'\2', text)
    text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', text)
    return text

def clean_obsidian_syntax(text):
    """Remove Obsidian-specific metadata and internal markers."""
    # Remove tag-only lines (markdown tags used for routing, not content)
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        stripped = line.strip()
        # Skip lines that are ONLY tags
        if stripped and all(w.startswith('#') or w.startswith('- [') or w == '' for w in stripped.split()):
            # Keep checkbox list items but strip standalone tags like #notebooklm
            if not re.match(r'^#\w+$', stripped):
                # Check if line is just tags and spaces
                tokens = stripped.split()
                if all(t.startswith('#') for t in tokens):
                    continue
        cleaned.append(line)
    return '\n'.join(cleaned)

def clean_divider_walls(text):
    """Convert ASCII art dividers/walls to simple --- hr."""
    lines = text.split('\n')
    cleaned = []
    in_wall = False
    for line in lines:
        s = line.strip()
        # Detect slash-wall patterns like the V4 header
        if re.match(r'^[\\/][ \\t]*[\\/]', s) and len(s) > 10:
            in_wall = True
            continue
        if in_wall:
            if re.match(r'^[\\/][ \\t]*[\\/]', s):
                continue
            in_wall = False
            cleaned.append('---')
        cleaned.append(line)
    return '\n'.join(cleaned)

def collapse_whitespace(text):
    """Collapse excessive blank lines."""
    while '\n\n\n' in text:
        text = text.replace('\n\n\n', '\n\n')
    return text.strip()

def extract_sources_info(content):
    """Extract any Obsidian embed links or external URLs referenced."""
    urls = re.findall(r'https?://[^\s\)\]>]+', content)
    return urls

def prepare_note(filepath, tag_hint=None):
    """Process a single vault note into NotebookLM-ready markdown."""
    with open(filepath, 'r') as f:
        raw = f.read()
    
    # Strip frontmatter
    body = strip_frontmatter(raw)
    
    # Clean syntax
    body = clean_wiki_links(body)
    body = clean_obsidian_syntax(body)
    body = clean_divider_walls(body)
    body = collapse_whitespace(body)
    
    # Get title
    title = get_note_title(filepath, body)
    
    # Strip the original # title line from body if it matches our title
    lines = body.split('\n')
    if lines and lines[0].strip() in (f'# {title}', f'# {title.strip()}'):
        lines = lines[1:]
        body = '\n'.join(lines).strip()
    
    # Add a brief header
    source_basename = os.path.basename(filepath)
    now_str = datetime.now().strftime("%Y-%m-%d")
    
    output = f"# {title}\n\n"
    output += f"*Source: {source_basename} | Prepared: {now_str}*\n\n"
    output += body
    
    # Compute hash for dedup tracking
    content_hash = hashlib.sha256(raw.encode()).hexdigest()[:12]
    
    # Save output
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_name = Path(filepath).stem.replace(' ', '-').lower()
    out_path = f"{OUTPUT_DIR}/{out_name}.md"
    
    with open(out_path, 'w') as f:
        f.write(output)
    
    # Track it
    tracking = {
        "source": filepath.replace(VAULT_ROOT, '.'),
        "source_hash": content_hash,
        "title": title,
        "processed_at": now_str,
        "output": out_path.replace(VAULT_ROOT, '.'),
        "size_bytes": len(output),
        "size_lines": output.count('\n'),
    }
    
    return tracking

def load_tracking():
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE) as f:
            return json.load(f)
    return {"sources": [], "last_run": None}

def save_tracking(data):
    data["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(TRACKING_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def find_candidates(tagged_only=True):
    """Find all markdown notes in the vault, filtered by tags or content signals."""
    candidates = []
    
    for root, dirs, files in os.walk(VAULT_ROOT):
        # Skip hidden dirs, scripts, git, and the output dir itself
        skip_dirs = {'.git', '__pycache__', 'node_modules', 'notebooklm-sources', 'scripts', 'Archive', '_legacy', 'archive'}
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in skip_dirs]
        
        for f in files:
            if not f.endswith('.md'):
                continue
            path = os.path.join(root, f)
            
            # Check size — skip tiny or huge files
            size = os.path.getsize(path)
            if size < 100 or size > 500_000:
                continue
            
            # Read first 30 lines to scan for tags/metadata
            with open(path, 'r') as fh:
                head = ''.join([fh.readline() for _ in range(30)])
            
            # Check for explicit notebooklm tags
            has_tag = any(tag in head for tag in LITERAL_TAGS)
            
            if tagged_only:
                if has_tag:
                    rel_path = path.replace(VAULT_ROOT, '.')
                    candidates.append({
                        "path": path,
                        "rel": rel_path,
                        "size": size,
                        "tagged": True,
                    })
            else:
                # Non-tagged mode — also look for status-based candidates
                has_status = 'status:' in head.lower() or 'status :' in head.lower()
                is_handoff = 'handoff' in f.lower() or 'handoff' in head[:200].lower()
                is_daily = bool(re.search(r'\d{4}-\d{2}-\d{2}', f)) and f.startswith(('000', '202'))
                
                if has_tag or (has_status and not is_handoff and not is_daily):
                    rel_path = path.replace(VAULT_ROOT, '.')
                    candidates.append({
                        "path": path,
                        "rel": rel_path,
                        "size": size,
                        "tagged": has_tag,
                        "status": has_status,
                    })
    
    return candidates

def show_status():
    """Show what's been prepared and what's available."""
    tracking = load_tracking()
    processed = {s["source"] for s in tracking["sources"]}
    candidates = find_candidates(tagged_only=True)  # tagged only for clean status
    
    print("=== NotebookLM Pipeline Status ===")
    print(f"Last run: {tracking.get('last_run', 'Never')}\n")
    print(f"Sources prepared: {len(tracking['sources'])}")
    
    if tracking['sources']:
        print("\nPrepared sources:")
        for s in tracking['sources'][-10:]:
            print(f"  ✅ {s['source']} → {s['output']}")
    
    print(f"\nTagged candidates (#notebooklm etc.): {len(candidates)}")
    new_candidates = [c for c in candidates if c['rel'] not in processed]
    
    if new_candidates:
        print("\nUnprocessed tagged candidates:")
        for c in new_candidates:
            print(f"  📌 {c['rel']}")
    else:
        print("\nAll tagged candidates processed.")
    
    # Show untagged-but-available with --scan flag
    print(f"\nOutput directory: {OUTPUT_DIR}")
    
    # List actual output files
    if os.path.exists(OUTPUT_DIR):
        files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.md') and f != '.tracking.json']
        print(f"Output files ready: {len(files)}")
        for f in sorted(files):
            fpath = os.path.join(OUTPUT_DIR, f)
            size = os.path.getsize(fpath)
            print(f"  📄 {f} ({size:,} bytes)")
    
    print(f"\nTo scan all status-based candidates: python scripts/notebooklm-prep.py --scan")
    print(f"To prepare all tagged sources:         python scripts/notebooklm-prep.py --all")

def show_scan():
    """Show ALL status-based candidates for manual selection."""
    tracking = load_tracking()
    processed = {s["source"] for s in tracking["sources"]}
    candidates = find_candidates(tagged_only=False)
    
    print("=== Full Candidate Scan (status-based notes) ===\n")
    print(f"Total candidates found: {len(candidates)}\n")
    
    # Group by directory
    groups = {}
    for c in candidates:
        dir_name = os.path.dirname(c['rel'])
        groups.setdefault(dir_name, []).append(c)
    
    for dir_name in sorted(groups.keys()):
        notes = groups[dir_name]
        print(f"\n{dir_name}/ ({len(notes)} notes)")
        for c in notes:
            tag = '📌' if c['tagged'] else '  '
            status = ' [processed]' if c['rel'] in processed else ''
            print(f"  {tag} {os.path.basename(c['rel'])}{status}")
    
    print(f"\nTo prepare one: python scripts/notebooklm-prep.py <filename>")
    print(f"To add tag first: add #notebooklm to the note's frontmatter")

def process_all():
    """Process all unprocessed tagged candidates."""
    tracking = load_tracking()
    processed = {s["source"] for s in tracking["sources"]}
    candidates = find_candidates(tagged_only=True)
    
    to_process = [c for c in candidates if c['rel'] not in processed]
    
    if not to_process:
        print("✅ All tagged candidates already processed. Nothing new.")
        return
    
    results = []
    for c in to_process:
        print(f"  Processing {c['rel']}...", end=' ')
        try:
            tr = prepare_note(c['path'])
            tracking['sources'].append(tr)
            results.append(tr)
            print(f"✅ ({tr['size_lines']} lines, {tr['size_bytes']:,} bytes)")
        except Exception as e:
            print(f"❌ {e}")
    
    save_tracking(tracking)
    print(f"\nDone. {len(results)} source(s) prepared for NotebookLM.")
    print(f"Open → notebooklm.google.com → Create new notebook → Add sources")

def process_single(path_or_name):
    """Process a single note by path or filename."""
    # Try literal path
    if os.path.exists(path_or_name):
        full_path = path_or_name
    else:
        # Search vault for matching filename
        matches = []
        for root, dirs, files in os.walk(VAULT_ROOT):
            skip_dirs = {'.git', '__pycache__', 'node_modules', 'notebooklm-sources', 'scripts'}
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for f in files:
                if path_or_name in f or path_or_name in os.path.join(root, f):
                    matches.append(os.path.join(root, f))
        
        if not matches:
            print(f"❌ No file found matching '{path_or_name}'")
            return
        full_path = matches[0]
        if len(matches) > 1:
            print(f"Multiple matches, using first: {full_path}")
    
    result = prepare_note(full_path)
    tracking = load_tracking()
    tracking['sources'].append(result)
    save_tracking(tracking)
    
    print(f"✅ Prepared: {result['title']}")
    print(f"   Source: {result['source']}")
    print(f"   Output: {result['output']}")
    print(f"   Size: {result['size_lines']} lines, {result['size_bytes']:,} bytes")
    print(f"\n📋 Next step: Open notebooklm.google.com → New notebook → Add source → Upload '{result['output']}'")

def create_git_sync_script():
    """Create the companion git sync shell script for the output directory."""
    os.makedirs(os.path.dirname(GIT_SYNC_SCRIPT), exist_ok=True)
    content = """#!/bin/bash
# NotebookLM Sources — Git Sync
# Adds and commits any new/changed prepared sources
# Run after manually processing sources in NotebookLM

cd "$(dirname "$0")/.."
VAULT_DIR=$(pwd)
OUTPUT_DIR="$VAULT_DIR/11-Mess Hall/notebooklm-sources"

echo "=== NotebookLM Sources Sync ==="
echo "Vault: $VAULT_DIR"

# Check for changes
CHANGED=$(git status --short "$OUTPUT_DIR" 2>/dev/null | grep -c .)
if [ "$CHANGED" -eq 0 ]; then
  echo "No changes to sync."
  exit 0
fi

echo "Changes detected:"
git status --short "$OUTPUT_DIR"

git add "$OUTPUT_DIR"
git commit -m "notebooklm-sources: update prepared sources $(date +%Y-%m-%d)" --quiet
git push 2>&1 | tail -3

echo "Done."
"""
    with open(GIT_SYNC_SCRIPT, 'w') as f:
        f.write(content)
    os.chmod(GIT_SYNC_SCRIPT, 0o755)

if __name__ == "__main__":
    create_git_sync_script()
    
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    flags = set(a for a in sys.argv[1:] if a.startswith('--'))
    
    if '--help' in flags:
        print(__doc__)
        sys.exit(0)
    
    if '--status' in flags or '--list' in flags:
        show_status()
        sys.exit(0)
    
    if '--scan' in flags:
        show_scan()
        sys.exit(0)
    
    if '--all' in flags:
        print("=== NotebookLM Source Prepper ===\n")
        print("Scanning vault for candidates...")
        process_all()
        sys.exit(0)
    
    if args:
        for arg in args:
            print(f"=== Preparing: {arg} ===\n")
            process_single(arg)
        sys.exit(0)
    
    # Default: show status
    show_status()
