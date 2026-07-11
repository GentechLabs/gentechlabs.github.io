# Agent Kit v2 — Specification

**Status:** Draft
**Created:** 2026-06-18
**Priority:** High — Core product for GenTech ecosystem

---

## Vision

Agent Kit v2 is a **modular, composable, self-healing agent framework** that anyone can install, configure, and extend. It's not just a bundle of skills — it's an **operating system for AI agents**.

---

## Architecture

### 1. Modular Skill System

**Structure:**
```
agent-kit/
├── core/                    # Essential (always installed)
│   ├── identity/            # Agent identity, personality, rules
│   ├── wake-up/             # Session start protocol + auto-recovery
│   ├── memory/              # Persistent memory management
│   ├── context/             # Context loading, vault integration
│   └── routing/             # Topic routing, group management
│
├── modules/                 # Optional (user selects)
│   ├── defi/                # DeFi operations
│   │   ├── lp-monitoring/   # LP position tracking
│   │   ├── portfolio-sync/  # Portfolio health checks
│   │   ├── yield-farming/   # Yield optimization
│   │   └── compound-extract/ # Fee extraction protocol
│   │
│   ├── content/             # Content creation
│   │   ├── social-drafts/   # Twitter/X, LinkedIn
│   │   ├── media-gen/       # Images, videos, audio
│   │   └── scheduling/      # Post scheduling
│   │
│   ├── research/            # Web research
│   │   ├── web-search/      # General search
│   │   ├── opportunity/     # Hackathons, grants, bounties
│   │   └── analysis/        # Market analysis, trends
│   │
│   └── marketplace/         # Platform integration
│       ├── evomap/          # EvoMap capsules, credits
│       ├── hive/            # Hive task claiming
│       └── wurk/            # WURK.fun microtasks
│
└── shared/                  # Common utilities
    ├── templates/           # Reusable patterns
    ├── scripts/             # Automation scripts
    └── docs/                # Documentation
```

**Installation:**
```bash
# Full install (all modules)
agent-kit install

# Minimal install (core only)
agent-kit install --core-only

# Custom install (pick modules)
agent-kit install --modules defi,content

# Add modules later
agent-kit add defi
agent-kit add content
```

**Benefits:**
- Lighter installs (10MB core vs 50MB full)
- Faster startup (fewer skills to load)
- Users only pay for what they use
- Easier maintenance (update modules independently)

---

### 2. Auto-Discovery

**Detection Logic:**
```yaml
discover:
  hermes:
    check: command -v hermes
    action: use_native_tools
    
  blockrun:
    check: test -f ~/.hermes/blockrun.json
    action: enable_paid_tools
    
  obsidian:
    check: test -d ~/vaults
    action: enable_vault_integration
    
  github:
    check: gh auth status
    action: enable_repo_management
    
  telegram:
    check: test -f ~/.hermes/telegram.json
    action: enable_messaging
```

**Adaptation:**
- Hermes detected → native tools
- No Hermes → CLI fallback
- BlockRun configured → paid models
- No BlockRun → free models only
- Obsidian detected → vault integration
- No Obsidian → local files only

**Config:**
```yaml
# ~/.agent-kit/config.yaml
auto_discover: true
fallback_mode: cli
modules:
  - core
  - defi
  - content
```

---

### 3. Identity Persistence

**Structure:**
```json
{
  "id": "agent-abc123",
  "name": "GenTech",
  "personality": {
    "tone": "warm, direct, technical",
    "style": "concise, actionable, no fluff",
    "values": ["build first", "ship products", "help users"]
  },
  "owner": {
    "name": "Jordan",
    "telegram": "@ProtoJay4789",
    "timezone": "America/New_York"
  },
  "created": "2026-06-18T00:00:00Z",
  "version": "2.0.0",
  "modules": ["core", "defi", "content"]
}
```

**Storage:**
- `~/.agent-kit/identity.json` — persistent identity
- `~/.agent-kit/profiles/` — multiple agent profiles
- `~/.agent-kit/sessions/` — session history

