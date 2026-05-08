---
name: strategic-resource-integration
description: Translate external resources (APIs, tools, datasets, hackathons) into actionable GenTech projects with vault docs, implementation plans, team assignments, and coordination handoffs.
trigger: "User shares an external resource (API directory, tool, dataset, opportunity) and asks to 'map it out', 'save this', or 'make a project' — especially when combined with a use case like 'travel agent' or 'street view'."
usage: "When Jordan or another agent provides an external resource that should be converted into an internal project with structure, ownership, and execution plan. The skill produces: strategy doc (03-Strategies), implementation plan (03-Projects), project folder structure, team notifications, and Green Room handoff."
context: |
  This skill formalizes the pattern Gentech uses when encountering useful external resources. It prevents ad-hoc, undocumented decisions and ensures every opportunity is:
  - Strategically positioned within GenTech's layered architecture (AAE, DeFi, Creative, etc.)
  - Broken into phased implementation with clear owners
  - Documented in the vault for institutional memory
  - Routed to correct department heads via their groups (not DMs)
  - Coordinated through Green Room for cross-team alignment

  The skill replaces reactive "I'll look into that" with a repeatable, documented process that scales.

steps:
  - name: Strategic Mapping
    steps:
      - "Analyze the external resource: what categories/APIs/opportunities does it contain?"
      - "Map to GenTech's current projects and strategic pillars (AAE, DeFi, Creative, etc.)"
      - "Identify Tier 1 (immediate) vs Tier 2 (strategic) vs Tier 3 (long-term) opportunities"
      - "Define minimal viable product for the highest-tier opportunity"
  - name: Vault Documentation
    steps:
      - "Create strategy document in 03-Strategies/ (or closest strategic layer)"
      - "Document: integration map, architecture pattern, API prioritization matrix, risks/mitigations, roadmap phases"
      - "Format as SKILL.md-friendly (clear headers, tables, bullet lists)"
  - name: Implementation Planning
    steps:
      - "Create project folder in 03-Projects/<Project-Name>/"
      - "Write Implementation-Plan.md with: sprint goal, task breakdown (owner + status), acceptance criteria, test vectors"
      - "Define 3-phase roadmap (Foundation → Enrichment → Production)"
      - "Create subdirectories: API-Adapters/, Demos/, Integration-Tests/, Docs/, Scripts/"
  - name: Team Routing
    steps:
      - "Identify owners by department: Dev → YoYo, Infra/Keys → DMOB, Creative/Content → Desmond"
      - "Route notifications to their Telegram groups (not DMs)"
      - "Include prerequisite list (keys, access, dependencies) and blocking relationships"
  - name: Coordination Handoff
    steps:
      - "Write Green Room handoff: `09-Green Room/Handoffs/YYYY-MM-DD-<Project-Short-Name>.md`"
      - "Document: decisions made, next steps per owner, metrics to track, go/no-go criteria"
      - "Add daily cadence suggestion (standup time, demo cadence)"
  - name: Notification Broadcast
    steps:
      - "Post to Gentech HQ: high-level summary with vault links"
      - "Post to responsible Labs/Strategies/Entertainment groups: detailed task breakdown"
      - "Include success criteria and timeline"
  - name: Vault Sync
    steps:
      - "After all files written, run: `cd /root/vaults/gentech && ob sync` (if configured)"
      - "Verify files appear in Obsidian at correct paths"
outputs:
  - "Strategy document saved to 03-Strategies/<Resource>-Integration-Toolkit.md"
  - "Implementation plan saved to 03-Projects/<Project-Name>/Implementation-Plan.md"
  - "Project structure initialized with subfolders"
  - "Green Room handoff at 09-Green Room/Handoffs/<date>-<project>.md"
  - "Team notification messages sent to relevant Telegram groups"
  - "Vault sync attempted (non-fatal if not configured)"
