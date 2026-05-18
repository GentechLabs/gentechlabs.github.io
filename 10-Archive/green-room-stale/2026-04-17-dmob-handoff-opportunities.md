# Handoff: Update opportunity monitoring cron jobs
- **From:** YoYo (Strategies group)
- **To:** Dmob
- **Requested by:** Jordan
- **Date:** 2026-04-17
- **Context:** Jordan wants to consolidate opportunity monitoring. You already have cron jobs scanning hackathons/bug bounties. He wants to expand coverage:
- **Action:** Update existing opportunity cron(s) to include:
  1. **Hackathons** — Encode Club, Gitcoin, ETHGlobal, Avalanche hackathons (keep existing)
  2. **Bug bounties** — Immunefi, Sherlock, Code4rena (keep existing)
  3. **Grant programs** — Ethereum Foundation, Avalanche Academy grants, Gitcoin rounds (add)
  4. **Security audit marketplace** — Areta marketplace (`ethereum.areta.market`) for new audit requests that could be opportunities (add)
  5. **Potential hires/auditors** — Monitor for independent auditors or small firms open to collaboration (add)
  6. **Tool alternatives** — Hyperbrowser pricing/sales as backup browser automation (add, low priority)
- **Key constraint:** Jordan said "see how it scales" — start broad, trim if noisy
- **Deliverable:** Updated cron job(s) with expanded scope, report back on what gets added
