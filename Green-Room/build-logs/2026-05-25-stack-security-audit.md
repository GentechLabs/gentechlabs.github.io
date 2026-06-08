# AAE Stack Security Assessment — May 25, 2026

## Risk Tiers

### 🟢 Low Risk (Verified/Compliant)
| Provider | Security Status | Notes |
|----------|----------------|-------|
| **Nango** | SOC2 + GDPR compliant | Enterprise-grade, 700+ API integrations |
| **Agent Launch (Fetch.ai)** | CertiK audited (100% score) | Fetch.ai staking contract verified. Agent Launch contract on BSC — check if same audit covers it |
| **Hermes Agent** | Core stack, self-hosted | We control the runtime |
| **OpenClaw** | Core stack, self-hosted | We control the runtime |

### 🟡 Medium Risk (Partial Security, Monitor)
| Provider | Security Status | Notes |
|----------|----------------|-------|
| **Swarms ACM** | SECURITY.md only, no formal audit | Open-source, community-reviewed. Agent orchestration (not custody). Low attack surface for us. |
| **x402 (Daydreams)** | No formal audit found | HTTP-native payments, no account/API key storage. Protocol-level security. Monitor for exploits. |
| **ERC-8004 (AACP)** | Whitepaper + BSC Testnet | TEE + zkVM proofs. Still testnet — wait for mainnet + audit before high-value use. |
| **GMGN.AI** | Centralized platform | API-based, hosted wallet architecture. Trust required. Don't store significant funds there. |

### 🔴 High Risk (No Audit / Recently Hacked)
| Provider | Security Status | Notes |
|----------|----------------|-------|
| **Bankr** | ⚠️ HACKED May 20, 2026 | 14 wallets compromised on Base. Integration PAUSED. Monitor post-hack response. |
| **Fhenix (FHE)** | No security audit found | Privacy layer, still research phase. Do NOT integrate until audited. |
| **TermiX AACP** | No formal audit found | Whitepaper only, BSC Testnet. Wait for mainnet audit. |

## Key Principles

1. **Never store user private keys** — Use handoff pattern (Agent Launch, x402)
2. **Testnet first** — All new integrations start on testnet
3. **Wait for audits** — No mainnet integration without formal security audit
4. **Monitor weekly** — Check for hacks, vulnerabilities, deprecations
5. **Bankr = hold** — Do not resume until post-hack security is proven

## Monitoring Checklist (Weekly)

- [ ] Check each provider's GitHub/Twitter for security advisories
- [ ] Check DeFi exploit databases (rekt.news, de.fi)
- [ ] Verify smart contract addresses haven't changed
- [ ] Check for new audit reports
- [ ] Monitor Bankr recovery status
