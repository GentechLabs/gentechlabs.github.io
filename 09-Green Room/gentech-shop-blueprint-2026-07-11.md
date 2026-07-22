# GenTech Shop — Blueprint

**Date:** 2026-07-11
**Status:** Scoped, ready to build
**Effort:** 2-3 hours total

---

## What We're Building

Two things that work together:
1. **`genTech-shop` repo** — the GitHub front door for GenTech's gaming services
2. **`genTech-shop` plugin** — MCP tools inside the Agent Kit that expose the services

---

## Repo: ProtoJay4789/genTech-shop

A README-driven repo. No code — just documentation + a pinned profile link.

```
genTech-shop/
├── README.md            ← Service listing + badges
├── SKILL.md             ← npx skills ecosystem format
└── .github/
    └── FUNDING.yml      ← Accept tips via GitHub Sponsors
```

**README layout:**
- **Header:** "GenTech Shop — Gaming intelligence for AI agents and humans"
- **Services table** (see below)
- **How to access** — "Install the Agent Kit to use these via MCP"
- **Status dashboard** — links to `ProtoJay4789.github.io/gaming/`
- **Roadmap** — upcoming tools

---

## Plugin: 4 MCP Tools

Each tool wraps existing cron data and exposes it through the Agent Kit.

### Tool 1: `gaming_deals`

```
gaming_deals(username: string, platform?: "steam" | "all")
```

Returns current wishlist deals from the vault's wishlist data.

**Data source:** The existing Steam wishlist HTML/JSON files in the vault. The MCP tool reads and parses them instead of the cron job.

**Output:**
```json
[
  {
    "game": "Path of Exile 2",
    "platform": "steam",
    "normal_price": 29.99,
    "sale_price": 23.99,
    "discount": "20%",
    "url": "https://store.steampowered.com/app/..."
  }
]
```

### Tool 2: `release_calendar`

```
release_calendar(from_date?: string, to_date?: string, genres?: string[])
```

Returns upcoming game releases. Uses web search (existing cron pattern) + cached vault data.

**Data source:** Web search for upcoming games, filtered by tracked titles from the vault's installed-games.json and wishlists.

**Output:**
```json
[
  {
    "game": "Hades II",
    "release_date": "2026-Q3",
    "platforms": ["PC", "Xbox"],
    "genre": "Roguelike",
    "tracked": true
  }
]
```

### Tool 3: `poe2_build_health`

```
poe2_build_health(class_name?: string)
```

Returns current POE2 patch health data for tracked builds.

**Data source:** The vault's `build-health.json`, `patch-data.json`, `patch-notes-log.json`, and character JSONs.

**Output:**
```json
{
  "current_patch": "0.2.1",
  "patch_notes_url": "...",
  "builds": [
    {"name": "Monk", "health": "stable", "last_updated": "2026-07-10"},
    {"name": "Warrior", "health": "nerfed", "notes": "Sunder damage reduced 15%"}
  ]
}
```

### Tool 4: `gaming_hub_status`

```
gaming_hub_status()
```

Returns the sync status and available data on the gaming hub.

**Data source:** Checks the vault Gaming/ directory and the GitHub Pages hub.

**Output:**
```json
{
  "data_sources": 18,
  "last_sync": "2026-07-11T22:00:00Z",
  "hub_url": "https://ProtoJay4789.github.io/gaming/",
  "builds_tracked": ["monk", "warrior", "vanito"],
  "wishlists_tracked": ["jordan", "vanito"]
}
```

---

## Plugin Structure

```
genTech-agent-kit/plugins/genTech-shop/
├── plugin.json
├── __init__.py        ← 4 MCP tool decorators
├── data/
│   └── vault_paths.py ← reads from /root/vaults/gentech/Gaming/
└── tests/
    └── test_shop.py
```

**plugin.json:**
```json
{
  "name": "genTech-shop",
  "version": "0.1.0",
  "description": "Gaming intelligence tools: deals, releases, POE2 builds, hub status",
  "tools": ["gaming_deals", "release_calendar", "poe2_build_health", "gaming_hub_status"],
  "dependencies": []
}
```

---

## The Profile Effect (Before vs After)

**Today:**
```
ProtoJay4789/
├── genTech-agent-kit    ← MCP server
├── gentech-vault        ← old
└── ProtoJay4789.github.io  ← portfolio
```

**After:**
```
ProtoJay4789/
├── genTech-agent-kit    ← MCP server (20+ tools)
├── genTech-shop         ← NEW: gaming services listing ★
├── ProtoJay4789.github.io  ← portfolio
└── (gentech-vault — deprecated/archived)
```

---

## Distribution

The MCP tools ride the **3 existing PRs** automatically:

| PR | What It Lists | Now Includes |
|----|--------------|-------------|
| public-apis #6539 | GenTech Agent Kit | "+ gaming intelligence tools" |
| awesome-x402 #810 | GenTech Agent Kit (MCP) | 4 new tools in description |
| awesome-agentic-commerce #440 | GenTech Labs listing | Gaming services mentioned |

---

## Build Order

1. Create `genTech-shop` repo — README + SKILL.md (15 min)
2. Add `genTech-shop` plugin to Agent Kit (1-2 hours)
3. Test each tool against vault data (30 min)
4. Commit + push — distribution updates automatically

---

## Future (Post-v0.1)

- **FiatDock listing** — list gaming tools as paid MCP services ($0.01/call)
- **Loadbay listing** — list as agent-accessible data harness
- **HOL registry** — register per-endpoint for x402 payments
- **Human-facing UI** — the ProtoJay4789.github.io/gaming/ dashboard
