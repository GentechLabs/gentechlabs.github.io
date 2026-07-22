# Circle Skills + arc-p2p-payments — Research

**Date:** 2026-07-23
**Queue Item:** #59 — Circle (USDC) — arc-p2p-payments + skills Contribution
**Priority:** High
**Difficulty:** Medium

## Key Findings

### Circle Skills Repo (133⭐, 38 forks)
- **Circle's open source AI development skills** — Apache 2.0 license
- 8 skills currently: `accept-agent-payments`, `use-usdc`, `bridge-stablecoin`, `use-arc`, `use-circle-wallets`, `use-developer-controlled-wallets`, `use-gateway`, `unify-balance`
- **Already has an `accept-agent-payments` skill** that covers Gateway Nanopayments + x402 seller integration
- CONTRIBUTING.md accepts contributions via GitHub issues + PRs
- Maintained by Circle + Anthropic (bryan-anthropic is a contributor)
- 13 commits, last updated June 22, 2026 — actively maintained

### arc-p2p-payments Repo (19⭐, 14 forks)
- **Sample app** demonstrating gasless P2P payments on Arc
- Stack: Next.js + Supabase + Circle Modular Wallets + Passkey security
- TypeScript (93%), PLpgSQL (3%), JavaScript (2.3%)
- 3 commits, last updated May 1, 2026
- 11 open PRs — actively accepting contributions
- 2 contributors (Circle team)

### Integration Opportunity

**Angle 1: Circle Skills — Contribute x402 Gateway Skill**
- The `accept-agent-payments` skill already covers Gateway Nanopayments
- Our **x402 gateway skill** (production-tested, 16 endpoints) would complement it
- We can contribute a dedicated `x402-gateway` skill showing how to deploy a multi-endpoint x402 gateway
- Pattern: same format as existing skills (YAML frontmatter + markdown body)

**Angle 2: arc-p2p-payments — Compliance Plugin**
- The app uses Circle Modular Wallets for gasless P2P
- We can contribute a compliance plugin (same pattern as GOAT AgentKit)
- Add x402 payment verification to the P2P flow
- TypeScript — our lane

**Angle 3: arc-fintech (36⭐)**
- Multi-chain treasury management
- Aligns with our Agentic Treasury work
- Reference for architecture patterns

### Recommended Approach
1. **Fork `circlefin/skills`** — Contribute an `x402-gateway` skill showing our production-tested x402 gateway pattern
2. **Fork `circlefin/arc-p2p-payments`** — Contribute compliance plugin or x402 integration pattern
3. Both are TypeScript/Python — fully cloud-actionable

### Blockers
- None — fully actionable by Gentech
- No Jordan dependency
- No special hardware needed
