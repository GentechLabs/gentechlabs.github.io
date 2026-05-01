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

LayerZero's "zero core protocol exploits" claim is technically true. The risk lives in the **integration layer**.

### Key Metric: DVN Configuration
- **1/1 DVN** = Single point of failure 🚩
- **3/5 DVN** = Reasonable security ✅
- **Multi-sig DVN** = Strong security ✅✅

**Current state (Apr 21, 2026):** 47% of integrations ran 1/1 DVN pre-exploit. Post-KelpDAO, LayerZero Labs is **refusing to sign 1/1 DVN configs** and actively migrating apps to multi-DVN. Worldpay/Global Payments launched enterprise DVN across 9+ chains (Mar 31, 2026).

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

### KelpDAO / rsETH Exploit — April 18, 2026 (~$290M)
- **Attacker:** DPRK Lazarus Group (TraderTraitor)
- **Vector:** RPC-poisoning of LayerZero Labs DVN infrastructure. Compromised 2 RPC nodes, DDoS'd uncompromised nodes to force failover, forged cross-chain messages. Malicious binary self-destructed post-attack.
- **Root cause:** KelpDAO used 1/1 DVN (single verifier: LayerZero Labs) despite explicit recommendations for multi-DVN.
- **Contagion:** Zero. Modular architecture contained blast radius to rsETH only.
- **LayerZero response:** DVN operational (RPCs replaced). Will not sign 1/1 DVN apps. Law enforcement engaged. Seal911 fund tracking.
- **KelpDAO recovery:** No public compensation/migration statement as of Apr 21, 2026. Website still live showing stale TVL ($1.64B).

### Enterprise DVN Entrants
- **Worldpay/Global Payments "Payments DVN"** (Mar 31, 2026) — enterprise-grade verification across 9+ chains (Ethereum, Base, Solana, +6 more). $3.7T/yr payment processor.

## Monitoring Approach

When web_search or web_extract fail (auth errors, rate limits):
1. Use `browser_navigate` to official blog URLs directly
2. Use `browser_console` with `document.querySelector('article').innerText` to extract full article text
3. Check KelpDAO blog at `blogs.kerneldao.com` for recovery updates

## Monitoring
- Cron job `00c200908ed0` checks every 6h for ecosystem updates
- Vault file: `02-Research/LayerZero-Risk-Analysis.md`

## Decision Rule for AAE (Updated Apr 21, 2026)
Do NOT integrate LayerZero endpoints for agent commerce until:
1. Multi-DVN verified on target endpoint (minimum 3/5)
2. KelpDAO recovery/compensation resolved
3. 1/1 DVN integration percentage confirmed dropped significantly from 47%

**Ecosystem self-correction signals observed (🟡):**
- ✅ LayerZero banning 1/1 DVN configs (strongest corrective action seen)
- ✅ Enterprise DVNs entering market (Worldpay)
- ✅ Zero contagion proved modular architecture value
- ⏳ Awaiting: mandatory multi-DVN enforcement, KelpDAO resolution
