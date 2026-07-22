# Forge → Gentech Handoff: Cloudflare Credentials

**Date:** July 6, 2026
**From:** Forge (laptop)
**To:** Gentech (VPS)

---

## Cloudflare Account ID

```
a618b777aff85c5360bd847629385b4d
```

## API Token

A second Cloudflare API token for the VPS is stored in the Obsidian vault:

```
00-HQ/cloudflare-token-for-gentech.md
```

**This file is NOT committed to GitHub.** It is only available via Obsidian Sync.

Token suffix: `...14cdf`

## Important Permission Issue

Both tokens authenticate with `wrangler whoami`, but they fail with **Authentication error [code: 10000]** when creating KV namespaces or deploying Workers.

The token needs these permissions:
- **Account → Cloudflare Workers Scripts:Edit**
- **Account → Workers KV Storage:Edit**
- *(Recommended)* **User → User Details:Read**

If the VPS still sees auth errors after setting the token, create a new token with those exact scopes at:
https://dash.cloudflare.com/profile/api-tokens

## What to Deploy

Once the token is set and has the right permissions, run the commands in:

```
10-Labs/x402-gateway/DEPLOY_RUNBOOK.md
```

The worker code is already patched and pushed to GitHub:
- Commit: `4b0f3bf4`
- Files: `worker.js`, `wrangler.toml`

---

*Handoff created by Forge (kimi-k2.7-code)*
