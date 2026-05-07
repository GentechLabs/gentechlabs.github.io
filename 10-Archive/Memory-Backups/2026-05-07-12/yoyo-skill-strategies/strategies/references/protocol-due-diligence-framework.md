# Protocol Due Diligence Framework (May 2026)

## Risk Rating Rubric (1–5 Scale)

| Score | TVL | Team | Audits | Age | Centralization | Use Case |
|-------|-----|------|--------|-----|----------------|----------|
| **1** | >$1B | Public, doxxed, track record | 3+ (formal) | >2 years | DAO/multi-sig | Blue-chip infrastructure |
| **2** | $100M–$1B | Public+doxxed core | 2–3 formal | 1–2 years | Timelock + multisig | Established DeFi |
| **3** | $10M–$100M | Pseudonymous but transparent | 1–2 audits | 6–12 months | Team multisig | Newer protocols |
| **4** | $1M–$10M | Anonymous or unproven | 1 informal / none | <6 months | Single owner / proxy | Experimental |
| **5** | < $1M | Completely anonymous | None | <3 months | Owner renounced but suspicious | Hype/rug likely |

**Scoring**: Assign worst-case across columns → final score is max applicable column. A protocol with < $1M TVL AND anonymous team AND no audits is automatically **5/5** even if other factors are neutral.

---

## Red Flag Checklist (Immediate Disqualifiers)

- [ ] **Liquidity Removal History**:Pair burned or removed >30% liquidity in past 90 days (check PancakeSwap/SushiSwap pair pages)
- [ ] **Team Wallet Dumping**: Top 10 wallet sells >5% of supply in any 7-day window (Etherscan "Large Transactions" filter)
- [ ] **Upgradable Proxy Without Timelock**: Contract has `upgradeTo()` but no OpenZeppelin Timelock attached (check governance section)
- [ ] **Ownership Not Renounced**: `owner()` address still points to EOA (not multisig/DAO) in active protocol (use `getOwner()` on contract)
- [ ] **GitHub Inactive**: Last commit >60 days for a protocol claiming "active development"
- [ ] **Suspicious Token Distribution**: Team/insiders control >30% of total supply (check tokenomics page or Etherscan read of `totalSupply()`/`balanceOf(teamWallet)`)
- [ ] **No Documentation**: Missing comprehensive docs or whitepaper; site has only marketing fluff
- [ ] **Suspicious Social Metrics**: 50%+ of Twitter followers are bots (check ratio: likes/retweets vs follows)
- [ ] **Unaudited Smart Contracts**: No formal or informal audit reports published (no link from docs to OpenZeppelin, ConsenSys Diligence, or Trail of Bits)
- [ ] **Unsustainable APR**: Staking/farming APRs >200% with no clear revenue source

---

## Protocol Vault File Pattern

**Filename**: `<protocol>-evaluation-<YYYY-MM-DD>.md`

**Frontmatter**:
```yaml
---
title: <Protocol Name> Evaluation
date: <YYYY-MM-DD>
status: Draft | Reviewed | Archived
protocol_risk: 1-5
ticker: <TOKEN>
chain: <Ethereum/Base/Avalanche/etc>
tvl_usd: <exact number>
volume_24h_usd: <exact number>
audited: Yes/No/Partial
team: Doxxed/Pseudonymous/Anonymous
monitoring: Active/Paused
---
```

**Body Sections**:
1. **Executive Summary** (2–3 sentences: what it is, risk score, immediate verdict)
2. **Metrics Snapshot** (TVL, volume, APR, tokenomics)
3. **Risk Analysis** — flag each red flag found with evidence links (Etherscan, GitHub, Dune query)
4. **Competitive Landscape** — similar protocols with lower risk or better fundamentals
5. **Monitoring Plan** — if not immediate avoid, specify what data to track weekly (TVL change, team wallet movement, audit updates)
6. **Recommended Action** — Avoid / Monitor with <X% allocation / Consider for integration (if tool/infra)

---

## Competitive Intel Categorization (from x402 Tier List)

When reviewing ecosystem-specific competitive landscapes (e.g., "AI on Base"), use these labels:

- **🔵 Core** — Protocol-level infrastructure, network effects, often venture-backed, highest adoption risk if failed (e.g., Virtuals, OpenWallet)
- **🟣 Active** — Tooling / convenience layers with live user bases, moderate integration value (e.g., Nevermined, Ampersend, Crossmint)
- **🟡 Emerging** — Early traction, unproven business model, high volatility risk (e.g., Ch40s, Executi0n, 1shot)
- **🟠 High Conviction** — Niche but differentiated; monitor for acquisition or partnership potential (e.g., Uptopia, Floe Labs)

**Rating impact**: Protocols in Core/Active tiers pose integration risk (dependency concentration) but offer network benefits. Emerging/High Conviction carry higher token volatility but lower systemic risk if held as small positions (<2% of portfolio).

---

## Watch-List Trigger Conditions

Add to `cron-watchlist-config.md` if protocol passes initial screen:

