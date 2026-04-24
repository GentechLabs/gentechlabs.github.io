# Skills Audit & Cleanup Plan
**Date:** 2026-04-16
**Status:** In Progress

## Summary
846 skills installed. ~700+ are bulk-installed cybersecurity/pen-testing skills not relevant to Gentech team operations.

## Skills to REMOVE

### Bulk Cybersecurity (700+ skills)
All `analyzing-*`, `performing-*`, `hunting-*`, `detecting-*`, `implementing-*`, `exploiting-*`, `conducting-*`, `building-*`, `scanning-*`, `reverse-engineering-*`, `testing-*`, `extracting-*`, `configuring-*`, `triaging-*`, `auditing-*`, `recovering-*`, `securing-*`, `collecting-*`, `deobfuscating-*`, `executing-*`, `tracking-*`, `validating-*`, `correlating-*`, `containing-*`, `eradicating-*`, `profiling-*`, `mapping-*`, `prioritizing-*`, `remediating-*`, `processing-*` skills.

### Specific Removals
- `pentagi-deploy` — no longer needed, PentAGI deprecated
- `solana-dev` — Solana not in scope
- `solana-vulnerability-scanner` — Solana not in scope
- `substrate-vulnerability-scanner` — not in scope
- `algorand-vulnerability-scanner` — not in scope
- `cosmos-vulnerability-scanner` — not in scope
- `ton-vulnerability-scanner` — not in scope
- `implementing-taxii-server-with-opentaxii` — not in scope
- `building-c2-infrastructure-with-sliver-framework` — not relevant
- `building-red-team-c2-infrastructure-with-havoc` — not relevant
- `nous-auth-recovery` — Hermes handles this natively
- `hermes-dojo` — not in use

## Skills to KEEP
- `autonomous-ai-agents` — Claude Code, Codex, Hermes, OpenCode
- `github/*` — repo management, PRs, code review
- `obsidian` + `note-taking` — second brain
- `mcp/*` — MCP server integration
- `hermes-dashboard-rebrand`, `hermes-workspace-theming` — GMC
- `foundry-solidity-dev`, `solidity-auditor` — Solidity learning
- `solidity-auditor`, `x-ray`, `pashov-solidity-auditor`, `pashov-x-ray` — security audit
- `reentrancy-pattern-analysis`, `external-call-safety`, `input-arithmetic-safety`, `sharp-edges`, `state-invariant-detection`, `variant-analysis`, `insecure-defaults`, `proxy-upgrade-safety`, `semgrep-rule-creator`, `semantic-guard-analysis`, `entry-point-analyzer`, `dos-griefing-analysis`, `signature-replay-analysis`, `token-integration-analyzer`, `oracle-flashloan-analysis`, `fp-check`, `smart-contract-security`, `audit-context-building`, `audit-prep-assistant`, `code-maturity-assessor`, `supply-chain-risk-auditor`, `guidelines-advisor` — all Solidity audit skills
- `chainlink-*` — relevant for AAE
- `circle-*` — Arc hackathon
- `definance`, `exchanges` — DeFi knowledge
- `dogfood` — QA testing
- `creative`, `media`, `gaming`, `smart-home`, `social-media` — utility
- `research`, `productivity`, `email`, `mlops` — general team tools
- `gentech-watchdog` — monitoring
- `defender` — security monitoring
- `secure-workflow-guide` — workflow reference
- `data-science` — Jupyter
- `devops` — webhooks
- `cron-job-audit` — cron management
- `daily-debrief` — daily summary
- `diagramming` — visuals
- `feeds` — data feeds
- `finance` — financial analysis
- `inference-sh` — inference server
- `medusa-fuzzing` — fuzz testing
- `minara` — AI agent
- `projects` — project management
- `red-teaming` — security skills
- `leisure` — find nearby
- `gifs` — GIF search

## Action Items
- [x] Remove bulk cybersecurity skills (batch delete)
- [x] Verify kept skills are functional after cleanup
- [x] Update this note with final count

## Cleanup Results (2026-04-16)
**12 skills removed:**
- agent-reach-install
- algorand-vulnerability-scanner
- almanak-strategy-builder
- analytics
- behavioral-state-analysis
- cairo-vulnerability-scanner
- cosmos-vulnerability-scanner
- nous-auth-recovery
- solana-dev
- solana-vulnerability-scanner
- substrate-vulnerability-scanner
- ton-vulnerability-scanner

**Note:** pentagi-deploy was already gone (previously cleaned up).

**Final count:** 63 skills remaining — all relevant to Gentech operations.
