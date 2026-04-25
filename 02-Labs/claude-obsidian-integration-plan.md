# Claude-Obsidian Integration Plan

**Repo:** https://github.com/AgriciDaniel/claude-obsidian
**Status:** Research complete, ready to implement
**Goal:** Add claude-obsidian features on top of our existing vault without breaking anything

## What claude-obsidian Provides

| Feature | Description |
|---------|-------------|
| `/wiki` | Scaffold and query a knowledge base |
| `/wiki-ingest` | Drop sources → auto-extract entities, concepts, cross-references |
| `/wiki-query` | Ask questions, answers cite your wiki not training data |
| `/wiki-lint` | Health check: orphans, dead links, stale claims, frontmatter gaps |
| `/save` | File current conversation context |
| `/autoresearch` | Autonomous research loop (3 rounds) |
| Hot cache | `wiki/hot.md` — persists recent context between sessions |
| Canvas maps | Visual knowledge graphs |

## Current Vault Structure

```
/root/Documents/Obsidian Vault/
├── 01-GenTech HQ/
├── 02-Labs/
├── 03-Strategies/
├── 04-Entertainment/
├── 11-Mess Hall/
├── 12-Skills/
```

## Integration Approach: Layer, Don't Replace

**Add a `wiki/` folder alongside our existing structure.** Don't touch existing folders.

### Proposed Vault Structure

```
/root/Documents/Obsidian Vault/
├── 01-GenTech HQ/          ← existing (unchanged)
├── 02-Labs/                ← existing (unchanged)
├── 03-Strategies/          ← existing (unchanged)
├── 04-Entertainment/       ← existing (unchanged)
├── 11-Mess Hall/           ← existing (unchanged)
├── 12-Skills/              ← existing (unchanged)
├── wiki/                   ← NEW: claude-obsidian knowledge base
│   ├── concepts/           ← extracted ideas and patterns
│   ├── entities/           ← people, projects, tools, protocols
│   ├── sources/            ← ingested URLs, papers, docs
│   ├── meta/               ← lint reports, dashboards, hot cache
│   └── hot.md              ← session continuity cache
├── .raw/                   ← NEW: immutable source documents
├── _templates/             ← NEW: note templates
└── .obsidian/              ← existing (merge configs carefully)
```

### What Changes

| Component | Action |
|-----------|--------|
| `wiki/` folder | Create new — no conflicts |
| `.raw/` folder | Create new — no conflicts |
| `_templates/` folder | Create new — no conflicts |
| `.obsidian/graph.json` | Merge — add wiki color groups to existing config |
| `.obsidian/app.json` | Merge — add claude-obsidian ignore filters |
| `.obsidian/appearance.json` | Merge — enable CSS snippets |
| `.obsidian/plugins/` | Add Calendar, Thino, Excalidraw, Banners if desired |
| Skills | Symlink `skills/` into our agent skill system |

### What Does NOT Change

- `01-GenTech HQ/` — untouched
- `02-Labs/` — untouched
- `03-Strategies/` — untouched
- `04-Entertainment/` — untouched
- `11-Mess Hall/` — untouched
- `12-Skills/` — untouched
- Existing cron job — keep running, add wiki lint to it

## Implementation Steps

### Step 1: Copy wiki structure (safe, no conflicts)
```bash
mkdir -p "/root/Documents/Obsidian Vault/wiki/concepts"
mkdir -p "/root/Documents/Obsidian Vault/wiki/entities"
mkdir -p "/root/Documents/Obsidian Vault/wiki/sources"
mkdir -p "/root/Documents/Obsidian Vault/wiki/meta"
mkdir -p "/root/Documents/Obsidian Vault/.raw"
mkdir -p "/root/Documents/Obsidian Vault/_templates"
```

### Step 2: Copy hot.md template
Copy the hot.md from `/tmp/claude-obsidian/wiki/hot.md` and customize for our use case.

### Step 3: Merge .obsidian configs (backup first!)
- Backup existing `.obsidian/` folder
- Merge `graph.json` — add wiki color groups
- Merge `app.json` — add ignore filters
- Skip plugins for now (can add later)

### Step 4: Add skills to agent system
Symlink or copy relevant skills:
- `wiki-lint` → add to our cron job rotation
- `save` → useful for filing conversation context

### Step 5: Update cron job
Add wiki lint to the daily 4 AM vault manager cron:
- Existing: archive old Mess Hall chats
- Add: run wiki-lint for orphan/dead link detection

## Risks

| Risk | Mitigation |
|------|------------|
| `.obsidian` config conflict | Backup before merge, test in dry-run |
| Cron job conflict | Add wiki lint as separate step, not replacing existing |
| Skill overlap with existing skills | Only add skills we'll actually use (wiki-lint, save) |

## Optional Plugins (Add Later)

| Plugin | Status | Notes |
|---|---|---|
| **Calendar** | ⏳ Add later | Daily note integration |
| **Thino** | ⏳ Add later | Quick capture / memos |
| **Banners** | ⏳ Add later | Header images for notes |

## What We Skip (for now)

- Excalidraw plugin (8MB, not essential)
- Visual workspace layout (keep our current setup)
- Multi-agent bootstrap files (we already have agent coordination)
- Canvas maps (can add later if useful)

## Files to Reference
- setup-vault.sh: `/tmp/claude-obsidian/bin/setup-vault.sh`
- wiki-lint skill: `/tmp/claude-obsidian/skills/wiki-lint/SKILL.md`
- save skill: `/tmp/claude-obsidian/skills/save/SKILL.md`
- AGENTS.md: `/tmp/claude-obsidian/AGENTS.md`