- **TVL/Volume Ratio** < 0.3x for 7 consecutive days → downgrade risk score +1
- **Team Wallet Movement** > 1% supply in 24h → immediate "🚨 TEAM DUMP" alert
- **Audit Published** → re-evaluate risk score downward by 1 (if reputable firm)
- **Contract Upgrade** (Etherscan "Contract" tab → "Code" → "More Options" → "Is this a proxy?") → flag for review within 24h
- **Social Engagement Drop** >50% (likes/mentions) for 30 days → downgrade narrative score

---

## Case Studies from This Session

### AVAX/USDC LP (LFJ v2.2) — Risk 3/5 (Moderate)
- **Metrics**: $3.9M TVL, 2.74x Vol/TVL, ~50% APR, 5bps fee tier
- **Red Flags**: Position within $0.07 of range edge; config mismatch between tracker and script; fee efficiency dropping 65% (likely weekend volume collapse)
- **Action Required**: Rebalance before Sunday or widen range to include $8.80 support buffer
- **Monitoring**: Check quiet hours interaction — edge positions need pre-emptive weekend rebalance even if quiet hours active

### Kite AI (Payment Blockchain) — Risk 4/5 (High)
- **Metrics**: Unknown mainnet status, minimal on-chain data, hackathon deadline May 6
- **Red Flags**: Settlement guarantees unclear; no public mainnet explorer; integration timeline aggressive
- **Action**: Treat as experimental; deploy only minimal exposure for demo; avoid treasury allocation until mainnet + audit

### Base Agent Commerce Ecosystem — Risk 4/5 (High)
- **Tier Distribution**: Core (Virtuals, OpenWallet, Venice), Active (Nevermined, Ampersend), Emerging (Ch40s, Executi0n)
- **Red Flags**: Pre-mainnet hype cycle; most tokenless or recently launched; value-drop likely post-airdrop speculation
- **Action**: Monitor for rug indicators (team wallet dumps, liquidity removal post-token generation event); consider integration partnerships only, not token investments yet

---

## Quiet Hours + Edge Position Gotcha

**Problem discovered**: LP monitor respects quiet hours (23:00–06:30 ET) and suppresses full metrics output. This is dangerous when position is near range edge — no alerts fire during overnight/weekend breakouts.

**Detection**: Check monitor logs for `"QUIET_HOURS"` messages when `price` is within 1% of `range_low` or `range_high`.

**Mitigation**:
1. Pre-emptive edge check: if `(price - range_low) / range_width < 0.05` OR `(range_high - price) / range_width < 0.05`, bypass quiet hours for that run only.
2. Weekend gap analysis: If `day_of_week in [5, 6]` (Sat/Sun) AND edge condition true, send alert regardless of quiet hours.
3. Stateful weekend monitor: Set `weekend_watch_mode = True` if edge triggered on Friday; keep monitoring through Sunday with reduced quiet hours window (only 01:00–05:00 silent).

---

## Config-Tracker Mismatch Pattern

**Symptom**: Weekly report shows "Position range: $9.00–$9.30" but script logs say "hardcoded range: $9.36–$9.53".

**Cause**: Manual rebalancing updates `.lfj-position-tracker.json` but monitoring script still has hardcoded constants from previous snapshot.

**Fix**:
1. Search all monitoring scripts for hardcoded `RANGE_LOW` / `RANGE_HIGH` literals.
2. Replace with `config["position"]["range_low"]` / `config["position"]["range_high"]`.
3. Add integrity check at script startup:
```python
tracker_range = (tracker["range_low"], tracker["range_high"])
script_range = (cfg["position"]["range_low"], cfg["position"]["range_high"])
if tracker_range != script_range:
    log("⚠️ CONFIG MISMATCH: tracker=%s script=%s — updating script config" % (tracker_range, script_range))
    # Option A: overwrite config file with tracker values (if tracker is source of truth)
    # Option B: abort with exit code 2 and alert Jordan
```
4. Document which file is the source of truth: position tracker JSON (human-updated via screenshot/sync) or config JSON (script parameter). Make them one and the same.

---

## Price Feed Fallback Chain

When querying on-chain or DEX price data, implement layered fallback:

1. **Primary**: DexScreener API (`https://api.dexscreener.com/latest/dex/pairs/avalanche/{pool}`) — fastest, includes volume/TVL
2. **Secondary**: DeFiLlama API (`https://api.llama.fi/pools/{pool}`) — slower but comprehensive; includes APR breakdown
3. **Tertiary**: Birdeye API (Solana) or Avalanche RPC `getPriceBySymbol()` for C-Chain tokens

**Error handling**: If primary fails (HTTP error or missing key), wait 1s and retry 2×; then fall back to secondary. Log fallback chain in state: `state["last_data_source"] = "dexscreener" | "defillama" | "birdeye"`.

---

## Silent Delivery Condition

When no protocols under active review and no new red flags detected, report `[SILENT]` only.

## Created

- 2026-05-03: First protocol due diligence pipeline execution (AVAX LP, Kite AI, Base AI agents)

---

*This document is referenced by the `strategies` skill. Keep updated with new observed failure modes.*
