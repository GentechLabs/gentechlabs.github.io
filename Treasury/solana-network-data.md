# Solana Network Data — Reference Source

**Source**: https://solana.com/data (Solana Foundation official dashboard, launched June 2026)
**Status**: ✅ Approved reference for treasury reads (Jordan, 2026-07-31)

## What it is
Foundation-run dashboard aggregating **9 data providers** (Allium, Artemis, Birdeye, Blockworks, DeFiLlama, DexPaprika, Dune, Token Terminal, Top Ledger, Uniblock) under one shared schema. Median across providers for latest available day.

## Key metrics tracked
- **Transaction Count (Total)** — includes vote + non-vote
- **Non-Vote Tx (Success / Failed)** — real usage vs. spam/junk
- **SOL Price** — cross-provider median
- **Compute Units** — blockspace demand
- **Fees** — base + priority fees only (SOL)
- **Slots** — block production
- **Fee Payers** — unique wallets paying fees (~new wallet activity proxy)

## Reading the signals (Gentech playbook)
- **Tx up + fees up** → strong real demand, fee competition healthy
- **Tx up + fees flat/down** → activity up, priority-fee pressure easing; blockspace healthier, less spam competition
- **Fee payers spiking** → new wallets entering; growth signal
- **Failed non-vote tx climbing** → possible spam, botting, or congestion issues — check

## Reference snapshot (2026-07-31)
- Tx total: 299.4M (+1.1%)
- SOL: $74.3 median (live ~$73.6)
- Compute units: 32.5M (+3.5%)
- Fees: 7.5K SOL (−3.1%)
- Fee payers: up to ~8M/day

## Related resources
- SDA (open source repo powering dashboard): github.com/solana-foundation/solana-data-aggregator
- RPC Latency Monitor: github.com/solana-foundation/rpc-latency-monitor
- Tx Sender Metrics (Grafana): rpclatency.grafana.net public dashboard
- Allium institutional data, Lightspeed dashboards, Dune, tokens.xyz
