# PR Portfolio — GenTech Ecosystem Listings

> Log of all submitted pull requests to awesome repos and directories.
> Each entry: repo, PR link, what was submitted, date, status.
> **Updated: 2026-07-22 — Night audit: 4 previously-unverified PRs confirmed open (pay-skills #190, #192; x402 #2905; awesome-erc8004 #82).**

## Audit Finding (Jul 22, 2026) — PRs WERE Actually Submitted

**Correction from earlier audit:** The `gh pr list` command uses GraphQL which has a separate rate limit bucket. REST API PR creation confirmed that PRs already exist for all 4 repos tested. The earlier "never submitted" conclusion was incorrect — the PRs were submitted but GraphQL queries returned empty due to rate limiting.

**Verified via REST API (PR creation returned "already exists"):**
- ✅ awesome-web3 — PR exists for `ProtoJay4789:add-gentech-x402-gateway`
- ✅ awesome-agent-cortex — PR exists for `ProtoJay4789:add-gentech-agent-kit-identity`
- ✅ awesome-agent-cortex — PR exists for `ProtoJay4789:add-gentech-x402-gateway-payments`
- ✅ awesome-agents — PR exists for `ProtoJay4789:add-gentech-x402-gateway`

**Rate limited — could not verify PR numbers/statuses for remaining repos:**
- ❓ pay-skills — `add/gentech-x402-gateway` branch exists, PR may exist
- ❓ x402 — `feat/compliance-scanner` branch exists, PR may exist
- ❓ awesome-erc8004 — `format-ordering` branch exists, PR may exist
- ❓ awesome-web3-services — only `main` branch, no PR possible yet
- ❓ awesome-ai-agents-2026 — fork deleted, needs re-fork

## Successfully Listed (No PR Needed)

| Repo | Listing | What | Status |
|------|---------|------|--------|
| xpaysh/awesome-x402 | Already listed | GenTech Labs (agent economy infrastructure, 48 x402 endpoints) | ✅ Listed in Production Implementations |
| sudeepb02/awesome-erc8004 | Already listed | GenTech Labs Agent (Avalanche #1770) | ✅ Listed under Agent Services |

## PRs Submitted (Verified)

| Repo | Branch | What | Status |
|------|--------|------|--------|
| ahmet/awesome-web3 | `add-gentech-x402-gateway` | GenTech x402 Gateway | ✅ PR exists (number TBD — rate limited) |
| 0xNyk/awesome-agent-cortex | `add-gentech-agent-kit-identity` | GenTech Agent Kit in Identity | ✅ PR exists |
| 0xNyk/awesome-agent-cortex | `add-gentech-x402-gateway-payments` | GenTech x402 Gateway in Payments | ✅ PR exists |
| Scottcjn/awesome-agents | `add-gentech-x402-gateway` | GenTech x402 Gateway | ✅ PR exists |

|## PRs Verified (Jul 22 Night Audit)
|
|| Repo | PR | Branch | What | Status |
||------|-----|--------|------|--------|
|| solana-foundation/pay-skills | **#192** | `add/gentech-x402-gateway` | GenTech x402 Gateway — 16 endpoints, 6 chains, Algorand | ✅ OPEN |
|| solana-foundation/pay-skills | **#190** | `update-gentech-catalog` | Refresh 9 services, add blockchain-rpc + defi-yields | ✅ OPEN |
|| x402-foundation/x402 | **#2905** | `feat/compliance-scanner` | x402 Compliance Scanner reference implementation | ✅ OPEN |
|| sudeepb02/awesome-erc8004 | **#82** | `format-ordering` | GenTech Agent Kit in Infrastructure & SDKs | ✅ OPEN |

## PRs That Need Work

| Repo | Branch | What | Action Needed |
|------|--------|------|---------------|
| caramaschiHG/awesome-ai-agents-2026 | Fork deleted | GenTech Agent Kit in Agent Frameworks | Re-fork, re-submit |
| VaitaR/awesome-web3-services | Only `main` branch | GenTech x402 Gateway | Create branch, submit PR |
| GOATNetwork/agentkit | N/A (own repo) | Compliance Plugin + ERC-8004 Fix | Manual web UI submission needed (Jordan) |

## GOAT AgentKit PR #7

| Repo | PR | What | Status |
|------|----|------|--------|
| GOATNetwork/agentkit | Not yet submitted | Compliance plugin (3 actions) + ERC-8004 fix for issue #4 | Code pushed to ProtoJay4789/goat-agentkit on `feat/compliance-plugin`. Needs Jordan to submit via web UI at https://github.com/ProtoJay4789/goat-agentkit → "Contribute" → "Open Pull Request" |

## x402 Foundation PRs

| Repo | PR | What | Status |
|------|----|------|--------|
| x402-foundation/x402 | May exist | x402 Compliance Scanner (feat/compliance-scanner) | Fork exists, branch ready. Verify when rate limit resets. |

## Pay-Skills PRs

| Repo | PR | What | Status |
|------|----|------|--------|
| solana-foundation/pay-skills | May exist | 12 GenTech x402 API services | Fork exists, branch `add/gentech-x402-gateway` ready. Verify when rate limit resets. |
