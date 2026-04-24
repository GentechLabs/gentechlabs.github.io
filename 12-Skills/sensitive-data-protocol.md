# Sensitive Data Protocol

**Added:** Apr 17, 2026
**Status:** Active — all agents must follow

## The Rule

When handling sensitive information (API keys, secrets, credentials, PII):

1. **Receive** — get the sensitive data
2. **Use** — apply it where needed (config, setup, etc.)
3. **Scrub** — remove it from ALL files within the same session
4. **Verify** — confirm no traces remain in vault, logs, or temp files

## What Counts as Sensitive

- API keys and tokens
- Passwords and secrets
- Personal identifying information (PII)
- Financial information
- Private wallet addresses / seed phrases
- Any data Jordan flags as sensitive

## Where to Check

| Location | Action |
|----------|--------|
| Obsidian vault (all .md files) | Search and remove |
| /tmp/ files | Delete after use |
| Config files | Keep key in config only, don't duplicate |
| Mess Hall / Green Room | Never log sensitive data |
| Git history | Don't commit secrets (use .env) |

## Scrub Command

After handling sensitive data, run this check:

```bash
# Search vault for API key patterns
grep -rn "api_key\|token\|secret\|password\|sk_\|pk_" "/root/Documents/Obsidian Vault/" 2>/dev/null

# Search temp files
grep -rn "api_key\|token\|secret" /tmp/*.txt /tmp/*.md 2>/dev/null
```

## Exceptions

- Config files (~/.hermes/config.yaml) — keys stay here, this is their home
- .env files — keys stay here, this is their home
- Everything else — scrub immediately

## Vault Manager Integration

The vault manager cron job now includes a sensitive data scan that flags any secrets found outside config/.env files.
