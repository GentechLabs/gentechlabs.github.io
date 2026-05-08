---
name: hackathon-tracker
description: Research, evaluate, and add hackathons to the vault tracking system. Covers Devpost/web research, deadline management, and multi-file vault updates.
tags: [hackathon, vault, research, tracking]
---

# Hackathon Tracker

Research a new hackathon opportunity and integrate it into the GenTech vault tracking system.

## When to Use

- Jordan mentions a new hackathon to evaluate
- Adding a hackathon to the active roster
- Updating hackathon status (submitted, withdrawn, etc.)
- Checking deadlines and priorities
- Periodic hackathon landscape review

## Workflow

### 1. Research the Hackathon

**Primary source:** Devpost (most hackathons are listed there)
```
https://devpost.com/hackathons?search=<keywords>
```

**Extract these details:**
- Name, deadline, prize pool
- Tech stack requirements (Solidity? Gemini? MCP?)
- Submission format (video length, repo requirements)
- Team size limits
- Participant count (competition density)
- Whether it's online or in-person
- Registration link

**If not on Devpost:** Search the hackathon's own website or Google for the landing page.

### 2. Evaluate Fit

Ask these questions:
- Does it align with our AAE (Agent Economy) narrative?
- Does the tech stack overlap with what we already have?
- Timeline conflict with existing hackathons?
- Prize-to-effort ratio worth it?
- Beginner-friendly or expert-only?

### 3. Competitive Landscape Analysis (Colosseum Copilot)

Before committing to a hackathon, run competitive analysis to understand what's already been built:

```bash
# Search for competing projects
curl -s -X POST "$COLOSSEUM_COPILOT_API_BASE/search/projects" \
  -H "Authorization: Bearer $COLOSSEUM_COPILOT_PAT" \
  -H "Content-Type: application/json" \
  -d '{"query": "<your concept keywords>", "limit": 10}'
```

**Analyze results for:**
- Who's built similar things (project name, hackathon, prize won)
- What gaps exist (full gap = nobody, partial gap = incomplete coverage)
- What judges have seen before (avoid "me too" submissions)
- Our differentiation angle

**Gap classification:**
- **Full gap:** Nobody has addressed this problem → strong positioning
- **Partial gap:** Incomplete coverage (segment, UX, geographic) → targeted wedge
- **False gap:** Already solved → pivot or find unique angle

Save competitive analysis to `06-Content/<hackathon>-Competitive-Analysis.md`.

### 4. Update Vault Files

**Always update these files (in order):**

1. **`03-Projects/HACKATHON-ROSTER-2026.md`** — Master roster
   - Add to "Active Focus" (if building now), "Watch" (if future), or "Skipped" (if not pursuing)

2. **`01-Agency/active-hackathons.md`** — Detailed active list
   - Add with status emoji: 🟢 building, 🟡 queued, 🔵 registered, ⏸️ paused

3. **`01-Agency/Approvals/HACKATHON-TODO.md`** — Command center
   - Add full section with TODO checklist, requirements, and timeline

4. **`03-Projects/Hackathons/<hackathon-name>.md`** — Individual detail note
   - Create if hackathon is actively being considered
   - Include: requirements, submission checklist, our angle, key dates

### 4. Status Emojis

| Emoji | Status | Meaning |
|-------|--------|---------|
| 🔴 | PRIMARY | Active sprint, building now |
| 🟡 | QUEUED | Coming up next |
| 🟢 | REGISTERED | Signed up, not building yet |
| ⏸️ | PAUSED | On hold |
| ⛔ | WITHDRAWN | Dropped/withdrawn |
| ⚪ | FUTURE | Far out, monitoring |

### 5. Git Commit

After updating files:
```bash
cd /root/vaults/gentech && git add -A && git commit -m "Add <hackathon> to tracker"
```

## Vault File Structure

```
03-Projects/
├── HACKATHON-ROSTER-2026.md        # Master roster
├── Hackathons/
│   ├── google-cloud-rapid-agent.md  # Individual notes
│   ├── solana-frontier.md
│   └── kite-ai.md
01-Agency/
├── active-hackathons.md             # Detailed active list
├── Approvals/
│   └── HACKATHON-TODO.md            # Command center
```

## Pitfalls

- **Don't forget to update ALL files** — roster, active list, command center, detail note
- **Check for date conflicts** before adding — don't stack 3 hackathons in the same week
- **Verify deadline accuracy** — always confirm from the official source, not memory
- **Prize amounts change** — re-check before submission
- **Partners/prizes sometimes announced later** — note "TBD" and set a reminder to check
- **Run competitive analysis BEFORE building** — Colosseum Copilot can tell you if someone already won with the same idea. Check the "crowdedness" score (higher = more competition in that space)
- **Latinum won $25K for MCP wallet** — direct competitor in AI agent payments space. Our escrow + x402 angle differentiates.

## Verification

After adding a hackathon, confirm:
- [ ] All 4 vault files updated
- [ ] No deadline conflicts with existing hackathons
- [ ] Git committed
- [ ] Detail note includes submission checklist
