---
name: colosseum-copilot-research
description: "Research Solana/crypto startup competitors and market landscape using Colosseum Copilot API. Search 5,400+ hackathon projects, analyze clusters, and compile competitive intelligence reports."
tags: [solana, crypto, competitive-research, colosseum, hackathon, market-intel, api]
triggers:
  - Researching competitors in a Solana/crypto space
  - Analyzing market landscape for a startup idea
  - Using Colosseum Copilot API for project search
  - Checking what's been built in a specific vertical
  - Finding gaps in existing Solana project ecosystem
  - Competitive analysis for hackathon positioning
  - Searching hackathon project database
---

# Colosseum Copilot Research

Use the Colosseum Copilot API to research competitors, analyze market landscape, and find gaps in the Solana/crypto startup ecosystem.

## Authentication Setup

### Token Storage
- Store PAT at: `/root/.hermes/profiles/desmond/config/colosseum-copilot-token.txt`
- Get token from: https://arena.colosseum.org/copilot

### Environment Variables
```bash
export COLOSSEUM_COPILOT_API_BASE="https://copilot.colosseum.com/api/v1"
export COLOSSEUM_COPILOT_PAT=$(cat /root/.hermes/profiles/desmond/config/colosseum-copilot-token.txt)
```

### Pre-Flight Auth Check
```bash
curl -s "$COLOSSEUM_COPILOT_API_BASE/status" \
  -H "Authorization: Bearer $COLOSSEUM_COPILOT_PAT"
# Expected: { "authenticated": true, "expiresAt": "...", "scope": "..." }
```

## API Endpoints

### Search Projects
```bash
curl -s -X POST "$COLOSSEUM_COPILOT_API_BASE/search/projects" \
  -H "Authorization: Bearer $COLOSSEUM_COPILOT_PAT" \
  -H "Content-Type: application/json" \
  -d '{"query": "AI agent payments", "limit": 10}'
```

**Optional filters:**
```json
{
  "query": "MCP tool monetization",
  "limit": 10,
  "filters": {
    "winnersOnly": true,
    "acceleratorOnly": true
  }
}
```

### Get Project Details by Slug
```bash
curl -s "$COLOSSEUM_COPILOT_API_BASE/projects/by-slug/mcpay" \
  -H "Authorization: Bearer $COLOSSEUM_COPILOT_PAT"
```

### Search Archives
```bash
curl -s -X POST "$COLOSSEUM_COPILOT_API_BASE/search/archives" \
  -H "Authorization: Bearer $COLOSSEUM_COPILOT_PAT" \
  -H "Content-Type: application/json" \
  -d '{"query": "agent payment infrastructure", "limit": 5}'
```

### Get Filters (Hackathons, Clusters)
```bash
curl -s "$COLOSSEUM_COPILOT_API_BASE/filters" \
  -H "Authorization: Bearer $COLOSSEUM_COPILOT_PAT"
```

### Get Cluster Details
```bash
curl -s "$COLOSSEUM_COPILOT_API_BASE/clusters/v1-c14" \
  -H "Authorization: Bearer $COLOSSEUM_COPILOT_PAT"
# Cluster key example: v1-c14 = "Solana AI Agent Infrastructure"
```

### Hackathon Analysis
```bash
curl -s -X POST "$COLOSSEUM_COPILOT_API_BASE/analyze" \
  -H "Authorization: Bearer $COLOSSEUM_COPILOT_PAT" \
  -H "Content-Type: application/json" \
  -d '{"hackathon": "cypherpunk", "topic": "AI agent payments"}'
```

### Compare Hackathons
```bash
curl -s -X POST "$COLOSSEUM_COPILOT_API_BASE/compare" \
  -H "Authorization: Bearer $COLOSSEUM_COPILOT_PAT" \
  -H "Content-Type: application/json" \
  -d '{"hackathons": ["breakout", "cypherpunk"], "topic": "payments"}'
```

## Hackathon Chronology

| Edition | Period | Slug |
|---------|--------|------|
| Hyperdrive | Sep 2023 | `hyperdrive` |
| Renaissance | Mar-Apr 2024 | `renaissance` |
| Radar | Sep-Oct 2024 | `radar` |
| Breakout | Apr-May 2025 | `breakout` |
| Cypherpunk | Sep-Oct 2025 | `cypherpunk` |

## Useful Clusters

- `v1-c14`: Solana AI Agent Infrastructure
- `v1-c22`: AI-Powered Solana DeFi Assistants
- `v1-c26`: Simplified Solana Payment Solutions
- `v1-c16`: Stablecoin Payment Rails and Infrastructure

## Competitive Analysis Workflow

1. **Search by vertical**: Use `search/projects` with relevant query
2. **Filter winners**: Add `filters: { "winnersOnly": true }` for serious competitors
3. **Get details**: Use `projects/by-slug/:slug` for top competitors
4. **Check accelerator**: Note which projects are in C4 accelerator
5. **Analyze clusters**: See what else is in the same space
6. **Compile report**: Tier competitors by prize, accelerator status, and threat level

## Report Structure

```markdown
# Competitive Landscape: [Topic]

## Tier 1: Prize Winners
| Project | Hackathon | Prize | What They Built |

## Tier 2: Active Competitors
| Project | Hackathon | What They Built |

## Tier 3: Adjacent Players
| Project | Hackathon | What They Built |

## Key Insights
- What's already built
- What nobody has built yet (gaps)

## Your Edge
[Positioning against competitors]
```

## Rate Limits

- Max 2 concurrent requests
- 429 errors: Back off per `Retry-After` header
- Feedback endpoint: 10 req/hr

## Token Management

- PATs are long-lived (~90 days)
- Token expires: check `/status` response
- Rotate by issuing new one at https://arena.colosseum.org/copilot

## Related Skills

- `crypto-hackathon-bounty-scout` — Finding new hackathons (this researches existing projects)
- `hackathon-tech-stack-evaluation` — Evaluating tech fit for specific hackathons
- `hackathon-project-scaffold` — Scaffolding new hackathon projects
