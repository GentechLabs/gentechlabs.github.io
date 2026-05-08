---
name: obsidian
description: Read, search, and create notes in the Obsidian vault.
---

# Obsidian Vault

**Location:** Set via `OBSIDIAN_VAULT_PATH` environment variable (e.g. in `~/.hermes/.env`).

If unset, defaults to `~/Documents/Obsidian Vault`.

Note: Vault paths may contain spaces - always quote them.

## Read a note

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"
cat "$VAULT/Note Name.md"
```

## List notes

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"

# All notes
find "$VAULT" -name "*.md" -type f

# In a specific folder
ls "$VAULT/Subfolder/"
```

## Search

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"

# By filename
find "$VAULT" -name "*.md" -iname "*keyword*"

# By content
grep -rli "keyword" "$VAULT" --include="*.md"
```

## Create a note

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"
cat > "$VAULT/New Note.md" << 'ENDNOTE'
# Title

Content here.
ENDNOTE
```

## Append to a note

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"
echo "
New content here." >> "$VAULT/Existing Note.md"
```

## Wikilinks

Obsidian links notes with `[[Note Name]]` syntax. When creating notes, use these to link related content.

## Deliverable Documentation Pattern (GenTech)

When producing work products for Jordan or team delivery, use the **triple-file pattern** for complete traceability:

**1. Analysis/Technical Note** → `00-HQ/Operations/{Topic}-{Date}.md`
- What was done, why, technical findings, metrics
- Frontmatter: `status: analysis-complete | cleanup-deferred | etc.`

**2. Script/Template** → `00-HQ/Operations/{Topic}-Instagram-Script.md` (if applicable)
- Exact text/script used for content generation
- Preserve style notes and timing considerations

**3. Delivery Log** → `00-HQ/Operations/{Topic}-Audio-Delivery-{Date}.md`
- What was sent, to whom, file paths, provider used, any issues
- Metadata: duration, format, recipient group, vault cross-references

**Cross-link all three** with `[[Note Name]]` wikilinks back to each other.

This pattern used in: `social-media-audio-content` skill, and any deliverable requiring audit trail.

---

[{'from-10-Archive/collateral/CG-hackathon-submission.md': "FOLDERS':", "Name': 'key to safe archiving.\n\n### Safety Pitfalls', 'Telegram security filter blocks variation selector characters', 'must be stripped or avoid emoji when writing to files that may be piped to shell commands. Use plain text in terminal outputs.\n\n### Schema Variant Detection',": "AND': 'Otherwise fall back to a Python-first discovery scan to map the actual vault structure before applying cleanup rules.\n\n### Python-First Scanning Pattern'", 'Proof-Concept Pattern': 'often more reliable than bash for complex age/glob scans, especially when dealing with spaces or large trees.\n\n```python\nimport os', 'from datetime import datetime': 'datetime', '# Example: find files older': '>",', '08-Daily\', \'nfor root, dirs, files in os.walk(folder):\n    for f in files:\n        fp = os.path.join(root, f)\n        try:\n            mtime = datetime.fromtimestamp(os.path.getmtime(fp))\n            if (datetime.now() - mtime).total_seconds() > 24*3600:\n                print(os.path.relpath(fp, VAULT))\n        except:\', \'pass\n```\n\n### Delivery Pattern\', \'Use the **triple-file pattern** for complete traceability:\n\n**1. Analysis/Technical Note** → `00-HQ/Operations/{topic}-{date}.md` (alternatives: `03-Projects/` or project folder)\n- What was done, why, technical findings, metrics\n- Frontmatter:```yaml\nstatus: analysis-complete | cleanup-deferred | etc.\n```\n\n**2. Script/Template** → `00-HQ/Operations/{topic}-<tool>-script.md`\n- Exact text/script used for content generation\n- Preserve style notes and timing considerations\n\n**3. Delivery Log** → `00-HQ/Operations/{topic}-delivery-{date}.md`\n- What was sent, to whom, file paths, provider used, any issues\n- Metadata: duration, format, recipient group, vault cross-references\n\n**Cross-link all three** with `[[Note Name]]` wikilinks back to each other.\n\nThis pattern is used in: `social-media-audio-content` skill, and any deliverable requiring audit trail.\n\n---\n\n## Vault Sweep Protocol\', \'Gentech uses a custom schema; do not assume standard folder names. Before running sweep tasks:\n\n1. Scan top-level to inventory actual folders (e.g., `ls -1`).\n2. Map equivalent semantics ("Temp" may be "08-Daily"; "Archive" may be "10-Archive" or "12-Archive").\n3. Adjust scripts to use discovered paths; if mapping unclear, default to Python-first scanning with age thresholds.\n\n4. Safe Archiving (DO NOT DELETE):\n- Move processed items from inbox-like folders (>7 days) to `12-Archive/` (or vault equivalent).\n- Move temp-area items (>24h) to archive.\n- Preserve history; empty archives are fine.\n\n5. Report should be written to the Mess Hall folder (`11-Mess Hall/`) with a dated filename.\n\n---\n\n## Notes on Vault Org\',': "ame'-level folder (e.g.", 'flexibility': 'vaults may use custom top-level folders; rely on semantic mapping'}]
