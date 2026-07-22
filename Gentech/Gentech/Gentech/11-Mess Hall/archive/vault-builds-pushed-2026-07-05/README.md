# Vault Builds Archive — 2026-07-05

**Archived to GitHub**: 9 builds pushed to public repos, vault copies moved to archive.

---

## Archived Builds (vault → GitHub)

| Vault Build | GitHub Repo | Files | Status |
|-------------|-------------|-------|--------|
| `agent-finance-intermediary` | https://github.com/ProtoJay4789/agent-finance-intermediary | BNPL MVP (contracts + API) | ✅ Archived Jul 5, 2026 |
| `agent-registration-api` | https://github.com/ProtoJay4789/agent-registration-api | Agent Registration (port 8001) | ✅ Archived Jul 5, 2026 |
| `agent-search-api` | https://github.com/ProtoJay4789/agent-search-api | Agent Search (port 8003) | ✅ Archived Jul 5, 2026 |
| `defi-intelligence-api` | https://github.com/ProtoJay4789/defi-intelligence-api | DeFi Intelligence (port 8002) | ✅ Archived Jul 5, 2026 |
| `gentech-erc8004-standard` | https://github.com/ProtoJay4789/gentech-erc8004-standard | ERC-8004 standard | ✅ Archived Jul 5, 2026 |
| `gentech-merchant-portal` | https://github.com/ProtoJay4789/gentech-merchant-portal | Merchant portal | ✅ Archived Jul 5, 2026 |
| `gentech-runtime` | https://github.com/ProtoJay4789/gentech-runtime | GenTech runtime | ✅ Archived Jul 5, 2026 |
| `gentech-tool-manifest` | https://github.com/ProtoJay4789/gentech-tool-manifest | Tool manifest | ✅ Archived Jul 5, 2026 |
| `gentech-wallet-abstraction` | https://github.com/ProtoJay4789/gentech-wallet-abstraction | Wallet abstraction | ✅ Archived Jul 5, 2026 |

---

## Why Archive?

**Problem**: You code in vault, but never push to GitHub. Lost work if VPS crashes. Forge can't contribute.

**Solution**:
1. ✅ Create GitHub repo for each build
2. ✅ Push code to GitHub
3. ✅ Archive vault copy (cleanup vault, prevent confusion)
4. ✅ Work now happens in GitHub repo (standard pattern)

---

## Going Forward

**Pattern**:
1. Develop in vault (quick iteration)
2. Create GitHub repo immediately when ready
3. Push to GitHub
4. Archive vault copy
5. All future work in GitHub repo

**Prevents**: "Idea in vault, never pushed to GitHub" gap

**Enables**: Forge collaboration, portfolio proof, disaster recovery

---

## Current Vault State

**`builds/` folder now contains**:
- `gentech-travel/` (only remaining build, has GitHub repo: gentech-travels)

**All other builds** archived here.

---

## Skills Updated

- `gentech-ops/vault-maintenance/SKILL.md` — Added `/vault-github-sync` audit pattern
- `gentech-ops/vault-maintenance/references/vault-github-sync-audit.md` — Created reference doc
- `genTech-agent-kit/docs/VAULT_MODULE_SYNC.md` — AgentKit version of pattern
- `hermes-model-routing/SKILL.md` — Updated pattern to Build → AUDIT + FIX

---

*Archived: July 5, 2026*
*Pattern added to vault maintenance skill*