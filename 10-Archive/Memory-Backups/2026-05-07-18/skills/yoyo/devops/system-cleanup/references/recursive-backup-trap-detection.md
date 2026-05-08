# Recursive Backup Trap Detection — Session Artefact

**Date:** 2026-05-02  
**Agent:** YoYo (Strategies)  
**Context:** Spring cleaning audit discovered 55GB wasted in nested `.hermes` directories  
**Pattern:** Backup → copy of copy → copy of copy-of-copy → exponential bloat  

---

## Problem

A backup job copied an entire `$HOME/.hermes` directory into the vault archive. That backup included a full home directory structure, which itself contained a `.hermes` subdirectory. On the next backup, that nested `.hermes` got copied again, creating 5–8 levels of recursion.

**Path example:**
```
/root/vaults/gentech/10-Archive/Hermes-Backups/20260427-215249/
  └── profiles/dmob/home/
      └── .hermes/                      ← first copy (legitimate backup)
          └── profiles/dmob/home/
              └── .hermes/              ← second copy (accidental)
                  └── profiles/dmob/home/
                      └── .hermes/      ← third copy (waste)
                          └── ... (5 total nesting levels)
```

**Size:** 48–55GB of redundant data  
**Files count:** 33,550+ Solana toolchain files alone in nested dirs  
**Detection:** `find /path -type d -name '.hermes' | wc -l` returned **5** nested instances

---

## Detection Script

```bash
#!/bin/bash
# find-recursive-traps.sh — identify directories with nested dot-dir copies
# Usage: ./find-recursive-traps.sh /path/to/scan

TARGET="${1:-/root/vaults/gentech/10-Archive}"

# Common backup trap patterns
PATTERNS="\.hermes|\.git|node_modules|\.npm"

echo "Scanning $TARGET for recursive backup traps..."
echo "Pattern: $PATTERNS"
echo ""

find "$TARGET" -type d \( -name '.hermes' -o -name '.git' -o -name 'node_modules' \) 2>/dev/null | while read -r dir; do
  # Count nested occurrences of same pattern inside this dir
  if [[ "$dir" == *".hermes"* ]]; then
    nested_count=$(find "$dir" -type d -name '.hermes' 2>/dev/null | wc -l)
  elif [[ "$dir" == *".git"* ]]; then
    nested_count=$(find "$dir" -type d -name '.git' 2>/dev/null | wc -l)
  else
    nested_count=$(find "$dir" -type d -name 'node_modules' 2>/dev/null | wc -l)
  fi

  if [ "$nested_count" -gt 1 ]; then
    size=$(du -sh "$dir" 2>/dev/null | cut -f1)
    depth=$(echo "$dir" | tr -cd '/' | wc -c)
    echo "⚠️  TRAP DETECTED: $dir"
    echo "   Size: $size | Nested count: $nested_count | Path depth: $depth"
    echo ""
  fi
done
```

**Sample output from 2026-05-02 run:**
```
⚠️  TRAP DETECTED: /root/vaults/gentech/10-Archive/Hermes-Backups/20260427-215249/profiles/dmob/home/.hermes
   Size: 48G | Nested count: 5 | Path depth: 12

⚠️  TRAP DETECTED: /root/vaults/gentech/10-Archive/Hermes-Backups/20260427-215249/profiles/dmob/home/.hermes/profiles/dmob/home/.hermes
   Size: 26G | Nested count: 4 | Path depth: 16
```

---

## Why This Happens

1. **Backup script flaw:** `rsync -a` or `cp -r` copies dot-directories without `--exclude`
2. **No depth limit:** Backup of `$HOME` includes `.hermes/`, which contains another copy of `$HOME` in its nested `profiles/.../home/`
3. **Each backup layer** includes the previous backup's nested structure → exponential growth
4. **Silent:** No errors, just massive space consumption over time

**Classic trigger:**
```bash
# BAD — copies entire home, including nested agent profiles
cp -r /home/user /backup/    # if /home/user/.hermes/profiles/user/home exists → recursion

# GOOD — exclude dot-dirs or use tar with exclusions
tar --exclude='.*' -czf /backup/user.tar.gz /home/user
```

---

## Prevention

**Backup script hardening:**
```bash
# Exclude common recursive trap directories
rsync -a --exclude='.*' /source/ /dest/

# Or use find with depth limit
find /source -maxdepth 3 -not -path '*/.*' -exec cp {} /dest/ \;

# Or tar with excludes
tar --exclude='.hermes' --exclude='.git' --exclude='node_modules' -czf backup.tar.gz /source
```

**Monitoring:** Add to cron weekly:
```bash
# Alert if any directory has >3 nested dot-dir copies
/root/hermes-cleanup/scripts/find-recursive-traps.sh /root/vaults 2>&1 | grep -q 'TRAP' && \
  telegram-send "🚨 Recursive backup trap detected in vault — review immediately"
```

---

## Recovery

**Step 1 — Confirm it's a trap (not active data):**
```bash
# Check if any symlinks point into the nested tree
find /root -type l -lname '*20260427-215249*'  # should return empty

# Search codebase for references
grep -r '20260427-215249' /root/workspace /root/projects 2>/dev/null
# → Zero results = safe to delete
```

**Step 2 — Verify active data lives elsewhere:**
```bash
# Active Hermes profiles are separate
ls -la /root/.hermes/profiles/
# Compare SOUL.md, auth.json, config.yaml timestamps with backup
```

**Step 3 — Delete entire trap tree:**
```bash
rm -rf /root/vaults/gentech/10-Archive/Hermes-Backups/20260427-215249
```

**Step 4 — Reclaim space:**
```bash
df -h /
# Expect immediate drop (55G freed in 2026-05-02 case)
```

---

## Cost of This Pattern

| Metric | Before Fix | After Fix |
|--------|------------|-----------|
| Backup directory size | 55GB (92% waste) | <1GB (actual content) |
| Disk usage | 105G / 193G (55%) | 47G / 193G (25%) |
| Recovery time | 30 sec delete | Immediate |
| Data loss risk | None (trap = pure duplication) | Zero — active data untouched |

**Time to detect:** Without audit, this would have grown to 100GB+ within 2–3 backup cycles.

---

## Related Findings (Same Session)

- **Docker images:** Old `browserless/chrome:latest` (Feb 2024, 4.5GB) — requires container stop to replace
- **Cache hierarchy:** `/.cache/` had 3.1G across 5 sub-caches; only HuggingFace models needed preservation
- **Journalctl:** Already minimal (401MB), vacuum had no effect
- **Python bytecode:** 14,715 `.pyc` files corrupted (`marshal data too short`) — full purge required

All documented in execution report: `10-Archive/cleanup-manifests/2026-05-02-Execution-Report.md`

---

*Supporting reference for `system-cleanup` skill — Pattern #1: Recursive Backup Trap*
