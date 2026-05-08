---
name: internship-application
description: Research and apply to curated internship opportunities from specialized platforms (College.xyz, hackathon job boards, etc.). Extracts role requirements, conducts company research, generates tailored cover letters and application materials, and organizes them in vault with follow-up workflow.
triggers:
  - User asks to apply to an internship found on College.xyz or a similar curated opportunity platform
  - User requests cover letter drafting for a specific role with provided context
  - User wants application packages for multiple roles from the same source
context: []
---

# Internship Application — Class-Level Skill

## When to Use

Use this skill when applying to internships or early-career roles sourced from **curated opportunity platforms** such as:
- College.xyz (student-focused crypto/Web3 roles)
- Hackathon career fairs / job boards
- University-specific internship portals
- Fellowship program application systems
- Any platform where opportunities are pre-vetted and grouped by source

**Do NOT use for**: Generic LinkedIn/Indeed job applications (those are broader, less structured). Use `hackathon-submission-package` for hackathon project writeups instead.

## Workflow Overview

```text
1. OPPORTUNITY DISCOVERY — Navigate platform → locate role → capture full context
2. REQUIREMENTS EXTRACTION — Parse responsibilities, qualifications, nice-to-haves
3. COMPANY RESEARCH — Gather company background, mission, recent news, tech stack
4. APPLICATION CRAFTING — Write tailored cover letter(s) emphasizing role-specific alignment
5. VAULT ORGANIZATION — Save materials with clear naming and structure
6. SUBMISSION & TRACKING — Provide next steps, follow-up schedule, decision framework
```

## Step-by-Step Process

### Phase 1: Discovery & Extraction

**Step 1: Access opportunity source**
- Navigate to the platform page containing the role listing
- Click into the specific role to load full details
- Snapshot the page (or copy-paste) all text fields: About the Role, Responsibilities, Qualifications, Nice-to-Haves, Compensation, Timeline

**Step 2: Parse role into structured form**
Create a quick reference block in your draft:

```
Role: [Title]
Company: [Name] — [one-line mission/pitch]
Platform: [College.xyz, etc.]
Compensation: [Specified or TBD]
Location: [Remote / NYC / etc.]
Timeline: [Summer 2026 / etc.]

Key responsibilities (3–5 bullets):
- ...
- ...
- ...

Key qualifications (must-haves):
- ...
- ...
- ...

Nice-to-haves:
- ...
- ...
```

**Step 3: Immediate company research attempt**
Use one of these approaches:
- Direct site crawl: `curl -s <company.com>/about` (if accessible)
- Web search via terminal: `curl -s "https://api.duckduckgo.com/?q=<company> <keywords>&format=json"` (simple, no dependencies)
- Fall back to known industry context if site is blocked/JS-heavy

**Failure fallback:** If company research fails due to site blocking or complexity, continue with generic industry knowledge and note: `[Research note: Specific company details unavailable; proceed with standard industry framing]`.

### Phase 2: Application Drafting

**Step 4: Choose positioning angle per role type**

| Role focus | Positioning emphasis | Tone |
|------------|---------------------|------|
| **Growth / Business Dev** | Growth loops, user acquisition, metrics, campaign execution, crypto-native hustle | Founder-coded, lean-in, "get things done" |
| **Product Management** | Analytical thinking, cross-functional collaboration, roadmap support, market analysis | Structured, process-oriented, executive-ready |
| **Engineering / Research** | Technical depth, open-source contributions, system design, research output | Precise, code-first, evidence-driven |
| **Design / Content** | Visual storytelling, brand alignment, portfolio emphasis | Creative, aesthetic-aware |
| **General Early-Career** | Agentic execution, fast learning, team contribution | Adaptable, eager, reliable |

**Step 5: Draft cover letter structure**

```
Subject: Application: [Role] — [Your Name]

Opening paragraph:
- Source platform (College.xyz)
- Signal you've read the role spec (mention 1–2 specific requirements)
- One-line company mission alignment (show you get what they do)

Why I'm a fit (2–3 bullets):
- Match each bullet to a key responsibility or qualification
- Use concrete, believable examples (even if small)
- Include metrics if possible (e.g., "grew Discord from 0 to 200 members")

What I can contribute (2–3 bullets):
- Forward-looking: what you'll actually do this summer
- Connect to their business goals (user growth, product velocity, research output)
- Show awareness of their team structure (report to Head of Growth, support CEO, etc.)

Closing:
- Availability confirmation (dates, location, work authorization)
- Links to relevant profiles (LinkedIn, GitHub, Twitter if crypto-native)
- Call to action ("Happy to jump on a call")

Signature: Name | Email | Phone | [Location if relevant]
```

