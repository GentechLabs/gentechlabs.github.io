# Telegraph #49 — Prediction-Market Rail Assessment (2026-08-22)

## The reference
`/root/telegraph-usecases/telegraph-supersignal/` (the "Polymarket Sniper Bot" from the official use-cases repo). This is a real, production-shaped prediction-market agent. We cloned + studied it as reference for our Agentic Treasury rail.

## How it works (the full loop)
1. **Telegraph WS signal feed** — subscribes to intents, receives normalized signals (news/prediction events) via wallet-authenticated WebSocket (`telegraph-signal.service.ts`).
2. **Market matcher** — `market-matcher.service.ts`: LLM matches the signal's question to a live, correctly-timed Polymarket market from candidates.
3. **Trade decision** — `trade-decision.service.ts`: LLM (Groq via Telegraph subnet 102) decides buy_yes/buy_no/wait, with a likelihood-based safety gate (won't force a trade below 50%).
4. **Execution** — `polymarket.service.ts`: fetches active markets from `gamma-api.polymarket.com`, prices, liquidity. Pays Telegraph inference via x402 (Polygon USDC).

## Fit for Agentic Treasury (The Steward)
This is **exactly** the prediction-market rail the brain has been building toward:
- **The Steward (Agentic Treasury)** — the current name for the autonomous treasury agent (GTA was the earlier working name). Core vision: deposit USDC, self-manages — earn, bridge, yield, pay.
- **Delphi Arena** ($10K, ends Aug 24) — same thesis, different venue (Gensyn Delphi info markets). Agent scaffold at `/root/delphi-arena/trade.js`. **SKIPPED 2026-08-22** (didn't go through with it).
- **#63 Somnia × DreamDEX** — prediction markets + AI trading agents (our prototype shipped last night).
- **Agent-Sentiment index** — prediction-market flow as a signal proxy.

The Telegraph signal → match → decide → trade loop is a reusable pattern: **consume Telegraph intelligence, route to a prediction-market rail, execute autonomously.** That's the machine-money loop. This becomes **The Steward's Polymarket rail**.

## Strategic recommendation
- **Miner track (#49):** ship the Token Security miner YAML (done) + 1 more. Cheap, config-only, 75% of score is normalized performance. Post on X (25%).
- **Prediction-market rail:** the supersignal pattern is the template for a GTA prediction-market capability. Reuse it as a Track 3 Application entry OR fold into the Agentic Treasury. Higher strategic value than the $5K Telegraph pool.

## Files
- Miner YAML: `10-Labs/telegraph-miners/gentech-token-security.yaml`
- Reference repo: `/root/telegraph-usecases/` (cloned)
