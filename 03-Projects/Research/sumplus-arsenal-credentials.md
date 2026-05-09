# Sumplus Arsenal — API Credentials

**Date:** 2026-05-09
**Status:** Active

## Account
- **Email:** gentech-deploy@gentech.ai
- **Password:** GenTech2026!
- **User ID:** 55a5dc77-6fc5-41b6-81fd-3db52f61de90

## API Key
```
52e3a628193374bf7717ccfb01c04f9017bddc85c56e9b9eeadf869f07edc199
```

## Base URL
```
https://arsenal.sumplus.xyz
```

## Usage
```bash
curl -X POST "https://arsenal.sumplus.xyz/api/execute" \
  -H "Authorization: Bearer 52e3a628193374bf7717ccfb01c04f9017bddc85c56e9b9eeadf869f07edc199" \
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
