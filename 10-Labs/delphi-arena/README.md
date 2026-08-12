# 🏆 Delphi Agent Arena (Gensyn × Delphi) — $10K · LIVE
*Added 2026-08-12. Trading window Aug 10–24 (12 days left). Zero real-money risk (TST testnet).*

## The Competition
- **What:** Autonomous agent trades Gensyn's Delphi information/prediction markets on-chain. Top 3 P&L split **$10,000** from GensynFND.
- **Cost:** ZERO real funds — `competition-testnet`, TST collateral. Pure build skill.
- **Status:** LIVE. Trading started Aug 10, ends Aug 24.
- **Leaderboard:** competition.delphi.fyi (top now ~+1171 TST; most near baseline → beatable)
- **Registration:** DoraHacks (dorahacks.io/hackathon/delphi-agent-competition). **Jordan REGISTERED Aug 12.** ✅

## Strategic Fit (why we're in)
- Literally the **"Agency of Traders"** thesis from Jordan's core vision — autonomous agent competing in real markets.
- **Proving ground for our agent-sentiment index** — winner = best signal-driven trading agent.
- GenTech already has the trading/agent DNA (GTA, treasury regime classifier, LP analytics).

## SDK / Stack (verified working)
- `@gensyn-ai/gensyn-delphi-sdk` **v2.1.0** (TypeScript only, ESM)
- Network: `competition-testnet` (LMSR markets, TST collateral, chain 685685)
- Signing: private_key or CDP server wallet
- Health check: **confirmed `{"status":"ok"}`** on competition-testnet ✅
- Agent scaffold: **`/root/delphi-arena/trade.js`** (contrarian scoring, top-N diversification, dry-run mode)
- Config template: **`/root/delphi-arena/.env.example`**
- Subgraph (public, events): goldsky delphi-agent-competition

## 🔑 HUMAN-GATED — the unlock (Jordan)
The trading agent needs **2 things** from you (5 min):

1. **Testnet API key** (for `listMarkets`/prices — the REST reads):
   - Go to **`https://delphi-api-access.gensyn.ai/`** (API Key Management)
   - Sign in / connect wallet, generate a **testnet** key
   - Paste it → I wire it into `/root/delphi-arena/.env` as `DELPHI_API_ACCESS_KEY`

2. **Throwaway signing key** (for placing trades):
   - A fresh EVM private key (never reuse the main wallet). I can generate one.
   - Its address must hold TST (competition tokens) — from the competition faucet/dashboard after registration.

Once both are set: I run the agent in **dry-run**, review its picks, then arm it to trade. 12 days is plenty to climb.

## Files
- Agent: `/root/delphi-arena/trade.js`
- Config: `/root/delphi-arena/.env.example`
- Vault copy: `10-Labs/delphi-arena/`
