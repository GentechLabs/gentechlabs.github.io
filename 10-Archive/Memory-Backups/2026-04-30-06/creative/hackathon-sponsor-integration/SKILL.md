---
name: hackathon-sponsor-integration
description: "Analyze new sponsor/partner announcements during active hackathons: evaluate integration options (integrate/differentiate/compete), recommend strategic positioning, and update submission materials."
tags:
  - hackathon
  - sponsor
  - integration
  - strategy
  - competitive-analysis
  - submission
triggers:
  - Jordan shares a new sponsor announcement or partnership tweet during an active hackathon
  - A sponsor/platform launches a feature relevant to the current hackathon project
  - Need to evaluate whether to integrate, differentiate, or compete with a new ecosystem player
  - Updating submission materials to reflect new sponsor capabilities
  - A partner announcement appears mid-hackathon that could strengthen the submission
---

# Hackathon Sponsor & Ecosystem Integration

When a new sponsor, partner, or ecosystem announcement drops during an active hackathon — or when Jordan shares an external crypto/web3 project for evaluation — analyze how it fits with the current project, evaluate integration options, recommend strategic positioning, and update submission materials.

## When to Use

- Jordan shares a sponsor announcement tweet/post during an active hackathon
- Jordan shares a non-sponsor crypto/web3 project and asks "do we need this?" or "how does this relate?"
- A sponsor launches a new feature/plugin that relates to the project
- An external infrastructure project launches that could be a partner, competitor, or complement
- Need to decide between: integrating the new capability, differentiating against it, or competing
- Updating the submission writeup to reflect new sponsor integrations
- Evaluating whether a new announcement strengthens or threatens the project's positioning

## Workflow

### 1. Capture & Research the Project

Extract key facts from the announcement or shared link:

**If it's a sponsor announcement:**
- **What**: Product, feature, or partnership announced
- **Who**: Sponsor name, partners involved
- **When**: Announcement date, rollout timeline
- **Evidence**: Views, likes, reposts (traction signal)
- **Technical details**: APIs, SDKs, integration patterns mentioned

**If it's a non-sponsor project (deep dive mode):**
1. **Browse the project website** — homepage, product pages, integrations page, team page
2. **Map their integration ecosystem** — what partners/chains/tools do they connect with?
3. **Check their technical claims** — "200K workflows/day" — is there evidence?
4. **Search for GitHub repos** — is there actual code or just marketing?
5. **Note their chain/blockchain focus** — are they on our chain or cross-chain?
6. **Extract their actual product** — not the marketing pitch. What does the SDK/API/tool actually do?

**For both cases, produce:**
- **What they actually built** (not the marketing copy)
- **Their integration stack** (table format: category → partners)
- **Traction signals** (claimed metrics, actual evidence)
- **Technical depth** (SDK maturity, API availability, documentation quality)

### 2. Read Current Project State

Pull context from the vault:

```bash
# Current architecture
cat "$VAULT/02-Labs/Hackathons/Active/[hackathon]/TECHNICAL-ARCHITECTURE.md"

# Current submission writeup
cat "$VAULT/02-Labs/Hackathons/Active/[hackathon]/SUBMISSION-WRITEUP.md"

# Competitive landscape
cat "$VAULT/02-Labs/Hackathons/Active/[hackathon]/../AgentEscrow-Competitive-Intel.md"
```

### 3. Search Competitive Landscape (Colosseum Copilot)

Find who else is building in this space — especially prize winners and accelerator companies:

```bash
# Search for competitors in the same vertical
curl -s -X POST "$COLOSSEUM_COPILOT_API_BASE/search/projects" \
  -H "Authorization: Bearer $COLOSSEUM_COPILOT_PAT" \
  -H "Content-Type: application/json" \
  -d '{"query": "[relevant vertical]", "limit": 10, "filters": {"winnersOnly": true}}'

# Check relevant clusters for project density
curl -s "$COLOSSEUM_COPILOT_API_BASE/clusters/[cluster-key]" \
  -H "Authorization: Bearer $COLOSSEUM_COPILOT_PAT"
```

**Useful clusters for agent/payment projects:**
- `v1-c14`: Solana AI Agent Infrastructure (325 projects)
- `v1-c16`: Stablecoin Payment Rails
- `v1-c26`: Simplified Solana Payment Solutions

**Produce a tiered competitive report:**
- **Tier 1: Prize winners** — who's already won in this space
- **Tier 2: Active competitors** — similar projects, no prize yet
- **Tier 3: Adjacent players** — overlapping but different angle
- **Key gaps** — what nobody has built yet

### 4. Map Overlap vs. Complement

Determine the relationship between the announcement and the project:

| Signal | Meaning | Action |
|--------|---------|--------|
| Solves same problem | Direct competitor | Differentiate or compete |
| Solves adjacent problem | Potential integration | Integrate |
| Enables new capability | Force multiplier | Integrate + extend |
| Overlaps with existing sponsor | Conflict risk | Choose one, differentiate |

### 4. Evaluate Three Options

Present Jordan with three clear options:

**Option 1: Integrate**
- Use their tool/plugin instead of building from scratch
- Saves development time
- Gets listed in their ecosystem/discovery layer
- Risk: dependency, less control

**Option 2: Differentiate**
- Position the project as complementary infrastructure
- They handle X; we handle Y
- Not competitive — layered value
- Risk: requires clear narrative

**Option 3: Compete**
- Build own equivalent
- More control, more work
- Differentiation through execution
- Risk: duplicated effort, less ecosystem support

### 5. Recommend One

