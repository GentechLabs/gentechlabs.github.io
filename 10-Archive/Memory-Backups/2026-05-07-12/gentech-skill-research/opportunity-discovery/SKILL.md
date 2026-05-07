---
name: opportunity-discovery
description: Systematic scanning, filtering, and categorization of competitive opportunities (hackathons, bug bounties, grants) with emphasis on beginner-friendly, open-entry criteria
trigger: User requests to "find opportunities", "scan for hackathons", "discover bug bounties", or similar competitive opportunity discovery tasks
input: User specifies target domains (e.g., "web3", "AI", "cybersecurity") and any prize range or deadline constraints
output: Categorized report of open-entry opportunities with prize pools, deadlines, stack relevance, and explicit entry requirements
---

# Opportunity Discovery — Systematic Approach

## Overview
This skill governs the end-to-end workflow for discovering competitive opportunities (hackathons, bug bounties, grants, competitions) with a critical filter for **open-entry accessibility**. It emphasizes identifying and excluding events with hidden barriers (staking, portfolio requirements, professional credentials) that would block independent developers and beginners.

## When to Use
- User asks to "find hackathons" or "discover opportunities"
- Need to identify beginner-friendly competitive events
- Scanning for platforms with low entry barriers
- Building opportunity pipelines for teams or individuals

## METHODOLOGY — Five-Phase Workflow

### Phase 1: Multi-Platform Discovery
Search across specialized platforms in parallel:
- **Hackathons**: Devpost, DoraHacks, ETHGlobal, Major League Hacking (MLH), Hack Club
- **Bug Bounties**: HackerOne, Bugcrowd, Intigriti
- **Grants/Competitions**: Grant-specific platforms (e.g., GrantWatch, specific ecosystem sites)

Use targeted search queries combining:
- Platform name + current year (e.g., "Devpost hackathon 2026")
- "Beginner friendly", "no experience", "open to all"
- "Now accepting submissions", "upcoming deadline"
- Domain keywords (e.g., "AI hackathon", "web3 security bounty")

### Phase 2: Barrier Detection & Filtering
For each opportunity, explicitly check sign-up/application requirements. **FILTER OUT** any with:
- ❌ **Staking/financial deposits** (e.g., ETH staking for ETHGlobal events)
- ❌ **Portfolio requirements** (explicit requests for LinkedIn, GitHub portfolio, prior work samples)
- ❌ **Professional tenure requirements** ("2+ years experience", "senior-level", "industry veterans")
- ❌ **Credential prerequisites** (OSCP, CISSP, specific certifications)
- ❌ **Invite-only / application-only** (not open public submission)
- ❌ **Domain-restricted email** (requiring .edu, corporate domain verification)
- ❌ **Geographic restrictions** beyond standard sanctions (unless user specifies region)

**KEEP** opportunities that are:
- ✅ Open to "all skill levels", "beginners welcome"
- ✅ No portfolio required beyond basic GitHub repo for code
- ✅ No financial stake or deposit
- ✅ Public registration with email verification only

### Phase 3: Categorization & Enrichment
For each qualifying opportunity, extract:
- **Prize Pool**: Total value, breakdown by rank if available
- **Deadline**: Submission end date + timezone
- **Stack/Tech**: Languages, frameworks, protocols (e.g., "MCP, A2A, FHIR", "Rust, TypeScript, ZK proofs")
- **Format**: Online/in-person, team size limits
- **Eligibility**: Age, student status, geographic constraints
- **Submission Requirements**: Code repo, demo video, live demo, documentation

Structure output by prize tier: $20K+, $10K–$19.99K, $1K–$9.99K, <$1K.

### Phase 4: Platform-Specific Intelligence
Build and maintain platform-specific notes:
- **Devpost**: Filter by "Beginner Friendly" tag; watch "Now Accepting Submissions" status
- **DoraHacks**: Check "upcoming" tab; ignore "closed" or "submission ended"
- **ETHGlobal**: Always check for staking requirement; email support if unclear
- **MLH**: All Member Events are beginner-friendly by policy; filter Diversity/High School as relevant
- **HackerOne/Bugcrowd**: Only consider public programs; avoid "invite-only" or "managed" programs; minimum bounty $50–$100 indicates beginner-friendly programs

### Phase 5: Strategic Prioritization
Rank opportunities by:
1. **Alignment with user's stated tech stack/interests**
2. **Deadline urgency** (days remaining)
3. **Prize value vs. effort ratio**
4. **Learning value** (skills taught: agentic workflows, new frameworks, standards)
5. **Post-event pathways** (accelerator invitations, investor Demo Days, publishing opportunities)

