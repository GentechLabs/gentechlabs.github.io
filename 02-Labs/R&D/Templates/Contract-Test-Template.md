# 📝 Contract Test Template

**Date:** YYYY-MM-DD
**Tester:** (Agent name)
**Contract:** (name + address if deployed)
**Chain:** (network name + chain ID)
**Layer:** (which AAE layer)

---

## Test Plan

### Unit Tests
```bash
forge test --match-contract {ContractName} -vvv
```

| Test Function | Description | Status |
|--------------|-------------|--------|
| | | ✅/❌ |

### Fuzz Tests
```bash
forge test --match-contract {ContractName} --fuzz-runs 1000
```

| Property | Description | Status |
|----------|-------------|--------|
| | | ✅/❌ |

### Deployment Test
- [ ] Contract deploys without revert
- [ ] Constructor params set correctly
- [ ] Initial state correct
- [ ] Access control working

### Gas Report
```bash
forge test --gas-report
```

| Function | Gas Used | Acceptable? |
|----------|----------|-------------|
| | | Y/N |

---

## Issues Found

### Issue 1: [SEVERITY] Title
- **File:** 
- **Line:** 
- **Description:** 
- **Repro:** 
- **Fix:** 

---

## Verdict
- [ ] All unit tests pass
- [ ] All fuzz tests pass
- [ ] Deployment successful
- [ ] Gas within limits
- [ ] No critical/major issues

**Ready for next phase:** YES / NO
**Blockers:** 
**Notes:**