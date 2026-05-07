---
name: candidate-opportunity-matching
description: "Filter job/contract opportunities against candidate constraints and generate tailored application materials (resumes, cover letters) for each opportunity type."
version: 1.0.0
author: DMOB (GenTech Labs)
license: MIT
metadata:
  hermes:
    tags: [recruiting, job-search, resume, filtering, candidate-match]
    related_skills: [hackathon-prep, kanban-worker, vault-atomic-operations]
---

# Candidate-Opportunity Matching

**Purpose:** Evaluate job/contract opportunities against candidate constraints, generate tailored resumes and cover letters, and manage application pipeline.

**Triggers:**
- User shares job listings and asks "which ones fit?"
- User requests resume creation or tailoring for specific roles
- Candidate constraints are updated (location, salary, schedule, remote policy)

---

## Candidate Constraints — ALWAYS ENFORCE

These are **hard filters** — no exceptions:

### 1. Remote Policy ✅ / ❌
**Requirement:** 100% remote only — **NO hybrids, NO "must come into office occasionally", NO "hybrid after probation"**

**Why:** User has Amazon Flex schedule; cannot accommodate office commutes or mandatory in-person days. Philippines relocation planned Q3 2026 but currently fully remote.

**Action:** If opportunity mentions office, hybrid, or on-site requirement — **FILTER OUT immediately**. Do not consider.

**Phone screen question:** "Is this role 100% remote with no office requirement?" — if answer is not an unequivocal yes, discard.

---

### 2. Schedule Compatibility ⏰
**Requirement:** Must align with flexible work (Amazon Flex) — prefer:
- Internships (10–12 weeks, ~20–30 hrs/wk)
- Part-time roles (<30 hrs/wk)
- Contract/freelance with flexible hours
- Full-time roles with async-friendly culture (rare, but possible)

**Action:** Estimate weekly time commitment. If >30 hrs/wk and rigid schedule → flag as incompatible unless user says otherwise.

---

### 3. Salary Floor 💰
**Minimum:** $25/hr equivalent OR $4K/month (base)

**Rationale:**
- Amazon Flex income baseline needs to be matched/exceeded
- Crypto internships typically range $20–35/hr — enforce $25+ floor
- Contract roles should clear $4K/mo minimum

**Action:** If pay is "unlisted" or "negotiable" — estimate based on company stage and role. If can't reasonably hit $25/hr → **skip**.

---

### 4. Crypto-Native Focus 🔗
**Preference:** DeFi protocols, smart contract platforms, crypto infrastructure, Web3 tooling

**Acceptable:**
- Pure crypto companies (Uniswap, Aave, Solana Foundation, Chainlink)
- Crypto-adjacent infrastructure (Cloudflare for Web3, GitHub for blockchain)
- Traditional companies with **dedicated crypto teams** (Amazon AWS Blockchain, Robinhood Crypto)

**Filter Out:**
- Pure TradFi (traditional banking, hedge funds without crypto mandate — unless explicitly DeFi-focused like No Limit Holdings)
- Enterprise SaaS with no blockchain component

---

### 5. Career Goal Alignment 🎯
**User Goal:** Full-time crypto role by Q4 2026 via hackathon wins → audit income → remote role

**Fit Indicators:**
- Internship → potential full-time conversion path
- Contract → extendable or convertible to retainer
- Junior/mid-level role that values hands-on shipping over years of experience
- Companies that participate in hackathons or sponsor events (ethglobal, solana foundation, etc.)

---

## Candidate Profile (Jordan)

**Stack:** Solidity, Python, Foundry, React, Cross-chain (LayerZero, Wormhole, CCIP), DeFi (Aave, Lido, Chainlink), AI agents

**Production Projects:**
- AgentEscrow — IN PRODUCTION (cross-chain payment infrastructure)
- AAE Dashboard — LIVE (yield farming LP tracker)
- Cross-Chain Position Adapter — DEV (ETHGlobal)
- Personal Finance Agent — PROTOTYPE

**Hackathon Activity:** ETHGlobal Open Agents (building), Solana Frontier (queued), Kite AI (queued), Retro9000 (queued)

**Current:** Amazon Flex (flexible schedule), GenTech Founder

**Location:** Remote, targeting Philippines Q3 2026 (geo-arbitrage)

---

