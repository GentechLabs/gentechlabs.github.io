---
name: encode-club-hackathon-monitor
description: Monitor Encode Club and related hackathon platforms for Kite AI / Gentech submission status, judging results, and deadlines.
tags: [hackathon, encode-club, kite-ai, monitoring, cron]
---

# Encode Club Hackathon Monitor

## When to Use
Recurring cron job to check hackathon status for Gentech/Kite AI submissions. Checks Encode Club, lablab.ai, and vault state.

## Encode Club Platform

### Key URLs
- **Programmes listing:** `https://www.encodeclub.com/programmes`
- **Kite AI Global Hackathon 2026:** `https://www.encodeclub.com/programmes/kites-hackathon-ai-agentic-economy`
- **April Agentic Mini Hack:** `https://www.encodeclub.com/programmes/april-agentic-mini-hack`

### ⚠️ Dynamic Rendering Issue
Encode Club pages use client-side JS rendering. `browser_snapshot` returns **empty content** on detail pages (only footer loads).

**Workaround — use `browser_vision` for full page analysis:**
```
browser_navigate(url) → browser_vision(question="What is on this page?")
```
Or extract text via `browser_console`:
```javascript
Array.from(document.querySelectorAll('h2, h3, h4, p, li')).map(e => e.innerText).join('\n')
```

### Page Structure (once rendered)
1. Hero: title, date, format (online/in-person), duration, sign-up button
2. Description & tracks
3. **Prizes & Challenges** — prize pool, requirements, judging criteria
4. **Programme Schedule** — weeks with milestone deadlines
5. **Workshops** — upcoming/finished tabs
6. **FAQ**
7. **"View Results" button** — appears on completed hackathons, but requires Encode Club authentication to access

### Schedule Extraction
The schedule section uses a combobox for timezone. Key dates appear as:
- `Week N — Phase Name`
- `DDth Month, HH:MM UTC` — Milestone description

## lablab.ai
- **Blocked by Cloudflare** — `browser_navigate` gets bot detection challenge
- Cannot reliably scrape; check vault or web_search as fallback
- Arc hackathon submission page: `https://lablab.ai/ai-hackathons/nano-payments-arc`

## Vault Structure for Hackathon Intel
```
02-Labs/Hackathons/Active/
  01-Arc-Hackathon-Apr25.md      — AgentEscrow on Arc (lablab.ai)
  02-Kite-AI-Apr26.md            — AgentEscrow on Kite AI (Encode Club)
  arc-hackathon-audit.md         — DMOB security audit report

03-Strategies/
  hackathon-tracker.md           — Master tracker with all upcoming hackathons

08-Daily/content-drafts/
  arc-hackathon-pitch.md         — Submission pitch script
  arc-hackathon-video-script.md  — Demo video script
```

## Gentech Active Hackathon Status (as of April 2026)

| Hackathon | Platform | Deadline | Status | Project |
|-----------|----------|----------|--------|---------|
| Kite AI Global 2026 | Encode Club | ~Apr 24 | Building (Week 3/4) | AgentEscrow on Kite |
| Agentic Economy on Arc | lablab.ai | Apr 25 | Building, deploy blocked | AgentEscrow (x402) |
| April Agentic Mini Hack | Encode Club | ~Apr 29 | Active, no submission yet | TBD |
| Encode x Arc Enterprise | Encode Club | ENDED Mar 2 | Results gated (auth required) | N/A |

## Judging Criteria Reference (Kite AI)
- Agent Autonomy — minimal human involvement
- Developer Experience — clear docs, README/video, simple UX
- Real-World Applicability — solves a real problem, runs in production
- Novel/Creativity — integration with AI tools, agentic workflows

## Reporting
When results are found, format as:
```
## [Hackathon Name] — [Status]
- Judging phase: ...
- Feedback received: ...
- Results/winners: ...
- Next deadline: ...
```
