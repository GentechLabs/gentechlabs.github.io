# Agent Rug 2.0 — Agent Security Platform

**Status:** Spec v1.0 | **Priority:** High | **Builds on:** Rugcheck v2 API (port 8088)
**Author:** Gentech | **Date:** 2026-07-20

---

## 1. The Problem

AI agent security is the #1 blind spot in enterprise 2026:

- **255% YoY increase** in AI agent CVEs (74 → 263 documented)
- **83%** of enterprises have deployed agents, only **29%** feel secure
- **48%** of production agents run with **zero security oversight**
- **54%** of organizations have already had an AI agent security incident
- **45.6%** use shared API keys for agent-to-agent authentication

Existing tools (Token Security, CertiK AI Auditor, Hacken) focus on smart contract audits and LLM red-teaming. **None** address agent-to-agent payment integrity, MCP server trust scoring, or x402 payment flow security.

## 2. Our Differentiator

Rugcheck v2 already scores Solana tokens for risk. Agent Rug 2.0 extends that to the **full agent security stack**:

| Layer | What We Check | Existing Tools |
|-------|--------------|----------------|
| Token | Rugcheck v2 — Solana token risk scoring | ✅ Already built |
| Agent Identity | ERC-8004 verification, wallet reputation | ❌ No one does this |
| MCP Server | Trust scoring, tool poisoning detection | ❌ No one does this |
| Payment Flow | x402 payment integrity, proof verification | ❌ No one does this |
| Attack Vector | OWASP Agentic Top 10 scanning | Partial (Promptfoo, Garak) |

## 3. Architecture

```
Agent Rug 2.0 API (port 8088 — extends existing rugcheck)
├── /v1/health          → Health check
├── /v1/score/{mint}    → Token risk score (existing)
├── /v1/agent/{id}      → Agent identity verification
│   ├── ERC-8004 registry check
│   ├── Wallet reputation score
│   └── Transaction history analysis
├── /v1/mcp/{url}       → MCP server trust score
│   ├── Tool description poisoning scan
│   ├── Schema integrity check
│   └── Supply chain provenance
├── /v1/x402/{endpoint} → x402 payment flow audit
│   ├── 402 response shape validation
│   ├── accepts[] schema check
│   ├── Proof verification
│   └── CORS/security headers
├── /v1/scan/{agent_id} → Full agent security scan
│   ├── OWASP Agentic Top 10 coverage
│   ├── Attack vector mapping
│   └── Risk report generation
└── /v1/report/{scan_id} → Detailed security report
```

## 4. OWASP Agentic Top 10 Coverage

| ID | Risk | Our Check | Status |
|----|------|-----------|--------|
| ASI01 | Agent Goal Hijacking | Prompt injection detection in tool descriptions | 🔲 |
| ASI02 | Tool Misuse | Tool permission boundary analysis | 🔲 |
| ASI03 | Identity Abuse | ERC-8004 + wallet reputation scoring | 🔲 |
| ASI04 | Supply Chain | MCP server provenance + integrity check | 🔲 |
| ASI05 | Code Execution | Sandbox detection, RCE pathway scan | 🔲 |
| ASI06 | Memory Poisoning | RAG/vector store backdoor detection | 🔲 |
| ASI07 | Inter-Agent Comms | Message authentication check | 🔲 |
| ASI08 | Payment Integrity | x402 flow validation (our specialty) | 🔲 |
| ASI09 | Credential Exposure | Hardcoded key scan in MCP configs | 🔲 |
| ASI10 | Authorization Bypass | Tool access boundary testing | 🔲 |

## 5. MCP Attack Surface Coverage

Based on Unit 42 findings and Invariant Labs research:

| Attack | Description | Detection Method |
|--------|-------------|-----------------|
| Tool Poisoning | Hidden instructions in tool descriptions | Static analysis of tool registration payloads |
| Rug Pull | Server swaps to malicious version after adoption | Version diff tracking, change notification audit |
| Cross-Server Shadowing | One compromised server infects others | Inter-server communication analysis |
| Sampling Injection | Malicious content via MCP Sampling | Response validation against expected schemas |
| Resource Poisoning | Malicious data in served resources | Content integrity verification |
| Prompt Theft | System prompt extraction via crafted inputs | Prompt leakage detection patterns |

## 6. Pricing Model

| Tier | Price | What You Get |
|------|-------|-------------|
| Free | $0 | 5 token scores/day, basic health check |
| Pro | $0.01/scan | Full agent scan, MCP trust score, x402 audit |
| Enterprise | Custom | Dedicated scanning, SLA, custom rules |

All paid via x402 micropayments (same as rugcheck v2).

## 7. Build Plan

### Phase 1: Foundation (Current — Rugcheck v2)
- [x] FastAPI server on port 8088
- [x] Solana token risk scoring
- [x] x402 payment middleware
- [x] CORS, rate limiting, error handling
- [x] Cloudflare DNS fixed (A record → 2.24.195.196)

### Phase 2: Agent Identity (Next)
- [ ] ERC-8004 registry integration
- [ ] Wallet reputation scoring (on-chain history analysis)
- [ ] Agent verification endpoint (`/v1/agent/{id}`)
- [ ] Tests for identity verification

### Phase 3: MCP Trust Scoring
- [ ] MCP server schema analysis
- [ ] Tool description poisoning detection
- [ ] Supply chain provenance check
- [ ] MCP trust score endpoint (`/v1/mcp/{url}`)

### Phase 4: x402 Payment Audit
- [ ] 402 response shape validation
- [ ] accepts[] schema verification
- [ ] Proof verification patterns
- [ ] Security header audit
- [ ] x402 audit endpoint (`/v1/x402/{endpoint}`)

### Phase 5: Full Agent Scan
- [ ] OWASP Agentic Top 10 coverage
- [ ] Attack vector mapping
- [ ] Risk report generation
- [ ] Full scan endpoint (`/v1/scan/{agent_id}`)

## 8. Revenue Model

| Source | Price | Market |
|--------|-------|--------|
| Per-scan (x402) | $0.01–$0.05 | Individual agents |
| Monthly subscription | $10–$25/mo | Agent operators |
| Enterprise audit | Custom | Protocols, funds |
| Compliance reports | $50–$500 | Regulated entities |

## 9. Competitive Landscape

| Tool | Focus | Our Advantage |
|------|-------|---------------|
| Token Security | Agent visibility/ governance | We do payment integrity + MCP trust |
| CertiK AI Auditor | Smart contract audit | We do runtime agent scanning |
| Hacken Audit Agent | Solidity audit | We do x402 + MCP |
| Promptfoo | LLM testing | We do agent-specific + payment |
| Garak (NVIDIA) | LLM vulnerability scan | We do agent-to-agent + supply chain |

## 10. Next Steps

1. [ ] Phase 2: Build agent identity verification
2. [ ] Phase 3: Build MCP trust scoring
3. [ ] Phase 4: Build x402 payment audit
4. [ ] Phase 5: Full scan + reporting
5. [ ] Deploy to production (extends existing rugcheck API)
6. [ ] List on pay-skills catalog
7. [ ] Submit to agent security marketplaces

---

*Built on GenTech Labs' existing rugcheck v2 infrastructure. Extends from token security to full agent security platform.*
