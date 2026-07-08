# Collaborator Identification — Testing Guide

## Test Plan

We'll test the collaborator identification and skill permission system when Vanito asks something.

---

## Test Cases

### Test 1: Vanito in Entertainment Group

**Message:** "Check POE2 build status"

**Expected behavior:**
1. Detect: Vanito (pattern: "POE2")
2. Load Vanito profile
3. Check permission: gaming skill → ✅ Allowed
4. Execute gaming skill
5. Return POE2 build status

**Expected response:** POE2 build status (not blocked)

---

### Test 2: Vanito tries to deploy

**Message (in any group):** "Deploy x402 to production"

**Expected behavior:**
1. Detect: Vanito (pattern: "deploy")
2. Load Vanito profile
3. Check permission: deploy skill → ❌ Blocked
4. Response: "You don't have permission for this operation. Only Jordan can deploy to production."

**Expected response:** Blocked message (not deployed)

---

### Test 3: Vanito in Labs Group

**Message:** "Check metaglasses integration"

**Expected behavior:**
1. Detect: Vanito (pattern: "metaglasses")
2. Load Vanito profile
3. Check permission: metaglasses skill → ✅ Allowed
4. Execute metaglasses skill
5. Return metaglasses integration status

**Expected response:** Metaglasses integration status (not blocked)

---

### Test 4: Jordan in any group

**Message:** "Deploy x402 to production"

**Expected behavior:**
1. Detect: Jordan (pattern: "Jordan:")
2. Load Jordan profile
3. Check permission: deploy skill → ✅ Allowed
4. Execute deploy skill
5. Deploy x402 to production

**Expected response:** Deployment proceeds (not blocked)

---

### Test 5: Vanito uses entertainment skill

**Message:** "Create a meme for the launch"

**Expected behavior:**
1. Detect: Vanito (pattern: "meme" + context)
2. Load Vanito profile
3. Check permission: social-content skill → ✅ Allowed
4. Execute meme-generation skill
5. Return meme image

**Expected response:** Meme image (not blocked)

---

### Test 6: Vanito tries to access finance

**Message:** "Check my portfolio balance"

**Expected behavior:**
1. Detect: Vanito (pattern: "portfolio")
2. Load Vanito profile
3. Check permission: finance skill → ❌ Blocked
4. Response: "You don't have permission for financial operations. Only Jordan can access portfolio data."

**Expected response:** Blocked message (not portfolio data)

---

## How to Verify Tests Pass

After each test, check:

1. **Collaborator correctly identified:**
   - Response mentions "Vanito" or "Jordan"

2. **Permission correctly applied:**
   - Allowed skills proceed
   - Blocked skills show error message

3. **Context maintained:**
   - Response is relevant to collaborator's role
   - Vanito gets gaming/entertainment context
   - Jordan gets full context

---

## Testing Locations

**All tests apply to all groups:**
- Gentech HQ
- Gentech Strategies
- Gentech Labs
- Gentech Entertainment

**System behavior is identical across all groups.**

---

## What We're Looking For

**Success indicators:**
- ✅ Vanito is correctly identified
- ✅ Vanito can use entertainment/gaming skills
- ✅ Vanito is blocked from critical operations
- ✅ Jordan can use all skills
- ✅ System works in all groups

**Failure indicators:**
- ❌ Vanito is confused with Jordan
- ❌ Vanito can deploy or access finance
- ❌ Jordan is blocked from any skill
- ❌ System only works in some groups

---

## After Testing

If tests pass, system is live.

If tests fail, debug:
1. Check collaborator-identification skill is loaded
2. Check mapping.json has correct data
3. Check detect.py tests still pass
4. Check permissions matrix is correct

---

## Next Steps After Tests Pass

1. Add Telegram user IDs (if available) for 100% reliability
2. Add more collaborators (if needed)
3. Expand skill permission matrix (if needed)
4. Document best practices for collaborators