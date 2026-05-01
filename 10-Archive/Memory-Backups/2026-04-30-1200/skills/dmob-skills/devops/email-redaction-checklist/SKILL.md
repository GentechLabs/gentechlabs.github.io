---
name: email-redaction-checklist
description: "Redact sensitive info from screenshots/images before sharing outside HQ. Covers emails, docs, and anything with PII."
---

# Email / Screenshot Redaction Checklist

When Jordan (or anyone) uploads a screenshot or image containing sensitive content, follow this before sharing to other channels.

## What to Redact

| Type | Example | Redaction |
|------|---------|-----------|
| Email addresses | user@domain.com | `u***@d***.com` or `[EMAIL]` |
| Phone numbers | +1-555-123-4567 | `[PHONE]` or `***-***-4567` |
| Account numbers | Checking ****1234 | `[ACCT]` or `****1234` |
| Passwords / API keys | sk-abc123... | `[REDACTED]` |
| SSN / Tax IDs | 123-45-6789 | `[REDACTED]` |
| Physical addresses | 123 Main St | `[ADDRESS]` or city only |
| Names (if private) | John Smith | `[NAME]` or first name only |
| Wallet addresses | 0x7ebf...296a | Keep if Jordan's (public), redact others |
| Login URLs | https://login.bank.com | Redact domain or show `[BANK LOGIN]` |
| Balances / amounts | $12,345.67 | Keep if relevant, redact if sensitive |

## Redaction Levels

1. **Full redact** — Replace with `[REDACTED]` (default for PII)
2. **Partial redact** — Mask most chars: `u***@d***.com`
3. **Summarize** — Just describe what the email says in text, no screenshot needed

## Channel Routing

| Channel | What to share |
|---------|---------------|
| HQ (private) | Raw screenshots, unredacted |
| Labs | Clean summary + redacted screenshots only |
| Mess Hall | Text summary only, no screenshots |
| Green Room | Work-relevant excerpts, redacted as needed |

## Workflow

1. **Receive** image in HQ
2. **Scan** for sensitive patterns (emails, phones, accounts, addresses, passwords, keys)
3. **Redact** using vision_analyze or manual review
4. **Summarize** the content in clean text
5. **Route** — send clean version to target channel, keep raw in HQ

## Quick Reference

When Jordan says "clean this for Labs/Mess Hall":
- Use `vision_analyze` to read the image
- Identify all PII/sensitive fields
- Produce a text summary with redacted details
- Send summary to the target channel
- Never forward the raw image outside HQ
