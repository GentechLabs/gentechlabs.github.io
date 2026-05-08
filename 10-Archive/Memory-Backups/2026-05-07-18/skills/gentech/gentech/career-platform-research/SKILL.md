---
name: career-platform-research
description: Research and evaluate internship/job opportunities from online platforms — extract full details, match against candidate profile, recommend application strategy, delegate resume/cover letter prep
trigger: User shares career platform link or says "review opportunities", "should I apply", "internship research"
input: Platform URL or list of opportunity links, plus optional user profile constraints (location, timeline, salary expectations, tech stack)
output: Structured opportunity summary with go/no-go recommendation, priority ranking, and delegated action items for resume/cover letter teams
---

# Career Platform Research — Strategic Opportunity Evaluation

## Overview
This skill governs the end-to-end workflow for researching, evaluating, and strategizing around internship/job opportunities from online talent platforms (college.xyz, LinkedIn, Handshake, etc.). It emphasizes **complete information extraction** before decision-making and **clear delegation** to preparation teams.

## When to Use
- User provides a platform link with opportunities (e.g., "college.xyz", "Handshake", "LinkedIn Jobs")
- User asks "should I apply to X?" without full details available
- Evaluating multiple opportunities across platforms for fit and priority
- Need to coordinate resume/cover letter tailoring across departments

## METHODOLOGY — Four-Phase Workflow

### Phase 1: Platform Discovery & Full Opportunity Capture
1. **Navigate to platform homepage** → confirm platform legitimacy and scope
2. **Locate opportunity listings** (Careers, Internships, Jobs section)
3. **Capture full list view** — snapshot all available opportunities with: title, company, location, comp, posting date
4. **Click into each relevant opportunity** individually
5. **Snapshot full details page** — capture entire page content, not just summary
6. **Extract complete data** for each opportunity:

**Required Fields:**
- Title & Role type (Internship/FT/Part-time)
- Company name & domain (DeFi/CEX/Infrastructure/Tools)
- Location (Remote/Hybrid/On-site + city)
- Compensation (salary range, token vesting, benefits)
- Timeline (Summer 2026, specific dates, duration, start/end)
- Application deadline (if listed)
- Direct apply link (button URL, not just page URL)

**Responsibilities:**
- Full bullet-point list of day-to-day tasks
- Project scope and ownership expectations
- Team structure and reporting lines

**Qualifications:**
- Required: degree, year, technical skills, prior experience
- Nice-to-have: specific tools, frameworks, domain knowledge
- Cultural/organizational fit expectations

**Company Context:**
- Business model (DEX, CEX, protocol, infra, tooling)
- Stage (early-stage startup, mature protocol, unicorn)
- Recent news/partnerships/funding (quick scan)

### Phase 2: Profile Matching & Constraint Checking
Compare opportunity against user's known constraints (from memory/user profile):
- **Geographic**: Remote-only? NYC relocation? Visa sponsorship needed?
- **Timeline**: Summer 2026 locked? Fall/winter flexibility?
- **Compensation**: Minimum acceptable range? Token-heavy vs. cash?
- **Role type**: Only internships? FT OK? Part-time acceptable?
- **Tech stack alignment**: Python/SQL/React/etc. match?
- **Domain interest**: DeFi/trading/infra/AI preference?

**Go/No-Go Filters:**
- ❌ Location mismatch (on-site in wrong city, no remote option)
- ❌ Timeline incompatible (wrong season, duration too short/long)
- ❌ Comp below threshold (if user has explicit minimums)
- ❌ Role type excluded (e.g., user said no full-time)
- ✅ All constraints satisfied → proceed

### Phase 3: Strategic Summary & Recommendation
Structure output into clear sections:

**Executive Summary:**
- Opportunity count found, constraint-satisfying count
- Top recommendation (with confidence level)
- Immediate action items (deadline awareness)

**Detailed Profiles** (one per qualifying opportunity):
- Company & role headline
- Why this fits (matching skills, interests, timeline)
- Why this may not fit (gaps, compromises needed)
- Application strength assessment (strong/medium/weak match)

**Priority Ranking** (if multiple):
1. **Tier 1** — Perfect fit, high-value comp, strategic company
2. **Tier 2** — Good fit, acceptable comp, learning opportunity
3. **Tier 3** — Borderline fit, consider only if Tier 1/2 decline

**Risk Assessment:**
- Deadline proximity (days remaining)
- Competition level (high-profile company → more applicants)
- Application complexity (multi-stage interview, take-home test)
- Red flags (early-stage risk, unclear comp, vague responsibilities)

### Phase 4: Delegation & Next Steps
Route tasks to appropriate GenTech departments:

**Resume Variant Shortcut:** For common role categories (Growth, Analyst, Product), pre-tailored resume variants are maintained in `02-Labs/Resumes/RESUME_STRATEGY.md`. Use this mapping as a starting point before further customization.

**To DMOB (Resume/CV):**
- "Tailor resume for [Company] [Role]"
- Emphasize: [specific skills from JD]
- Highlight: [relevant projects/experience from user profile]
- Format: [traditional vs. crypto-native?]

