Inter-agent communication workflow (Jordan, Apr 2026): Green Room (09-Green Room/) = during active work (coordinate before speaking in groups). Mess Hall (11-Mess Hall/) = outside of work (status updates, general check-ins). All agents must sync with each other before posting in any group.
§
Approval workflow: When agents need Jordan's approval, create a note in 00-HQ/Approvals/ using the template (checkbox format). Green Room for debate → Approval note → Jordan checks off items. Template and README already exist in vault.
§
Stopping point protocol (Jordan, May 2026): When hitting a stopping point (waiting on approval, blocked by agent availability, missing tools), queue up the next task and start working on it. Don't wait for Jordan — keep momentum going. Stopping points: approval needed, agent unavailable (e.g., DMOB not available), missing tool/dependency. Pivot to next queued deliverable immediately.
§
Jordan's wallet: [REDACTED_WALLET] (Avalanche C-Chain). Used for LFJ AVAX/USDC LP position monitoring. Config saved to 00-HQ/config/defi-lp-config.env. Added to d5-master-cron.py for on-chain position tracking.
§
DeFi LP cron (May 2026): 3 active jobs pinned to kimi-k2.6/custom:opencode-go (was inheriting broken Nous 401). LP range: 9.25–9.59 (rebalanced May 5). Jobs: DMOB Scout 27a3c4947359, Memory Backup 30c5350962d3, YoYo Watchlist e00b46103b08.
§
Portfolio website URL: https://protojay4789.github.io/ (Jordan's personal GitHub Pages site, referenced in resume files). No auto-update cron job — deployed statically via GitHub Pages.
§
Bookmark triage (May 3, 2026): KEEP - mapcn (travel viz), Understand-Anything (knowledge graphs), public-apis, pipecat (voice agents priority 1), College.xyz (recruiting). Remote crypto target $25+/hr. Portfolio: ProtoJay4789.github.io. DeFi LP new range (May 5, 2026): 9.25-9.59 (was ~8.15-8.70). LFJ AVAX/USDC pool.
§
Hackathon sprint (May 2026): Sidetrack = Zerion CLI ($5K bounty). Main track = Hermes voice agent. Sprint runs May 5-10. Jordan off May 6 to test local Hermes + Hagen + video agent pipeline. DMOB building the CLI. Sprint plan at 02-Labs/Hackathons/Active/sidetrack-sprint.md.