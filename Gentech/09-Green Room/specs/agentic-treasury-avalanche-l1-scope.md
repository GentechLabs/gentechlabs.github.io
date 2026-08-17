# Agentic Treasury as an Avalanche L1 — Honest Scope
**Status:** Scoped (Aug 15, 2026) | **Source:** Jordan — "Is there a way to upgrade the Agentic Treasury as an L1? Yes let's scope this out"
**Build flow:** per `develop-and-verify` + `build-queue` (DEV → AUDIT, Karpathy-gated)
**Related:** `09-Green Room/ideas.md` → Avalanche Retro9000 idea | `specs/agentic-treasury-yield-trade-engine.md` (AAE core)

---

## 0. What "Treasury as an L1" actually means (3 distinct things)

Jordan's question bundles three very different builds. Scoping honestly means separating them — the effort and value diverge sharply.

| # | Interpretation | Effort | Value | When it matters |
|---|---------------|--------|-------|-----------------|
| **A** | **Run an Avalanche L1 validator node on our VPS** | 🟢 Small (1-2 days) | Ops showcase + Retro9000 tooling angle | Now |
| **B** | **Deploy our own Avalanche L1 chain** (a sovereign chain the AAE treasury lives on) | 🟡 Medium (1-2 wks) | Real product surface + Retro9000 L1s round eligibility | Next |
| **C** | **Migrate the AAE treasury's state/ledger onto our own L1** as its home chain | 🔴 Large (multi-week, high risk) | Full sovereignty; probably not worth it yet | Later / never |

**My recommendation:** Scope **B** as the real deliverable (deploy our own L1), with **A** as the prerequisite. **Do NOT pursue C now** — the treasury is currently venue-agnostic by design (chains are interchangeable config, locked by Jordan Aug 5), and forcing it onto a 1-validator chain trades portability for sovereignty we don't need yet. C becomes interesting only if the treasury outgrows public-chain constraints (fee control, custom VM, own gas token).

---

## 1. Ground truth (post-Etna / Avalanche9000)

The economics changed completely. From the Avalanche Builder Hub + Etna docs:

- **L1 validators NO LONGER stake 2,000 AVAX** (ACP-77/Etna). They pay a **continuous (recurring) fee** instead — roughly **~1.3 AVAX/month** (~$8.50/mo) per Reddit/Eco sourcing.
- Primary Network validators (C-Chain) still require 2,000 AVAX — we are NOT doing that.
- Avalanche L1s are **sovereign chains**: own validator set, own gas token, own VM, own rules. Launched via open-source **`avalanche-cli`** (`avalanche blockchain create <name>` → `deploy`), local → Fuji testnet → mainnet.
- **ICM (Interchain Messaging) + Teleporter** = native cross-L1 messaging (BLS-signed, no external bridge trust). This is how our L1 talks to the C-Chain/USDC/other L1s.
- Minimum to launch an L1 with a single validator dropped **>99%** post-Etna (Delphi).
- Hardware for an L1 validator is VPS-viable: 2-4 cores, 4-16GB, NVMe, 25-100Mbps. We already run 24/7 infra.

**The takeaway:** the $13K/2,000-AVAX wall only applies to Primary Network validation, which we don't need. Deploying **our own L1** is now a low-capital, VPS-ops build — exactly the "agent as the bypass for electricity/hardware" play.

---

## 2. Why this matters for us (the strategic case)

- **Retro9000 (live round: Avalanche L1s & Infrastructure Tooling, $40M AVAX):** deploying an L1 is *literally* the eligibility criterion. This is not a stretch — it's the direct submission.
- **C-Chain Round 5 (July 30):** rewards on-chain activity measured by **AVAX burned via gas fees**. An L1 that routes treasury traffic + a Teleporter bridge generates measurable activity.
- **Product story:** "The Agentic Treasury runs on its own sovereign Avalanche L1" is a flagship differentiator nobody else has. It converts the AAE stack (which is currently smart but invisible) into *owned infrastructure*.
- **Extends the portable-home-chain thesis (Jordan, Aug 5):** "make Algorand your home... the wallet is chain-portable." Owning our own L1 is the logical end-state of that — we control the home chain too.
- **Agent-native rails:** L1s support custom VMs, custom gas tokens, permissioning precompiles — we could mint our own gas token, gate by ERC-8004 identity, add fee logic at protocol level. This is the agent-economy infrastructure thesis made literal.

---

## 3. Scope — Phase B (deploy our own L1) broken down

> Karpathy-gated: Easy → Hard, each phase testable, no scope creep.

