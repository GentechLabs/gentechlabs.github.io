---
name: obsidian
description: Read, search, create notes, and sync Obsidian vaults (including headless).
---

# Obsidian Vault

## Vault location
Set via environment variable or detect from system. Always quote paths with spaces.

## Read a note
```bash
cat "$VAULT/Note Name.md"
```

## List notes
```bash
find "$VAULT" -name "*.md" -type f        # all notes
ls "$VAULT/Subfolder/"                     # specific folder
```

## Search
```bash
find "$VAULT" -name "*.md" -iname "*keyword*"   # by filename
grep -rli "keyword" "$VAULT" --include="*.md"    # by content
```

## Create / Append
```bash
cat > "$VAULT/New Note.md" << 'ENDNOTE'
# Title
Content here.
ENDNOTE

echo "\nNew content." >> "$VAULT/Existing.md"
```

## Wikilinks
Obsidian links notes with `[[Note Name]]` syntax. Use these when creating linked notes.

## Headless Sync (obsidian-headless CLI)
For syncing vaults to headless servers. Requires Obsidian Sync subscription.

Key commands:
- `ob login` — authenticate (supports `--email`, `--password`, `--mfa` flags)
- `ob sync-list-remote` — list remote vaults
- `ob sync-setup --vault "Name"` — link local dir to remote vault
- `ob sync` — one-time sync
- `ob sync --continuous` — continuous sync
- `ob sync-list-local` — list local vault configs
- `ob sync-create-remote --name "Name"` — create new remote vault

Notes: Do NOT mix desktop Sync and Headless Sync on same device. E2E vaults need password on setup.