**Benefits:**
- Survives session restarts
- No re-reading skills for identity
- Multiple agents on same machine
- Version tracking for updates

---

### 4. Skill Marketplace

**Package Format:**
```yaml
# skill.yaml
name: defi-monitoring
version: 1.0.0
author: gentech
description: Track DeFi LP positions and alert on changes
category: defi
tags: [defi, lp, monitoring, alerts]
dependencies:
  - core
  - blockrun (optional)
price: 0  # Free
license: MIT
```

**Distribution:**
```bash
# Publish skill
agent-kit publish defi-monitoring

# Install from marketplace
agent-kit install defi-monitoring

# Search marketplace
agent-kit search defi
```

**Revenue Model:**
- Free skills: 0 credits
- Paid skills: 1-100 credits
- Premium skills: 100+ credits
- Kit gets 10% platform fee

---

### 5. Revenue Sharing

**Flow:**
1. User creates skill
2. Publishes to marketplace
3. Other users install/use
4. Creator earns credits
5. Kit gets 10% fee

**Tracking:**
```json
{
  "skill": "defi-monitoring",
  "author": "gentech",
  "installs": 150,
  "revenue": 1500,
  "fee": 150,
  "net": 1350
}
```

**Payout:**
- Credits → USDC on Base
- Minimum payout: 100 credits
- Auto-payout weekly

---

### 6. Health Dashboard

**Metrics:**
```yaml
health:
  cron_jobs:
    total: 23
    healthy: 21
    failed: 2
    
  skills:
    total: 45
    active: 42
    outdated: 3
    
  memory:
    used: 2067
    limit: 2200
    percentage: 94
    
  performance:
    avg_response_time: 2.3s
    tokens_per_session: 15000
    cost_per_day: 0.50
    
  platform:
    evomap:
      credits: 100
      capsules: 1
      status: active
    blockrun:
      balance: 5.00
      spend_today: 0.25
```

**Alerts:**
- Cron job failures
- Memory > 80%
- Platform balance low
- Skills outdated

---

### 7. Multi-Profile Support

**Structure:**
```
~/.agent-kit/
├── profiles/
│   ├── gentech/           # Full DeFi stack
│   │   ├── identity.json
│   │   ├── config.yaml
│   │   ├── modules/
│   │   └── skills/
│   │
│   ├── content/           # Social media focus
│   │   ├── identity.json
│   │   ├── config.yaml
│   │   ├── modules/
│   │   └── skills/
│   │
│   └── research/          # Web research only
│       ├── identity.json
│       ├── config.yaml
│       ├── modules/
│       └── skills/
│
└── shared/                # Common skills
    ├── core/
    └── templates/
```

**Switching:**
```bash
# List profiles
agent-kit profiles

# Switch profile
agent-kit profile use gentech

# Create new profile
agent-kit profile create content --modules content,marketplace
```

---

### 8. Update Mechanism

**Auto-Update:**
```yaml
# ~/.agent-kit/config.yaml
updates:
  auto: true
  check_interval: 24h
  channels:
    - stable
    - beta (optional)
```

**Manual Update:**
```bash
# Check for updates
agent-kit update --check

# Update all
agent-kit update

# Update specific module
agent-kit update defi

# Rollback
agent-kit rollback defi --version 1.0.0
```

**Versioning:**
- Semantic versioning (MAJOR.MINOR.PATCH)
- Changelog for each version
- Rollback support

---

### 9. Auto-Recovery System (NEW — JUL 2026)

**Purpose:** Never lose context after gateway restarts, session resets, or context compaction. Automatically detect, recover, and present active work to the user without manual intervention.

**Problem This Solves:**
- Gateway restarts kill in-progress work
- Session resets require manual "what were we doing?" conversations
- Context compaction loses task state
- Duplicate work when context is lost
- Users have to remember what was active

