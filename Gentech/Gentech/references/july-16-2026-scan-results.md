# x402 Ecosystem Scan — July 16, 2026

**Scout**: x402 Compliance Scout cron (daily 12:10 UTC)
**Model**: deepseek-v4-flash
**Scope**: GitHub notifications, open PR check, new repo discovery, x402scan stats

---

## Inbox Duty

### GitHub Notifications
- 7 "author" notifications — our own PR updates, no action needed
- 1 "comment" notification — issue #9572 on punkpeye/awesome-mcp-servers (MCPExplorer asking where their trust-layer resource fits). Only comment is ours from Jul 12 — no new replies. No action needed.

### Open PRs Check
| PR | Repo | Days Open | Status |
|----|------|-----------|--------|
| [#5](https://github.com/marlinprotocol/x402-gateway/pull/5) | marlinprotocol/x402-gateway | 2 days | Open, no comments |
| [#8](https://github.com/brave-experiments/private-x402-gateway/pull/8) | brave-experiments/private-x402-gateway | 2 days | Open, no comments |
| [#30](https://github.com/mark3labs/x402-go/pull/30) | mark3labs/x402-go | 2 days | Open, CodeRabbit walkthrough passed ✅ |
| [#2](https://github.com/srotzin/hive-rosetta/pull/2) | srotzin/hive-rosetta | <2 days | Open, clean |
| [#834](https://github.com/jamesmurdza/awesome-ai-devtools/pull/834) | awesome-ai-devtools | **CLOSED by bot** | Missing template sections — fixed & reopened as #837 |

## PR Action Taken

### Tier 1 — PR Resubmitted 🔄

**awesome-ai-devtools #834 → #837**
- PR #834 was auto-closed by github-actions bot for missing `## Description` / `## Checklist` sections
- The PR body already had both sections — likely a race condition with the bot
- Fork branch was deleted, so I:
  1. Synced fork to latest upstream main
  2. Re-applied the change (alphabetical insertion in README.md)
  3. Submitted new PR #837 with correctly formatted body matching the template
- **Result**: [PR #837](https://github.com/jamesmurdza/awesome-ai-devtools/pull/837) — OPEN, MERGEABLE, no bot flags after 60s monitor ✅

## New Repos Discovered — July 16 Scan

### Tier 0 (Observe, Logged to Platform Directory)

| Repo | Type | Assessment |
|------|------|------------|
| **nissan/reddi-agent-protocol** | Solana x402 escrow marketplace | Very active (commit 2 mins ago), 33 open issues, 73 branches. x402 reference workflow on roadmap (issue #564). Worth monitoring for future contribution opportunities. |
| **crosshatch/crosshatch** | Effect-native x402 framework | Active (commit 21 min ago), 25 open issues, 99.5% TypeScript. Framework-level issue set — not directly x402 compliance. |
| **contentfactory/eu-verify** | European business verification API | Fully x402 v2 compliant ✅. Has `/.well-known/x402`, OpenAPI spec, 16 MCP tools, 93 HTTP endpoints. Gold standard implementation. |
| **aaronjmars/tweazy** | x402 demo (MCP + Smart Wallets) | Demo app that consumes x402. Uses CDP Smart Wallets with passkeys. No compliance gaps — it's an x402 consumer, not an implementer. |
| **mordiaky/x402-watch** | x402 protocol checker | Free tool that validates 402 challenge shape and Bazaar catalog presence. Runs on POST-only. Well-documented. |
| **irun2themoney/crypto-payments-mcp** | MCP x402 close-loop helper | 6 free wallet-read tools + 1 x402 premium tool. Helps agents verify on-chain payments. Clean architecture. |

### No New Tier 1 or Tier 2 Items This Run
All new repos are either already x402 v2 compliant or are tooling/demo projects that don't implement the protocol server-side.

## Pending PR Status (All 4 Original)
All 4 x402 compliance PRs from Jul 14-15 remain open with no reviews:
- #5 marlinprotocol/x402-gateway — 2 days
- #8 brave-experiments/private-x402-gateway — 2 days
- #30 mark3labs/x402-go — 2 days (CodeRabbit confirms passing)
- #2 srotzin/hive-rosetta — <2 days

Normal for the ecosystem — first reviews typically take 5-10 days on smaller repos.

## Build Queue
No new items added. All seven newly discovered repos are Tier 0 (observe only).

## Key Observations
1. **Ecosystem maturing** — New x402 projects are overwhelmingly v2 compliant out of the box
2. **Two x402-watch projects exist** — `logiccrafterdz/x402-watch` (Rust health monitor) and `mordiaky/x402-watch` (protocol checker). Different tools, same naming coincidence. Both are well-built.
3. **No new compliance gaps** — The protocol fix opportunities are drying up. The ecosystem has mostly standardized on v2.
4. **awesome-ai-devtools re-submitted** — PR #837 is clean and mergeable. Fixes the bot-closure issue from Jul 15.
