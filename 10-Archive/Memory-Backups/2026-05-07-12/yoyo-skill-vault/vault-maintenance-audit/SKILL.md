---
name: vault-maintenance-audit
category: vault
description: "Weekly vault health checks: orphaned files detection, empty folder cleanup, duplicate content analysis with whitelisting, naming convention enforcement, and daily log retention cleanup."
---

# Vault Maintenance Audit

**Systematic weekly health check for the Gentech vault — detect orphaned artifacts, structural issues, naming violations, and enforce retention policies.**

---

## When to Run

- **Scheduled:** Every Sunday as cron job
- **Ad-hoc:** After major agent migrations, archive imports, or integration sprints
- **Pre-audit:** Before quarterly reviews or security assessments
- **Post-cleanup:** Follow-up 24h after any mass deletion to catch leftovers

---

## Trigger Conditions

Any of these warrants an audit:
- Daily logs in `08-Daily/` exceed 5 files (retention buildup)
- `02-Labs/` or `03-Strategies/scripts/` contain `.tmp`/`.bak` files
- New zero-byte folders appear from aborted operations
- Memory-Backups directory grows >15% week-over-week
- Grep finds files with spaces/Unicode dashes outside `10-Archive/`

---

## Step-by-Step Procedure

### Phase 1 — Structure Inventory
```bash
cd /root/vaults/gentech
ls -d */  # verify all numbered folders present
find . -maxdepth 2 -type d | sort > /tmp/vault-structure.txt
```
Expected: `00-HQ/`, `00-System/`, `01-Agency/`, `01-Agents/`, `02-AAE/`, `02-Labs/`, `03-Projects/`, `03-Strategies/`, `04-Entertainment/`, `08-Daily/`, `10-Archive/`, `11-Mess Hall/`, etc.

### Phase 2 — Orphaned File Detection
Search for common temporary/backup patterns:
```bash
find "$VAULT" -type f \( \
  -name "*.tmp" -o -name "*.temp" -o -name "*.bak" -o -name "*.backup" \
  -o -name "*.swp" -o -name "*.swo" -o -name "*~" -o -name "*.orig" \
  -o -name "*.BASE" -o -name "*.LOCAL" -o -name "*.REMOTE" \)
```

**Action:** For each match:
- `grep -r "$(basename "$f")" . --include="*.md"` — check if referenced in docs
- If unreferenced → **delete**
- If referenced → note in report, consider moving to `00-Inbox/` for triage

### Phase 3 — Empty Folder Identification
```bash
find "$VAULT" -type d -empty -not -path "*/\\.*"
```

**Validation before deletion:**
```bash
folder="path/to/empty/folder"
grep -r "$folder" "$VAULT" --include="*.md" && echo "REFERENCED" || echo "SAFE TO DELETE"
```

Also check symlinks:
```bash
find "$VAULT" -type l -lname "*$folder*"
```

If no references and no symlinks → `rmdir "$folder"`

### Phase 4 — Duplicate Content Check (WITH WHITELIST)

**Step 1 — Hash all .md files:**
```bash
find "$VAULT" -type f -name "*.md" -size +100c -not -path "*/\\.*" \
  -exec sha256sum {} \; 2>/dev/null | sort > /tmp/hashes.txt
```

**Step 2 — Find collisions:**
```bash
awk '{print $1}' /tmp/hashes.txt | uniq -d > /tmp/dup_hashes.txt
grep -F -f /tmp/dup_hashes.txt /tmp/hashes.txt > /tmp/duplicates.txt
```

**Step 3 — Whitelist review** (critical step):

See `references/memory-backups-intentional-duplicates.md` for the exact whitelist criteria. In short:

✅ **EXEMPT** (do NOT delete):
- Files under `10-Archive/Memory-Backups/<timestamp>/` matching pattern `^(yoyo|dmob|desmond|gentech)-skills-.*\.md$`
- Identical files across agent workspaces that are part of DR snapshots
- Cross-referenced duplicates (if `grep -r` finds links between copies)

❌ **DELETE** (true duplicates):
- Two `README.md` files with same content in different project folders (unless one is archived)
- Copy-pasted spec documents that diverged but accidentally re-converged
- Duplicate meeting notes with different filenames but identical content

**Decision:** If duplicate set size ≥3 and prefix pattern matches agent names → **whitelist**. Log in report under "Intentional Duplicates" but take no action.

### Phase 5 — Naming Convention Audit

**Problematic patterns to flag:**
```bash
# Spaces in filenames (bother some tools)
find "$VAULT" -type f -name "* *" | grep -v "^$VAULT/10-Archive"

# Em dashes (—) and curly quotes (' '"")
find "$VAULT" -type f -name "*—*" -o -name "*’*" -o -name "*"*""
```

**Exception:** `10-Archive/` is append-only historical record — do NOT rename, even if naming violates current conventions.

**Action for violations:**
- Create rename suggestion: `mv "file name.md" "file-name.md"`
- Use git to preserve history: `git mv "old name.md" "new-name.md"`
- Update any wiki-links if doing a mass rename (separate PR)

### Phase 6 — Daily Log Retention Cleanup

**Scope:** Direct child files of `/08-Daily/` matching `YYYY-MM-DD.md`
**Protected subdirs (NOT touched):** `Daily-Summaries/`, `2026-Weekly/`, `Monthly-Summaries/`, `Reviews/`, `agent-states/`, `content-drafts/`, `cron-changes/`

