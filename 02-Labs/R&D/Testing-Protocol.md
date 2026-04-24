# 📋 Testing Protocol — The Playbook

## The Cycle

### 1. Scope the Test
Before testing, define:
- **What:** Specific component/layer being tested
- **Why:** What assumption are we validating?
- **Success criteria:** Pass = _____, Fail = _____
- **Owner:** Who runs it, who reviews results

### 2. Execute
- Follow the test plan (see templates)
- Log EVERYTHING — commands run, outputs, errors, timestamps
- Screenshot/video when relevant
- If something feels wrong but passes, flag it anyway

### 3. Report
Fill out the test report template:
- What was tested
- What passed ✅
- What failed ❌
- What's weird ⚠️ (passed but suspicious)
- Severity: Critical / Major / Minor / Cosmetic
- Recommended fix (if obvious)

### 4. Triage (Gentech)
- Critical → immediate fix, blocks everything
- Major → fix before next milestone
- Minor → backlog, fix when convenient
- Cosmetic → nice-to-have, backlog

### 5. Adjust & Retest
- Dmob applies fixes
- Retest ONLY what failed + anything the fix could have broken
- Update report with resolution

---

## Test Categories

### Contract Tests (Dmob)
- Unit tests (Foundry forge test)
- Fuzz tests (forge fuzz)
- Deployment verification (can it deploy? does it initialize correctly?)
- Integration tests (end-to-end flow)
- Gas optimization check

### Agent Integration Tests (Dmob + YoYo)
- Agent can call contract
- Agent receives correct responses
- Error handling (what happens when things break?)
- Timeout behavior
- Multi-agent coordination

### Data/Research Tests (YoYo)
- Source accuracy (is the data correct?)
- Freshness (is the data current?)
- Edge cases (what breaks the analysis?)
- Competitor comparison validation

### Content Tests (Desmond)
- Copy accuracy (no hallucinated features)
- Narrative flow (does it make sense to a judge/user?)
- Link verification (do all links work?)
- Tone consistency

---

## Report Format

Every report goes in `R&D/Reports/` with filename:
`YYYY-MM-DD-{component}-{cycle}.md`

```markdown
# Test Report: {Component}
**Date:** YYYY-MM-DD
**Tester:** {Agent}
**Cycle:** {N}
**Layer:** {Which AAE layer}

## Scope
- What was tested

## Results
| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| ... | ... | ... | ✅/❌/⚠️ |

## Issues Found
1. [CRITICAL/MAJOR/MINOR] Description
   - Repro steps
   - Suggested fix

## Verdict
- Ready to ship: YES/NO
- Blockers: ...
- Next cycle focus: ...
```

---

## Rules

1. **No self-testing** — the person who builds it doesn't get final say on whether it works
2. **Log everything** — if it's not in the report, it didn't happen
3. **Fail fast** — finding a bug early is a win, not a setback
4. **One cycle per day max** — don't rush testing to hit deadlines
5. **Retest after every fix** — no "probably fine"

---

*"We test, we report, we make adjustments." — Jordan*