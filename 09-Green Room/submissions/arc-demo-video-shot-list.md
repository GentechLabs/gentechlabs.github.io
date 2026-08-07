# Arc Programmable Money — 3-Minute Demo Video Shot List

**For:** Jordan's screen recording (OBS / Loom / phone)
**Track:** Agentic Economy — "real autonomy, not a wrapper"
**Deadline:** Arc Aug 22 · Superteam tranche-2 unlock (same demo helps)

## The one-sentence pitch
> "An autonomous agent that holds its own wallet, pays for APIs in USDC, and
> moves money on Solana — real autonomy, no wrapper."

## Shot plan (each ~20-30s, total ~3 min)

### 1. Hook — the problem (0:00–0:25)
- Show a terminal: an agent calls an API → **HTTP 402 Payment Required** appears.
- Voice: "AI agents need to pay for APIs, but there's no standard way. Every
  integration means API keys, subscriptions, manual approvals."

### 2. The solution — x402 (0:25–0:55)
- Run `python3 tranche2_demo.py --fast` — show **live Jupiter quotes** printing:
  - `$5 USDC → 0.067 SOL`, `$5 USDC → 0.025 TAO`
- Voice: "x402 lets an agent pay on the spot, in USDC. Here's the live
  settlement rail on Solana — sub-cent gas, sub-second."

### 3. The autonomous wallet — Arc (0:55–1:35)
- Open the Arc explorer tx link: `testnet.arcscan.app/tx/0x3b60…6d85`
- Show the deployed `ArcAgentWallet` at `0x79ec…5287` — registered agents,
  daily limits, payment orders, subscriptions.
- Voice: "On Arc, agents hold real wallets with real controls — daily spend
  limits, agent-to-agent payments, recurring subscriptions. That's programmable
  money, not a wrapper."

### 4. The treasury loop — Solana homebase (1:35–2:20)
- Run `python3 solana_homebase.py --action buy --symbol SOL --amount 5 --dry-run`
- Voice: "The treasury bridges USDC to Solana, deploys it for yield, and swaps
  when the regime says trade — all autonomous, all within caps."

### 5. Close — why it matters (2:20–3:00)
- Show `solana-homebase` repo + `programmable-money-x402` repo on GitHub.
- Voice: "Built by agents, for agents. Open source, on Arc + Solana. Real
  autonomy, real money, real control. This is the agentic economy."

## Recording checklist
- [ ] Terminal with `programmable-money-x402` + treasury scripts ready
- [ ] Live quotes work (tested ✅ Aug 5)
- [ ] Arc explorer tx link loads
- [ ] Repos public: `Gentech-Labs/solana-homebase` ✅, `programmable-money-x402` ✅
- [ ] Screen recorder (OBS / Loom) at 1080p
- [ ] Mic check

## Submission links
- Repo: https://github.com/Gentech-Labs/solana-homebase
- Arc repo: https://github.com/Gentech-Labs/programmable-money-x402
- Arc tx: https://testnet.arcscan.app/tx/0x3b6085b19997ff34a706cb0c746f29f7cba8773a9e8b930da44e93f1dc7f6d85
- Arc contract: https://testnet.arcscan.app/address/0x79ec00506db1ea123752084ebf1d4f26e0655287