**Preferred method — mtime-based:**
```bash
cd "$VAULT/08-Daily"
find . -maxdepth 1 -type f -name "*.md" -mtime +7 -print  # review
find . -maxdepth 1 -type f -name "*.md" -mtime +7 -delete  # delete
```

**Alternative — filename date comparison** (if files are never manually touched):
```bash
CUTOFF=$(date -d "7 days ago" +%Y-%m-%d)
find . -maxdepth 1 -type f -name "*.md" | while read f; do
  fdate=$(basename "$f" .md)
  [[ "$fdate" < "$CUTOFF" ]] && echo "DELETE: $f"
done
```

**Verification:**
```bash
echo "Remaining daily logs:"
ls -1 *.md  # should show only last 7 days
```

### Phase 7 — Verification & Reporting

**Post-cleanup counts:**
```bash
echo "Temp files remaining:" $(find "$VAULT" -type f \( -name "*.tmp" -o -name "*.bak" \) | wc -l)
echo "Empty folders remaining:" $(find "$VAULT" -type d -empty -not -path "*/\\.*" | wc -l)
echo "Daily logs >7d old:" $(find "$VAULT/08-Daily/" -maxdepth 1 -type f -name "*.md" -mtime +7 | wc -l)
```

**Report template** (save to `00-HQ/Vault-Audit-$(date +%Y-%m-%d)-Report.md`):
See `templates/vault-audit-report.md`.

---

## Pitfalls

### Pitfall 1 — Deleting Intentional Memory-Backup Duplicates
**Symptom:** Hash collision detection flags 1000+ files in `10-Archive/Memory-Backups/` as duplicates across `desmond-`, `dmob-`, `yoyo-`, `gentech-` prefixes.

**Cause:** Agent DR snapshots intentionally distribute identical skill docs to each agent's namespace for isolation/backup.

**Fix:** Add whitelist pattern: `10-Archive/Memory-Backups/*/^(yoyo|dmob|desmond|gentech)-skills-*.md` → exempt from duplicate deletion. These are **features**, not bugs.

### Pitfall 2 — Daily Log Deletion by Name vs Mtime
**Symptom:** Deleting `2026-04-30.md` because filename is >7 days old, but file was just copied today (mtime is fresh).

**Cause:** Using filename date instead of filesystem modification time.

**Fix:** Always prefer `-mtime +7` (actual age) over filename parsing. If you must use filenames, cross-check with `stat`:
```bash
stat -c %Y "$f"  # mtime epoch
stat -c %y "$f"  # human-readable mtime
```

### Pitfall 3 — Empty Folder with Hidden References
**Symptom:** Deleting an "empty" directory that is:
- Symlinked from elsewhere in vault
- Referenced in a cron job script
- Mentioned in a spec as a future workspace

**Fix:** Three checks before `rmdir`:
1. `grep -r "folder_name" "$VAULT" --include="*.md" --include="*.yaml" --include="*.py"`
2. `find "$VAULT" -type l -lname "*folder_name*"`
3. `grep -r "cron" "$VAULT" --include="*.json" | grep "folder_name"`

Only delete if all three return empty.

### Pitfall 4 — Archive Renaming Breaks Historical Links
**Symptom:** Renaming `Chat — 2026-04-19.md` to `Chat-2026-04-19.md` in `10-Archive/` breaks cross-links in old handoff docs.

**Cause:** Archive is append-only; renaming is destructive to historical context.

**Fix:** Never rename archived content. If broken link is discovered, create a redirect note instead. Leave archive filenames as-is; fix only live documents linking to them.

### Pitfall 5 — Missing Protected Subdirs in Daily Cleanup
**Symptom:** `find ... -delete` removes files inside `Daily-Summaries/` or `agent-states/` subdirectories of `08-Daily/`.

**Cause:** Using `-mindepth 1` without excluding known protected subdirectories.

**Fix:** Two safeguards:
1. `-maxdepth 1` restricts to direct children only (protects all subdirs)
2. Double-check with `ls -R 08-Daily/` before deletion to enumerate subdir structure

---

## Verification Checklist

- [ ] Temp files (`.tmp`, `.bak`, `*.swp`) removed from active dirs
- [ ] Empty folders verified unreferenced before deletion
- [ ] Duplicate detection run with Memory-Backups whitelist applied
- [ ] Naming violations only flagged outside `10-Archive/`
- [ ] Daily log cleanup used `-mtime +7` (mtime, not filename date)
- [ ] Protected subdirs excluded from deletion
- [ ] Report written and saved to `00-HQ/`

---

## Related Skills

- `vault-staleness-audit` — Content freshness, not structural health
- `vault-reorganization` — Major restructures, not weekly maintenance
- `vault-daily-rotation` — Daily log rotation (rotation, not cleanup)
- `handoff-reporting` — Report generation patterns (similar output format)

---

## Quick Reference Card

```
Weekly vault audit sequence:
1. Inventory structure → confirm all numbered folders present
2. Find temp/backup files → delete if orphaned
3. Find empty dirs → grep for refs → rmdir if safe
4. Hash .md files → compare → WHITELIST Memory-Backups/*/agent-skills-*.md
5. Naming scan → skip 10-Archive/ → flag others
6. Daily logs: find -mtime +7 -maxdepth 1 → review → delete
7. Write report → 00-HQ/Vault-Audit-YYYY-MM-DD-Report.md
```

---

## Change Log

- **2026-05-03** — Initial skill created from weekly audit session; added whitelist pattern for Memory-Backups after discovering intentional agent-prefixed duplicates