## Opportunity Filtering Checklist

For each opportunity, validate ALL items:

- [ ] **Remote:** 100% remote, no office requirement (explicitly confirmed)
- [ ] **Pay:** ≥$25/hr or ≥$4K/mo estimated
- [ ] **Schedule:** ≤30 hrs/wk OR flexible hours OR internship duration
- [ ] **Crypto-native:** Company/protocol is in crypto/Web3 space
- [ ] **Stack match:** At least 2-3 technical alignments (Solidity, Python, DeFi, cross-chain, etc.)
- [ ] **Goal alignment:** Supports transition to full-time crypto by Q4 2026

**If any [ ] is unchecked → DISCARD opportunity.**

---

## Resume Variant Strategy

### Master Resume
`Jordan_Master_Resume.md` — source of truth; update when projects/metrics change.

### Variant Mapping

| Role Type | Resume File | Emphasis |
|-----------|-------------|----------|
| Investment Analyst | `Jordan_Analyst_Resume.pdf` | Financial analytics, yield benchmarking, Python data pipelines, on-chain metrics |
| GTM Engineer | `Jordan_GTM_Resume.pdf` | Full-stack shipping, product growth, user acquisition, cross-chain expansion |
| Growth Intern / Analytics | `Jordan_Growth_Resume.pdf` | SQL/Python, growth metrics, funnel analysis, automation |

**Tailoring Process:**
1. Identify role's primary focus from job description
2. Select matching variant (or hybrid if ambiguous)
3. Inject company-specific keywords (protocols they use, metrics they track)
4. Add concrete metrics if available (users, volume, GitHub stars)
5. Ensure "fully remote" and "availability: immediate" are explicit

---

## Pitfalls — What NOT to Do

❌ **DON'T** suggest hybrid/on-site roles — user explicitly requires 100% remote. Ever.
❌ **DON'T** recommend unpaid or sub-$25/hr internships — salary floor is hard constraint.
❌ **DON'T** propose roles that conflict with Amazon Flex schedule — flexibility is non-negotiable.
❌ **DON'T** submit generic resumes — each application needs tailored variant.
❌ **DON'T** omit Philippines relocation context when discussing long-term fit.

✅ **DO** highlight production deployments over theoretical knowledge.
✅ **DO** emphasize hackathon velocity as proof of shipping ability.
✅ **DO** connect projects to business outcomes (growth, retention, new markets).
✅ **DO** mention Amazon Flex as proof of discipline and self-management.
✅ **DO** prominently include portfolio URL: https://protojay4789.github.io/

---

## Application Workflow

1. **Filter** opportunity against checklist (5 hard constraints)
2. **Select** appropriate resume variant
3. **Customize** with role-specific keywords and metrics
4. **Submit** with tailored cover letter (use template if available)
5. **Track** in application spreadsheet: company, role, resume used, date applied, status
6. **Prepare** for role-specific interview (see interview prep guides)

---

## Interview Preparation by Role

### Investment Analyst
- Discuss yield strategies, LP risks, impermanent loss calculations
- Talk through AAE Dashboard metrics you track
- Explain cross-chain yield arbitrage logic
- Prepare protocol evaluation framework (code review + tokenomics)

### GTM Engineer
- Frame projects as growth products with user acquisition/retention metrics
- Discuss feature adoption tracking and funnel optimization
- Talk cross-chain as market expansion strategy
- Show data on user engagement (even if informal)

### Growth Intern
- Practice SQL questions (cohort analysis, funnel queries)
- Python data analysis (pandas, CSV processing, API calls)
- Growth experiment design (A/B tests, metrics selection)
- On-chain user behavior metrics (TVL, active addresses, transaction patterns)

---

## Related Skills

- `hackathon-prep` — for hackathon-related opportunity evaluation (many crypto internships come from hackathon sponsorship)
- `kanban-worker` — for tracking application pipeline and follow-ups
- `vault-atomic-operations` — for concurrent-safe resume file updates
- `security-contest-monitoring` — for bug bounty opportunities that might overlap with internship pipelines

---

## Support Files

- `references/resume-variants-comparison.md` — detailed matrix of which bullet points belong to which variant
- `templates/cover-letter-template.md` — customizable skeleton per role type
- `templates/application-tracker.csv` — spreadsheet template for tracking submitted applications
