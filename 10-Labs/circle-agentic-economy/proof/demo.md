# Proof Item 2 — Recorded Demo (shot list)

A real, verifiable USDC transaction executed by the agent. No human checkout.

## Shot list (3-minute video)

1. **Intro (0:00–0:20)** — "An AI agent paying another agent's inference
   service in USDC." Show the architecture diagram.

2. **The agent boots (0:20–0:50)** — Circle Agent Stack agent fetches the
   setup skill, creates an agent wallet on Base. Show `circle wallets create`.

3. **Discovery (0:50–1:20)** — Agent searches the Circle Agent Marketplace for
   the GenTech SIE service, inspects price + endpoint.

4. **The payment (1:20–2:00)** — Agent pays with a USDC nanopayment. Show the
   on-chain tx hash + the agent's Circle wallet address. **This is the money
   shot** — must show a real tx on a block explorer (Basescan).

5. **The call (2:00–2:30)** — Agent calls the SIE service, gets embeddings
   back. Show the HTTP 200 response.

6. **Outro (2:30–3:00)** — "One agent paid another agent's service. That's
   the machine-money loop." Show the wallet address + explorer URL again.

## Requirements

- Real USDC transaction (not simulated)
- Agent-driven (no human clicking checkout)
- On-chain proof visible (tx hash + explorer)
- Hosted on GCP (base competition rule)
