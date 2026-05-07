# Cron Provider Troubleshooting — May 5, 2026

## Context
All 3 Desmond cron jobs were erroring with 401 after the `custom:opencode-go` (Nous Research) provider died.

## Discovery Path

### Step 1: Check error logs
```bash
cat /root/.hermes/logs/errors.log | tail -30
```
Found: `401 - {'status': 401, 'message': 'Your API key is invalid, blocked or out of funds.'}`

### Step 2: Check available providers in config.yaml
```bash
cat /root/.hermes/config.yaml | grep -A 10 "providers\|custom_providers"
```
Found TWO Xiaomi providers:
- `xiaomi` (built-in): key `tp-swwfjocru348e2fwqo84bqk4wzdoo9bd15slwfmmbpysklvx`
- `custom:XiaomiMega`: key `tp-s7yfatimk7astrb11sqrkxcqvlsd3vhdtalj0xavfnoinixm`

### Step 3: First fix attempt — switch to `xiaomi`
```bash
hermes cron update e00b46103b08 --model '{"model":"mimo-v2.5","provider":"xiaomi"}'
```
Result: Still 401. The built-in `xiaomi` provider works interactively but fails in cron sessions.

### Step 4: Second fix — switch to `custom:XiaomiMega`
```bash
hermes cron update e00b46103b08 --model '{"model":"mimo-v2.5","provider":"custom:XiaomiMega"}'
```
Result: Same 401, BUT this is what DMOB's working jobs use. The 401 was actually from missing skills (`cmc-watchlist-scraper`, `crypto-monitoring-cron`) trying to call their APIs, not from the model provider.

### Step 5: Clear broken skill references
After removing skills from the job definition and rewriting the prompt to embed logic directly, the provider works.

## Key Takeaways

1. **`custom:XiaomiMega` is the correct provider for all cron jobs** — it's what DMOB's jobs use and it works
2. **`xiaomi` (built-in) may fail in cron sessions** even though it works interactively — different auth path
3. **Missing skills cause misleading 401 errors** — the error comes from the skill's API call, not the model provider. Always clear `skills: []` on jobs that reference non-existent skills
4. **Always verify by running the script manually first** — if `python3 d5-lp-consolidated.py` works, the issue is provider/config, not the script

## Current Desmond Cron Job Registry (Post-Fix)

| Job | ID | Schedule | Provider | Status |
|-----|----|----------|----------|--------|
| DMOB — Hackathon Scout | `27a3c4947359` | 10am/6pm | custom:XiaomiMega | Fixed |
| Memory & Profile Backup | `30c5350962d3` | Every 6h | custom:XiaomiMega | Fixed |
| YoYo — Watchlist + LP | `e00b46103b08` | 8:15, 12:15, 4:15, 8:15 | custom:XiaomiMega | Fixed |
