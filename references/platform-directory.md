# Platform Directory — x402 Ecosystem

## GenTech Gateway
- **URL**: api.gentechlabs.net
- **Type**: x402 v2 gateway (Cloudflare Worker)
- **Status**: Deployed, 15 endpoints, registered on x402scan
- **Pay-Skills PR**: #154 submitted to solana-foundation/pay-skills (pending)

## x402scan
- **URL**: https://www.x402scan.com
- **Stats**: 18.62M txns, $863.98K volume (as of July 2026)
- **Register**: https://www.x402scan.com/resources/register
- **API**: /api/stats endpoint returned 404 — may have moved or been removed

## Discovery Tool
- **@agentcash/discovery**: `npx -y @agentcash/discovery@latest discover <origin>`
- **x402-check**: github.com/suryast/x402-check (PR #12 pending header priority fix)
- **x402trace**: github.com/fardinvahdat/x402trace
- **x402-watch**: github.com/logiccrafterdz/x402-watch — new Rust-based x402 health monitor

## Ecosystem Repos — Tracked

### Canonical SDK
| Repo | Type | Status |
|------|------|--------|
| x402-foundation/x402 | Multi-language SDK (6.3k ⭐) | Canonical v2 reference |
| x402-rs/x402-rs | Rust SDK + Axum middleware | V2 support, missing discovery |
| mark3labs/x402-go | Go SDK (net/http, Gin, MCP) | V2 package (PR #30 pending for asset casing) |

### Gateway Implementations
| Repo | Type | Status |
|------|------|--------|
| marlinprotocol/x402-gateway | Rust/Axum gateway | PR #5 open (docs fix) |
| brave-experiments/private-x402-gateway | TypeScript gateway | PR #8 open (header fix) |
| selfradiance/x402-license-gateway | Hono gateway | V2 compliant ✅ |
| HyperbolicLabs/hyperbolic-x402 | Vercel deployment | 400 instead of 402 (Zod runs before paywall) |
| Nexus Agent Services | Production deployment | Gold standard (30+ endpoints, paymentContextToken) |
| MikeyPetrillo/Agent402 | Production | 504 tools, full v2 discovery |

### Facilitators
| Repo | Type | Status |
|------|------|--------|
| raid-guild/x402-facilitator-go | Go facilitator (new) | V2 compliant ✅, one-click Vercel deploy |
| quiknode-labs/x402-payments | Ruby client gem | V2 compliant ✅ |
| quiknode-labs/x402-rails | Rails middleware | V2 compliant ✅ |

### Language-Specific SDKs
| Repo | Type | Status |
|------|------|--------|
| x402-foundation/x402 (Python) | FastAPI middleware | V2 with proper config |
| mark3labs/x402-go | Go (net/http, Gin, MCP) | PR #30 pending |
| adipundir/aptos-x402 | TypeScript/Aptos SDK (v3.0.1) | V2 compliant client; server missing `resource` field in response |
| srotzin/hive-rosetta | Node.js + Python signer | V2 compliant (PR #2 pending for asset casing) |

### Monitoring & Tooling
| Repo | Type | Status |
|------|------|--------|
| logiccrafterdz/x402-watch | Rust monitoring (new) | V2 compliant, full payment cycle verification |
| rplryan/x402-discovery-mcp | MCP server for x402 discovery | x402scan integration |
| z-purr/x402-api-gateway | Reference implementation | V2, EVM + Solana |
| mark3labs/mcp-go-x402 | MCP transport for Go | Uses x402 payments for MCP |

### Mixed v1/v2 (Documented)
| Repo | Type | Issue |
|------|------|-------|
| itublockchain/hackmoney-router402 | ETHGlobal finalist | Server v2 ✅, client auto-pay v1 ❌ |

### Non-Actionable / Archived
| Repo | Reason |
|------|--------|
| Samdevrel/x402-api-gateway | Demo-only |
| ekailabs/x402-openrouter | Stale (11 months) |
| vercel-labs/x402-ai-starter | Archived by owner |
| google-agentic-commerce/a2a-x402 | Spec repo only |
| sailorpepe/undesirables-x402-server | V2 compliant, v1 headers intentional |

## Open Compliance PRs
| PR | Repo | Fix | Status |
|----|------|-----|--------|
| #5 | marlinprotocol/x402-gateway | README header docs fix | open since Jul 14 |
| #8 | brave-experiments/private-x402-gateway | X-Payment-Required → Payment-Required | open since Jul 14 |
| #30 | mark3labs/x402-go | Lowercase EVM asset addresses | open since Jul 14 |
| #2 | srotzin/hive-rosetta | Lowercase asset addresses | open since Jul 15 |
| #423 | strands-agents/tools | payment-required header in http_request | **MERGED** ✅ |

## Tier System
- Tier 0: Free probe, observe only
- Tier 1: Quick automated PRs (no human needed)
- Tier 2: Gentech Only (build queue + auto-work)
- Tier 3: Needs Jordan ($0.10+ or decision)