### Phase B0 — Prerequisite: L1 validator node on our VPS (the "bypass")
- Install `avalanche-cli` + run an Avalanche node on the VPS (the existing 24/7 box).
- This is literally what Retro9000 wants to reward — running the infra via agent, not own electricity.
- **Acceptance:** node healthy, `avalanche` CLI functional, docs captured. (This is interpretation A done — small, do it first.)

### Phase B1 — Deploy L1 on Fuji testnet
- `avalanche blockchain create gentech-l1` → deploy to Fuji.
- Stand up a **single validator** (us) + register our node as the validator set.
- Wire a native gas token (we choose the model — could be a treasury-issued token).
- **Acceptance:** L1 producing blocks on Fuji, RPC reachable, our node validating.

### Phase B2 — Teleporter/ICM bridge to C-Chain
- Deploy Teleporter to move USDC between our L1 and the C-Chain (burn-and-mint via ICM).
- This is the piece that makes the L1 *useful* — the treasury can move real USDC onto/off its own chain.
- **Acceptance:** verified USDC bridge round-trip Fuji L1 ↔ Fuji C-Chain, tx receipt on both.

### Phase B3 — Mainnet L1 + Retro9000 submission
- Deploy to Avalanche mainnet (recurring ~1.3 AVAX/mo fee).
- Assemble the Retro9000 L1s & Infrastructure Tooling submission: repo, docs, demo of the sovereign treasury chain.
- **Acceptance:** live mainnet L1 + Retro9000 application submitted.

### Phase B4 — (deferred, NOT in this build) migrate AAE treasury onto the L1 as home chain
- Only if the chain proves reliable + the treasury wants sovereignty.
- Deferred to avoid locking the venue-agnostic treasury into 1-validator infra prematurely.

---

## 4. What we are NOT doing (honesty guardrails)

- ❌ **Not staking 2,000 AVAX / running a Primary Network validator** (~$13K locked — that's the wall, and we skip it entirely).
- ❌ **Not migrating the AAE treasury's state onto our L1 yet** (Phase C deferred — sovereignty we don't need, portability we'd lose).
- ❌ **Not building a new AMM/farm** — composition model stands (we compose Trader Joe/Morpho/etc.; the L1 is the *home rail*, not a venue).
- ❌ **No new token launch** unless the L1's gas-token design requires it — and even then, that's a separate, larger decision.

---

## 5. Cost estimate (honest)

| Item | Cost |
|------|------|
| VPS (existing 24/7 box — reuse, maybe small bump) | $0 marginal (already pay) |
| L1 recurring validation fee (mainnet) | ~1.3 AVAX/mo ≈ **$8.50/mo** |
| AVAX gas for genesis + Teleporter deploys | ~$5-20 one-time (small txs) |
| Our time (B0-B3) | 1-2 weeks dev, Karpathy-gated |

**Total capital exposure: well under $50.** Compare to the $13K Primary Network wall. This is genuinely cheap — the agent + VPS is the cost-killer.

---

## 6. Risks / honest flags

- **Single-validator security:** a 1-validator L1 is not decentralized. Fine for a product/demo chain, NOT for holding the treasury's real funds at scale. Mitigation: bridge only small test slices; keep main treasury on public chains until validator set grows.
- **Retro9000 eligibility is not guaranteed:** the program rewards *real on-chain activity*, not just "we deployed a chain." We must drive actual usage/traffic to qualify for meaningful AVAX. Deployment is necessary, not sufficient.
- **~1.3 AVAX/mo is my sourced figure (Reddit/Eco/Delphi), not an official hard number** — must confirm against `build.avax.network` before committing to cost.
- **L1 tooling maturity:** avalanche-cli is solid but younger than EVM tooling. Expect friction.

---

## 7. Definition of Done (Phase B)

The Agentic Treasury L1 is "real" when, end to end:
1. Our node validates our L1 (VPS, agent-run) — Phase B0
2. L1 live on Fuji, producing blocks with our validator set — Phase B1
3. USDC moves L1 ↔ C-Chain via Teleporter, verified on-chain — Phase B2
4. Mainnet L1 live + Retro9000 submission filed — Phase B3
5. Every step verified by block/tx receipt, not declared success

---

## 8. Next action (blocker for me)

- **Needs Jordan:** (1) greenlight Phase B0-B3 (small capital, ~1-2 wks), (2) confirm whether to run the L1 node on the existing VPS or a small separate box, (3) any AVAX for genesis/fees (small — can fund from existing AVAX gas).
- Then I start B0: install avalanche-cli, stand up the validator node, capture Retro9000 eligibility.
