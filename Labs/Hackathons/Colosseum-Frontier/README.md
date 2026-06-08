# AgentEscrow: Decentralized Job Marketplace with DVN Redundancy

**Tagline**: Cross-chain job validation with **2-of-3 DVN quorum** and **Kite AI threat detection**.

## The Problem
LayerZero’s architecture allows applications to configure their own **decentralized verifier networks (DVNs)**, but defaults to **1-of-1 DVN setups**—creating single points of failure. A compromised DVN can approve malicious jobs, drain escrow funds, or manipulate reputation scores. With the recent **Kite AI integration**, LayerZero now supports AI-powered threat detection, but **application-level safeguards are still required** to enforce redundancy and validate DVN behavior.

## The Solution
AgentEscrow is a **Solana-based job marketplace** that enforces **minimum DVN redundancy at the application level**. Key features:
- **2-of-3 DVN Quorum**: Jobs require validation from at least 2 out of 3 whitelisted DVNs.
- **Kite AI Integration**: DisputeResolver module uses Kite AI to flag anomalous DVN behavior (e.g., sudden vote flips, collusion patterns).
- **Modular Security**: Architecture adapts to future LayerZero governance changes (e.g., on-chain DVN whitelisting).

## Architecture
```ascii
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Agent      │    │  Job        │    │  Dispute    │
│  Registry   │───▶│  Escrow     │───▶│  Resolver   │
└─────────────┘    └─────────────┘    └─────────────┘
       ▲                  │                  ▲
       │                  ▼                  │
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  World ID   │    │  DVN 1      │    │  Kite AI    │
│  (Swig)     │    │  DVN 2      │    │  Threat     │
└─────────────┘    │  DVN 3      │    │  Detection  │
                     └─────────────┘    └─────────────┘
```

## Sponsor Integrations
| Sponsor      | Integration                          | Depth          |
|--------------|--------------------------------------|----------------|
| **LayerZero**| Cross-chain job validation via DVNs  | High           |
| **Kite AI**  | DisputeResolver threat detection     | High           |
| **World ID** | Agent identity verification          | Medium         |
| **Metaplex** | Reputation as soulbound NFTs         | Medium         |

## Security: Risk vs. Mitigation
| Risk                          | Mitigation Strategy                          |
|-------------------------------|---------------------------------------------|
| Malicious DVN                 | 2-of-3 quorum + Kite AI anomaly detection    |
| Colluding DVNs                | Reputation slashing + Kite AI pattern analysis |
| LayerZero governance changes  | Modular DVN whitelist (upgradable)           |

## Demo Flow
1. **Agent Registration**: Alice registers as a worker using World ID (Swig).
2. **Job Posting**: Bob posts a job with 10 SOL escrow, requiring 2-of-3 DVN validation.
3. **DVN Validation**: DVNs 1 and 2 approve; DVN 3 is flagged by Kite AI as malicious.
4. **Dispute Resolution**: JobEscrow rejects DVN 3’s vote and completes the job with 2-of-2.

## Getting Started
```bash
# Clone the repo
git clone https://github.com/ProtoJay4789/agent-escrow
cd agent-escrow

# Install dependencies
npm install

# Test DVN quorum validation
anchor test --skip-build
```

## Why AgentEscrow Wins
| Judge Criterion          | AgentEscrow’s Edge                          |
|--------------------------|---------------------------------------------|
| **Technical Innovation** | First job marketplace with DVN redundancy   |
| **Sponsor Integration**  | Deep LayerZero + Kite AI integration        |
| **Security**             | 2-of-3 quorum + AI threat detection         |
| **Market Fit**           | Solves real pain for cross-chain developers |

## License
MIT