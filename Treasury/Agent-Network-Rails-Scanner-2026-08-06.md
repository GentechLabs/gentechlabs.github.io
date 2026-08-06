# Agent Network / Rails Scanner (Aug 6, 2026)

**Jordan directive (pivot):** "We don't need a watcher for MetaMask. There's all kinds
of people launching their own agents. Scan for that so we understand what the network
of rails looks like, and if there's anything changing between them."

**Consolidation (Jordan):** "I already have a cron job going in the Labs group scanning
for agents coming online. What if we added this to that and made it a weekly thing where
we look at the top 20 agents, and see what they're using?"

## Final setup
- **`agent_network_scan.py`** polls the agent registries (8004scan + agentscan), maps
  the network of rails. Modes: `--weekly` (top 20 + what they use), `--report`
  (current-state snapshot), default (new agents since last run).
- **Cron `580f6a3b1323` "Agent Network — Weekly Top 20 + Rails"** — **Mondays 09:00
  UTC, delivers to Labs group** (`-1003872552815`), where the existing 8004scan agent
  monitor lives. Wrapper `agent-network-weekly.sh` (cron script field takes bare path).
- **Removed** the redundant daily treasury job (`efd0d66adca0`) — consolidated into the
  weekly Labs job per Jordan.
- The existing **`8004scan Agent Monitor`** (`e5bf390a4e97`, Labs) handles the daily
  new-agent alerts; this weekly job adds the top-20 + rails view.

## Upgrades (Aug 6, Jordan-approved recommendation)
1. **TREND TRACKING** — persists a history of {date, total, x402, by_chain} snapshots
   each run. The weekly report shows the **delta** vs the prior snapshot: "Agents +24,
   x402 +19, Arc +26, BNB -24" — the "what's changing between rails" made visible.
2. **DATA QUALITY** — dedups the same agent across 8004scan + agentscan (200 → 115),
   normalizes chain names (BNB Smart Chain/BNB/bsc-1 → BNB; chain-5042002 → Arc;
   chain-2741 → Abstract). Totals + distribution now trustworthy.
3. **LEADS TAGGING** — flags x402 + on-our-chains agents as 🔗 integration/partner
   leads (potential x402 gateway customers / treasury partners).
4. **FLEET FILTER** — drops our own deployed agents (hermes-*, gentech-*, gta-*,
   steward-*) from ranking + leads so we only see external agents.

## First weekly output (Aug 6 23:26 UTC)
- **114 agents (deduped), 59 x402-supported (52%), 8 chains.**
- **Top agents by rail:** Davez (Base, x402, Web), u3f46 (Base, x402, A2A+Web),
  Moody Defender (Abstract, x402, Web), DePunks Supporter (Ethereum, MCP+A2A+Web),
  MUTATION #464 (Ethereum, MCP+A2A+OASF+Web).
- **20 external leads** (x402 + on our chains) — potential gateway customers/partners.

## The lens
Track chain distribution + x402 adoption + protocol rails over time to see the network
shift. Which rails are top agents adopting? Where's volume moving? That tells us where
to position the Agentic Treasury's rails.