Based on:
- **Hackathon timeline**: Integrating is faster if deadline is tight
- **Sponsor judge signal**: Using sponsor tools directly scores higher
- **Ecosystem positioning**: Complementary plays often stronger than competitive
- **Technical fit**: How much refactoring is required

### 6. Research the Actual SDK/API

Before committing to integration, verify the sponsor's actual tooling exists:

```bash
# Search npm for SDK packages
npm search @[sponsor-org]

# Check GitHub for repos
gh repo list [sponsor-org] --limit 10

# Look for Anchor program IDs (Solana hackathons)
grep -r "program_id\|Program ID" [sponsor-docs]
```

**Key questions:**
- Is there an npm package? What version?
- Is the program deployed to devnet/mainnet?
- What are the PDA seeds for account derivation?
- Can we CPI into it from our Anchor program?

**If SDK is immature (< v1.0):** Note the fallback strategy. Don't block on incomplete APIs.

### 7. Create Integration Strategy Document

Save to `[hackathon]/OOBE-INTEGRATION-STRATEGY.md` (or sponsor-name variant):

```markdown
# [Sponsor] x [Project] — Integration Strategy

**Date:** [date]
**Decision:** [Option number] — [one-line summary]
**Status:** Approved by Jordan

---

## Strategic Positioning
[One sentence: who handles what]

## How [Sponsor] Fits Into the Stack
[ASCII diagram showing layered architecture]

## Updated Sponsor Integration Table
[Table with all sponsors, integration depth, roles]

## Creative Positioning
- **Narrative:** [Compelling one-liner]
- **Story arc:** [3-4 step progression]
- **Social thread angle:** [Draft tweet/post]

## Technical Integration Points
[Specific API/SDK patterns, code examples]

## Why This Wins
[For judges + for ecosystem]

## Next Steps
[Numbered action items]
```

### 8. Update ALL Submission Materials

Patch every submission document — not just the writeup:

**Submission Writeup:**
1. Sponsor table: Add new sponsor with integration depth
2. "What Makes This Different": Add integration as differentiator
3. Demo flow: Add sponsor integration to demo steps

**Demo Storyboard:**
- Update scene where sponsor integrates (often Scene 1: identity registration)
- Update voiceover to mention sponsor by name
- Update closing tagline if it changes

**Social Thread:**
- Add sponsor to tweet that lists integrations
- Update hook if sponsor changes the narrative angle

**Architecture Doc:**
- Update system architecture diagram (add new layer if needed)
- Add new sponsor section with code examples
- Update risk matrix (SDK maturity, fallback strategy)
- Update build order if integration adds work

**Don't forget:** Each file needs the sponsor name, program ID, and SDK package name consistently across all docs.

### 9. Save Research to Vault (Non-Sponsor Deep Dives)

When the project is NOT a sponsor, save the full analysis to the hackathon folder:

```bash
# Save deep dive document
cat > "$VAULT/02-Labs/Hackathons/Active/[hackathon]/RESEARCH-[project-name]-deep-dive.md" << 'EOF'
# [Project Name] — Deep Dive Analysis

## What [Project] Actually Is
[Clear description, not marketing copy]

## Their Integration Stack
[Table of categories → partners]

## Competitive Landscape (Colosseum)
[Tiered competitor report]

## Relevance to [Our Project]
[How it connects — synergy or competition]

## Bottom Line
[One-paragraph recommendation: integrate, track, or ignore]
EOF
```

**This creates a research trail** — future sessions can pull context from these docs.

### 10. Report to Jordan

Summarize:
- Decision made (with reasoning)
- Files created/updated (list all 5+ docs)
- Technical integration details (SDK, program ID, PDA seeds)
- Next steps needed

## Pitfalls

- **Don't integrate without checking SDK availability.** Announcements ≠ shipped APIs. Verify the integration is actually possible before committing. Check npm, GitHub, and program IDs.
- **Don't trust marketing claims.** "200K workflows/day" sounds impressive — but is there evidence? Always verify claimed metrics against actual usage data, GitHub activity, or independent sources.
- **Don't assume non-sponsors are competitors.** A project like W3.io (decentralized cloud) might be infrastructure *below* your application layer — complementary, not competitive. Map the layers before deciding.
- **Don't over-narrate.** Judges want technical depth, not marketing fluff. Keep strategy docs tight.
- **Don't forget demo impact.** If you add a sponsor integration, the demo must show it.
- **Don't compete when you can compose.** Complementary positioning almost always stronger in hackathons.
- **Don't update submission without Jordan's approval.** Strategy docs are recommendations; submission changes need sign-off.
- **Don't forget ALL docs.** Updating just the writeup leaves stale info in the demo storyboard, social thread, and architecture doc. Update everything consistently.
- **Don't trust announcement naming.** "AgentIdentity plugin" might actually be "SAP v2 Identity Layer" — dig into the actual SDK to get the real names and patterns.

## Example Trigger Phrases

- "OOBE Protocol x Metaplex — this is relevant to our submission"
- "New sponsor announcement, how should we position?"
- "Should we integrate this or build our own?"
- "Update the submission to include [sponsor]"
- "How does [external project] relate to what we're building?" (non-sponsor)
- "Do we need this?" (when sharing a crypto/web3 project link)
- "Looking into [project] tomorrow" (signals upcoming evaluation)

## Related Skills

- `hackathon-submission-package` — Generates submission materials (this skill updates them mid-hackathon)
- `hackathon-content-curation` — Curates existing docs (this skill handles new announcements)
- `hackathon-tech-stack-evaluation` — Evaluates hackathon platforms (this sponsor integration analysis)
- `colosseum-copilot-research` — Researches competitors (this analyzes new ecosystem players)
