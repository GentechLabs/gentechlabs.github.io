---
name: email-redaction-checklist
description: "Checklist for redacting sensitive info from emails/screenshots before sharing in other channels"
version: 1.0.0
author: desmond
category: productivity
tags: [email, privacy, redaction, security]
---

# Email Redaction Checklist

Use this when processing emails/screenshots that may be shared outside HQ.

## What to Redact

| Pattern | Example | Redact To |
|---------|---------|-----------|
| Email addresses | john@company.com | j***@c*****.com |
| Phone numbers | +1-555-123-4567 | +1-***-***-**** |
| Account numbers | Acct: 123456789 | Acct: ****789 |
| Passwords/API keys | sk-abc123xyz | [REDACTED] |
| SSNs | 123-45-6789 | ***-**-**** |
| Credit cards | 4111 1111 1111 1111 | **** **** **** 1111 |
| Login URLs | https://bank.com/login | [bank login page] |
| Full names (if sensitive) | John Michael Smith | J. Smith or [NAME] |
| Physical addresses | 123 Main St, City, ST | [ADDRESS] |
| Dates of birth | DOB: 01/15/1985 | DOB: **/**/**** |

## Redaction Levels

**Full redaction** — Replace entirely (passwords, API keys, SSNs)
```
Password: [REDACTED]
API Key: [REDACTED]
```

**Partial redaction** — Keep enough to identify (emails, phones, accounts)
```
Email: j***@g*****.com
Phone: +1-***-***-4567
Account: ****789
```

**Summarize** — Replace with description
```
"Contains wire transfer instructions for $5,000"
"Login credentials for crypto exchange"
"Medical appointment details"
```

## Channel Routing Guide

| Content Type | HQ | Labs | Mess Hall |
|--------------|-----|------|-----------|
| Full email with sensitive data | ✅ | ❌ | ❌ |
| Redacted summary | ✅ | ✅ | ✅ |
| Action items only | ✅ | ✅ | ✅ |
| Screenshots (original) | ✅ | ❌ | ❌ |
| Screenshots (redacted) | ✅ | ✅ | ✅ |

## Quick Process

1. **Receive** — Email/screenshot arrives in HQ
2. **Scan** — Check for sensitive patterns (use checklist above)
3. **Redact** — Apply appropriate redaction level
4. **Route** — Share clean version to target channel
5. **Confirm** — Verify no sensitive data leaked

## Common Sensitive Keywords to Flag

```
password, passcode, PIN, SSN, social security
account number, routing number, SWIFT, IBAN
API key, secret key, token, private key
login, credentials, authentication
wire transfer, ACH, payment
medical, diagnosis, prescription
```

## Notes

- When in doubt, redact more rather than less
- Private photos/screenshots stay in HQ — text summaries only elsewhere
- Always get Jordan's approval before sharing redacted content externally