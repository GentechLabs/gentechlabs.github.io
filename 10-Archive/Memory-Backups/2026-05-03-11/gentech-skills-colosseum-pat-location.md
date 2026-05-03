# Colosseum Copilot PAT — Gentech Organization

**Location:** `~/.hermes/scripts/colosseum-config.json` (DMOB's profile)  
**Username:** ProtoJay4789 (Jordan Jones)  
**Scope:** `colosseum_copilot:read`  
**Expires:** ~2026-07-27 (90 days from Apr 28, 2026)  
**API Base:** `https://copilot.colosseum.com/api/v1`

## Usage

When running Colosseum Copilot as DMOB, the PAT is automatically available in your environment via the `colosseum-config.json` file. The `colosseum-resources` skill and `colosseum-copilot` skill will use it for authenticated API calls.

**Pre-flight check (required):**
```bash
export COLOSSEUM_COPILOT_PAT=$(jq -r .token ~/.hermes/scripts/colosseum-config.json)
curl -s "https://copilot.colosseum.com/api/v1/status" -H "Authorization: Bearer $COLOSSEUM_COPILOT_PAT"
```

For other agents: Coordinate with DMOB to run Copilot queries or request temporary access.

## Related Infrastructure

DMOB maintains the `security-contest-monitoring` skill which includes a daily cron scanning:
- Devpost (hackathons)
- Code4rena (audit competitions)
- Cantina (bug bounties)
- Colosseum (Solana hackathons)

This scanner populates the `02-Labs/Contest-Scan-YYYY-MM-DD.md` reports. These reports should be integrated into the vault via the `hackathon-tracker` workflow.
