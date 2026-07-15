# Cloudflare Email Agent — MCP Integration

**Status:** 🟢 Building
**Owner:** Forge (Desktop)
**Priority:** P11 (1-2 days)
**Stack:** Cloudflare MCP Server (⭐3.9k) + Workers + Email Routing

---

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────┐
│  Sender     │────▶│  Cloudflare      │────▶│  MCP Server   │
│  (any)      │     │  Email Routing   │     │  (Workers)    │
└─────────────┘     └──────────────────┘     └──────┬───────┘
                                                     │
                                                     ▼
                                            ┌──────────────┐
                                            │  Forge Agent  │
                                            │  (Desktop)    │
                                            └──────────────┘
```

## What It Does

- **Inbound:** Emails sent to `*@gentechlabs.net` → Email Routing → Workers → MCP → Forge reads them
- **Outbound:** Forge sends emails via Workers API → Email Routing → Recipient
- **Storage:** Attachments to R2, parsed content to KV for quick lookup

## Setup

### 1. Cloudflare Email Routing (Dashboard)

1. Go to Cloudflare Dashboard → Email Routing
2. Add `gentechlabs.net` domain
3. Create catch-all rule: `*@gentechlabs.net` → Email Worker
4. Deploy the email worker

### 2. Email Worker

```js
// workers/email-worker.js
export default {
  async email(message, env, ctx) {
    // Parse email
    const from = message.from;
    const to = message.to;
    const subject = message.subject;
    const text = message.rawText;
    const html = message.rawHtml;

    // Store in KV for MCP server to read
    await env.EMAIL_KV.put(
      `inbox:${Date.now()}`,
      JSON.stringify({ from, to, subject, text, html }),
      { expirationTtl: 86400 * 7 } // 7 days
    );

    // Store attachments in R2
    for (const attachment of message.attachments) {
      await env.EMAIL_R2.put(
        `attachments/${Date.now()}-${attachment.filename}`,
        attachment.content
      );
    }
  }
};
```

### 3. MCP Server Config

```json
{
  "mcpServers": {
    "cloudflare": {
      "command": "npx",
      "args": [
        "@cloudflare/mcp-server-cloudflare",
        "--email-routing",
        "--kv",
        "--r2"
      ],
      "env": {
        "CLOUDFLARE_API_TOKEN": "${CLOUDFLARE_API_TOKEN}",
        "CLOUDFLARE_ACCOUNT_ID": "${CLOUDFLARE_ACCOUNT_ID}"
      }
    }
  }
}
```

### 4. Forge Reads Inbox

```python
# forge reads new emails
import json, os
from hermes_tools import terminal

def check_inbox():
    result = terminal("""
        npx @cloudflare/mcp-server-cloudflare email list --limit 10
    """)
    emails = json.loads(result["output"])
    for email in emails:
        print(f"From: {email['from']}")
        print(f"Subject: {email['subject']}")
        print(f"Body: {email['text'][:500]}")
```

## Revenue Model

| Service | Price | Notes |
|---------|-------|-------|
| Email forwarding | $0 | Included with Cloudflare |
| R2 storage | ~$0.01/GB | Attachments |
| Email Worker | $0 | Workers free tier (100K req/day) |
| **Total** | **~$0/mo** | Near-zero cost |

## Files

- `workers/email-worker.js` — Email routing handler
- `workers/wrangler.toml` — Worker config
- `scripts/check-email.py` — Forge reads inbox
- `README.md` — Setup guide
