# 🧭 ROUTING.md — Vault Index for Agents

> **Purpose:** One-line description per folder so any agent (Gentech, Forge, cron) knows
> *which folder to open* before scanning. Load this FIRST on any retrieval. If a folder
> isn't listed here, it's either legacy, generated output, or not worth routing to.
>
> **Rule:** write → index → route → open two files. Never scan the whole vault.
> **Maintain:** update this file whenever a new top-level folder is created or repurposed.
> **Canonical queue:** `scripts/build_queue.json` (single source of truth for builds).

---

## 🏠 Core Ops

| Folder | What lives here | Open when |
|---|---|---|
| `00-HQ/` | Coordination, decisions, status, context-weight, brain snapshots, go/no-go, monetization thesis | Session start, any coordination/decision |
| `01-HANDOFFS/` | Cross-agent + Jordan action items, group inboxes, completions | Morning digest, delegation, human-gated tasks |
| `11-Mess Hall/` | Open decisions (`considerations.md`), ideas, marketplace registry, archives | Any decision point, idea capture |
| `09-Green Room/` | Ideas, specs, character sheets, film bibles, context-bridge | New ideas, deep-dive specs, creative/film work |
| `10-Labs/` | Build projects, hackathons, x402 gateway, agent kits, research | Any build, hackathon, or technical project |
| `03-Projects/` | Named projects (AgentEscrow, Agora, genlayer, portfolio) | Named-project work |
| `06-Content/` | Portfolio, frontend design, social layer, content projects | Content/portfolio/frontend work |

## 💰 Finance & Treasury

| Folder | What lives here | Open when |
|---|---|---|
| `Treasury/` | Wallet funding, grants, GTA rails, DeFi monitor, LP positions | Any treasury/finance/DeFi decision |
| `DeFi/` | DeFi research, LP analytics | DeFi/LP work |
| `Strategies/` | Trading/market strategies | Strategy work |

## 🎮 Gaming & Entertainment

| Folder | What lives here | Open when |
|---|---|---|
| `Gaming/` | Game projects, loadouts, release intel | Gaming work |
| `Games/` | Game files (redirect) | Game work |
| `Entertainment/` | Entertainment content | Entertainment group work |
| `POE-2/` | POE2 loadout tracker | POE2 questions |
| `Meta-Rayban-Fighter/` | AR wearable game | AR game work |
| `Agent-Arena/` | Agent arena / trading arena | Arena work |

## 👤 People & Personal

| Folder | What lives here | Open when |
|---|---|---|
| `Jordan/` | Jordan's personal items | Jordan-specific |
| `Vanito/` | Vanito profile, projects | Vanito work |
| `Vanito-Travel/` | Vanito travel | Vanito travel |
| `Travel/` | Travel research | Travel |
| `Cookbook/` | Filipino recipes, substitution engine | Cooking/substitutions |
| `Journal/` | Journal entries | Journaling |
| `Profiles/` | Agent/person profiles | Profile lookups |

## 🛠️ Technical / Generated

| Folder | What lives here | Open when |
|---|---|---|
| `scripts/` | Build queue JSON, automation scripts | Scripts, canonical queue |
| `config/` | Config files | Config |
| `data/` | Data files | Data |
| `models/` | Model notes (e.g. qwen3-vl) | Model work |
| `analytics/` | Analytics | Analytics |
| `reports/` | Reports | Reports |
| `assets/` `audio/` `music/` `my-music/` `public/` `src/` `templates/` `tmp/` `_legacy/` `graphify-out/` `contrib/` `deals/` `games/` `Dashboards/` `Hub/` `GenTech-Atlas/` `Daily-Digest/` `Audits/` `agent-credit-score/` `ProtoBots/` `HQ/` | Legacy, generated output, or media assets — **do not route here by default** | Only when explicitly referenced |

---

## ⚡ Quick routing decisions

- **"What's active / status?"** → `00-HQ/context-weight.md` + `scripts/build_queue.json`
- **"What's Jordan waiting on?"** → `01-HANDOFFS/<date>-jordan-items.md` + `HQ/jordan-queue.md`
- **"Open decision?"** → `11-Mess Hall/considerations.md`
- **"New idea / spec?"** → `09-Green Room/`
- **"Build / hackathon?"** → `10-Labs/`
- **"Treasury / DeFi / money?"** → `Treasury/`
- **"Gaming?"** → `Gaming/`