**How It Works:**

**A. Automatic Detection**
```yaml
auto_recovery:
  enabled: true
  triggers:
    - gateway_restart
    - session_reset
    - context_compaction
    - memory_limit_warning
  
  detection:
    # Check if session is fresh
    message_count: 1
    
    # Check if restart marker exists
    marker_file: ~/.agent-kit/state/restart_marker
    
    # Check if context was compacted
    check_compaction: true
```

**B. Context Recovery Sequence**
```bash
# 1. Run wake-up protocol first (identity + behavior)
wake-up-protocol

# 2. Search recent sessions for active work
session_search(limit=3, days=7)

# 3. Check handoffs folder for pending work
search_files("*.md", path="~/vaults/handoffs/", limit=5)

# 4. Check in-memory build queue if exists
read_file("~/vaults/HQ/jordan-queue.md")
read_file("~/vaults/10-Labs/build-queue.md")

# 5. Cross-reference and consolidate
# Session work + handoffs + queue = "What was in progress"
```

**C. Presentation to User**
```bash
# Don't auto-resume — always ask user
present_recovery_summary:
  format: |
    "Before the restart, I was working on:"
    "• [Task from session history] — [status]"
    "• [Handoff from handoffs/] — [status]"
    "Continue these or start fresh?"
  
  options:
    - continue    # Resume all tasks
    - select      # User picks which to resume
    - fresh       # Start new work, save old for later
```

**Why Not Auto-Resume?**
- User might want to pivot to something else
- Some work might be stale after long interruption
- User should always be in control
- Prevents "agent working on wrong thing" scenarios

**D. Shared Vault Support (Dual-Agent)**
```yaml
vault_recovery:
  path: ~/vaults/  # Shared between Gentech (VPS) and Forge (desktop)
  
  # Works for both agents
  gentech:
    detect: session_search(profile="gentech")
    
  forge:
    detect: session_search(profile="forge")
  
  # Cross-reference to avoid duplicate work
  dedup:
    enabled: true
    window: 30m  # If both worked on same thing in 30m, flag it
```

**E. Benefits for Agent Kit Users**
- Zero configuration: works out of the box
- Never lose task state again
- Eliminates "what were we doing?" conversations
- Prevents duplicate work across sessions
- Works for multi-agent setups (shared vault)
- Reduces cognitive load for users

**F. Implementation in Agent Kit v2**
```bash
# Core module includes auto-recovery
agent-kit install --core

# Auto-recovery is always on (can be disabled)
agent-kit config set auto_recovery.enabled false

# Check recovery status
agent-kit recovery status

# View last recovery summary
agent-kit recovery last

# Manually trigger recovery (if needed)
agent-kit recovery run
```

**G. Recovery State Storage**
```yaml
# ~/.agent-kit/state/recovery_state.json
{
  "last_recovery": "2026-07-04T17:30:00Z",
  "detected_tasks": [
    {
      "id": "task-001",
      "description": "Fix BUG-001 in Agent Search API",
      "status": "in_progress",
      "source": "session",
      "priority": "high"
    },
    {
      "id": "task-002",
      "description": "Deploy Cloudflare x402 Gateway",
      "status": "blocked",
      "source": "handoff",
      "priority": "urgent"
    }
  ],
  "user_choice": "continue"
}
```

**H. Edge Cases Handled**
| Case | Detection | Action |
|------|-----------|--------|
| Session hit memory limit | Memory warning marker | Run wake-up + recovery |
| Gateway restarted | Marker missing on startup | Run wake-up + recovery |
| User sent `/new` | Message count = 1 | Run wake-up + recovery |
| Context compaction | Compaction marker present | Run wake-up + recovery |
| Dual-agent collision | Same task in both sessions | Flag to user, dedup |

