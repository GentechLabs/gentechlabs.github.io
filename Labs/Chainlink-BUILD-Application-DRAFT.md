---
title: Chainlink BUILD Application
project: Agent Shield — AI Agent Security Powered by Chainlink
applicant: Jordan (ProtoJay4789)
date: 2026-06-14
status: Final — Ready to Submit
apply_url: https://chain.link/build-program
---

# Chainlink BUILD Application

## Project Name
**Agent Shield — Real-Time AI Agent Threat Detection**

## One-Liner
Chainlink oracle-powered security layer that detects prompt injection, rug pulls, and malicious agent behavior in real-time.

## Problem Statement
AI agents are becoming targets for attacks:
- **Prompt injection:** Attackers hide commands in agent inputs (Bankr exploit: $200K stolen)
- **Rug pulls:** Malicious token launches exploit agent automation
- **Agent impersonation:** Fake agents drain wallets through social engineering

Agents need real-time threat data that only oracles can provide.

## Solution
Agent Shield uses Chainlink:
- **Chainlink Functions:** Fetch threat intelligence from off-chain APIs (Slack alerts, exploit databases, honeypot detectors)
- **Chainlink Data Feeds:** Real-time token price data to detect flash loan attacks
- **Chainlink CCIP:** Cross-chain threat coordination — if an attack happens on Base, Arbitrum agents know instantly

## Why Chainlink
| Capability | Use Case |
|------------|----------|
| **Functions** | Fetch exploit databases, Slack alerts, honeypot detection APIs |
| **Data Feeds** | Real-time token prices for flash loan detection |
| **CCIP** | Cross-chain threat sharing between agent fleets |
| **Automation** | Auto-pause agent operations when threats detected |

## Artifacts (Proof of Work)
| Project | Chain | Tests | Status | Relevance |
|---------|-------|-------|--------|-----------|
| Agent Shield | EVM | 22/22 | Live | Direct — prompt injection defense |
| Agent Registry | Solana/EVM | ✅ | Live | Agent identity for threat attribution |
| Agent Credit Score | Multi-chain | 22/22 | Live | Trust scoring for agent reputation |
| AAE Safety Module | Base | 22/22 | Live | Transfer gate, input firewall, circuit breaker |

## Integration Plan
| Phase | Integration | Timeline |
|-------|-------------|----------|
| 1 | Chainlink Functions — fetch exploit DB | Month 1 |
| 2 | Data Feeds — real-time price monitoring | Month 1 |
| 3 | CCIP — cross-chain threat sharing | Month 2 |
| 4 | Automation — auto-pause on detection | Month 2 |
| 5 | SDK — "Add Agent Shield to your agent in 5 lines" | Month 3 |

## Funding Request
- **Type:** BUILD membership (oracle access + co-marketing)
- **Value:** Free oracle services + technical mentorship + ecosystem integration

## Team
- **Jordan** — Solo builder, security-focused AI agent developer
- **Gentech Labs** — Multi-agent orchestration platform
- **Track record:** 22/22 security tests, Bankr exploit research, hackathon submissions

## Links
- Portfolio: ProtoJay4789.github.io
- Agent Shield: github.com/ProtoJay4789/agent-shield
- Bankr Case Study: (in vault)

## Why BUILD
We're building the security infrastructure that makes AI agents safe. Chainlink oracles are the missing piece — without real-time threat data, agents are flying blind. Let us build the shield together.

---

*Ready to submit at https://chain.link/build-program*
