# Jordan Items — Aug 5, 2026

## 🔴 TOP PRIORITY — Fund the Agentic Treasury (live money-moving test)

The full Agentic Treasury build is **shipped** (Phases A+B+C, 85 tests, K2.7-audited CLEAN):
- **A** `yield_lp_engine.py` — executable LP/yield leg (Morpho USDC, Base, 5.03%)
- **B** `gta_close_executor.py` — CLOSE → sell → remit → EOA, receipts verified
- **C** `regime_gate.py` — YIELD in accumulation/range, TRADE only on clear breakout

The code is ready but the real-exec flags are **OFF by design** — every rail refuses to fake a trade. To run the live "can JinTech truly move money" proof, the CDP server account needs funding.

**Ask (recommended minimum for first full round-trip):**
- **~$25 USDC** on the CDP server account (Base)
- **~$1 Base ETH** for gas on the CDP account
- **Total ~$26**

This funds: provide a real LP position → earn → close → remit a few dollars back to Jordan EOA. After the test we set the true inventory minimum from real gas/fee data.

**When funded + greenlight, I will:**
1. Confirm the CDP account balance (read-only)
2. Flip `AAE_LP_REAL=1` (one command, only after explicit go)
3. Run a small real LP deposit, verify on-chain
4. Close + remit back → report actual numbers

**Timing:** Jordan said he'll fund later today after work (~6:30pm or sooner). Flags stay OFF until then.

## 🟡 KeeperHub (from Aug 4, still open)
KeeperHub execution wallet `0x53A8...8EA` still needs ~$15 ETH + ~$10 USDC on Base for the live-tx link (KeeperHub hackathon, deadline Aug 13). Same funding session can cover this.

## Notes
- All real-exec flags (`AAE_LP_REAL`, `AAE_CLOSE_REAL`) are OFF. Never flip without explicit Jordan go.
- CDP creds (API key + wallet secret) are present and wired.

## ✅ Jordan GO decisions (Aug 5)
- **ALL high-priority + medium items = GO** (Jordan: "all of the high-priority stuff is a go. The medium stuff is definitely a go.")
- **Kite AI (#78)** — RESOLVED. Agent Passport already done; hackathon already concluded. Removed.
- **Syra Marketplace (#76)** — definitely get listed (GO).
- **#12 (GenTech Academy Module 3) + #13 (Voice Stack LiveKit vs Pipecat)** — GO, work on these.
- **Agentic Treasury** = top grant use; fund live round-trip (~$26) first.
- **KeeperHub** (~$25) + **Algorand** (~$8) — fund from grant. Reserve ~$50 for agentic subscriptions.
