# GenLayer Tooling Tracker

Running inventory of GenLayer dev tools, deployers, and infrastructure we discover.

---

## Shipyard — No-CLI Deployment

| Field | Detail |
|---|---|
| **URL** | gen-shipyard.vercel.app |
| **Builder** | @gaymused (also built genscope) |
| **What it does** | Web UI for deploying GenLayer contracts without touching CLI |
| **Networks** | Bradbury, Asimov, StudioNet, Localnet (dashboard switcher) |
| **Key features** | Live tx hashes, AI agent integration (plug contract address into agents like Antigravity) |
| **Relevance** | Speeds up hackathon demos; removes CLI friction for non-technical teammates |
| **Date added** | 2026-04-25 |

### Notes
- Potential integration: Shipyard-deployed contract → plug into Antigravity AI agent → auto frontend scaffold.
- Could cut our GenLayer demo prep time significantly if we're targeting the BuildersClaw track or any GenLayer-native hackathon.

---

## How to use this doc
- Append new tools as H2 sections with the same table schema.
- Tag with `date added` so we know what's stale.
- When a tool graduates to "used in production," move it to `genlayer-recon/index.md` under a **Production Stack** section.
