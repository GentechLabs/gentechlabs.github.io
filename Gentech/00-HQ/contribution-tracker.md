# Contribution Tracker

Last updated: 2026-07-18 (Saturday — Weekly Follow-up)

---

## Open PRs

### 1. NousResearch/hermes-agent #50239 — fix(telegram): preserve markdown formatting in fallback paths
- **Status**: OPEN | Mergeable: YES | Merge state: BLOCKED (needs maintainer review)
- **Branch**: fix/telegram-strip-mdv2-bold → main
- **Created**: 2026-06-21
- **Last activity**: 2026-07-17 (rebase + "Ready for review" comment)
- **CI**: No checks reported on branch
- **Comments**: 4 total (2 from us, 1 from alt-glitch/collaborator, 1 from teknium1 automated review)
- **Reviews**: 1 (teknium1/contributor — COMMENTED, automated hermes-sweeper)
- **Blockers**: Needs maintainer approval. teknium1 flagged that fallback paths use plain text (parse_mode=None) and markdown markers are exposed literally.
- **Next step**: Wait for maintainer review. The rebase and comment were left 5 days ago.

### 2. solana-foundation/pay-skills #154 — feat: Add GenTech Labs — 12 x402 API services
- **Status**: OPEN | Mergeable: YES | Merge state: BLOCKED (needs maintainer review/approval)
- **Branch**: ProtoJay4789:main → main (fork)
- **Created**: 2026-06-24
- **Last activity**: 2026-07-09 (rebase + response to lgalabru)
- **CI**: Greptile Review — PASS ✅
- **Comments**: 7 total (4 from us, 1 from lgalabru/collaborator, 2 from greptile-apps)
- **Reviews**: 5 (all greptile-apps/COMMENTED — automated)
- **Blockers**: ~~Solana mainnet~~ ✅ Resolved. ~~Category/402 issues~~ ✅ Resolved. ~~CI failure~~ ✅ PASS. Now waiting for maintainer re-review.
- **Next step**: Follow up with lgalabru if no movement by next week. PR has been clean for 9 days.

---

## Open Issues

### 3. BankrBot/claude-plugins #21 — Fix invalid dependency x402-fetch@^latest in @bankr/sdk
- **Status**: OPEN — No maintainer response since June 24
- **Comments**: 1 from us (workaround provided)
- **Blockers**: Need Bankr team to acknowledge and fix the dependency
- **Next step**: Still blocked — no response from maintainers. Re-evaluate if integration is still blocked.

---

## Weekly Summary
- **Week of July 12-18**: No new comments or merges on any open contributions
- **hermes-agent #50239**: Rebased July 17, ready for maintainer review
- **pay-skills #154**: CI passing, all blockers resolved, waiting 9 days for maintainer
- **claude-plugins #21**: Stale — no maintainer response in 24 days

## Action Items
1. Pay-skills: If no movement next week, consider a gentle follow-up comment to lgalabru
2. Claude-plugins: Re-evaluate whether integration path with Bankr is still critical
3. Search for new open-source contribution opportunities if these stall further
