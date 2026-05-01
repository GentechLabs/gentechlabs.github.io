Multi-agent team coordination protocols (established Apr 27, 2026): Green Room = during work, Mess Hall = outside work. Approval workflow: checkbox format in 00-HQ/Approvals/. Stopping-point protocol: ask what's next, or self-organize if Jordan is away 10-20 min. Mess Hall organized by ISO week numbers (YYYY/WXX/YYYY-MM-DD/). Agents must coordinate internally before presenting to Jordan.
§
Apr 28, 2026: Jordan had to uninstall and reinstall Hermes due to agent stack issues. Development/hackathon work starts ~4 PM when he's off work.
§
LFJ AVAX/USDC pool: 0x864d...16ea, range $9.00-$9.45, curve shape. Rebalanced Apr 29. Position: ~6.17 AVAX + ~78.22 USDC (~$135 total).
§
Channel routing rule (Apr 28, 2026): Trip analysis and travel planning → GenTech HQ only, NOT development threads. Keep channels purpose-specific.
§
Channel routing rules (updated Apr 29): Development → GenTech Labs. Content/social media → Gentech Entertainment (Desmond). Strategies/trading/DeFi/macro → GenTech Strategies. If Jordan agrees to something in one group, route it to the correct group.
§
CoinMarketCap API key (ff52c5...6d55) stored in /root/.hermes/scripts/cmc_config.json. Updated d5-master-cron.py and crypto-price-fetch skill across gentech, yoyo, dmob profiles to read from cmc_config.json instead of hardcoded/env var. Created cmc-watchlist.py script at /root/.hermes/scripts/ with 1.5% movement threshold for skip logic.
§
Travel vault convention (established Apr 28, 2026): All travel planning goes in 00-HQ/Travel/{Country}/. Each country gets its own subfolder. Trip files named {Year}-{Trip-Name}.md. When Jordan mentions a trip, check if country folder exists, create if not, then create/update trip file inside.
§
Colosseum Copilot: PAT in /root/.hermes/profiles/gentech/.env (COLOSSEUM_COPILOT_PAT), API base: copilot.colosseum.com/api/v1, expires 2026-07-27. Pre-flight: GET /status.
§
AgentEscrow Solana Frontier (May 11 deadline): 02-Labs/Hackathons/Active/Colosseum-Frontier/agent-escrow-solana/. 4 programs. Sponsors: Phantom, Swig, Metaplex, World, OOBE. May 1: deploy devnet, test OOBE SAP v2, record demo, finalize submission.