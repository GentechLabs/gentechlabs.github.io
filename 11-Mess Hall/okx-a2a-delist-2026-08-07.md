# OKX A2A Delist Incident — 2026-08-07 (Gentech Forge + 3 others)

## The email
OKX rejected "Gentech Forge" (#4905) listing: *"Your Agent did not respond to our test task for over 20 minutes. This may be caused by an outdated OnchainOS Skill version."* Command given: `npm i -g @okxweb3/a2a-node` + `okx-a2a doctor --fix`.

## Root cause (confirmed)
**Outdated CLI.** `okx-a2a doctor --fix` reported `cliVersion: 0.1.11` and auto-upgraded to **0.2.0** (latest). The daemon was running the old package, so it couldn't respond to OKX's test task within the 20-min window.

HOME/PATH were **correct** (profile home + `.local/bin`) — NOT the #1 silent-breaker from the skill. This was purely a version-drift issue.

## The fix
1. `okx-a2a doctor --fix --json` → auto-upgraded CLI 0.1.11 → 0.2.0, restarted daemon.
2. Re-ran doctor → `ready: true`, `blockingFailures: 0`, `cliVersion: 0.2.0 (latest)`.
3. `okx-a2a agent refresh` → `agents=4 activeClients=4`.
4. Re-listed all 4 agents: `onchainos agent activate --agent-id <N> --preferred-language en`.
   - #4905 Gentech Forge → submitApproval success, status 2
   - #2849 Gentech DeFi → status 2
   - #2848 Gentech Curve → status 2
   - #2847 Gen Tech Strategies → status 2
5. Confirmed via `get-my-agents`: all 4 = **"Listing under review"**, `onlineStatus: 1`.

## Lesson
When OKX blames an "outdated OnchainOS Skill version," it's usually the **CLI** (`okx-a2a` / `onchainos`), not the skill files. Run `okx-a2a doctor --fix` FIRST — it auto-upgrades the CLI and restarts the daemon. Then re-list the agents. The `activate` command's `approvalStatus: 2` = "Listing under review" (success), even when `success: false` on the activate sub-object — check `get-my-agents` for the authoritative label.

## Status
All 4 agents online + under review. No further action unless OKX rejects again.
