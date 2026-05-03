---
name: email-redaction-checklist
description: Checklist for redacting sensitive information before sharing emails/screenshots in other channels
category: productivity
version: 1.0.0
---

# Email Redaction Checklist

Use this when sharing email content, screenshots, or uploaded documents outside of private channels (HQ).

## Before Sharing

### 1. Identify Sensitive Patterns
Scan for and redact these:
- **Email addresses** → `email@redacted.com`
- **Phone numbers** → `***-***-****`
- **Account/account numbers** → `****1234` (keep last 4 if needed)
- **SSN/Tax IDs** → Remove entirely
- **Passwords/PINs** → Remove entirely
- **Credit card numbers** → `****-****-****-1234` (keep last 4)
- **API keys/tokens** → Remove entirely
- **Login URLs** → Remove or simplify to domain only

### 2. Assess What's Shareable
Ask yourself:
- Does the recipient *need* the full email to understand the context?
- Can I summarize the key point in 1-2 sentences instead?
- Is this financial/legal/personal info that should stay private?

### 3. Redaction Methods
- **Full redact**: Replace with `***` or `[REDACTED]`
- **Partial redact**: Keep first/last, mask middle (e.g., `J***n` for Jordan)
- **Summarize**: Extract key info, drop sensitive details

### 4. Channel Routing
- **HQ**: Full content allowed (private/sensitive)
- **Labs**: Process/redact here before sharing elsewhere
- **Mess Hall/Groups**: Summary only, no images with sensitive data

## Quick Reference
| Content Type | Action |
|-------------|--------|
| Account balances | Summarize only ("Balance: ~$X") |
| Transaction details | Redact account numbers, keep amounts/dates |
| Personal info | Remove or summarize |
| Business emails | Redact sender/recipient emails, keep content |
| Screenshots | Crop to relevant portion, redact headers |

## Example Redaction
**Before:**
> From: jordan@gmail.com
> To: support@bank.com
> Account: 1234567890
> Balance: $5,234.56

**After (for Mess Hall):**
> Got a bank update — balance looks good at ~$5.2k. No action needed.

---

*Created: Apr 28, 2026 — GenTech Labs*