examples:
  - input: "public-apis GitHub directory — let's map this for our travel agent / street view use case"
    output: "Created Travel-Agent project with Google Maps/OSM/Skyscanner integration adapters, 3-phase roadmap, DMOB key provisioning tasks, YoYo dev tasks, Green Room handoff, team notifications."
references:
  - name: integration-architecture-patterns
    description: "Common integration stack patterns: 6-layer model (Search → Location → Street View → Context → Transport → Support), adapter pattern with provider fallback, caching strategies, rate-limit handling. Used in Travel-Agent implementation."
    path: "references/integration-architecture-patterns.md"
  - name: public-apis-travel-category
    description: "Travel-related APIs from public-apis directory with free tier info, rate limits, and suitability for GenTech stack. Covers flights, hotels, geocoding, maps, street view, weather, currency, transport, and support services."
    path: "references/public-apis-travel-category.md"
pitfalls:
  - "Don't skip Green Room handoff — it's the coordination layer that prevents duplicate work across teams."
  - "Always create vault files BEFORE team notifications so links resolve."
  - "Never assign tasks in DMs — always use department groups per routing rules."
  - "If API keys are needed, DMOB must provision BEFORE dev starts; block on keys, don't guess."
  - "Keep strategy docs at class level (Tier 1–3, integration patterns), keep implementation plans at session level (specific tasks, owners, dates)."
  - "When user says 'map it out', they want both strategic positioning AND concrete next steps — not one or the other."
related:
  - skill: agent-coordination
    relationship: "Relies on agent-coordination for the routing/handoff mechanics (Green Room, Mess Hall, group vs DM rules). strategic-resource-integration decides WHAT to route; agent-coordination decides WHERE and HOW."
  - skill: writing-plans
    relationship: "Uses writing-plans principles (bite-sized tasks, clear paths) for the Implementation-Plan.md deliverable."
  - skill: vault-compliance-audit
    relationship: "New projects created by this skill should pass vault-compliance-audit checks (proper frontmatter, correct folder placement, linked relationships)."
---

# Strategic Resource Integration & Project Kickoff

## Purpose

This is Gentech's standard operating procedure for converting external discoveries (APIs, tools, datasets, hackathons, research) into structured, actionable projects with clear ownership and execution plans.

**When triggered:** User says "map it out", "save this", "make a project" in response to an external resource.

**End state:** Vault-stamped project with strategy, implementation plan, team assignments, and coordination artifacts — no ambiguity about who does what next.

---

## The 7-Step Playbook

### Step 1: Strategic Mapping

Before writing anything, clarify the strategic fit.

**Questions to answer:**
- Which GenTech strategic layer does this belong to? (AAE/DeFi/Creative/Hackathon)
- Is this a Tier 1 (build now), Tier 2 (strategic asset), or Tier 3 (monitor) opportunity?
- What's the Minimum Viable Product? What's the smallest thing that demonstrates value?
- Which existing projects does this complement or extend?
- Does this create a new revenue stream, reduce costs, or build IP?

**Output:** One-paragraph positioning statement. Example from Travel-Agent:
> "We're building a travel intelligence agent using free public APIs to avoid SaaS costs. The adapter pattern lets us swap providers, cache aggressively, and fail over seamlessly."

---

### Step 2: Vault Strategy Document

Location: `03-Strategies/<Topic>-Integration-Toolkit.md` (or strategic layer if more specific)

**Required sections:**
1. Executive Summary (what & why)
2. Priority Categories (Tier 1–3 table with impact/effort)
3. Integration Map (architecture diagram or stack list)
4. Implementation Roadmap (phases with timelines)
5. API Prioritization Matrix (free tier info, rate limits)
6. Pitfalls & Mitigations
7. Reference Links (upstream docs)
8. Pro Tips (institutional knowledge)

**Format:** Medium-length markdown with clear headers, tables, bullet lists. Not a wall of text — readable in Telegram previews.

---

### Step 3: Implementation Plan

Location: `03-Projects/<Project-Name>/Implementation-Plan.md`

