# Sumplus Arsenal — API Credentials

**Date:** 2026-05-09
**Status:** Active

## Account
- **Email:** [REDACTED_EMAIL]
- **Password:** [REDACTED_PASSWORD]
- **User ID:** 55a5dc77-6fc5-41b6-81fd-3db52f61de90

## API Key
```
[REDACTED_API_KEY]
```

## Base URL
```
https://arsenal.sumplus.xyz
```

## Usage
```bash
curl -X POST "https://arsenal.sumplus.xyz/api/execute" \
  -H "Authorization: Bearer [REDACTED_API_KEY]" \
  -H "Content-Type: application/json" \
  -d '{
    "skill_id": "<skill-id>",
    "input": { "action": "<action>", ... }
  }'
```

## Verified Skills
- ✅ Jupiter Aggregator (Solana) — quotes work
- ✅ DefiLlama — TVL queries work

## Notes
- API key is permanent (no expiry)
- Skills list is public, execution requires auth
- Some skills are Arsenal-hosted (they run the infrastructure)
