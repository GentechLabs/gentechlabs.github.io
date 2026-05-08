# Telegram Routing — YoYo Reports

## Destination Groups

| Agent | Group ID | Purpose |
|-------|----------|---------|
| YoYo | `-1002916759037` | Crypto watchlist + LP position updates |
| Gentech HQ | `-100...` | Daily digests, strategic summaries |
| Mess Hall | `-100...` | Error logs, system status |

## Message Format Standards

### Short Summary (Stable, No Material Change)
```
✅ YoYo Watchlist — No 1.5%+ movement
💰 LP Position: AVAX/USDC → Stable (IL -0.0%, eff. 98.1%)
📄 Vault: 03-Projects/DeFi/LFJ-AVAX-USDC.md (last: 2026-05-03)
```

**Rules**:
- Start with status emoji (✅ stable, 🚨 alert, ⚠️ review)
- One line per section (watchlist, LP, vault ref)
- No blank lines in Telegram (they render as paragraph breaks)
- Include last vault date for traceability

### Alert Message (Material Change Detected)
```
🚨 YoYo Watchlist Alert
• TAO: $291.07 🟢 +6.6%
• AVAX: $9.42 🔴 -2.1%

⚠️ LP Position: AVAX/USDC → Review Needed
- Price $9.42 outside range $8.95–$9.36
- IL: -2.3% (exceeds 2% threshold)
- Efficiency: 32% (<50%)

📄 Vault updated: 03-Projects/DeFi/LFJ-AVAX-USDC.md
```

**Rules**:
- Watchlist alerts list each token with emoji and % change
- LP section lists at least 2 bullet points (price, IL, efficiency)
- Vault file path only (no date needed; user can open file)
- End with single-line summary

### Monday DCA Reminder (always included if Monday)
```
📅 Monday DCA Reminder
💰 Shape-aware DCA: $50 (Center zone, eff. ≥70%)
📈 Next milestone: $20/day (Raider) — 0.0% progress
```

Merge with regular report; do not send standalone.

## Silent Mode

When `[SILENT]` is printed to stdout:
- No Telegram message sent
- Cron job exits 0
- Used when all tokens <1.5% AND LP stable AND not Monday

## Error Reporting

If API fetch fails:
```
⚠️ YoYo Monitor Error
- CMC API: timeout after 15s (retry pending)
- DexScreener: OK
- Last known: AVAX $9.16, IL 0.1%
📄 Vault: 03-Projects/DeFi/LFJ-AVAX-USDC.md (no update)
```

Send to YoYo group with `⚠️` prefix, not `🚨`.

## Routing Logic

1. Build report body
2. Determine alert level:
   - Any 1.5%+ token move → 🚨
   - LP out of range OR IL ≥2% → 🚨
   - Efficiency <50% → ⚠️
   - Otherwise → ✅
3. Prepend appropriate emoji line
4. Post to group via `send_message` tool or Telegram Bot API

**Do not** send duplicate messages within same 4h window. Track last sent state in `~/.hermes/scripts/.last-telegram-sent.json`.

## Message Retention

Telegram group history serves as audit trail. Do not edit/delete sent messages. If correction needed:
- Send follow-up: `↩️ Correction: [corrected fact]`
- Update vault entry with `[CORRECTED]` tag

## Related

- `cron-job-standards` — Silent mode and scheduling
- `defi-lp-monitor` — Report generation