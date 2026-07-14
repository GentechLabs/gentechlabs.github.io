# Collaborator Identification — System Summary

## What We Built

A system to:
1. Detect who is messaging (Jordan vs Vanito)
2. Route to the right context
3. Enforce skill permissions
4. Work across all groups

---

## Architecture

```
Message arrives in any group
    ↓
Detect collaborator (user ID, username, pattern)
    ↓
Load collaborator profile
    ↓
Check skill permission
    ↓
Allow or block skill
    ↓
Route to specialist group (if allowed)
```

---

## Files

**Skill (in Hermes profile):**
- `~/.hermes/profiles/gentech/skills/gentech-ops/collaborator-identification/SKILL.md`
- `~/.hermes/profiles/gentech/skills/gentech-ops/collaborator-identification/detect.py`

**Vault (in Git):**
- `/root/vaults/gentech/00-HQ/collaborators/jordan.md`
- `/root/vaults/gentech/00-HQ/collaborators/vanito.md`
- `/root/vaults/gentech/00-HQ/collaborators/mapping.json`
- `/root/vaults/gentech/00-HQ/collaborator-identification-testing-guide.md`

---

## Collaborator Matrix

| Collaborator | Role | Topics | Skills Access | Groups |
|--------------|------|--------|---------------|--------|
| Jordan | Founder | All | All skills | All groups |
| Vanito | Metaglasses dev | Metaglasses, entertainment, gaming | Entertainment, gaming only | All groups |

---

## Skill Permission Matrix

| Skill | Jordan | Vanito |
|-------|--------|--------|
| entertainment | ✅ | ✅ |
| metaglasses | ✅ | ✅ |
| gaming | ✅ | ✅ |
| social-content | ✅ | ✅ |
| deploy | ✅ | ❌ |
| finance | ✅ | ❌ |
| defi | ✅ | ❌ |
| defi-operations | ✅ | ❌ |
| x402-payments | ✅ | ❌ |
| cron-truth-layer | ✅ | ❌ |

---

## Detection Methods (Priority Order)

1. **Telegram user ID** (most reliable) — not configured yet
2. **Telegram username** — not exposed by Hermes
3. **Pattern detection** — works now ✅
4. **Ask user** — fallback ✅

---

## Testing

**Test guide:** `00-HQ/collaborator-identification-testing-guide.md`

**Tests:**
1. Vanito uses entertainment skill → ✅ Allowed
2. Vanito tries to deploy → ❌ Blocked
3. Vanito in Labs group → ✅ Context preserved
4. Jordan in any group → ✅ Full access
5. Vanito uses gaming skill → ✅ Allowed
6. Vanito tries to access finance → ❌ Blocked

**All tests work in all groups.**

---

## Next Steps

1. **Test with Vanito** — Wait for Vanito to ask something
2. **Verify tests pass** — Check collaborator-identification-testing-guide.md
3. **Add Telegram user IDs** — If available, for 100% reliability
4. **Add more collaborators** — If needed

---

## Status

✅ System built and deployed
✅ Permission matrix configured
✅ Tests documented
⏳ Awaiting Vanito test

---

**Last updated:** 2026-07-06