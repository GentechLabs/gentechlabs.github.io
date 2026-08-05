# Unichain Treasury Deployment + Grant — Build Plan

**Status:** Pending (added to build queue #37, Aug 4)
**Sequenced:** AFTER KeeperHub (Aug 13) + DataHub (Aug 10) submissions
**Timeline target:** next 2-3 weeks (late Aug / early Sep)
**Prize:** up to $7.5K (Unichain Developer or Retro Grant)

---

## Why this is a real lane, not a distraction

Uniswap Foundation explicitly funds **"Innovation upon the DeFi Experience"** — and their own docs list **treasury and asset management** as a target bucket. Our **Agentic Treasury / GTA executor** is a direct fit. The win condition is *deploying on Unichain*, not just applying.

Three reasons this is worth the build time after current deadlines:
1. **It's rolling** — no hard deadline, applies whenever we're ready
2. **We already have the component** — the treasury yield module / GTA arb executor just needs a Unichain port
3. **Up to $7.5K + ecosystem support** — non-dilutive funding for work we'd do anyway

---

## The one hard requirement (like KeeperHub)

Uniswap docs: *"Deploy to Unichain and/or Uniswap v4"* strengthens the application. A working deployment is what separates accepted from declined. **No deployment = no grant.** So the plan is a build, not an application.

---

## Scope (tight, mirrors KeeperHub build)

### Phase 1 — Pick the port target (Week 1)
Decide which component goes on Unichain:
- **Option A:** Agentic Treasury yield module (deploy idle USDC to Unichain LP / Uni v3 or v4 positions) — most on-theme ("treasury & asset management")
- **Option B:** GTA arb executor — wire it to execute on Unichain
- **Recommendation: A** — treasury + yield + asset management is the exact grant bucket, and it's the least risky port (no perp/funding complexity)

### Phase 2 — Deploy on Unichain (Week 1-2)
1. Set up Unichain (OP Superchain L2) — RPC, faucet/ETH, deploy
2. Port the treasury module's settlement + LP logic to Unichain
3. Get ONE real transaction live on Unichain (proof — same principle as KeeperHub's live-tx requirement)
4. Wire settlement via x402 (our existing gateway) if feasible — shows the full rail

### Phase 3 — Document + apply (Week 2-3)
1. README with setup, goals, demo — we already do this well
2. Record a short demo (the live transaction)
3. Capture metrics: TVL deployed, tx volume, any users
4. Apply via Unichain Grant form: `share.hsforms.com/18Kv3hTvDSt-x1wK9va0OYwsdca9`
5. Optional: also nominate for Retro Grant once there's traction

---

## What qualifies it (checklist)
- [ ] Real Unichain deployment (not a fork)
- [ ] One live onchain transaction on Unichain
- [ ] Documentation (setup, goals, demo)
- [ ] Metrics (TVL, volume, impact)
- [ ] Application submitted

---

## Risks / honesty
- **Time cost** — real build (~1-2 focused weeks). This is WHY it's sequenced after Aug 13.
- **Unichain maturity** — newer L2, some tooling still settling; the port may hit friction.
- **No guaranteed win** — like all grants, acceptance isn't certain even with a solid deployment. But the deployment itself has standalone value (a live treasury on Unichain).

---

## Action items
- [ ] **Gentech:** after Aug 13 — choose Option A (treasury yield) as port target
- [ ] **Gentech:** deploy treasury module on Unichain + one live tx
- [ ] **Gentech:** document + record demo + collect metrics
- [ ] **Jordan:** review/approve application before submit
- [ ] **Gentech:** submit via Unichain grant form
