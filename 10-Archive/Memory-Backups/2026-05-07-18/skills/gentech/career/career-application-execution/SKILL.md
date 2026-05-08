---
name: career-application-execution
description: Draft, consolidate, track, and submit job/internship applications — especially multi-opportunity batches using vault-based coordination
trigger: After opportunity evaluation is complete, when ready to draft/submit applications; user says "let's apply", "submit applications", or "prepare application packets"
input: Evaluated opportunities with role details, resume variant mapping, user personal details (name, LinkedIn, portfolio)
output: Ready-to-submit application packets (cover letters + tracking) and submission checklist
---

# Career Application Execution — Drafting to Submission

## Overview
This skill governs the **execution phase** after opportunity research and evaluation. It covers turning evaluated opportunities into actual submissions: drafting tailored cover letters, consolidating multi-application packets, tracking, and final submission. It emphasizes **vault-based coordination** and **batch processing** to minimize context-switch.

## When to Use
- `career-platform-research` has produced go/no-go recommendations
- Multiple opportunities need to be applied to in a single batch
- User has confirmed which roles to pursue and is ready to draft/submit
- Need to maintain version control across cover letters and track submission dates

## METHODOLOGY — Five-Phase Workflow

### Phase 1: Inventory & Gap Analysis
1. **Check existing application drafts** in vault (`04-Entertainment/Applications/` or similar)
   - Look for: `{Company}-{Role}-CoverLetter.md` standalone files
   - Look for: consolidated docs like `College.xyz-{Name}-{Roles}.md`
2. **Identify gaps** — which roles lack cover letters?
3. **Catalog resume variants** available (`02-Labs/Resumes/`):
   - Growth-focused resume
   - Analyst-focused resume
   - Master/General resume
   - Verify file existence and PDF generation

### Phase 2: Standalone Draft Creation (for missing roles)
For each missing role, create a standalone cover letter file following `career-platform-research` template structure:
- Use company/role-specific emphasis from the evaluation doc
- Include: subject line, why-I'm-interested, why-I-fit, contributions, links, sign-off
- Keep length: 200–300 words (concise but substantive)
- Save as: `{Company}-{Role}-CoverLetter.md`

**Do not** edit consolidated master yet — keep versioned.

### Phase 3: Consolidation
Patch the master application document (e.g., `College.xyz-Jordan-Hibachi-Injective.md`) to integrate new role:
1. Add role to **Target Roles** header
2. Insert **Role Overview** section (mission, needs, requirements, comp)
3. Add to **Distinguishing Factors** under Application Strategy
4. Insert **Cover Letter Template** section with full letter
5. Update **Tracking** checklist with new role entry
6. Update **Social Media Templates** to include new company/handle
7. Expand **Decision Framework** table if multi-offer scenario possible
8. Update **Notes / Customization** with role-specific tips

**Commit message style:** "Add {Role} to college.xyz application batch — cover letter, strategy, tracking."

### Phase 4: Cross-Check & Delegation
- **Resume mapping:** Confirm each role gets correct resume variant (Growth→Growth_Resume, Analyst→Analyst_Resume, Product→Master or tailored)
- **DMOB handoff:** Send message to GenTech HQ or DMOB group:
  - "Verify resume PDFs exist for [list roles]"
  - "Prepare simple tracking sheet (date, resume used, status)"
- **Personal details fill-in:** Create checklist of brackets to replace: [Name], [Email], [LinkedIn], [Portfolio], [Quantifiable achievements]

### Phase 5: Submission Execution
- User submits all applications in **single batch** (same sitting)
- Use direct links or college.xyz portal
- Screenshot confirmations or log submission URLs for tracking
- Optional: post social media templates (Twitter/LinkedIn) to signal interest
- Mark tracking checklist as submitted with dates

## OUTPUT TEMPLATE

```markdown
# Application Packet — [Date] — [User]

## Applications Submitted
| Company | Role | Resume Used | Date | Portal Link |
|---------|------|-------------|------|-------------|
| Hibachi | Growth Intern | Jordan_Growth_Resume.pdf | 2026-05-05 | [link] |
| Injective | PM Intern | Jordan_Master_Resume.pdf | 2026-05-05 | [link] |
| No Limit Holdings | Investment Analyst Intern | Jordan_Analyst_Resume.pdf | 2026-05-05 | [link] |

## Follow-Up Schedule
- [ ] Day 3–5: DM hiring managers (handles listed)
- [ ] Week 2: Follow-up email if no response
- [ ] Update tracking sheet with status changes

## Social Posts
- [ ] Twitter posted (URL)
- [ ] LinkedIn posted (URL)

## Next Steps
- [ ] Prepare for potential interviews (see `interview-prep` skill)
- [ ] Update portfolio with recent projects if needed
```

## PITFALLS & EDGE CASES

1. **Pitfall**: Submitting before resume verification — PDF missing or wrong variant.
   - **Fix**: DMOB sign-off required before submission morning. Check `02-Labs/Resumes/` for file existence.
   - **Verification**: `ls 02-Labs/Resumes/` → confirm all three PDFs present.

2. **Pitfall**: Inconsistent personal details across letters (different name spelling, missing LinkedIn).
   - **Fix**: Create a single `personal-details.md` snippet and paste into each letter before finalizing.
   - **Verification**: Read all three letters side-by-side; spot-check brackets.

3. **Pitfall**: Forgetting to update consolidated doc after creating standalone letter.
   - **Fix**: Always perform Phase 3 immediately after Phase 2. The standalone file is draft; the consolidated doc is source of truth.
   - **Verification**: grep for company name in consolidated doc; ensure present.

4. **Pitfall**: Not noting application portal quirks (some require separate account creation).
   - **Fix**: When evaluating, note "Application portal: Greenhouse / Lever / external". Allocate extra time for account setup.
   - **Verification**: Click each APPLY button before batch session to confirm flow.

5. **Pitfall**: Missing social media handles in follow-up step.
   - **Fix**: During consolidation, research and note Twitter/LinkedIn handles of hiring managers in the document.
   - **Verification**: Check each company's career page or Twitter bio for team members.

## RELATED SKILLS
- `career-platform-research` — research → evaluation → recommendation phase
- `gentech.vault-compliance-audit` — track deadlines and follow-ups in vault
- `agent-coordination` — handoff patterns to DMOB and GenTech HQ

## MAINTENANCE
College.xyz UI changes may affect APPLY button behavior or external form flows. Revalidate quarterly.

---
**Status:** Available