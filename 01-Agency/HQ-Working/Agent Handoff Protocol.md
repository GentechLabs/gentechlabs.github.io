# Agent Handoff Protocol

How agents chain work together. One agent's output feeds the next agent's input.

---

## Chain 1: Protocol Due Diligence (YoYo → Dmob)

**Trigger:** YoYo finds a DeFi protocol worth investigating

**Flow:**
```
YoYo researches protocol
  ↓ outputs: vault note in 03-Strategies/
  ↓ includes: TVL, team, tokenomics, red flags
  ↓ tags: #due-diligence #needs-audit
  ↓
Gentech detects new #needs-audit note
  ↓ routes to Dmob
  ↓
Dmob audits contracts
  ↓ outputs: vault note in 06-Security/
  ↓ includes: vuln findings, proxy risks, upgrade concerns
  ↓ tags: #audit-complete #risk-assessment
  ↓
Gentech compiles final report → delivers to Jordan
```

## Chain 2: Content Pipeline (YoYo/Dmob → Desmond)

**Trigger:** Research or audit complete, content needed

**Flow:**
```
YoYo or Dmob completes work
  ↓ note tagged #needs-content
  ↓
Gentech routes to Desmond
  ↓
Desmond creates: thread, blog post, or summary
  ↓ outputs: vault note in 04-Entertainment/
  ↓ tags: #draft #needs-review
  ↓
Gentech delivers draft to Jordan for approval
```

## Chain 3: Security Alert (Any → Jordan, IMMEDIATE)

**Trigger:** Critical vulnerability or scam detected

**Flow:**
```
Dmob finds critical vuln OR YoYo finds scam tokenomics
  ↓ IMMEDIATE alert to Jordan
  ↓ vault note in 06-Security/ with #CRITICAL tag
  ↓ NO content chain — just the alert
```

---

## Tokenomics Red Flags (YoYo Checklist)

When researching any token, flag these immediately:

| Red Flag | Why It Matters | Example |
|----------|---------------|---------|
| **Unlocked team tokens** | Team can dump anytime | WILFI-style |
| **No vesting schedule** | No commitment from team | |
| **Single wallet holds >20%** | Whale risk / rug pull | |
| **Mint function without limit** | Infinite supply risk | |
| **Proxy contract (upgradeable)** | Logic can change post-deploy | |
| **No liquidity lock** | LP can be pulled | |
| **Tax >10% on buy/sell** | Usually scam pattern | |
| **Anonymous team + no audit** | Classic rug setup | |
| **Reflection/rebase mechanics** | Often hides extraction | |
| **"Fair launch" but dev holds 5%+** | Not actually fair | |

## Contract Red Flags (Dmob Checklist)

When auditing contracts, flag these:

| Red Flag | Severity |
|----------|----------|
| **Unverified source code** | HIGH |
| **Proxy with no timelock** | CRITICAL |
| **Owner can pause transfers** | HIGH |
| **Blacklist function** | MEDIUM-HIGH |
| **Hidden mint function** | CRITICAL |
| **Self-destruct callable** | CRITICAL |
| **External calls without checks** | HIGH |
| **Reentrancy patterns** | CRITICAL |
| **Centralized oracle dependency** | MEDIUM |

---

## Vault Tags Reference

| Tag | Meaning | Who Uses |
|-----|---------|----------|
| #due-diligence | Research complete | YoYo |
| #needs-audit | Needs contract review | YoYo → Dmob |
| #audit-complete | Contract review done | Dmob |
| #risk-assessment | Risk level assigned | Dmob |
| #needs-content | Needs writeup | Any → Desmond |
| #draft | Content drafted | Desmond |
| #needs-review | Needs Jordan's approval | Any |
| #CRITICAL | Immediate attention | Any |
| #flagged | Avoid this protocol | Any |
| #opportunity | Worth exploring further | YoYo |
