---
name: hackathon-research-tracking
description: "Research hackathon details from Devpost/web, assess fit, and update all vault tracking files. Pre-development workflow before hackathon-prep-audit."
version: 1.0.0
author: DMOB
license: MIT
metadata:
  hermes:
    tags: [hackathon, research, devpost, vault-tracking, timeline]
    related_skills: [hackathon-prep-audit]
prerequisites:
  commands: [grep, ls]
---

# Hackathon Research & Vault Tracking Update

Research a hackathon from web sources, assess fit for GenTech's AAE narrative, and update all vault tracking files. This is the **pre-development phase** — happens before any code audit or building.

## When to Use

- Jordan says "add X hackathon" or "research Y hackathon"
- Jordan says "check the status of Z" for a hackathon
- A new hackathon appears on the radar
- Need to verify current details (dates, prizes, requirements) for an already-tracked hackathon
- Updating the active hackathons table in HQ after a change

## Phase 1: Research the Hackathon

### Colosseum Copilot API (for Solana hackathons)

```bash
# API base: https://copilot.colosseum.com/api/v1
# Token: ~/.hermes/scripts/colosseum-config.json
# Docs: https://docs.colosseum.com/copilot/api-reference

# Search for hackathon projects
curl -X POST "$COLOSSEUM_COPILOT_API_BASE/search/projects" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "agent payments solana"}'

# Get project details by slug
curl "$COLOSSEUM_COPILOT_API_BASE/projects/by-slug/agentescrow" \
  -H "Authorization: Bearer $TOKEN"

# Analyze a project
curl -X POST "$COLOSSEUM_COPILOT_API_BASE/analyze" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"project_ids": ["..."]}'
```

### Browse the Source

```bash
# Most hackathons are on Devpost
# Navigate to the URL and extract:
# - Exact dates (start + end)
# - Prize pool breakdown
# - Requirements (what to build, tech stack)
# - Team size limits
# - Submission requirements (hosted URL, repo, demo video)
# - Participant count
# - Partner/sponsor details
```

### Devpost Navigation Pattern

1. Open Devpost URL in browser
2. Read Overview page for high-level info
3. Check Rules tab for full requirements
4. Check Schedule for exact dates
5. Note participant count (shows competition level)

### Key Data Points to Extract

| Field | Why It Matters |
|-------|---------------|
| Start/end dates | Timeline and sprint planning |
| Prize pool | ROI assessment |
| Tech requirements | Stack fit (Solana? EVM? Google Cloud?) |
| Submission format | What we need to produce |
| Team size | Solo vs. collaboration |
| Participant count | Competition level |
| Partner integrations | MCP servers, APIs we'd use |

## Phase 2: Vault Files to Update

There are **3 files** that need updating for any hackathon change:

### 1. `01-Agency/active-hackathons.md`
- **Section-based**: Current Focus / Registered / Opportunistic / Skipped
- Move hackathon between sections as status changes
- Keep descriptions concise with key facts

