# Colosseum Copilot API — Frontier Track Discovery (DMOB Labs)

## Purpose
Use Colosseum's read-only Copilot API to enumerate active Frontier competition tracks and their prize breakdowns without logging into the arena dashboard.

## Authentication

### Token Location
- **Primary:** `/root/vaults/gentech/00-HQ/Credentials/colosseum-copilot-token.md`
- **Runtime:** `/root/vaults/gentech/00-HQ/config/colosseum-copilot-token.txt`

Token format: JWT (starts with `eyJhbG...`). Scope: `colosseum_copilot:read` (read-only).

### Token Lifetime
- Issued: ~90-day expiry
- Current token (as of 2026-05-02) may be expired/masked; regeneration required at `https://arena.colosseum.org/copilot`

### Usage
```bash
export COLOSSEUM_COPILOT_API_BASE="https://copilot.colosseum.com/api/v1"
export COLOSSEUM_COPILOT_PAT=$(cat /root/vaults/gentech/00-HQ/config/colosseum-copilot-token.txt)

# Pre-flight check
curl -s "$COLOSSEUM_COPILOT_API_BASE/status" \
  -H "Authorization: Bearer $COLOSSEUM_COPILOT_PAT"
# Expected: {"authenticated": true, "expiresAt": "...", "scope": "..."}
```

## Endpoints

### 1. Get Filters (Hackathons + Clusters)
```bash
curl -s "$COLOSSEUM_COPILOT_API_BASE/filters" \
  -H "Authorization: Bearer $COLOSSEUM_COPILOT_PAT"
```

**Response structure:**
```json
{
  "hackathons": [
    {
      "name": "Solana Frontier",
      "slug": "solana-frontier-2026",
      "phase": "active",
      "startDate": "2026-04-28",
      "endDate": "2026-05-11"
    }
    // ... up to 5 active tracks per Frontier
  ],
  "clusters": [ ... ]
}
```

Filter by `name` containing "Ignition" or "Frontier" or "Solana".

### 2. Search Projects (Track-specific submissions)
Once you have the hackathon `slug`:

```bash
curl -s -X POST "$COLOSSEUM_COPILOT_API_BASE/search/projects" \
  -H "Authorization: Bearer $COLOSSEUM_COPILOT_PAT" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "agent",
    "hackathonSlug": "solana-frontier-2026",
    "limit": 20
  }'
```

Returns past projects in that track — useful for competitive analysis, not for current prize pool.

### 3. Get Project Details by Slug
```bash
curl -s "$COLOSSEUM_COPILOT_API_BASE/projects/by-slug/mcpay" \
  -H "Authorization: Bearer $COLOSSEUM_COPILOT_PAT"
```

## Integration Into Scanner

Update `opportunity_scanner_daily.py`:

```python
def scan_colosseum_via_copilot():
    token = (VAULT / "00-HQ/config/colosseum-copilot-token.txt").read_text().strip()
    base = "https://copilot.colosseum.com/api/v1"
    # 1. Get filters
    resp = requests.get(f"{base}/filters", headers={"Authorization": f"Bearer {token}"})
    data = resp.json()
    frontier = [h for h in data["hackathons"] if "frontier" in h["name"].lower()]
    
    contests = []
    for track in frontier:
        # Each track typically maps to a Devpost microsite; extract from track metadata or fall back to cached mapping
        contests.append({
            "platform": "Colosseum",
            "name": f"Solana Frontier — {track['name']}",
            "prize": "TBD (see IGNITION $5.12M total)",  # can refine after parsing track card
            "days_left": days_remaining(track.get("endDate","TBD")),
            "deadline": track.get("endDate","TBD"),
            "chain": "Solana",
            "link": f"https://arena.colosseum.org/hackathon",
        })
    return contests
```

## PAT Regeneration (When 401/UNAUTHORIZED)

1. Log into `arena.colosseum.org` with Jordan's account (ProtoJay4789)
2. Navigate to **Settings → Developer → Personal Access Tokens**
3. Generate new token with `colosseum_copilot:read` scope
4. Overwrite both credential files:
   - `/root/vaults/gentech/00-HQ/Credentials/colosseum-copilot-token.md`
   - `/root/vaults/gentech/00-HQ/config/colosseum-copilot-token.txt`
5. Update `COLOSSEUM_COPILOT_PAT` in environment if set in cron context

## Pitfalls
- Token expiry ~90 days; schedule monthly refresh check
- API base URL is `copilot.colosseum.com`, NOT `arena.colosseum.org`
- Some endpoints require `POST` with JSON body (search); `GET` for filters/status
- Rate limit: unspecified; throttle to ≤1 request/sec

## Related
- Sprint plan: `02-Labs/sprint-plan-solana-frontier-kite-ai.md` (Frontier submission task)
- Scanner script: `02-Labs/scripts/opportunity_scanner_daily.py` (integration point)
- Token docs: `00-HQ/Credentials/colosseum-copilot-token.md`
