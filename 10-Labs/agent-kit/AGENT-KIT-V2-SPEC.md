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
│   ├── wake-up/             # Session start protocol
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

### 9. Templates for Common Use Cases

**Pre-Built Profiles:**
```bash
# DeFi Farmer
agent-kit profile create defi-farmer --template defi

# Content Creator
agent-kit profile create content-creator --template content

# Research Agent
agent-kit profile create research-agent --template research

# Full Stack (everything)
agent-kit profile create full-stack --template full
```

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