### 2. `02-Labs/Hackathon-Tracker.md`
- **Detailed entries**: Prize pool, dates, focus, relevance rating, status
- Numbered entries (### 1, ### 2, etc.)
- Status emojis: 🔴 PRIMARY / 🟢 ACTIVE / 🟡 REVIEW / ⏸️ SKIP / ⛔ DROPPED

### 3. `03-Projects/HACKATHON-ROSTER-2026.md`
- **Table format**: Name | Deadline | Notes | Status
- Concise — one-liner per hackathon
- Sections: Active Focus / Watch for Future / Skipped

### Update Pattern

```bash
# Always update all 3 files for consistency
# Use patch mode (not full rewrite) to avoid merge conflicts
# Preserve existing entries — only modify the target hackathon
```

## Phase 3: Competitive Landscape Analysis

Before positioning our submission, map the competitive space across chains.

### Colosseum Copilot — Search Competing Projects

```bash
TOKEN=$(jq -r .token ~/.hermes/scripts/colosseum-config.json)
BASE="https://copilot.colosseum.com/api/v1"

# Search by topic/technology
curl -s -X POST "$BASE/search/projects" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "AI agent payments x402 escrow", "limit": 10}'

# Get cluster data (e.g., v1-c14 = Solana AI Agent Infrastructure)
curl -s "$BASE/clusters/v1-c14" -H "Authorization: Bearer $TOKEN"
```

Key fields per result: `slug`, `name`, `oneLiner`, `prize` (type/amount/placement), `tags` (problemTags, solutionTags, techStack), `crowdedness` (project count in cluster), `cluster.label`.

### GitHub Search — Cross-Chain Competitors

```bash
# Base chain competitors
curl -s "https://api.github.com/search/repositories?q=agent+escrow+base+chain&sort=updated&order=desc&per_page=10"

# Avalanche competitors
curl -s "https://api.github.com/search/repositories?q=agent+escrow+avalanche&sort=updated&order=desc&per_page=10"

# x402 agent payments across chains
curl -s "https://api.github.com/search/repositories?q=x402+agent+payments+base+OR+avalanche&sort=updated&order=desc&per_page=10"
```

### Competitive Matrix Template

Build a table comparing our project vs. competitors across dimensions:

| Feature | Competitor A | Competitor B | **Our Project** |
|---------|-------------|-------------|-----------------|
| Core capability (e.g., x402) | ✅ | ✅ | ✅ |
| Gap they don't fill | ❌ | ❌ | ✅ |

**Output**: Clear positioning statement — "Competitors solve X. We solve Y."

### Chain-Specific Intelligence

| Chain | What to Check |
|-------|---------------|
| **Solana** | Colosseum clusters (325+ AI agent projects), hackathon winners |
| **Base** | GitHub repos, L2 TVL, onchain kit ecosystem |
| **Avalanche** | Often empty — first mover opportunity |
| **Ethereum** | Grant programs, ERC standards (ERC-8004, etc.) |

### Winner Analysis (Colosseum)

Study past winners in the target cluster to reverse-engineer what judges reward:

```bash
# Get cluster details (includes winnerCount + representative projects)
curl -s "$BASE/clusters/v1-c14" -H "Authorization: Bearer $TOKEN"

# Fetch a specific winner project
curl -s "$BASE/projects/by-slug/PROJECT_SLUG" -H "Authorization: Bearer $TOKEN"
```

Winner fields to analyze: `tags.problemTags`, `tags.solutionTags`, `tags.techStack`, `prize.trackName`, `prize.amount`, `team.count`, `links.presentation` (Loom/video).

**Patterns to extract:**
- What problem do winners solve? (specific pain > broad vision)
- What's their team size? (solo vs. team)
- How many sponsor integrations? (more = stronger signal)
- What's their demo format? (Loom video, live demo, slides)
- What tech stack do they use? (anchor, rust, typescript)

Output a "winning patterns" summary before brainstorming angles.

## Phase 3.5: Angle Brainstorm

After competitive analysis + winner study, generate 3-5 positioning approaches:

For each angle:
1. **Name** — memorable, pitch-ready
2. **Core pitch** — one sentence
3. **Judge appeal** — why this stands out
4. **Risk assessment** — what could go wrong
5. **Sponsor fit** — which sponsors it integrates
6. **Differentiation** — what competitors don't have

Present as a comparison table. Let Jordan pick the direction before building architecture.

## Phase 4: Fit Assessment

### Fit Rating Criteria

| Rating | Criteria |
|--------|----------|
| ⭐⭐⭐ | Directly aligns with AAE/agent economy narrative, uses our existing stack |
| ⭐⭐ | Partially fits, requires some adaptation |
| ⭐ | Tangential — only if we have spare bandwidth |

### Timeline Assessment

Calculate for each hackathon:
- **Days remaining** from today
- **Conflicts** with other active hackathons
- **Resource contention** (same team members, same codebase)
- **Sequencing** (can we reuse work from another hackathon?)

## Phase 5: Summary Format

When reporting back to Jordan, use this structure:

```markdown
## [Hackathon Name]

**Key Facts:**
- Dates: X – Y (N days from now)
- Prizes: $X cash + Y credits
- Participants: N
- Focus: [one-liner]

**Requirements:**
1. [Tech stack requirement]
2. [Submission format]
3. [Team limits]

**Why this fits / doesn't fit:**
- [2-3 bullet assessment]

**Updated Timeline:**
| Hackathon | Deadline | Days Left | Status |
|-----------|----------|-----------|--------|
| ... | ... | ... | ... |

**Action items:**
- [What needs to happen next]
```

## Phase 6: Architecture Design (When Jordan Confirms Direction)

After Jordan picks an angle from the brainstorm, generate a full technical architecture doc:

**Required sections:**
1. **The Pitch** — one-liner + problem statement
2. **Architecture Overview** — ASCII diagram of the full stack
3. **Program Architecture** — Anchor programs with PDA layouts, instructions, error codes
4. **Sponsor Integration Map** — table showing each sponsor, their program, integration point, and judge signal
5. **Demo Flow** — scene-by-scene breakdown (aim for 5 min total)
6. **Repository Structure** — file tree with program + frontend layout
7. **Sprint Plan** — phased build order with day estimates
8. **Risks + Mitigations** — table of risks and fallbacks
9. **Competitive Positioning** — feature matrix vs. competitors

Save to: `02-Labs/Hackathons/Active/[ProjectName]-Architecture.md`

## Phase 7: Sync

```bash
cd /root/vaults/gentech && ob sync
```

## Pitfalls

1. **Colosseum API endpoint**: Use `https://copilot.colosseum.com/api/v1` NOT `arena.colosseum.com`. The arena domain redirects to signup page.
2. **Colosseum API is Solana-only** — It covers 5,400+ Solana hackathon projects. For Base/Avalanche competitors, use GitHub search API (`api.github.com/search/repositories`).
3. **Don't confuse Google events** — There are multiple Google hackathons (Rapid Agent, Google for Startups AI, etc.). Track each separately.
2. **Devpost dates can shift** — Always verify current dates, don't rely on cached info from earlier research.
3. **Prizes often TBA** — Many hackathons announce prizes closer to start date. Note "TBA ~May 5" rather than guessing.
4. **Status emoji consistency** — Use the same emoji scheme across all 3 files. Don't mix 🔴 and 🟢 for the same hackathon.
5. **Section placement matters** — Moving a hackathon from "Opportunistic" to "Current Focus" signals priority change to other agents.
