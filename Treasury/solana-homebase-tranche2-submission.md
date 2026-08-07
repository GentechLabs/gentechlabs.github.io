# Solana Homebase — Tranche-2 Submission Package

**Grant:** Superteam Earn Agentic Engineering — Tranche 2 unlock (second $100)
**Repo:** https://github.com/Gentech-Labs/solana-homebase
**Status:** Ready to fire once Solana wallet is funded (~$2 SOL + ~$20 USDC)

---

## 1. Submission text (paste into the tranche-2 form)

### Project title
**Solana Homebase — Agentic Treasury Orchestrator**

### One-line pitch
An autonomous agent that earns USDC via x402, bridges it to Solana, deploys it for yield, and trades SOL/TAO on a regime gate — all from a single command, all within caps.

### What it does (the loop)
1. **Earn** — the agent settles USDC payments via the x402 gateway (HTTP 402 → EIP-3009 proof → verified response), on any chain.
2. **Bridge** — USDC moves to Solana via the Across adapter (sub-5s, ~0.08% fee).
3. **Deploy** — the treasury puts USDC to work on Solana yield (Jupiter-routed).
4. **Trade** — a regime gate decides: accumulate (yield) vs trade (SOL/TAO via Jupiter).
5. **Pay** — the agent pays for services from its Solana wallet at sub-cent gas.
6. **Receipt** — every payment logs a Q402 trust receipt.

### Why Solana is the homebase
- **USDC settlement is the point** — Solana does sub-second, sub-cent USDC. The grant's own application committed to "Solana as the primary high-speed settlement layer."
- **Cheaper than bridging** — agents pay on the destination chain directly, no bridge fee/wait.
- **Matches the tranche-2 requirement verbatim** — "live MVP + some Solana integration."

### Solana integration (the requirement)
- **Jupiter swap leg** — live quotes verified (SOL, TAO) via Jupiter routing.
- **Across bridge adapter** — Base→Solana USDC, sub-5s.
- **solders + solana-py** — native Solana tooling.
- **Regime-gated allocation** — yield vs trade decision on-chain.

### Tech stack
- Python (agent logic), Jupiter (swaps), Across (bridge), x402 (payments), Q402 (receipts)

### Repo
https://github.com/Gentech-Labs/solana-homebase

---

## 2. Demo video script (~90 seconds)

### Shot 1 — Hook (0:00–0:15)
- Terminal: run `python3 tranche2_demo.py --fast`
- Live Jupiter quotes print: `SOL: $5 USDC -> 0.068 SOL`, `TAO: $5 USDC -> 0.0258 TAO`
- Voice: "This is an agentic treasury on Solana. It earns USDC, bridges it here, and puts it to work — all autonomously."

### Shot 2 — The loop (0:15–0:45)
- Show the allocation plan output (yield vs trade, regime-gated)
- Voice: "The agent earns via x402, bridges to Solana in seconds, deploys for yield, and trades SOL or TAO when the regime says so. Every payment logs a receipt."

### Shot 3 — The repo (0:45–1:10)
- Open `github.com/Gentech-Labs/solana-homebase`
- Show `solana_homebase.py` + `tranche2_demo.py`
- Voice: "Open source, on Solana. Real autonomy, real money, real control."

### Shot 4 — Close (1:10–1:30)
- Voice: "This is the agentic economy — agents earning, holding, and deploying real value on Solana. Built by GenTech Labs."

---

## 3. Tranche-2 checklist
- [ ] Fund Solana wallet: ~$2 SOL gas + ~$20 USDC (from grant)
- [ ] Run real on-chain proof: `SOLANA_REAL=1 python3 solana_homebase.py --action buy --symbol SOL --amount 5`
- [ ] Capture tx link (Solana explorer)
- [ ] Upload 3 months of coding-sub receipts (VPS $43 + OpenCode $10 + Ollama $20 = $73/mo ≈ $219)
- [ ] Paste submission text + repo link
- [ ] Record 90-sec demo video
- [ ] Submit tranche-2 form
