---
name: github-first-research
description: Research a technology/platform by going directly to GitHub when web search/scrape tools are unavailable or rate-limited. Especially effective for blockchain/Web3 projects where official docs may be sparse but repos contain connection details, ABIs, and SDK info.
---

## When to Use
- Web search is rate-limited or blocked
- You need technical details (chain IDs, RPC URLs, contract addresses, SDK structure)
- Researching blockchain projects, SDKs, or developer tools
- Official docs site is down or returns 404

## Steps

### 1. Search GitHub directly via browser
Navigate to: `https://github.com/search?q=<query>&type=repositories`
- Try exact phrase: `"beams sdk"`, `"project-name" avalanche`
- Filter by language if relevant (Solidity, TypeScript, etc.)

### 2. Find the org, not just one repo
Click through to the organization page (e.g., `github.com/BuildOnBeam`). This reveals:
- **All repos** — connection details, SDKs, contracts, docs, token contracts
- **Recent activity** — how actively maintained (check commit dates)
- **Repo descriptions** — often more precise than marketing pages

### 3. Prioritize these repo types for blockchain projects
| Repo Pattern | What It Contains |
|-------------|-----------------|
| `*-subnet` or `*-chain` | Chain IDs, RPC URLs, explorers, faucet links |
| `*-api-clients` or `*-sdk` | Official SDKs, API specs |
| `*-docs` (MDX/Nextra) | Full documentation as source code |
| `*-contracts` or `*-abis` | Contract ABIs, deployment addresses |
| `*-token` | Token contract details |

### 4. Read the README.md directly
Navigate to: `https://github.com/<org>/<repo>/blob/main/README.md`
- Use `raw.githubusercontent.com` URL if `web_extract` works
- Otherwise read via browser snapshot — often contains chain details, RPC endpoints, and links

### 5. Cross-reference with official docs
Once you know the docs domain (from README links), navigate directly:
- `docs.onbeam.com/sdk` (path discovered from README)
- Avoids homepage marketing fluff

## Pitfalls
- GitHub search may show irrelevant repos with matching keywords (e.g., "Pusher Beams SDK" vs "Beam blockchain SDK") — filter by org
- Some docs repos use Nextra/Docusaurus with client-side rendering — browser snapshot may truncate; scroll to get full content
- README connection details may be outdated — check commit dates

## Example: Beam SDK Research
```
1. GitHub search "beams sdk" → found BuildOnBeam/beam-api-clients (3 stars)
2. Navigate to github.com/BuildOnBeam → 44 repos, active development
3. beam-subnet repo README → Chain ID 4337, RPC URLs, explorer links
4. beam-docs repo → MDX docs source, last updated Apr 2026
5. docs.onbeam.com/sdk → full SDK structure (Player + Automation services)
6. Total time: ~5 browser navigations, ~3 minutes
```