**Step 6: Tailor keywords per platform**

College.xyz roles: emphasize "crypto-native," "student builder," "undergraduate," "Web3," "decentralized," "protocol," "community growth," "hackathon experience."

Hibachi-style: "perpetuals," "trading venue," "liquidity," "user acquisition," "growth campaigns," "affiliate strategy."

Injective-style: "L1 blockchain," "DeFi infrastructure," "order book," "cross-chain," "product roadmap," "executive support," "analytical."

### Phase 3: Vault & Follow-Up

**Step 7: Vault organization structure**

```
/root/vaults/gentech/04-Entertainment/Applications/
├── <Company>-<Role>-CoverLetter.md          # Submission-ready letter
├── <Company>-<Role>-ApplicationNotes.md     # Research, role breakdown, personalization points
└── <source-platform>-ApplicationsIndex.md   # Tracking sheet (optional, for multi-role applications)
```

File naming: `Hibachi-Growth-Intern-CoverLetter.md`, `Injective-PM-Intern-ApplicationNotes.md`

**Step 8: Create tracking checklist at bottom of draft**

```
Application submitted: [date]
Follow-up scheduled: [date + 7–10 days]
Interview prep notes: [link to prep doc if created]
Decision expected: [timeline if stated]
```

**Step 9: Generate auxiliary materials (if user requests)**

- LinkedIn post announcing application (optional signaling)
- Twitter/X thread about why you're excited about the company
- Follow-up email template for 7–10 days post-submission
- Outreach template for connecting with employees on LinkedIn/Twitter

## Output Format

Deliver to user as:
1. **Cover letter** — ready to copy-paste into application form or email body
2. **Application notes** — role breakdown + company research + your talking points
3. **Next steps checklist** — submission, follow-up, interview prep
4. **Optional: Social media post templates** — for professional signaling

Save all files to vault with descriptive names. Send brief confirmation to user's home group (GenTech Entertainment for college.xyz work) with file paths and what's needed to finalize.

## Pitfalls

**Research gaps when company is obscure or site blocked:** Proceed with industry-standard framing. Note research limitations in your notes file. For crypto companies, rely on known ecosystem context (e.g., "Injective is an L1 for DeFi with Tendermint consensus") rather than waiting for perfect info.

**Work authorization ambiguity:** For US-based roles, you MUST address work authorization directly in the cover letter or be prepared for an automatic screen-out. Ask user explicitly: "Are you authorized to work in the US, or do you require sponsorship?" Cannot skip.

**Over-personalization trap:** Avoid writing a unique letter from scratch for every role if applying to multiple roles at same company. Create a **master template** then slice per role. Document the template in `references/`.

**Timeline conflicts:** Confirm availability matches role dates before drafting. If user has known conflicts (wedding, travel), surface early and propose accommodations (e.g., "I can start June 1–August 15, with full availability except July 5–12").

**Platform-specific nuances:** College.xyz explicitly targets "undergraduates who build" — emphasize student status, hackathons, campus clubs, academic projects. For non-student platforms, skip student framing.

## Related Skills

- `hackathon-submission-package` — for project-focused applications (Hackathon submissions, grant proposals, bounty writeups)
- `hackathon-project-scaffold` — if the internship application requires project proposals
- `humanizer` — to strip overly formal language if company brand is casual
- `research` — for deeper company/ecosystem investigation beyond surface-level

## Templates

See `templates/` directory for:
- `cover-letter-template.md` — Role-agnostic template with fill-in blocks and tone adaptation matrix
- `application-tracking-sheet.md` — Multi-application tracker with follow-up schedule

## Support Files

See `references/` directory for platform-specific role breakdowns:
- `college-xyz-hibachi-growth-intern-template.md` — Growth role template
- `college-xyz-injective-pm-intern-template.md` — Product role template

Add new case studies under `references/` as needed for different companies/roles.
