# PentAGI — Project Notes

**Status:** ⚠️ MARKED FOR REMOVAL — superseded by Hermes multi-agent setup
**Decision:** Redundant. Hermes agents (YoYo, Dmob, Desmond, Gentech) cover the orchestration layer. Cygent (Cyfrin) covers AI security testing. PentAGI adds cost (OpenRouter credits) and maintenance (Docker) without unique value.
**Last Verified:** April 12, 2026 (deployment wiped since)
**Action:** Uninstall skill, clean up any remnants

## What It Was
- Self-hosted PentAGI instance (AI agent platform)
- Ran on VPS at https://127.0.0.1:8443
- Admin creds: [PENTAGI-ADMIN-REDACTED] / admin
- Nous API integration was attempted but returned 404 from Go client

## Current State
- Service is DOWN as of April 16, 2026
- Not urgent — Jordan wants to revisit as a future project
- Could be useful as a self-hosted agent orchestration layer

## TODO (When Revisiting)
- [ ] Dmob: assess if Go client can be fixed for Nous API
- [ ] Evaluate if PentAGI still fits the architecture (Hermes agents may have superseded it)
- [ ] Check VPS resource availability before restarting (currently 19% disk, 5.7G RAM used)
- [ ] Decide: standalone tool vs integrated with Gentech agent system

## Notes
- May have been superseded by the current Hermes multi-agent setup
- Worth a conversation with Dmob before investing more time
- Could serve a different purpose than Hermes (security testing? pen testing automation?)

---

#project:pentagi #status:pinned #collab:dmob #agent:yoyo
