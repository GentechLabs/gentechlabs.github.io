# Phase 1 Implementation Checklist — Composio Pilot

**Owner**: DMOB (Labs)
**Timeline**: Week of 2026-05-03 → 2026-05-10
**Goal**: Single production integration live (Google Workspace or Slack) with monitored usage

---

## Pre-flight

- [ ] Get Composio API key from dashboard
- [ ] Add `COMPOSIO_API_KEY` to `~/.hermes/.env`
- [ ] Run `hermes doctor` — confirm no config conflicts
- [ ] Verify Python SDK: `python -c "from composio import Composio; print(Composio().tools.list())"`
- [ ] Create `02-Labs/Audits/Composio-Pilot-Phase1.md` (empty for now)

---

## Day 1: Google Auth Pilot (P0)

- [ ] Link Google account: `python -c "from composio import Composio; Composio().integrations.link('gmail')"`
- [ ] Grant scopes: Gmail + Calendar (minimum viable)
- [ ] Verify connection: `python -c "from composio import Composio; print(Composio().integrations.list())"`
- [ ] **Test read**: `GMAIL_SEARCH_EMAILS` with query `is:unread`
  - Expected: JSON array of ≤5 messages
  - If fail → check OAuth dashboard, re-link if needed
- [ ] **Test write**: `GMAIL_SEND_EMAIL` to your own address (dry-run subject "[TEST] Composio pilot")
  - Expected: `{"status":"sent","id":"..."}`
  - Confirm email received
- [ ] Document results in `02-Labs/Audits/Composio-Pilot-Phase1.md`
  - Include: OAuth flow screenshots (if any), errors encountered, fix applied

**Success criteria**: Both read + write actions succeed on first try without manual token intervention.

---

## Day 2: Slack Webhook Pilot (P1)

*Alternative path if Google blocked by org policy.*

- [ ] Link Slack workspace via Composio dashboard
- [ ] Grant: `chat:write`, `chat:write.public` (minimum)
- [ ] Test: `SLACK_POST_MESSAGE` to `#general` or a test channel
  - Message: `"Composio pilot — DMOB online"`
- [ ] Verify message appears with correct formatting
- [ ] Log action in `02-Labs/Audits/Composio-Pilot-Phase1.md`

**Success criteria**: Message posted within 2 seconds, no rate-limit errors.

---

## Day 3: Wrapper Script

Create reusable wrapper to avoid repeating auth boilerplate:

- [ ] Write `02-Labs/scripts/composio_client.py` (see `composio-quick-start.md` for template)
- [ ] Make executable: `chmod +x`
- [ ] Test: `./composio_client.py GMAIL_SEARCH_EMAILS '{"query":"is:unread"}'`
- [ ] Add to `~/.hermes/skills/devops/managed-integration-platforms/scripts/` (symlink or copy)
- [ ] Document usage in skill README if not already there

---

## Day 4: Replace One Production Webhook

**Candidate**: `02-Labs/scripts/opportunity_scanner_daily.py` (currently uses Slack webhook)

- [ ] Open script, locate `requests.post(WEBHOOK_URL, json={...})`
- [ ] Replace with: `python composio_client.py SLACK_POST_MESSAGE '{"channel":"#opportunities","text":"..."}'`
- [ ] Test locally: `python opportunity_scanner_daily.py --dry-run` (if supported)
- [ ] Run actual scan once (monitor Slack channel)
- [ ] Confirm message arrives with same content quality
- [ ] Commit change (if using git) with message: `chore: replace Slack webhook with Composio managed`
- [ ] Archive old webhook URL (rotate at provider, mark as deprecated in vault)

---

## Day 5: Monitoring & Logging

- [ ] Create `02-Labs/Audits/Composio-Usage-YYYY-MM.md` (current month)
- [ ] Add wrapper hook to log every invocation:
  ```python
  def log(action, params, result):
      # append JSON line to audit file
  ```
- [ ] Verify file writes after each test call
- [ ] Add basic metrics: total calls today, success rate
- [ ] Set up cron reminder: `0 9 * * * /root/vaults/gentech/02-Labs/scripts/check_composio_usage.py` → send Slack summary if >80% of free tier used

---

## Day 6: Review & Decision

- [ ] Count total pilot invocations (should be < 100)
- [ ] Calculate actual cost (likely $0.00 on free tier)
- [ ] Document lessons learned:
  - OAuth flow friction?
  - Error messages clear?
  - Rate limits hit?
  - Latency acceptable?
- [ ] Recommendation: **Proceed to Phase 2**? Yes/No/Conditions
- [ ] Write summary in `02-Labs/Audits/Composio-Pilot-Phase1.md`

---

## Day 7: Cleanup / Handoff

- [ ] If proceeding: create `02-Labs/Audits/Composio-Rollout-Plan.md` (Phase 2–3 tasks)
- [ ] If stopping: document blockers and alternative plan
- [ ] Notify team in GenTech HQ: summary + next steps
- [ ] Update `managed-integration-platforms` skill with any corrections found

---

## Rollback Plan

If any test fails irrecoverably:

1. **Re-enable old skill**: `hermes skills enable google-workspace` (if disabled)
2. **Restore webhook URLs** from vault backup (pre-change commit)
3. **Remove COMPOSIO_API_KEY** from `.env` (or comment out)
4. **Stop all Composio-linked accounts** in dashboard (Delete connection)
5. **Revert** script changes from git

---

## Success Metrics

| Metric | Target | Actual |
|--------|--------|--------|
| OAuth flow completion time | < 5 min | |
| First tool call latency | < 3 sec | |
| Pilot invocations (total) | ≥ 20 | |
| Zero auth errors after linkage | Yes | |
| Cost incurred | ≤ $0.00 | |
| Production webhook replaced | 1 | |

---

**After completing this checklist, proceed to Phase 2 without further approval.**
