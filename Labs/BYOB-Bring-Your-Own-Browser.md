# BYOB — Bring Your Own Browser
**Date:** 2026-04-25
**Source:** https://github.com/wxtsky/byob
**Author:** wxtsky
**License:** MIT

## What It Is
BYOB lets your AI assistant (Claude, Cursor, Cline) control the Chrome browser you already have open. Instead of using headless browsers or cloud services, it taps into your real browser session — with all your logins, cookies, and sessions intact.

## Key Data
| Metric | Value |
|--------|-------|
| Stars | 28 |
| Forks | 1 |
| Commits | 45 |
| Last commit | 4 hours ago |
| License | MIT |
| Language | TypeScript (Bun) |
| Structure | Monorepo (packages: bridge, extension, mcp-server) |

## Core Tools
| Tool | Function |
|------|----------|
| browser_read | Open page, scroll, read content |
| browser_screenshot | Screenshot to disk (not base64) |
| browser_click | Click elements |
| browser_type | Type into inputs |
| browser_get_cookies | Extract cookies for curl/scripts |
| browser_navigate | Go to URL (new or existing tab) |
| browser_wait_for | Wait for element |
| browser_list_tabs | List open tabs |
| browser_switch_tab | Switch tabs |
| browser_eval | Run JS (off by default) |

## Architecture
```
Claude Code → byob-mcp → byob-bridge → Chrome extension → your Chrome tab
```
All local. Nothing leaves the machine. Close Chrome = everything quits.

## Security Features
- `browser_eval` is off by default (opt-in via `BYOB_ALLOW_EVAL=1`)
- Blocked sites by default: `chrome://`, `file://`, Google/Microsoft/Apple login pages
- Per-user extension key (no ID clashes)
- Files are private (0600 sockets, 0700 folders)
- Zero outbound traffic (no analytics, auto-update, crash reports)

## Why It Matters vs. Alternatives
| Feature | WebFetch | Headless Puppeteer | BYOB |
|---------|----------|-------------------|------|
| Login sessions | ❌ | ⚠️ (manual cookies) | ✅ (already logged in) |
| Bot detection | ❌ | ❌ | ✅ (real human browser) |
| Setup | 0 | Hours | 5 min |
| Cost | Free | Cloud $ | Free |

## Relevance to GenTech
- **Agent Economy thesis:** This is BYOA (Bring Your Own Agent) infrastructure — exactly our space
- **Competitive intel:** Could be a tool we use internally for browser automation
- **Potential integration:** Our agents could leverage BYOB for authenticated web tasks
- **MCP ecosystem:** Uses Model Context Protocol — aligned with our Hermes/Claude stack
- **Privacy-first:** Local-only execution matches our ethos

## Action Items
- [ ] Evaluate BYOB for internal agent use (authenticated browsing, social monitoring)
- [ ] Check if it integrates cleanly with our Hermes agent setup
- [ ] Monitor star growth — 28 stars, very new, could become a key project
- [ ] Consider forking or contributing if we build on it

## Tags
#agent-infrastructure #mcp #browser-automation #byoa #open-source #devtools
