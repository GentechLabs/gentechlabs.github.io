# May 3, 2026 — Auth Revocation Cascade & Fleet Degradation

## Executive Summary

All four agents (Gentech, YoYo, DMOB, Desmond) experienced **Nous Portal OAuth session revocation**, triggering a fleet-wide degradation where 23+ cron jobs failed with `Refresh session has been revoked`. Gateways remained connected to Telegram and could respond to direct messages (using fallback providers), but all scheduled automation requiring Nous API access was broken.

**Key observation**: The auth revocation affected the `Nous OAuth Proactive Refresh` job itself, creating a circular failure loop where the very job meant to prevent this condition was blocked by it.

## Timeline of Events

- **11:18 AM**: First auth failure warnings appear in all agent gateway logs: `Primary provider auth failed: Hermes is not logged into Nous Portal. — trying fallback`
- **11:37 AM**: Series of Telegram disconnects across all agents (likely triggered by auth failures during provider resolution)
- **11:52–12:05 PM**: Window of sustained disconnection; agents offline for ~8 minutes
- **12:05 PM**: Agents reconnect and stabilize; begin using fallback providers
- **12:20 PM**: Gentech encounters `Chat not found` Telegram error (separate issue)
- **12:47 PM**: All agents actively receiving messages and responding; auth failures continue in background

## Error Signatures

```
RuntimeError: Refresh session has been revoked Run `hermes model` to re-authenticate.
```

Locations:
- `gateway.log`: `WARNING gateway.run: Primary provider auth failed: Refresh session has been revoked — trying fallback`
- `errors.log`: `hermes_cli.auth.AuthError: Refresh session has been revoked`
- Cron failures: `last_error: "RuntimeError: Refresh session has revoked Run \`hermes model\` to re-authenticate."`

## Affected Jobs (sample)

**Gentech** (14 of 31 jobs failing):
- Post-Shift, Weekly Skills Update Check
- LayerZero DVN Monitor, hackathon-bounty-monitor
- Nous OAuth Proactive Refresh (ironic circular dependency)
- Vault Manager — Nightly Sweep (OK — uses different provider)

**Desmond** (3 of 6 jobs failing):
- DMOB — Hackathon & Bug Bounty Scout
- 🧠 Memory & Profile Backup
- YoYo — Crypto Watchlist + LP Monitor (Hardened)

**DMOB** (2 of 8 jobs failing):
- Sunday Skill Update Check (requires Nous auth)
- Brain Backup → GitHub (requires Nous auth)

**YoYo** (5 of 27 jobs failing):
- Post-Shift, Weekly Skills Update Check
- Brain Backup → GitHub
- LayerZero DVN Monitor
- x402 Ecosystem Monitor

**Pattern**: Jobs using Nous Research API (`stepfun/step-3.5-flash` throughNous provider) failed. Jobs using other providers (e.g., `stepfun` direct, or local scripts) continued.

## Root Cause Hypothesis

1. **Nous Portal session TTL expired** — OAuth refresh tokens have limited lifetime; manual re-authentication via `hermes model` required
2. **Refresh mechanism blocked** — The `Nous OAuth Proactive Refresh` job itself failed, indicating the refresh endpoint may be unreachable or the refresh token itself revoked
3. **Fallback provider chain exhausted** — Agents fell back to alternative providers (likely StepFun direct or Google), allowing message responses but breaking scheduled Nous-dependent jobs

## Recovery Path

### Immediate (per agent)
```bash
# For each agent profile, run:
hermes model
# Complete OAuth flow in browser/terminal to obtain fresh Nous Portal session
```

### Fleet-wide validation
- Monitor cron job `last_status` transitioning from `error` → `ok`
- Confirm ` Nous OAuth Proactive Refresh` job succeeds
- Check that jobs previously failing with auth errors now complete

## Secondary Issues Uncovered

1. **Chat not found** (Gentech):
   - `telegram.error.BadRequest: Chat not found`
   - Bot may not be member of target chat `-1003863540828` (Gentech HQ) or chat ID changed
   - Affects message delivery but not inbound message reception

2. **Shared ELEVENLABS_API_KEY invalid**:
   - All four agents share same key prefix: `bb158b2f80...`
   - Multiple jobs failing with `401 Invalid API key` for TTS
   - Rotation required fleet-wide

3. **Gateway churn**:
   - 13–21 disconnect/reconnect cycles per agent in 1-hour window
   - Correlated with auth failure window; stabilized after fallback providers engaged

## Diagnostic Checklist (next occurrence)

- [ ] Check gateway logs for `Refresh session has been revoked` within last hour
- [ ] Verify `Nous OAuth Proactive Refresh` job `last_status` == `ok`
- [ ] Count cron jobs by `last_status` per agent (expect >90% OK)
- [ ] Test Nous-dependent job execution (e.g., Daily Digest, Scanners)
- [ ] Validate ElevenLabs API key with a TTS request
- [ ] Confirm Telegram bot membership in all target chats

## References

- Session: `cron_9ecfada01952_20260503_...` (May 3 health check run)
- Related skill: `agent-health-audit` — updated with auth revocation pattern, chat not found error, and global vs profile cron distinction
- Known false positive: `Chat not found` may appear when bot is active but chat metadata changed; verify with direct message test
