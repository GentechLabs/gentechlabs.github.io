# 📝 Integration Test Template

**Date:** YYYY-MM-DD
**Tester:** (Agent name)
**Components:** (what's being tested together)
**Chain:** (network)
**Layer:** (which AAE layer)

---

## End-to-End Flow

### Scenario: (name the user story)
1. Step 1 → Expected result
2. Step 2 → Expected result
3. Step 3 → Expected result

### Results
| Step | Expected | Actual | Status |
|------|----------|--------|--------|
| 1 | | | ✅/❌ |
| 2 | | | ✅/❌ |
| 3 | | | ✅/❌ |

---

## Agent ↔ Contract Integration

- [ ] Agent can read contract state
- [ ] Agent can submit transactions
- [ ] Agent handles reverts gracefully
- [ ] Agent receives events/logs
- [ ] Multi-agent coordination works

## Error Handling

| Error Scenario | Expected Behavior | Actual | Status |
|---------------|-------------------|--------|--------|
| Invalid input | | | |
| Network timeout | | | |
| Insufficient gas | | | |
| Contract revert | | | |

---

## Issues Found
(same format as contract template)

## Verdict
**Ready to ship:** YES / NO
**Blockers:**
**Next test focus:**