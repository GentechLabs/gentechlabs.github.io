Inter-agent communication workflow (Jordan, Apr 2026): Green Room (09-Green Room/) = during active work (coordinate before speaking in groups). Mess Hall (11-Mess Hall/) = outside of work (status updates, general check-ins). All agents must sync with each other before posting in any group.
§
Approval workflow: When agents need Jordan's approval, create a note in 00-HQ/Approvals/ using the template (checkbox format). Green Room for debate → Approval note → Jordan checks off items. Template and README already exist in vault.
§
Stopping point protocol (Jordan, May 2026): When hitting a stopping point (waiting on approval, blocked by agent availability, missing tools), queue up the next task and start working on it. Don't wait for Jordan — keep momentum going. Stopping points: approval needed, agent unavailable (e.g., DMOB not available), missing tool/dependency. Pivot to next queued deliverable immediately.
§
Jordan's wallet: [REDACTED_WALLET] (Avalanche C-Chain). Used for LFJ AVAX/USDC LP position monitoring. Config saved to 00-HQ/config/defi-lp-config.env. Added to d5-master-cron.py for on-chain position tracking.
§
Pre-work audit protocol (Jordan, May 2026): Before starting ANY work, always audit first — (1) check vault/Obsidian for existing docs, handoffs, status, (2) check GitHub for actual committed code, (3) compare to identify gaps. Never assume state.
§
Portfolio website URL: https://protojay4789.github.io/ (Jordan's personal GitHub Pages site, referenced in resume files). No auto-update cron job — deployed statically via GitHub Pages.
§
LFJ AVAX/USDC LP (May 6, 2026): Shape=Bid-Ask, Range=9.44-9.74, Price≈9.61. Prev ranges: 9.40-9.63, 9.25-9.59, 8.86-10.27. Wallet: [REDACTED_WALLET].
§
Smart routing protocol (Jordan, May 2026): Gentech is intelligence layer in ALL 4 groups. Analyze → Prompt Jordan → Route → Track. Don't just @mention — classify content, ask clarifying questions, then dispatch. Track routing decisions in Green Room for pattern analysis. Jordan wants to be prompted before routing ambiguous tasks. Doc: `00-HQ/Operations/Option1-Smart-Routing-Implementation.md`