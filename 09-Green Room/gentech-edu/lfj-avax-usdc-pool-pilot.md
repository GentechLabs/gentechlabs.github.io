# GenTech EDU — LFJ AVAX/USDC Pool (Pilot Page)

### Honest-expectations guide for the Agentic Treasury's default rail
**Built:** 2026-08-21 (nightly build) · **Status:** ✅ LIVE (position verified on-chain)

> Every yield-farmer promises big APY and hides the small-capital reality.
> GenTech EDU is the opposite: we show you the **real numbers** for a **real,
> live position** — before you commit a dollar. This is the pilot EDU page for
> the pool we actually run on real funds.

---

## 1. What this pool is

**LFJ (formerly Trader Joe) V2.2 — AVAX/USDC** is a concentrated-liquidity
automated market maker on the **Avalanche C-Chain**. You provide AVAX and USDC
into a narrow price band (a "curve") around the current AVAX/USDC price. As
traders swap within your band, you earn a slice of their fees.

- **Pool contract:** `0x864d4e5ee7318e97483db7eb0912e09f161516ea`
- **Pair:** WAVAX / USDC · binStep 10 · V2.2 factory `0xb43120c4`
- **Why we recommend it:** it's the rail we've fired live and verified end-to-end
  (deploy → monitor → rebalance → redeploy), and it's the default shape in the
  Agentic Treasury.

---

## 2. What a real, live position looks like (verified Aug 21, 2026)

This is not a hypothetical. The Steward wallet currently holds a live curve:

| Field | Value |
|---|---|
| Shape | CURVE (Gaussian distribution) |
| Bins | 11 (active ±5) |
| Range | $7.27 – $7.34 |
| Live price | **$7.31** (IN range ✅) |
| Deployed value | **$26.77** |
| Wallet | `0x572ABd6461...d05037` |

---

## 3. Honest returns at your size (the part everyone hides)

A position earns fees only when the price **moves inside your band**. Returns
scale with **how much you deploy**, not with APY marketing.

| Deployed | Realistic fee earnings | What that means |
|---|---|---|
| $25 (live position) | ~$0.10–0.15/day | pennies — proves the loop |
| $50 | ~$0.26–0.30/day | ~$3–4/yr. Real, not fantasy. |
| $500 | ~$2.60–3.00/day | ~$95–110/yr — starting to matter |
| $5,000 | ~$26–30/day | ~$950–1,100/yr — a real income leg |

**The honest truth:** at $25–50, you are not making money. You are **proving the
loop works and building trust** before you scale. That is the entire point of
the market-maker funnel — every market maker starts small. Don't deposit money
you expect to live on next month.

---

## 4. How to get started (exact steps)

1. **Fund your own wallet** (never ours — self-custody) on **Avalanche** with:
   - **USDC** for the LP side (the stable leg)
   - a little native **AVAX** for gas (gas is ~$0.001/tx on Avalanche — trivial;
     we keep a ~$1 buffer rule)
2. **Tell the treasury your wallet address.** It auto-discovers your position —
   no manual wiring.
3. **The agent deploys a CURVE** around the live AVAX price (the default shape).
4. **Watch it work.** The agent reports your position live every 10 min. If it
   drifts out of range, you get a signal with a suggested fix.

---

## 5. Common mistakes (read before you deposit)

- **Not funding gas.** No native AVAX = the agent can't move anything.
- **Wrong chain.** Send USDC to **Avalanche**, not Base. Cross-chain costs gas.
- **Expecting big returns on tiny capital.** A $20–50 position earns pennies.
  That's physics, not a bug.
- **Ignoring the out-of-range signal.** When price leaves your band you earn 0%.
  The agent flags it — act on it (or let the operator rebalance).
- **Deploying a flat distribution.** Flat `[1]*n` weights revert on LFJ
  (`CompositionFactorFlawed`). We use the correct Gaussian curve distribution —
  a real bug we hit and fixed live.

---

## 6. Risk profile (be honest with yourself)

| Risk | What it is | Mitigation |
|---|---|---|
| **Impermanent loss** | If AVAX moves hard, your LP can underperform holding AVAX alone | Agent DCA / exit-to-hold signals; you confirm |
| **Range drift** | Price leaves your band → 0% fees | Auto-rebalance wired + live-proven |
| **Chain risk** | Avalanche C-Chain | Battle-tested rail; gas ~free |
| **Custody** | Keys/wallet are yours | Self-custody; nothing auto-executes on Tier-2 |

---

## 7. The milestone ladder (what we're climbing, honest numbers)

| Tier | Label | Daily fees | Unlocks |
|---|---|---|---|
| 1 | Scout | $5/day | Entry strategies (CURVE) |
| 2 | Raider | $20/day | SPOT + BIDIRECTIONAL |
| 3 | Warlord | $55/day | Multi-pool |
| 4 | Fisher | $100/day | Multi-asset farming |
| 5 | Sovereign | $200/day | Custom strategy |

The current $26.77 live position is at the very bottom of the ladder. That is
fine and expected — **the goal is a working, trusted loop you can scale.**

---

## 8. The trust contract

- **Your keys, your wallet, your money.** We never hold custody.
- **Nothing auto-executes on a Tier-2 account.** Every real move is confirmed.
- **We show real on-chain numbers, never a fabricated APY.** This page cites a
  live, verified position — not a promise.
- **When in doubt, we hold.** If a transaction reverts, the agent stops and tells
  you honestly. It refuses to fake success.

---

*This is GenTech EDU — the honest-expectations layer. Pilot page for the LFJ
AVAX/USDC pool, built 2026-08-21 on the day the curve is live on real funds
(~$26.77 deployed, 11 bins, IN range at $7.31).*