**Required sections:**
- Project context (link to strategy doc)
- Sprint goal (what's delivered this sprint)
- Task breakdown table (Task | Owner | Status | Blocked By)
- Test vectors (concrete inputs + expected outputs)
- Definition of Done (checklist)
- Timeline (daily or per-phase)

**Subdirectory structure:**
```
<Project-Name>/
├── API-Adapters/     # Normalization layers for each provider
├── Demos/            # Interactive demo endpoints or scripts
├── Integration-Tests/ # API contract tests
├── Docs/             # Supplementary docs (API references, schemas)
└── Scripts/          # Utility scripts (fixture generators, probes)
```

---

### Step 4: Team Routing

Assign owners by department function:

| Function | Team/Person | Telegram Group |
|----------|-------------|----------------|
| Backend development | YoYo | GenTech Labs |
| DevOps / keys / infra | DMOB | GenTech Strategies |
| Creative / audio / video | Desmond | GenTech Entertainment |
| Cross-team coordination | Gentech (CEO) | Green Room |
| Stakeholder updates | All | Gentech HQ |

**Golden rule:** Never DMs. Always route to the group where that department lives.

---

### Step 5: Green Room Handoff

Location: `09-Green Room/Handoffs/YYYY-MM-DD-<Project-Short-Name>.md`

**Purpose:** Internal coordination record during execution.

**Must include:**
- What we decided (summary of strategic choices)
- Immediate next steps (per owner, blocking order)
- Metrics & monitoring plan
- Escalation path (who to ping for what)
- Daily cadence (standup time, demo cadence)
- Go/No-Go criteria (when to stop/continue)

This is the **single source of truth** for "what's the current plan" during execution.

---

### Step 6: Notification Broadcast

Two messages minimum:

**To Gentech HQ** (all stakeholders):
- High-level summary (2–3 sentences)
- Strategic importance
- Links to vault docs
- Timeline
- Owners

**To responsible group(s)** (Labs/Strategies/Entertainment):
- Detailed task list
- Prerequisites
- Blocking relationships
- Test vectors
- Reference links to strategy doc
- Daily cadence

---

### Step 7: Vault Sync

Run `ob sync` if configured. Verify files appear in Obsidian at expected paths.

---

## Integration Architecture Patterns (Reference)

### 6-Layer Stack (Travel Example)

```
Layer 1: SEARCH      (Skyscanner, Amadeus) — find options
Layer 2: LOCATION    (Google Maps, OSM)     — geocoding, coords
Layer 3: STREET VIEW (Street View API)      — immersive imagery
Layer 4: CONTEXT     (Weather, Currency)    — environment data
Layer 5: TRANSPORT   (Uber, TransitLand)    — mobility
Layer 6: SUPPORT     (Email, PDF, Payments) — fulfillment
```

### Adapter Pattern

Normalize multiple providers behind single interface:
```python
class APIAdapter:
    def __init__(self, provider): ...
    async def call(self, method, params): ...  # normalize in/out
    def _cache_key(self): ...
    def _with_fallback(self, primary, secondary): ...
```

Benefits: swap providers without touching agent logic, A/B test, centralized logging.

---

## Common Pitfalls

- **Missing prerequisites:** Dev starts before keys provisioned → always have DMOB create vault files FIRST, then assign dev tasks.
- **Duplicate messaging:** Sending both HQ and Labs almost same info → tailor each (strategic vs tactical).
- **Skipping handoff:** Team doesn't know current decisions → Green Room is the coordination layer.
- **Class-level vs session-level confusion:** Strategy docs are timeless (Tier 1–3 patterns); implementation plans are time-boxed (May 4–10 tasks). Keep separate.
- **DM assignments:** Violates routing rules → always use groups.

---

## Related Skills

- **agent-coordination** — provides the routing/handoff mechanics this skill relies on
- **writing-plans** — informs the implementation plan structure (bite-sized tasks, clear paths)
- **vault-compliance-audit** — audits should pass for artifacts created by this skill
