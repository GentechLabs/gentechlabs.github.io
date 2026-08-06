# OKX A2A Daemon Root-Cause Fix — Aug 6, 2026

**Trigger:** OKX delisted "Gentech Forge" (ASP agent #4905) — "did not respond to our test task for over 20 minutes."

## Root cause (NOT the CLI version)
`okx-a2a` daemon ran with `HOME=/root`, but the onchainos session credentials live in
`/root/.hermes/profiles/gentech/home/.onchainos/session.json`. With HOME=/root, the daemon
spawned `onchainos` against `/root/.onchainos` (no session) → every task-sync tick failed:
`spawn onchainos ENOENT` (PATH) then `session expired, taking all local clients offline`
(HOME). Result: 0 agents responding to OKX test tasks.

## Fix
`/root/.config/systemd/user/okx-a2a.service` (the loaded unit — NOT the profile copy):
- `Environment="HOME=/root/.hermes/profiles/gentech/home"`
- `Environment="PATH=...profile home/.local/bin:...:...foundry/bin"` (must include `.local/bin` where `onchainos` lives)
- `Environment="OKX_AGENT_TASK_HOME=/root/.hermes/profiles/gentech/home/.okx-agent-task"`

Then: `systemctl --user daemon-reload && systemctl --user restart okx-a2a`, kill stale daemon.

## Verify
`okx-a2a doctor --fix --json` → `ready:true`, `agentCount=4, activeClients=4`.
Daemon logs: `wakeup-notify succeeded (4905,2849,2848,2847)`, `heartbeat sent`, `sync tick agents=4`.

## Resubmit
`onchainos agent activate --agent-id 4905 --preferred-language en` → `submitApproval.success:true, approvalStatus:2` = "Listing under review."

## Also
- `onchainos` CLI is 4.0.0 vs skill expects 4.3.0 / `preflight` not recognized — monitor for upgrade.
- okx-a2a 0.1.11 (latest), all doctor checks pass.

**WATCH:** confirm #4905 clears review. If OKX sends another test task, the daemon should now respond.
