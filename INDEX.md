|# 🧠 Gentech — Second Brain

Welcome to the Gentech knowledge base. This vault is the shared memory for the multi-agent team.

## 📂 Structure (Cleaned — Apr 24 2026)

- **00-Inbox** — Jordan's approval queue
- **00-System** — Agent configs, templates, channel maps, cron jobs
- **00-Working-Memory.md** — Personal notes (durable memory)
- **01-HQ** — Team lead, operations (empty — pending Jordan's content)
- **01-News** — External news/updates (placeholder — no content yet)
- **02-Labs** — DMOB: contracts, hackathons, security, audits
  - `06-Security/` — Audit findings, vuln patterns
  - `Audits/` — Completed audit reports
- **03-Projects** — Active development projects
- **03-Strategies** — YoYo: DeFi research, market analysis, LP tracking

## 📂 Archived / Redundant (Do Not Use)

- `01-Agency` — Agent configs moved to `00-System`
- `04-Entertainment` — Content ideas moved to `11-Mess Hall`
- `05-Learning` — Course notes archived
- `06-Content`, `07-Ideas`, `08-Logs`, `11-Mess`, `00-Sessions` — All migrated or obsolete

## 🏷️ Tags
- `#agent:yoyo` `#agent:dmob` `#agent:desmond` `#agent:gentech`
- `#status:active` `#status:todo` `#status:done`
- `#type:research` `#type:code` `#type:content`

## 🔗 Key Pages
- [[00-System/README|System Config]]
- [[02-Labs/README|Labs]]
- [[03-Strategies/README|Strategies]]

## 🤖 Agents — Smart Routing v2
**[Full Protocol →](00-System/agents-protocol.md)**

| Agent | Group | Domain | Writes To |
|-------|-------|--------|-----------|
| Gentech | GenTech HQ (-1003863540828) | Coordinator — receives all, routes to specialists | 00-Sessions |
| YoYo | GenTech Strategies (-1002916759037) | DeFi, investing, market research, financial analysis | 03-Strategies |
| DMOB | GenTech Labs (-1003872552815) | Smart contracts, security, code, hackathons | 02-Labs, 06-Security |
| Desmond | GenTech Creative (-1003893562036) | Content, docs, branding, social media | 04-Entertainment |

### How We Work
- **Gentech receives → routes to specialist group → agent works → summary to HQ**
- **Green Room** → Active task collaboration (`09-Green Room/`)
- **Mess Hall** → Off-topic, banter, ideas, disagreements (`11-Mess Hall/`)
- **Before replying** → Check Green Room + Mess Hall for context
- **Non-domain work** → Route home, don't do it here
- **Vault sync** → Git-based, Obsidian sync disabled to prevent conflicts

## 🏆 Active Hackathons
| Hackathon | Deadline | Priority |
|-----------|----------|----------|
| Kite AI | Apr 26 | 🟢 PRIMARY ||
| ETHGlobal Open Agents | May 3 | 🟢 STRONG |
| Solana Frontier | May 11 | ⚪ WAIT |

[Full hackathon plan →](00-Inbox/HACKATHON-TODO.md)
