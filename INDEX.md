# 🧠 Gentech — Second Brain

Welcome to the Gentech knowledge base. This vault is the shared memory for the multi-agent team.

## 📂 Structure
- **00-Inbox** — Triage, incoming items
- **01-Agency** — Business ops, LLC, finances, HQ working docs
- **02-Labs** — Dev projects, code notes, audits, AAE contracts
- **03-Strategies** — DeFi research, market analysis, project plans
- **04-Entertainment** — Content ideas, social media, branding
- **05-Learning** — Course notes (Cyfrin, AVAX Academy)
- **06-Security** — Audit findings, vuln patterns
- **07-Ideas** — Raw ideas, brain dumps, travel
- **08-Activity log** — Daily notes, weekly/monthly summaries, organized by month/week (12 months, 4 weeks each)
- **09-Green Room** — Agent collaboration, handoffs, active coordination
- **09-Templates** — Note templates
- **10-Archive** — Completed/old stuff (auto-archived)
- **11-Mess Hall** — Small talk, disagreements, fun, ideas, extended conversations
- **12-Skills** — Agent protocols, cron registry, coordination rules
- **assets** — Branding images, voice files

## 🏷️ Tags
- `#agent:yoyo` `#agent:dmob` `#agent:desmond` `#agent:gentech`
- `#status:active` `#status:todo` `#status:done`
- `#type:research` `#type:code` `#type:content`

## 🔗 Key Pages
- [[01-Agency/README|Agency]]
- [[02-Labs/README|Labs]]
- [[03-Strategies/README|Strategies]]
- [[05-Learning/README|Learning Progress]]

## 🤖 Agents — Smart Routing v2
**[Full Protocol →](12-Skills/agents-protocol.md)**

| Agent | Group | Domain | Writes To |
|-------|-------|--------|-----------|
| Gentech | GenTech HQ (-1003863540828) | Coordinator — receives all, routes to specialists | 08-Daily |
| YoYo | GenTech Strategies (-1002916759037) | DeFi, investing, market research, financial analysis | 03-Strategies |
| DMOB | GenTech Labs (-1003872552815) | Smart contracts, security, code, hackathons | 02-Labs, 06-Security |
| Desmond | GenTech Creative (-1003893562036) | Content, docs, branding, social media | 04-Entertainment |

### How We Work
- **Gentech receives → routes to specialist group → agent works → summary to HQ**
- **Green Room** → Active task collaboration (`09-Green Room/`)
- **Mess Hall** → Off-topic, banter, ideas, disagreements (`11-Mess Hall/`)
- **Before replying** → Check Green Room + Mess Hall for context
- **Non-domain work** → Route home, don't do it here
- **Vault sync** → `cd /root/vaults/gentech && ob sync`

## 🏆 Active Hackathons
| Hackathon | Deadline | Priority |
|-----------|----------|----------|
|| Kite AI | Apr 26 | 🟢 PRIMARY ||
| ETHGlobal Open Agents | May 3 | 🟢 STRONG |
| Solana Frontier | May 11 | ⚪ WAIT |

[Full hackathon plan →](00-Inbox/HACKATHON-TODO.md)
