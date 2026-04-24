# Threat Models

**Date**: 2026-04-21  \
**Purpose**: Per-protocol threat modeling before deployment

---

## Template

For each protocol/contract we build:

### 1. Attack Surface
- External calls (which addresses, what can go wrong)
- Admin/owner privileges (who can rug)
- Oracle dependencies (stale data, manipulation)
- Cross-chain messaging (DVN config, replay attacks)

### 2. Threat Matrix

| Threat | Likelihood | Impact | Mitigation |
|--------|-----------|--------|------------|
| Reentrancy | | | CEI pattern, reentrancy guard |
| Oracle manipulation | | | TWAP, multiple sources |
| Admin key compromise | | | Multisig, timelock |
| Flash loan attack | | | Check for spot price reliance |
| Cross-chain replay | | | Nonce tracking, chain ID |

### 3. Checklist
- [ ] All external calls identified
- [ ] Access control reviewed
- [ ] Oracle dependencies documented
- [ ] Reentrancy surface mapped
- [ ] Admin functions listed + secured
- [ ] Upgrade path safe (if proxy)

---

## Active Threat Models
_None yet — start with LayerZero DVN + any deployed contracts_

---

## Chainlink-Specific Threats (from Cyfrin course)
_TBD — document as course progresses_
