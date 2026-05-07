# Provider Strategy Reference

**Last updated:** 2026-05-05

## User Preference: Transparent Billing

User explicitly prefers providers with:
- API key auth (not OAuth refresh loops)
- Visible usage dashboards
- Predictable billing (no "surprise" charges)
- No auth refresh watchdog crons

## Current Provider Stack

| Provider | Role | Auth | Models | Status |
|----------|------|------|--------|--------|
| Xiaomi | Primary | API key | MiMo-V2.5 | ✅ Active |
| OpenCode Go | Secondary | API key | MiMo-V2.5 + 13 others | ✅ Subscribed |
| OpenRouter | Vision | API key | Gemini 2.0 Flash | ✅ Active |
| Nous Research | Dropped | OAuth | — | ❌ Removed (billing blind spot + 15-min refresh) |

## OpenCode Go Models (confirmed)

MiMo-V2-Pro, MiMo-V2-Omni, MiMo-V2.5-Pro, MiMo-V2.5, GLM-5.1, GLM-5, Kimi K2.5, Kimi K2.6, Qwen3.5 Plus, Qwen3.6 Plus, MiniMax M2.5, M2.7, DeepSeek V4 Pro, V4 Flash

## OpenCode Go Pricing

- $5 first month, then $10/month
- Rolling usage limits (5-hour windows)
- Weekly usage limits
- Top-up credit available

## Provider Swap Pattern

When switching providers for the same model:
1. Verify model availability on new provider
2. Update `model.provider` and `model.base_url` in config
3. Update `api_key` in `.env`
4. Test connection
5. Remove old provider config
6. Kill any auth-refresh watchdog crons

## Usage Monitoring

Usage cron job should:
- Poll provider dashboard/API for current usage
- Alert when approaching rolling or weekly limits
- Log usage trends to vault
- Run daily (not more frequent — usage resets every 5 hours)
