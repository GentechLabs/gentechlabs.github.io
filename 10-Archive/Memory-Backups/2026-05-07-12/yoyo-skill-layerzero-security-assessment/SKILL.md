---
name: layerzero-security-assessment
description: Security assessment framework for LayerZero integrations — DVN config evaluation and risk scoring
version: 1.0
created: 2026-04-21
---

# LayerZero Security Assessment

## Trigger
When evaluating any LayerZero integration, bridge, or cross-chain messaging endpoint for AAE or DeFi positions.

## Risk Framework: Core vs. Integration Security

LayerZero's "zero core protocol exploits" claim holds; risk primarily resides in the **integration layer** (DVN configuration).

### Key Metric: DVN Configuration Threshold (X-of-Y-of-N)
LayerZero v2 uses a per-channel configurable threshold model:
- **X** — specific DVNs required to always witness a message
- **Y** — total threshold (required + optional DVNs)
- **N** — total DVNs available for that channel

Protocol-level constraints (from source analysis):
- `Multisig::sanity_check()`: `quorum > 0 && quorum as usize <= signers.len()` → **minimum quorum of 1 is valid**
- `DST_CONFIG_MAX_LEN: 200` per-destination configs (increased from 140 in Apr 2025)
- **No minimum-DVN mandate** found in code or documentation; thresholds are application-specific and immutable once set by the delegate

**Security posture as of May 2025:**
- Pre-exploit: ~47% of integrations used 1/1 DVN (single verifier)
- Post-KelpDAO (Feb 2025): **No protocol-level changes mandating multi-DVN** detected in codebase, releases, or official documentation
- Enterprise DVN entrants (e.g., Worldpay Mar 31, 2026) are market-driven, not protocol-forced

### Safe Integration Patterns
- **3/5 DVN** or higher: Reasonable fault tolerance ✅
- **Multi-sig DVN committees** (7-signer quorum possible): Strong security ✅✅
- **Single-DVN (1/1)**: Acceptable for low-value/low-risk early deployments; monitor for future protocol minimum changes

### Red Flags
- 1/1 DVN with high TVL exposure
- No public DVN configuration documentation
- Team unresponsive to KelpDAO incident lessons
- No plan to add secondary verifiers after mainnet launch

## Assessment Checklist

1. **Check DVN config** — How many verifiers? Who runs them?
2. **Check integration age** — Older = more battle-tested
3. **Check TVL** — Higher TVL = more audit scrutiny
4. **Check team response history** — How did they handle past incidents?

## Known Safe Integrations (Higher Confidence)
- Stargate Finance (LayerZero's own, better audited)
- Established bridges with multi-DVN (verify individually)

## Red Flags
- 1/1 DVN setup
- No public DVN configuration docs
- Team hasn't responded to KelpDAO incident
- Cheap/easy deployment with single relayer

## Known Incidents

### KelpDAO / rsETH Exploit — February 22–23, 2025
- **Attacker:** DPRK Lazarus Group (TraderTraitor)
- **Vector:** RPC-poisoning of LayerZero Labs DVN infrastructure. Compromised 2 RPC nodes, DDoS'd uncompromised nodes to force failover, forged cross-chain messages. Malicious binary self-destructed post-attack.
- **Root cause:** KelpDAO used 1/1 DVN (single verifier: LayerZero Labs) despite explicit recommendations for multi-DVN deployments.
- **Contagion:** Zero. Modular architecture contained blast radius to rsETH only.
- **LayerZero response (as of May 2025):** DVN operational (RPCs replaced). No public evidence of blanket 1/1 DVN sign-out policy. Law enforcement engaged (Seal911 tracking).
- **KelpDAO recovery:** No public compensation/migration statement as of May 2025; website remained live with stale TVL figures.

**Post-incident LayerZero v2 code audit (Feb–Apr 2025):** No emergency security patches found in commit tree. Only measurable DVN-related change was PR #136 (Apr 10, 2025) — `extend_dvn_config` instruction increasing `DST_CONFIG_DEFAULT_LEN` from 140 to 200 (operational capacity increase). No minimum-DVN mandate implemented at protocol level.

*Note: Previous skill versions incorrectly dated this incident as April 2026 and claimed "LZ refusing to sign 1/1 DVN configs." Those claims are unverified; protocol still supports threshold quorum of 1.*

### Enterprise DVN Entrants
- **Worldpay/Global Payments "Payments DVN"** (Mar 31, 2026) — enterprise-grade verification across 9+ chains (Ethereum, Base, Solana, +6 more). $3.7T/yr payment processor.

## Technical Verification via GitHub (Recommended)

When assessing current LayerZero protocol constraints, bypass rendered docs (which may be stale) and check source directly. See `references/2025-05-dvn-configuration-analysis.md` for concrete code excerpts and URLs.

**Quick sanity check (May 2025 findings):**
- `quorum > 0` allowed → 1/1 DVN channels technically permitted
- No `MIN_REQUIRED_DVNS` constant present in codebase
- Threshold logic is application-configured, not protocol-mandated
- `DST_CONFIG_MAX_LEN` enlarged to 200 (operational capacity, not security patch)
## Monitoring

- **Scheduled check:** Cron job `00c200908ed0` polls every 6h for ecosystem updates (blogs, GitHub releases)
- **Vault file:** `02-Research/LayerZero-Risk-Analysis.md` stores historical findings
- **Technical verification methods:** See `references/2025-05-dvn-configuration-analysis.md` for direct GitHub/file-based checks when web UI is rate-limited or blocked

## Decision Rule for Integrations (Updated May 2025)

Integration risk depends on **value at risk** and **TVL exposure**:

| TVL / Risk Level | Minimum Recommended DVN Threshold | Action |
|-------------------|-----------------------------------|--------|
| **High (>$10M equivalent)** | 3/5+ with multi-sig DVN committee | Required |
| **Medium ($1–10M)** | 2/3+ multi-DVN | Recommended |
| **Low / Early Phase (<$1M)** | 1/1 acceptable for bootstrapping | Permitted |

**Trigger to re-evaluate for ANY integration:**
1. LayerZero announces protocol-level minimum-DVN enforcement >1
2. A second major exploit occurs involving single-DVN patterns
3. GenLayer or similar AI-verifier model requires custom adapter — ensure your DVN threshold accommodates additional verification latency

**Ecosystem self-correction signals observed (🟡):**
- ✅ OperationalDVN capacity expanded (`DST_CONFIG_MAX_LEN` 140→200) enabling broader per-channel configs
- ✅ Enterprise DVNs entering market (Worldpay) – increasing verifier diversity
- ✅ Zero contagion proved modular architecture value
- ⏳ Awaiting: mandatory multi-DVN enforcement (not yet implemented)
- ⏳ Awaiting: KelpDAO full recovery/compensation statement

**Ecosystem self-correction signals observed (🟡):**
- ✅ LayerZero banning 1/1 DVN configs (strongest corrective action seen)
- ✅ Enterprise DVNs entering market (Worldpay)
- ✅ Zero contagion proved modular architecture value
- ⏳ Awaiting: mandatory multi-DVN enforcement, KelpDAO resolution
