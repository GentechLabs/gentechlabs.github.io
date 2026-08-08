# HawkFi — Stack & Integration Research (Aug 7, 2026)

**Trigger:** Jordan shared HawkFi post ($TTWO market making live). "They were the first
AI-yield-farming platform I saw... somebody's actually doing it. If there's a way we can
contribute or look at their stack, let's do deep research — we could connect to them or
use them as a rail. None of these guys are our competition; we get paid by being the
connector and supplier."

**Source sites:** hawkfi.ag (behind Vercel checkpoint — use Wayback/GitBook), docs at
`hawkfi.gitbook.io/whitepaper/` (fully accessible, incl. `llms.txt`).

---

## What HawkFi is
Deploy 24/7 **quant agents** on **Solana spot markets** for:
1. **Market Making Agent** — agentic "grid trading" via a live ladder of resting
   **Dynamic Limit Orders (DLO) on Meteora DLMM**. Continuously places buys just below
   price + sells just above on pools (SOL-USDC, cbBTC, whETH, ZEC, JUP, JLP, MET, JTO,
   HYPE). Institutional-style MM made permissionless. **Private beta, DM-led rollout.**
2. **Screener Agent (Osprey V2)** — catches ~70% of daily runners, auto-deploys LP.
3. **Osprey Trading Agent** — autonomous token trading, 1% swap fee.

## Tech stack
- **Chain:** Solana (spot assets only). Confirmed via `/meteora/<solana-address>` URL
  history in Wayback (2024–2025) + docs.
- **DEX infra:** Meteora DLMM (Dynamic Limit Orders).
- **Execution models:** quant-optimized, regime/asset-adaptive. Named: "Blue-chip Wide"
  (deep pools, adverse-selection protection) + "Blue-chip Tight". User-tunable settings:
  inventory split/utilization, live orders, max quoted notional, spread factor, refresh
  cadence.
- **Docs:** GitBook with `llms.txt` + "Use HawkFi Docs with AI" → AI-accessible docs
  (a potential integration/contribution surface for GenTech).
- **Custody:** self-custodial — HawkFi cannot control your wallet.
- **Open source?** NO official public GitHub repo found (search returned only unrelated
  forks). MM agent framework is **closed**.

## Fees / model
- **Market Making Agent:** 0% execution cost for agents funded with **>$500**. Fee table
  on docs (specifics to verify live).
- Osprey Trading: 1% per swap.
- Laboratory (backtest) is simulation; live fees per workflow.

## Deploy requirements (MM agent)
- Access (private beta, DM-led), choose agent type, fund agent wallet
  (self-custodial), keep a SOL reserve for gas, configure position size/inventory.

## Integration/contribution surface for GenTech
1. **Docs-with-AI + llms.txt** — we can build tools/agents that consume HawkFi docs →
   contribute back (e.g. an onboarding/strategy guide). Open door.
2. **Referral program** — exists in docs.
3. **Rail use:** HawkFi MM agents operate on Solana/Meteora — complementary to our
   Solana homebase (gta_solana_leg, Meteora DLMM in vault-config). We could deploy a
   GenTech MM agent on HawkFi as a live demo of the treasury making markets, OR supply
   our own Meteora DLMM rail alongside.
4. **Connector angle (Jordan's principle):** HawkFi is a venue; we're the x402
   middleware + treasury layer. Paying/revenue link possible as we connect their agent
   wallets to our rails.

## Verdict (honest)
HawkFi is **real and adjacent** — Solana/Meteora MM agents, closed-source but with an
AI-accessible docs surface and a referral program. **Not a competitor**; a **rail +
potential partner** under the "connector and supplier" principle. Next step to
activate: request MM agent beta access (DM @HawkFi_), or research their referral program
as a distribution entry — or wait for them to open an API/SDK.

## Open items
- [ ] Request HawkFi MM agent beta access (DM @HawkFi_) — Jordan
- [ ] Verify MM fee table + $500 threshold live
- [ ] Explore HawkFi referral program as a connect/distribution entry
- [ ] Re-evaluate when/if HawkFi opens an API or SDK for external agents