## OUTPUT FORMAT
Deliver a structured report with:
1. **Executive Summary** — Count of opportunities by tier, immediate action items
2. **Opportunity Table** — Name | Prize | Deadline | Stack | Entry Barrier
3. **Detailed Entries** — For each: full description, requirements, sign-up link, judging criteria (if available)
4. **Filtered-Out List** — Events excluded and why (transparency)
5. **Priority Recommendations** — Top 3–5 picks with reasoning
6. **Strategic Next Steps** — Platform sign-ups, account creations, calendar reminders

## COMMON BARRIERS — Red Flags
Watch for these phrases in event descriptions:
- "Stake a small amount of ETH" → Financial barrier
- "Portfolio required" / "Show us your past work" → Experience barrier
- "2+ years professional experience" → Credential barrier
- "Invite-only program" → Access barrier
- "OSCP/GIAC certification required" → Certification barrier
- "Submit via hacker application review" → Process barrier (not open entry)
- "Minimum bounty: $500+" (for bug bounties) → May indicate higher entry threshold (beginner programs often $50–$100)

## PLATFORM-SPECIFIC TIPS
- **Devpost search**: Use `https://devpost.com/hackathons?utf8=✓&sort=recent&page=1` and filter "Beginner Friendly"
- **DoraHacks**: Upcoming events at `dorahacks.io/hackathon?status=upcoming` — check "Submission End Time" column
- **ETHGlobal**: Every event page has an "info/start" page; always read the staking section first
- **Bugcrowd**: Public programs at `bugcrowd.com/bug-bounty-list` — no account needed to view
- **Intigriti**: `intigriti.com/researchers/bug-bounty-programs` — fastest triage for beginners

## COMPANY-SPECIFIC PAGE INSPECTION

When an opportunity is tied to a specific company's grant or hackathon program (e.g., ElevenLabs Grants, Google Cloud Sprint, Anthropic Claude API grant), directly inspect the company's official program page using structured data extraction techniques rather than relying solely on aggregator sites.

Many modern program pages embed structured data using schema.org JSON-LD, which provides clean eligibility criteria, deadlines, and requirements without needing to parse rendered HTML.

### Extraction Workflow

1. **Fetch raw HTML** (bypass JavaScript rendering):
   ```
   curl -s https://example.com/startup-grants -o page.html
   ```

2. **Parse JSON-LD** for `FAQPage`, `Product`, or `WebPage` schemas. See `references/structured-data-extraction.md` for ready-to-use extraction scripts (Python, bash one-liners, and JS console snippets).

3. **Fallback: DOM extraction** if no JSON-LD present — use `browser_console` to expand interactive FAQ sections and pull `innerText` (see reference for exact snippet).

4. **Cross-check** key facts (deadline, eligibility) against a fresh browser visit to catch outdated structured data.

### Pitfalls

- Some sites block curl; add a user-agent: `curl -A 'Mozilla/5.0' ...`
- JSON-LD may include HTML entities; decode with `html.unescape()`
- Client-side rendered pages may serve empty initial HTML; use `browser_navigate` instead
- Structured data can lag behind page updates; always verify critical details directly from the rendered page

> **Reference:** `references/structured-data-extraction.md` contains complete scripts, edge-case handling, schema-type variations, and verification steps.

## PITFALLS & MISCONCEPTIONS
1. **Pitfall**: "All MLH events are beginner-friendly" — mostly true but some require university affiliation; always check "Who can attend?"
2. **Pitfall**: "No portfolio means no barrier" — some hackathons require GitHub with prior commits; check submission requirements for "existing code prohibited" clauses
3. **Pitfall**: "Bug bounties are all open" — many are private/invite-only; stick to explicitly public programs
4. **Pitfall**: "Cash prize = worth it" — some high-prize events have complex judging or exclusive eligibility; always verify open entry first
5. **Pitfall**: "Online = accessible" — some virtual events have timezone-locked live presentations; check schedule before committing

## MAINTENANCE
This methodology assumes current platform UIs and typical 2026 conventions. Revalidate quarterly:
- Devpost tag changes ("Beginner Friendly" may become "New to Hacking")
- Staking minimums on ETHGlobal may fluctuate with ETH price
- Bug bounty platform onboarding flows may require updated verification steps
