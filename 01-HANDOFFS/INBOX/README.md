# 📥 Group Inboxes — Delegation & Handoff

Clean group-to-group handoff. **Anyone can drop a note into any group's inbox.**
This is the delegation board Jordan reads to see every handoff and where it's going.

## Layout
```
01-HANDOFFS/INBOX/<group>/
    <YYYY-MM-DD>-<topic>.md    ← a handoff note for that group
    _archive/                  ← resolved notes (auto-moved, purged weekly)
```

## Groups
- **hq** — coordination, decisions, blockers (Gentech's home = this HQ)
- **forge** — desktop dev workbench
- **labs** — build/code work
- **entertainment** — content, social, arcade
- **treasury** — finance, DeFi, portfolio, yield (consolidated from "strategies"/"finance" Aug 12)
- **gizmo** — Labs bot

## Protocol
1. **Send:** write `<date>-<topic>.md` into the target group's inbox folder.
   Format below. Commit + push (or `ob sync`).
2. **Read:** each group's wake-up / morning digest reads its inbox.
   Gentech reads ALL inboxes every morning and surfaces anything unaddressed.
3. **Resolve:** when addressed, tick the checkbox `- [x]` and move the file to
   `_archive/` (or delete). 
4. **Purge:** nightly maintenance wipes `_archive/` entries older than 7 days.

## Note format
```markdown
# <topic>
**From:** <agent/group>
**To:** <group>
**Date:** <YYYY-MM-DD>
**Status:** open | [x] resolved

## What's needed
<what the receiving group should do>

## Context / files
<any links or paths>
```
