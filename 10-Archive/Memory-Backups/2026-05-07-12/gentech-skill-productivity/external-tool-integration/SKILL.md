---
title: External Tool Integration
name: external-tool-integration
description: Connect and orchestrate external SaaS tools (Gmail, Slack, Notion, etc.) via third-party proxy platforms like Composio. Covers OAuth setup, SDK usage patterns, account linking, and unified wrapper design.
docs: https://hermes-agent.nousresearch.com/docs
---

## When to Use

[... existing content ...]

## References

### Official Documentation
- [Composio Python SDK Quickstart](https://github.com/ComposioHQ/composio-python)
- [OAuth 2.0 for Google APIs](https://developers.google.com/identity/protocols/oauth)
- [Gmail API Scopes](https://developers.google.com/gmail/api/auth/scopes)

### Session Notes & Examples
- **references/composio-gmail-session-20260503.md** — Detailed exploration of Composio Gmail integration: response structures, attribute locations, OAuth initiation, cleanup of stale connections, and troubleshooting from May 03, 2026 session.

### Templates & Scripts
- **scripts/gmail_unified.py** — Reusable unified Gmail wrapper that routes between direct Google API and Composio proxy. Includes lazy initialization, status checking, dry-run mode, and fallback logic. Use as starting point for multi-account Gmail automation.

## Common Pitfalls

[Rest of existing content unchanged...]