---
name: hackathon-status-audit
description: Audit hackathon submission status — verify actual deployment vs claimed readiness, detect deadline discrepancies, and flag incomplete requirements
triggers:
  - "status of * hackathon"
  - "is * hackathon submitted"
  - "deadline verification"
  - "submission readiness audit"
  - "hackathon status check"
  - "results of * hackathon"
  - "winner announcement for * hackathon"
  - "did * hackathon win"
---

# Hackathon Status Audit

**Purpose:** Verify actual submission readiness and status for hackathon deadlines — distinguish between "code ready", "submitted", and "post-submission follow-up". Detect deadline discrepancies and flag incomplete requirements.

## When to Use
- Checking if a hackathon submission is actually submitted or just "ready"
- Auditing multiple hackathons for deadline accuracy (official vs vault vs team memory)
- Pre-submission checklist verification (24-48h before deadline)
- Post-commit status verification (has code been actually deployed/submitted?)
- Cross-referencing vault records with external sources (Encode Club, GitHub, official pages)

## Trigger Conditions
- User asks "what's the status of X hackathon"
- Deadline approaching (< 7 days) and need to verify submission completeness
- Found conflicting deadline dates in different sources
- Need to audit whether demo video/UI deployment is actually done
- Checking if wallet/gas/faucet blockers resolved

## Process

### Phase 1: Vault Record Audit
1. Read `Gentech-HQ.md` kanban board for declared deadline and status
2. Check `02-Labs/Hackathons/Active/<hackathon-name>.md` for detailed status
3. Review `10-Archive/green-room-handoffs/` for most recent handoff (last 7 days)
4. Check `11-Mess Hall/` recent rotation logs for status mentions
5. Extract: claimed status, deadline, submission URL/repo, remaining tasks
6. Use `search_files` with pattern "*<hackathon-name>*" to find all relevant files across the vault

### Phase 2: Repository Verification
1. Query GitHub API for latest commit date on claimed repo
2. Check for deployment-related commits (deploy scripts, UI, verified contracts)
3. Look for issues/PRs titled "submission", "hackathon", "demo"
4. Verify test counts passing match claims
5. Check branch status (main vs hackathon-specific branch)

### Phase 3: External Source Cross-Check
1. Attempt to retrieve official hackathon page (Encode Club, etc.)
2. Search for deadline mentions in page source ( grep for "deadline", "due", "submission")
3. Look for winner announcements or judging phase indicators
4. If page blocked/minimal, note "external verification failed — rely on vault + repo"
5. Check if deadline in vault matches official source; flag discrepancies
6. Check for submission confirmation emails or GitHub PRs
7. Look for winner announcements or prize allocations
8. Verify if prizes were awarded and to whom

### Phase 4: Readiness Criteria Checklist
Verify ALL required elements according to hackathon rules:
- [ ] Code deployed to target chain/testnet (check for verified contract addresses)
- [ ] Demo UI deployed (Vercel/AWS/etc) — look for deployment URLs in README
- [ ] Demo video recorded (check for video links, YouTube URLs)
- [ ] Publicly accessible demo (try accessing demo URL if provided)
- [ ] Submission actually made (look for "submitted" markers in vault, not just "ready")
- [ ] GitHub repo public and matches submission requirements
- [ ] README meets judging criteria (clear, demo flow, architecture)
- [ ] Wallet/gas blockers resolved (for chain deployments)

### Phase 5: Blockers & Next Actions
1. Identify blockers: gas, UI, verification, attestations, documentation
2. Check handoff board for unclaimed tasks related to this hackathon
3. Determine if deadline is realistic given remaining work
4. Recommend escalation if deadline at risk
5. Note who owns each remaining task (Labs/Strategies/Entertainment)

### Phase 6: Results Verification
1. Check official hackathon page for winner announcements
2. Verify if submission was received and by whom
3. Document next steps based on outcome:
   - If won: claim prizes, request feedback, plan for future
   - If not won: request feedback, analyze shortcomings, plan improvements
   - If results delayed: note expected timeline, set follow-up reminder
4. Update status in vault and notify team

## Output Format (Max 100 words)
```
[Status: SUBMITTED/READY-NOT-SUBMITTED/IN-PROGRESS/BLOCKED/RESULTS-PENDING]
Deadline: YYYY-MM-DD (source: official/vault/GitHub)
Repo: <url> (last commit: <date>)
Critical blockers: <list if any>
Next 24h actions: <concrete steps>
```

## Common Pitfalls
- **Mistaking "code ready" for "submitted"** — always look for explicit submission marker
- **Trusting stale vault records** — vaults get out of date; cross-check with GitHub
- **Deadline confusion** — encode club may extend; check official source directly
- **Missing demo deployment** — contracts deployed but no UI = partial completion
- **Wrong chain** — code on Avalanche but hackathon requires Kite testnet
- **Unfunded wallet** — deploy script ready but no gas = not actually deployed

## Decision Rules
- If no GitHub commits in last 7 days and status says "building", mark as STALLED
- If deadline discrepancy > 2 days between sources, escalate to HQ for verification
- If demo URL listed but returns 404, mark DEMO-BROKEN
- If wallet address found but balance = 0, mark GAS-BLOCKED
- If README lacks judging criteria coverage, mark DOCS-INCOMPLETE

## Escalation Triggers
- Deadline < 72h and submission incomplete → HQ alert
- 3+ blockers unresolved → HQ strategy session
- Deadline discrepancy found → HQ confirmation required
- No activity in 5+ days on active hackathon → HQ status check

## Integration Notes
- Cross-reference with `agent-coordination` skill for handoff board status
- Use `kanban-orchestrator` skill if task decomposition required
- Always report back through Mess Hall rotation logs
- If submission complete, note in `kite-submission-readme.md` and mark Gentech-HQ task Done

---
*Skill captures audit pattern from Kite AI Hackathon status check (May 2, 2026): discovered deadline discrepancy (May 11 vs May 17), verified code ready but not submitted, identified gas blocker, and flagged DMOB overload.*