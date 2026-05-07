# Vault Scan Commands — Quick Reference

These are the core terminal commands used by the `handoff-reporting` skill to gather vault state.

## Daily Logs
```bash
# List recent daily logs
find /root/vaults/gentech/08-Daily/ -type f -name '*.md' | sort
```

## Mess Hall (Team Discussions)
```bash
# This week's Mess Hall files (auto-calculated)
YEAR=$(date +%Y)
WEEK=$(date +%V)
find /root/vaults/gentech/11-Mess\ Hall/$YEAR/W$WEEK/ -type f -name '*.md' | sort

# Search Mess Hall for pending/approval keywords
grep -r -i "pending approval\|awaiting jordan\|\[ \]\|todo" /root/vaults/gentech/11-Mess\ Hall/ --include='*.md' | head -20
```

## Green Room (Cross-Team Handoffs)
```bash
# Active handoffs (current)
find /root/vaults/gentech/09-Green\ Room/active-handoffs/ -type f -name '*.md'

# Top-level Green Room notes (open questions, debates)
find /root/vaults/gentech/09-Green\ Room/ -maxdepth 1 -type f -name '*.md' | sort
```

## Approvals (Jordan Sign-Off)
```bash
# This week's approval files
find /root/vaults/gentech/00-HQ/Approvals/ -type f -name '*.md' -newermt "$(date --date='-7 days' +%Y-%m-%d)" | sort
```

## Keyword Searches (Vault-Wide)
```bash
# Pending items and checkboxes
grep -r -i "pending approval\|awaiting jordan\|\[ \]\|todo\|to do" /root/vaults/gentech --include='*.md' 2>/dev/null | head -50

# Blocked items
grep -r -i "blocked\|waiting on\|blocking" /root/vaults/gentech --include='*.md' 2>/dev/null | head -30
```

## Recent Activity
```bash
# Files modified in last 2 hours (code or notes)
find /root/vaults/gentech -type f \( -name '*.md' -o -name '*.py' \) -mmin -120 2>/dev/null

# Files created today
find /root/vaults/gentech -type f -newermt "$(date +%Y-%m-%d)" 2>/dev/null

# Modified in last 24 hours (by day boundary)
find /root/vaults/gentech -type f -mtime -1 2>/dev/null | head -20
```

## Frontmatter Extraction (jq if installed)
```bash
# Extract titles and status from markdown frontmatter
grep -r "^---$" /root/vaults/gentech --include='*.md' -l | while read f; do
  awk '/^---$/{if (p) exit; p=1; next} p && /^[a-z]+:/ {print FILENAME " — " $0}' "$f"
done
```

## Notes
- Escape spaces in paths (`11-Mess\ Hall/`) or quote them.
- Suppress errors with `2>/dev/null` to keep output clean.
- Use `head -N` to limit results for manual review; remove for full dump.
- `date +%V` gives ISO week number (W18 for May). Adjust if your week starts Monday vs Sunday.