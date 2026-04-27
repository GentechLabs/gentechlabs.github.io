# 🧠 Gentech — Second Brain

Welcome to the Gentech knowledge base. This vault is the shared memory for the multi-agent team.

> **Last cleaned:** Apr 27 2026  
> **Process:** Merge artifacts archived, single-file folders consolidated, canonical homes assigned.

---

## 📂 Active Top-Level

| Zone | Agent | What lives here | Notes |
|------|-------|-----------------|-------|
| **00-Inbox** | Jordan | Approval queue — checkboxes, pending decisions | Jordan writes here; agents **read-only** |
| **00-System** | Gentech | Agent configs, channel maps, cron jobs, secrets | Source of truth for routing |
| **00-Sessions** | Gentech | Session transcripts, one-off context | Ephemeral — sweep monthly |
| **00-HQ** | Gentech | Summaries, Ops, Approvals | Consolidated output goes here |
| **01-Agency** | Gentech | Org docs, working files, team roster | Not config — narrative docs |
| **01-Agents** | Gentech | Bot configs, voice profiles | Runtime settings |
| **02-Labs** | DMOB | Contracts, hackathons, security, audits, research | **Master domain** |
| **03-Projects** | DMOB/YoYo | Active builds with repos (Foundry, Anchor) | Contains real `.git` repos |
| **03-Strategies** | YoYo | DeFi research, market analysis, LP tracking | |
| **04-Entertainment** | Desmond | Content strategy, branding, episode drafts | |
| **05-Learning** | Jordan | Course notes, academy material | Cyfrin/Chainlink etc |
| **06-Content** | Desmond | X drafts, blog posts, podcast concepts, social | |
| **07-Ideas** | All | Off-domain brainstorming | |
| **08-Logs** | Auto | Monthly summaries, operational logs | |
| **09-Green Room** | All | Task collaboration, active handoffs | Coordinates before HQ output |
| **09-Templates** | All | Reusable note templates | |
| **10-Archive** | Auto | Stale folders, swept history, merge artifacts | Do not code against this |
| **11-Mess Hall** | All | Banter, non-work, debates | |
| **12-Skills** | Auto | Agent skill exports, skill wikis | Synced from `~/.hermes/profiles/*/skills/` |
| **memories/** | Auto | Legacy JSON memory backups | Migrate to 12-Skills |

---

## 🏷️ Tags

- `#agent:yoyo` `#agent:dmob` `#agent:desmond` `#agent:gentech`
- `#status:active` `#status:todo` `#status:done`
- `#type:research` `#type:code` `#type:content`

---

## 🤖 Agents — Smart Routing v2

[Full Protocol →](00-System/agents-protocol.md)

| Agent | Group | Domain | Writes To |
|-------|-------|--------|-----------|
| **Gentech** | HQ (`-1003863540828`) | Coordinator — receives all, routes | `00-Sessions` |
| **YoYo** | Strategies (`-1002916759037`) | DeFi, market research, LP tracking | `03-Strategies` |
| **DMOB** | Labs (`-1003872552815`) | Smart contracts, security, code, hackathons | `02-Labs` |
| **Desmond** | Creative (`-1003893562036`) | Content, branding, social media | `04-Entertainment`, `06-Content` |

### How We Work
- **Gentech receives → routes to specialist group → agent works → summary to HQ**
- **Green Room** → Active task collaboration (`09-Green Room/`)
- **Mess Hall** → Off-topic, banter (`11-Mess Hall/`)
- **Before replying** → Check Green Room + Mess Hall for context
- **Vault sync** → Git-based; Obsidian sync disabled to prevent conflicts

---

## 🔒 Consolidation Rules

1. **Single-file folders** → Move file to parent MOC; delete empty shell
2. **Merge artifacts** (`_*`) → Archive to `10-Archive/` with provenance
3. **Cross-domain duplicates** → Route to canonical agent owner:
   - Code/UI → `02-Labs/`
   - Content scripts → `04-Entertainment/`
   - Analytics → `03-Strategies/`
4. **Real repos** (Foundry, Anchor) → Stay in `03-Projects/` or code root
5. **Index** → This file updated on every consolidation pass
