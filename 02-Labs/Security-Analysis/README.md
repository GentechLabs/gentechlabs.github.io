# 🔒 Security Analysis — Labs

**Owner**: DMOB  \
**Focus**: Smart contract audits, cross-chain messaging security, oracle architecture  \
**Created**: 2026-04-21

---

## Directory

| File | Topic |
|------|-------|
| Security-Checklist.md | Audit template — use for every contract review |
| LayerZero-DVN-Analysis.md | Cross-chain messaging security — DVN configs, KelpDAO exploit review |
| Oracle-Architecture.md | Chainlink vs alternatives — price feeds, VRF, CCIP |
| Contract-Audit-Index.md | Running list of all contracts audited + status |
| Threat-Models.md | Per-protocol threat modeling |

---

## Jordan's Stack Preferences
- **Oracle**: Chainlink preferred (enrolled in Cyfrin Chainlink course)
- **Cross-chain**: Evaluate LayerZero DVN risks before using in production
- **Standards**: OpenZeppelin base contracts, custom errors, checks-effects-interactions

## Audit History
- **2026-04-18**: First pass on ethglobal-open-agents, agent-escrow, AAE → `../Smart-Contract-Audit-2026-04-18.md`

---

## Principles
1. Every external call is a potential exploit
2. checks-effects-interactions, no exceptions
3. OpenZeppelin base contracts always
4. List issues by severity (Critical → High → Medium → Low → Info)
5. For financial analysis, collab with YoYo in Green Room
