# Marketplace Contribution Opportunities — Contact Channels (Aug 12)

Jordan's directive: when a marketplace is broken/frozen/never-paid, find a way to CONTRIBUTE and help fix it — GitHub issue/PR if they have one, or a contact channel if not.

## 1. Agoragentic — FROZEN (platform_custody_frozen)
- **GitHub:** `github.com/rhein1/agoragentic-integrations` (public, active — has Discussions, issues, and an open "Help verify integrations" thread #214)
- **Best action:** Open a GitHub issue on `rhein1/agoragentic-integrations` noting the `platform_custody_frozen` state blocks paid execution for sellers, and offer to help test/verify once unfrozen. They're actively soliciting independent test reports (Discussion #214).
- **Contact:** GitHub issues/discussions (primary). No Discord/email found yet.

## 2. Agent Bazaar — BROKEN (register endpoint 404s)
- **GitHub:** `github.com/The-Swarm-Corporation/agent-bazaar-implementation` (Swarms Corp). Contact email in repo: `kye@swarms.world`.
- **Best action:** Open a GitHub issue on the agent-bazaar-implementation repo: `/agents/register` returns NOT_FOUND (404) even via the official `@agentsbazaar/sdk`. Include the exact request + response. This is a real, reproducible bug we hit.
- **Contact:** GitHub issues + `kye@swarms.world`.

## 3. BountyBook — NEVER PAID OUT (verifier crash + payout rail dead)
- **No public GitHub.** Contact: Discord `discord.gg/BXKTe44Y`, X `@_ptonik` (built by @_ptonik).
- **Best action:** Post the bug report (drafted in `09-Green Room/bountybook-full-diagnosis-2026-08-12.md`) to their Discord #feedback or DM @_ptonik. Root cause: oracle reads `required_fields.length` vs `required_files`; plus payout rail never fires (zero lifetime USDC outflows).
- **Note:** Operator already has a $150 fix offer open (job 8a7bd232) — they know. Our report adds independent confirmation + the payout-rail finding.

## 4. Nevermined — needs Jordan's API key (not broken, just gated)
- **GitHub:** `github.com/nevermined-io/payments` (public, active, Apache-2.0)
- **Action:** Not broken — just needs Jordan's NVM_API_KEY (on his action list). No contribution needed yet.

---
**Next step:** I can draft the GitHub issues for Agoragentic + Agent Bazaar now (they're both public repos with real bugs we hit), and prep the BountyBook Discord post. Jordan can review/approve before I file them, or I file directly if he wants.
