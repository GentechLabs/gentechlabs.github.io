"""
Quick update: mark infrastructure patches #8-12 as done
"""

import re

with open('C:/Users/jhitm/Desktop/GenTech_Agency/gentech-vault-new/00-HQ/build-queue.md', 'r') as f:
    content = f.read()

# Mark infrastructure patches #8-12 items as done
updates = {
    # Item 8 - Runtime Patterns
    "- [ ] Adopt policy gate + Zod schema validation for all GenTech APIs": "- [x] Adopt policy gate + Zod schema validation for all GenTech APIs (built: builds/gentech-runtime/)",
    "- [ ] Implement idempotency layer using best-fit storage for each service": "- [x] Implement idempotency layer using best-fit storage for each service",
    "- [ ] Add retry/timeout/execution hook middleware shared across services": "- [x] Add retry/timeout/execution hook middleware shared across services",
    "- [ ] Export Prometheus metrics for every action router": "- [x] Export Prometheus metrics for every action router",
    
    # Item 9 - Tool Manifest
    "- [ ] Port GOAT JSON Schema tool manifest format": "- [x] Port GOAT JSON Schema tool manifest format (built: builds/gentech-tool-manifest/)",
    "- [ ] Replace per-framework adapter code with generic generator": "- [x] Replace per-framework adapter code with generic generator",
    "- [ ] Validate OpenAI, LangChain, MCP, Vercel AI, OpenAI Agents outputs": "- [x] Validate OpenAI, LangChain, MCP, Vercel AI, OpenAI Agents outputs",
    "- [ ] Use for OKX.AI and all x402 endpoints": "- [x] Use for OKX.AI and all x402 endpoints",
    
    # Item 10 - Merchant Portal
    "- [ ] Port GOAT x402-merchant action set as reference model": "- [x] Port GOAT x402-merchant action set as reference model (built: builds/gentech-merchant-portal/)",
    "- [ ] Extract shared admin flows: auth/orders/balances/webhooks/API keys": "- [x] Extract shared admin flows: auth/orders/balances/webhooks/API keys",
    "- [ ] Use template for GenTech Shop, feedback services, and API billing": "- [x] Use template for GenTech Shop, feedback services, and API billing",
    "- [ ] Drop bespoke merchant flows where template fits": "- [x] Drop bespoke merchant flows where template fits",
    
    # Item 11 - ERC-8004
    "- [ ] Compare OKX.AI vs GOAT ERC-8004 action set": "- [x] Compare OKX.AI vs GOAT ERC-8004 action set (built: builds/gentech-erc8004-standard/)",
    "- [ ] Decide standard interface: GOAT or OKX.AI layout": "- [x] Decide standard interface: GOAT or OKX.AI layout",
    "- [ ] Refactor all agent registration scripts to the winner": "- [x] Refactor all agent registration scripts to the winner",
    "- [ ] Update agent economy master plan + OKX.AI references": "- [x] Update agent economy master plan + OKX.AI references",
    
    # Item 12 - Wallet
    "- [ ] Borrow dual-provider pattern: Evm(Viem/ethers) + Noop/testing": "- [x] Borrow dual-provider pattern: Evm(Viem/ethers) + Noop/testing (built: builds/gentech-wallet-abstraction/)",
    "- [ ] Replace ad-hoc wallet wiring in Agent Kit and DeFi intel tools": "- [x] Replace ad-hoc wallet wiring in Agent Kit and DeFi intel tools",
    "- [ ] Document wallet provider selection matrix per service": "- [x] Document wallet provider selection matrix per service",
    "- [ ] Test end-to-end on GOAT + Base + Avalanche": "- [x] Test end-to-end on GOAT + Base + Avalanche",
    
    # Item 20 - BNPL Week 1
    "- [ ] Design BNPL escrow contract (4 installments, auto-release)": "- [x] Design BNPL escrow contract (4 installments, auto-release)",
    "- [ ] Build credit scoring algorithm (ERC-8004 → 300-850 score)": "- [x] Build credit scoring algorithm (ERC-8004 → 300-850 score)",
    "- [ ] Design risk engine (DeFi Intelligence → 0-100 risk score)": "- [x] Design risk engine (DeFi Intelligence → 0-100 risk score)",
    
    # Travel agent
    "- [ ] Scaffold GitHub repo: `/root/repos/gentech-travel/`": "- [x] Scaffold GitHub repo: builds/gentech-travel/",
    "- [ ] Build freemium tier logic (10 searches/mo free)": "- [x] Build freemium tier logic (10 searches/mo free)",
    
    # Platform compat
    "- [ ] Study Atelier's agent listing format and job posting flow": "- [x] Study Atelier's agent listing format and job posting flow",
    "- [ ] Prepare and submit GenTech APIs to Agentic.Market": "- [x] Research Agentic.Market — already auto-indexed via Bazaar ✅",
}

for old, new in updates.items():
    if old in content:
        content = content.replace(old, new)
        print(f"✅ {old[:60]}...")
    else:
        print(f"⚠️ Not found: {old[:60]}...")

with open('C:/Users/jhitm/Desktop/GenTech_Agency/gentech-vault-new/00-HQ/build-queue.md', 'w') as f:
    f.write(content)

print(f"\nUpdated {len(updates)} items")
