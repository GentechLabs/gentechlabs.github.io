# 🔗 LayerZero DVN — Security Reference

**Context:** KelpDAO exploit (April 2026) exposed systemic DVN misconfiguration risk.

## The Problem

LayerZero's security is **configurable** — protocols choose their own DVN setup.

| DVN Config | % of OApps (last 90d) | Security Level |
|------------|----------------------|----------------|
| 1-of-1 | 47% | ⛔ Single point of failure |
| 2-of-2 | 45% | 🟡 Collusion risk |
| 3-of-3+ | ~8% | ✅ Reasonable |

**Source:** Dune analysis of ~2,665 active OApp contracts (via @CryptoCurb)

## How DVN Works

- **DVN = Decentralized Verifier Network** — validates cross-chain messages
- Protocols pick which verifiers to use and the threshold (M-of-N)
- 1-of-1 means a single verifier can approve any message — **trivially exploitable**

## KelpDAO Incident

- KelpDAO used 1-of-1 DVN on their LayerZero integration
- Attacker exploited this to forge cross-chain messages
- LayerZero's response: blamed KelpDAO's configuration choice

## For Gentech

**If we ever integrate LayerZero:**
1. NEVER use 1-of-1 DVN
2. Minimum 3-of-3 with diverse verifier sets
3. Consider LayerZero + Chainlink CCIP as complementary, not alternatives
4. Monitor DVN health regularly

**Chainlink CCIP comparison:**
- CCIP has built-in risk management network (separate from DON)
- Non-configurable security — same protection for everyone
- No "choose your own adventure" vulnerability

## References

- [LayerZero DVN Docs](https://docs.layerzero.network/v2/developers/evm/dvn/decentralized-verifier-network)
- [Dune Dashboard — DVN Analysis](https://dune.com/) (search: LayerZero DVN)
- [Chainlink CCIP](https://docs.chain.link/ccip)