**I. Testing Checklist**
- [ ] Gateway restart → recovery triggers
- [ ] Session reset → recovery triggers
- [ ] Memory limit → recovery triggers
- [ ] Context compaction → recovery triggers
- [ ] User sees "Continue or fresh?" prompt
- [ ] User can select individual tasks
- [ ] Shared vault works for both agents
- [ ] Duplicate work prevention works
- [ ] Recovery can be disabled if needed

---

### 10. Templates for Common Use Cases

**Pre-Built Profiles:**
```bash
# DeFi Farmer
agent-kit profile create defi-farmer --template defi

# Content Creator
agent-kit profile create content-creator --template content

# Research Agent
agent-kit profile create research-agent --template research

# Agent Swarm (new!)
agent-kit profile create my-swarm --template swarm

# Full Stack (everything)
agent-kit profile create full-stack --template full
```

**Swarm Template** (`templates/swarm.yaml`):
```yaml
name: Agent Swarm
description: Two+ agents working as a coordinated team (24/7 coverage)
type: multi-agent
agents:
  - id: lead
    role: Team Lead — coordination, planning, heavy work
    platform: telegram
    model: high-tier
    location: vps
    always_on: true
  - id: builder
    role: Builder — daily coding, quick responses
    platform: telegram
    model: mid-tier
    location: laptop
    always_on: false
config:
  vault:
    type: github
    sync_interval: 5m
  coordination:
    method: vault
    dedup_window: 30s
```

Full documentation: `02-Labs/agent-kit/agent-swarm-template.md`
Config file format: `02-Labs/agent-kit/swarm-config.yaml`

**Template Contents:**
```yaml
# templates/defi.yaml
name: DeFi Farmer
description: LP monitoring, yield optimization, portfolio sync
modules:
  - core
  - defi
skills:
  - lp-monitoring
  - portfolio-sync
  - yield-farming
  - compound-extract
cron_jobs:
  - portfolio-health-check
  - lp-monitor-10min
  - yield-optimizer
```

---

### 10. Documentation Site

**Structure:**
```
docs.gentech.dev/
├── getting-started/
│   ├── installation.md
│   ├── configuration.md
│   └── first-agent.md
│
├── modules/
│   ├── core/
│   ├── defi/
│   ├── content/
│   ├── research/
│   └── marketplace/
│
├── api/
│   ├── cli-reference.md
│   ├── skill-format.md
│   └── marketplace-api.md
│
├── examples/
│   ├── defi-farmer.md
│   ├── content-creator.md
│   └── research-agent.md
│
└── community/
    ├── contributing.md
    ├── skills.md
    └── support.md
```

**Tech Stack:**
- Static site (Hugo/Astro)
- Auto-generated from YAML/MD
- Searchable API reference
- Interactive examples

---

## Implementation Roadmap

### Phase 1: Core (Week 1-2)
- [ ] Restructure kit into modular layout
- [ ] Implement auto-discovery
- [ ] Add identity persistence
- [ ] Basic CLI for install/modules

### Phase 2: Marketplace (Week 3-4)
- [ ] Skill package format (skill.yaml)
- [ ] Publish/install commands
- [ ] Credit system integration
- [ ] Revenue sharing

### Phase 3: Operations (Week 5-6)
- [ ] Health dashboard
- [ ] Multi-profile support
- [ ] Update mechanism
- [ ] Rollback support

### Phase 4: Distribution (Week 7-8)
- [ ] Pre-built templates
- [ ] Documentation site
- [ ] Community contributions
- [ ] Marketing/launch

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Install size (core) | < 10MB |
| Startup time | < 5s |
| Module load time | < 1s each |
| Marketplace skills | 50+ in 3 months |
| Active installations | 100+ in 6 months |
| Revenue | $500/mo in 6 months |

---

## Next Steps

1. **Spec out modular layout** — Define exact file structure
2. **Build auto-discovery** — Detection logic for tools/platforms
3. **Implement identity persistence** — JSON-based identity
4. **Create skill package format** — YAML metadata + MD content
5. **Build marketplace MVP** — Publish/install/credits

Want me to start building any of these?