**To GenTech Strategies (Cover Letter/Messaging):**
- "Draft cover letter for [Company]"
- Narrative: [why user fits + why company exciting]
- Tone: [professional/startup-energy/technical]
- Length: [short email vs. detailed letter]

**To Gentech (CEO) for strategy:**
- "Review final recommendation before application"
- "Coordinate mock interview prep if needed"

**User Actions:**
- [ ] Create accounts on application platforms
- [ ] Draft custom responses to supplemental questions
- [ ] Schedule availability for interviews
- [ ] Set deadline reminders (X days before)

## OUTPUT TEMPLATE
Use the following markdown structure:

```markdown
# Opportunity Evaluation: [Company] — [Role]

**Platform:** college.xyz | [Link]
**Constraints Check:** ✓ Remote ✓ Summer2026 ✓ Comp range ✓ Role type

## Executive Summary
[One-paragraph recommendation with confidence]

## Opportunity Profile

### Company Overview
[Business model, stage, recent news]

### Role Details
- **Title:** [Title]
- **Location:** [Remote/NYC/etc.]
- **Timeline:** [Summer 2026 + duration]
- **Compensation:** [$ range / $K per month]
- **Application Deadline:** [Date] (in X days)

### Responsibilities
- Bullet 1
- Bullet 2

### Qualifications
**Required:** [list]
**Nice-to-have:** [list]

## Profile Match Analysis
**Strengths:** [user's relevant skills/experience]
**Gaps:** [missing quals, compromises needed]
**Overall:** [Strong/Medium/Weak] fit

## Priority Ranking
[ ] Tier 1 — Strong fit, strategic value
[ ] Tier 2 — Good fit, solid option
[ ] Tier 3 — Borderline, apply only if others decline

## Risks & Considerations
- ⚠️ [Deadline in X days — prepare materials by Y]
- ⚠️ [High competition — $X funding round just announced]
- ℹ️ [Note about interview process, take-home test]

## Delegated Tasks
- **DMOB:** Tailor resume for [specific matches]
- **GenTech Strategies:** Draft cover letter emphasizing [narrative]
- **Gentech:** [Final review / coordination]

## User Next Steps
- [ ] [Action with deadline]
- [ ] [Action]
```

## PLATFORM-SPECIFIC CONSIDERATIONS

### college.xyz
- Student-focused nonprofit platform
- Opportunities often beginner-friendly, no portfolio required
- Application may be direct (company careers page) or platform-mediated
- Check if "Apply →" button links externally or uses platform form
- For multi-application batching patterns and session notes, see `references/college-xyz-multi-application-2026-05-04.md`

### LinkedIn Jobs
- Requires LinkedIn account; some postings need Premium to apply
- Salary range often hidden; negotiate later
- Easy-apply button may auto-submit with profile

### Handshake
- University-verified student platform
- Often requires .edu email verification
- Employers explicitly recruiting students/new grads

### Company Career Pages (Direct)
- Most reliable source for full details
- May have additional steps (HackerRank test, Calendly screening)
- Check for "Early Career" or "Students" section filters

## PITFALLS & EDGE CASES

1. **Pitfall**: Incomplete extraction — only reading summary, missing detailed responsibilities/qualifications.
   - **Fix**: Scroll full page, expand all accordions, check tabs ("Responsibilities", "Qualifications", "Benefits").
   - **Verification**: Compare page source vs. rendered text; check for lazy-loaded sections.

2. **Pitfall**: Assuming comp range is annual when it's monthly (or vice versa).
   - **Fix**: Explicitly state "per month" or "annual" in extracted comp; convert to comparable units.
   - **Example**: Injective PM intern: $7.5K–$8K per month → ~$90K–$96K annualized.

3. **Pitfall**: Overlooking implicit requirements ("must be currently enrolled").
   - **Fix**: Check eligibility section word-by-word; if unclear, flag as "verify eligibility" risk.

4. **Pitfall**: Missing deadline timezone conversion.
   - **Fix**: Convert all deadlines to user's local timezone; add buffer (apply 2 days early).

5. **Pitfall**: Not checking remote vs. hybrid vs. on-site nuances.
   - **Fix**: "Remote" may mean "US-only remote" — check if "Worldwide remote" specified; if not, assume US-only.

6. **Pitfall**: Failing to identify company business model correctly.
   - **Fix**: Quick Google search "[Company Name] crypto" or "[Company] web3" to confirm domain (DEX vs. CEX vs. infra).

7. **Pitfall**: Delegating without context — sending raw JD to resume team.
   - **Fix**: Always include: why this role, user's matching strengths, specific tailoring instructions.

## RELATED SKILLS
- `research.opportunity-discovery` — for hackathons/bounties/grants (competitive events)
- `gentech.strategic-resource-integration` — for evaluating API/tool partnerships
- `gentech.vault-compliance-audit` — for tracking application deadlines in vault

## MAINTENANCE
Platform UIs change (college.xyz redesign, LinkedIn layout updates). Revalidate extraction patterns quarterly.

---

**Status:** Available