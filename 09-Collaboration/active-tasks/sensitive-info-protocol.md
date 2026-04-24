# 🔒 Sensitive Information Protocol

**Added:** 2026-04-17
**Status:** Active

## Rule
If you receive sensitive information (API keys, credentials, passwords, tokens):
1. **Use it** for the task at hand
2. **Pass it** to the agent who needs it (via Labs/Direct, not vault files)
3. **Scrub it** — remove from any files, notes, or logs immediately after use
4. **Confirm** — mark the task done only after scrubbing

## What Counts as Sensitive
- API keys
- Passwords
- Auth tokens
- Private wallet keys
- Personal identification info
- Anything Jordan wouldn't want in a shared file

## Where NOT to Store
- ❌ Obsidian vault (synced, potentially shared)
- ❌ Green room / mess hall files
- ❌ Handoff board entries
- ❌ Cron job prompts

## Where TO Store (if needed)
- ✅ Agent memory (personal, not shared)
- ✅ Temporary terminal variables (cleared after use)
- ✅ Ask Jordan to provide directly when needed

## Vault Scrub Check
During nightly vault maintenance, scan for:
- Patterns matching API keys (long alphanumeric strings)
- Passwords or tokens in markdown files
- URLs with embedded credentials
- Flag and remove any found
