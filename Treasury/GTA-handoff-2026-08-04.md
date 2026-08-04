# GTA Handoff — Treasury Group Context Update

**Date:** 2026-08-04
**From:** Gentech (HQ)
**To:** Agentic Treasury Group
**Why:** Jordan asked to ensure the Treasury group has the GTA updates so the fused command center reads GTA correctly.

---

## What changed (GTA, Aug 3–4)

GTA has a **bigger vision now** and its Coinbase spot leg is **live**. This updates how the `⚡ GTA Arb` line in the fused report should be interpreted.

### 1. GTA Product Thesis — now the flagship
Captured in `09-Green Room/specs/gta-product-thesis.md`. GTA = **open execution + authorized-proxy layer**, two layers:
1. Open aggregation across agent-native rails (Coinbase ✅ live, Robinhood ⏳ pending, Polymarket, Ondo)
2. Authorized proxy — agent operates *your* accounts via OAuth/saved sessions (the "agent-as-VPN" reframe)

**Strategic edge:** CLARITY Act deepens US venues, so the arb opportunity moves onto clean US rails. We arbitrage *between* platforms while everyone picks one.

### 2. Coinbase spot leg — built, tested, live
- `gta_coinbase_leg.py` — executes the "long spot" side of contango arb via CDP
- **15/15 tests green** (9 executor + 6 coinbase leg, incl. live BTC quote)
- `get_swap_price` verified as the **read-only basis oracle** (works unfunded)
- **Real swap** needs: funded account + contract addresses + raw integer amounts — all wired, awaiting funding

### 3. CDP wallet signing secret — secured Aug 4
- The `CDP_WALLET_SECRET` (signing secret for the Coinbase wallet) was **missing on the box** and is now provided by Jordan and stored at `/root/.blockrun/cdp-wallet-secret` (chmod 600, not echoed).
- This is the **trade-capable** credential (vs `CDP_API_KEY_SECRET` which is read-only API auth).
- **Not yet wired into execution** — pending funding.

### 4. What the Treasury group should know about the ⚡ GTA Arb line
- Current `10.4 bps (tradeable)` reads are from the **read-only basis oracle** — signal only, NO real money moving.
- GTA **is not yet executing real trades** — it's dry-run/signal mode until the Coinbase wallet is funded.
- Do NOT treat "tradeable" as "a position is being taken." It means an arb window is *live on the feed*.

---

## Open items (do not block on these for the fused report)

| Item | Status | Owner |
|---|---|---|
| Fund GTA Coinbase wallet (real spot exec) | Pending — modest ETH + small asset amount | Jordan (when ready) |
| Robinhood perp leg (KYC/OAuth) | Pending — enables short side / full basis arb | Jordan |
| Wire CDP wallet secret into execution | Ready, awaiting funding | Gentech |
| KeeperHub Base wallet `0x53A8...8EA` funding | Separate build (KeeperHub hackathon, Aug 13) | Jordan |

---

## Fused report interpretation note
The fused command center is correct as-is. GTA Arb is a **live signal feed**, not an executed position, until funding lands. Keep the ⚡ line as signal-only. Do not include GTA as a P&L or position layer.
