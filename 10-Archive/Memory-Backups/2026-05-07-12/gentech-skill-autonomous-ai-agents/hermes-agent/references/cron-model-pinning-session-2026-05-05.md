# Cron Job Model Pinning — Session 2026-05-05

## Context

On May 5, 2026, Jordan reported mass cron job failures across the Gentech fleet. Investigation revealed:

- **Root cause:** Gateway provider chain was broken during a window of restarts/config changes. The `nous` OAuth provider returned `401: Refresh session has been revoked`, and the fallback chain (`openrouter`) had no valid API key. Jobs with `model: null` inherited this broken chain.
- **Scope:** 17 out of 30 cron jobs showed `last_status: error`. Jobs that ran before (~00:00–03:00 UTC) or after (~13:50+ UTC) the broken window succeeded. Jobs that ran during the window (06:00–12:15 UTC) all failed.
- **Fix applied:** All 30 jobs updated to explicitly pin `model: "mimo-v2.5"` and `provider: "custom:XiaomiMega"` via the `cronjob` tool API.
- **Verification:** `Master Morning Digest` (job `b006812998df`) ran at 14:06 UTC and succeeded, confirming the fix.

## Additional Issue Found

`hackathon-bounty-monitor` (job `ef324b70c014`) has a delivery error: `Telegram send failed: Chat not found` for chat ID `-100386354028`. This is likely a truncated/wrong chat ID — should be `-1003863540828` (HQ). Not fixed in this session (flagged to Jordan).

## Provider Error Window Timeline (May 5, 2026)

| Time (UTC) | Event | Impact |
|------------|-------|--------|
| ~00:00–03:00 | Provider chain working | Pre-shift, daily rotation jobs succeed |
| ~06:00 | Provider chain broken | Brain Review, Sync Check, Mess Hall jobs fail |
| ~06:00–12:15 | Sustained provider failure | All jobs in this window fail (17 total) |
| ~13:50 | Gateway restarted, provider restored | Gentech Watchdog succeeds |
| 14:06 | First pinned-model job runs | Master Morning Digest succeeds ✅ |

## Custom Provider Reference

Config (gentech profile):
```yaml
model:
  default: mimo-v2.5
  provider: custom
  base_url: https://token-plan-sgp.xiaomimimo.com/v1
  api_key: tp-s7yfatimk7astrb11sqrkxcqvlsd3vhdtalj0xavfnoinixm

custom_providers:
- name: XiaomiMega
  base_url: https://token-plan-sgp.xiaomimimo.com/v1
  api_key: tp-s7yfatimk7astrb11sqrkxcqvlsd3vhdtalj0xavfnoinixm
  model: mimo-v2.5
```

Cronjob API format: `provider: "custom:XiaomiMega"` (not just `"custom"`)
Config YAML format: `provider: custom` (resolved via `custom_providers` list)

## All 30 Jobs Updated

Every job now has explicit model/provider pinning:
```
model: mimo-v2.5
provider: custom:XiaomiMega
```

Job IDs: `682e9597b8d6`, `9ecfada01952`, `95777eb3da90`, `3531ebe1d549`, `6f9f1a93155a`, `4835b4241e9d`, `faed4f588aef`, `aebc6f0a84bd`, `c1a4094f2b7f`, `fda9fd75f4a6`, `effa7ee494bb`, `fdaddce49730`, `5a765db9dce2`, `051dcc8d3f11`, `88bd487d79aa`, `9240a0e89275`, `301fb5e35732`, `0c6f528f1685`, `b394020b8319`, `a9880f234c2b`, `cd3a275dbae3`, `dd5a156365f8`, `fc4bead12d22`, `c3053df6b3d3`, `6ea057d66d64`, `7d18ebcb8443`, `61965c05ce7d`, `b006812998df`, `ef324b70c014`, `4e21a92b8c79`
