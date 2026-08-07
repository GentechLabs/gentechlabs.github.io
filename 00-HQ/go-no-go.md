---
date: 2026-08-07
status: active
last-updated: 2026-08-07 06:50 ET
owner: Jordan
purpose: "Jordan's go/no-go control panel. Check a box = decision made. Gentech reads this daily to know what to build and where it routes."
---

# ✅ Go / No-Go — Jordan's Decision Panel

> **How this works:** Jordan checks a box. That's the decision. Gentech reads this file (via vault sync) to know what's greenlit and where it routes.
>
> **Routing:** `[x]` = GO → moves to the build list. `[ ]` = NO-GO / not decided → stays here.
> - **Gentech list** = cloud/VPS work (Labs group)
> - **Forge list** = desktop/PC work (Forge agent)
>
> **Rule:** A checked box is a green light. Gentech builds it. No further confirmation needed.

---

## 🟢 GO — Greenlit, build it

> Check these when you want Gentech to start. Once checked, it leaves this panel and enters the build queue.

- [ ] **Algorand First-Mover x402** — provide Algorand wallet address so `X402_PAYTO_ALGORAND` goes live. Zero code change. First-mover on a fresh x402 venue.
- [ ] **KeeperHub Agents Onchain #80** — wallet funded (10 USDC + 0.0079 ETH on Base). Waiting on KeeperHub outage to clear, then execute the live tx. Deadline Aug 13.
- [ ] **Arc Programmable Money Hackathon** — provide Arc wallet address for deploy. x402 + AgentWallet.sol ready. Deadline Aug 22 (corrected).
- [ ] **AI Factory Hackathon #79** — register? Runs Aug 3-10.
- [ ] **Super Arcade Tennis #73** — deploy production build + wire crypto payments.
- [ ] **FrameForge #71** — AI Storyboard Service. Direction decision?
- [ ] **Open Generative AI #77** — self-host AI media studio. Go/no-go?
- [ ] **CockroachDB × AWS Agentic Memory #83** — register? $8.75K, Aug 18.
- [ ] **Kimi K3 Content Pipeline #82** — fund wallet → test frame consistency loop.
- [ ] **Bug Bounties Comeback** — test open·kritt on our own repos first (build-queue #34), then decide on Immunefi.

---

## 🔴 NO-GO / Hold — decided against, or parked

> Check these when you've decided NOT to do something, or to park it. Gentech stops touching it.

- [ ] **Gears E:D pre-order** — NOT pre-ordering for beta. Waiting for Open Beta (Aug 13-17). (Price-watch only, no purchase.)
- [ ] **Physical agent card / plastic / fiat settlement** — parked. Needs licensed card issuer + KYC/AML partner. Software layer first.

---

## 🎯 Learning Track — AWS + Cyfrin

> Jordan's commitment. Check in Sunday (Aug 9).

- [ ] **AWS SAA-C03** — 2-3 week sprint. Amazon subsidizes exam.
- [ ] **Cyfrin Updraft Solidity/audit** — deep multi-week. Highest differentiation.

---

## 🧭 Routing Legend

| Checked box | Routes to | Where |
|-------------|-----------|-------|
| GO (cloud/VPS) | **Gentech list** | Labs group → build queue |
| GO (desktop/PC) | **Forge list** | Forge agent (desktop) |
| NO-GO / Hold | **Stays parked** | This panel |

---

## 🔗 Related

- [[considerations]] — full open decisions with context
- [[build_queue.json]] — the build list this panel feeds
- [[context-weight]] — auto-generated project overview
