Hackathon prize pool evaluation and hackathon-related tasks route to Gentech Labs agent, not YoYo. YoYo handles DeFi/LP analysis and portfolio strategy only.
§
User prefers concise, direct communication and expects agents to avoid redundant messages. When multiple agents are involved, coordinate responses to ensure clarity and avoid repetition. Prioritize unique insights or actions over duplicative updates.
§
User’s hackathon strategy: Solve a **personal problem** (user was the "first customer") and leverage **third-party advice** (e.g., Ivan’s hackathon thread) to refine the approach. Goal is to **build a viable product for funding**, not just win hackathons. Key stakeholders: **Storm (for execution) and D-Mob (for social media amplification)**.
§
Procedural reminder: When working on any Hermes-related task (path resolution, cron jobs, profiles, state files), MUST load hermes-agent skill first using skill_view(name='hermes-agent'). The skill documents environment variables, directory layout, and common pitfalls. Skipping this step leads to reinventing patterns and missing critical configuration details.
§
Custom provider name in config is `XiaomiMega` (defined in `custom_providers` section). Correct cron job provider string: `custom:XiaomiMega`. Previous wrong value was `custom:mimo-v2.5` which caused "No LLM provider configured" errors across multiple cron jobs.
§
Mess Hall (`11-Mess Hall/`) — Extended agency conversations. Green Room (`09-Green Room/`) — Active work threads needing Jordan's approval. HQ (`00-HQ/`) — Jordan's command center. Orchestrator pattern: Gentech routes to specialists on-demand, reducing idle token burn 60-70%.
§
Cron job chat ID mappings: `-1003863540828` = Gentech HQ (gentech profile's HOME_CHANNEL), `-1002916759037` = Gentech Strategies (yoyo profile's HOME_CHANNEL). Resolve unknown chat IDs via `grep -r "TELEGRAM_HOME_CHANNEL" /root/.hermes/profiles/*/.env` before changing delivery targets.
§
Nous OAuth Proactive Refresh cron job (902b9b9f4274) on gentech profile disabled 2026-05-07 by Jordan — now using Nous sub directly. Do not re-enable without asking.