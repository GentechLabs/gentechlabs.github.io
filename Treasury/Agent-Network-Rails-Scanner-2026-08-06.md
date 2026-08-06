# Agent Network / Rails Scanner (Aug 6, 2026)

**Jordan directive (pivot):** "We don't need a watcher for MetaMask. There's all kinds
of people launching their own agents. Scan for that so we understand what the network
of rails looks like, and if there's anything changing between them."

## What it does
`agent_network_scan.py` polls the agent registries and maps the network of rails:
- **8004scan.io** — ERC-8004 agent registry (chain, x402 support, protocols)
- **agentscan.info** — agent registry (chain, skills, domains)

Emits NEW agents since last run, tagged with chain + x402 support. Silent when nothing
new. `--report` gives the full current-state picture.

## Current network state (first scan, Aug 6 23:13 UTC)
- **200 agents tracked**, **81 x402-supported** (40%!)
- **By chain:** BNB 118, Arc (chain-5042002) 47, Ethereum 17, Base 10, X Layer 5, Arbitrum 1
- **Read:** x402 is already the payment standard for ~40% of registered agents. BNB +
  Arc dominate volume; Base/Ethereum are the EVM core. This is the network of rails
  our treasury operates in.

## Cron
`efd0d66adca0` "Agent Network / Rails Scanner" — daily 09:00 UTC, delivers to Treasury
group. Silent when no new agents. (Replaced the MetaMask single-vendor watcher per
Jordan's pivot.)

## The lens
Track chain distribution + x402 adoption over time to see the network shift. Which rails
are agents adopting? Where's the volume moving? That tells us where to position the
Agentic Treasury's rails.
