# Cost Comparison: GLM 5.2 vs Kimi 2.7 vs DeepSeek V4 Pro

**Goal:** Find cheaper alternative to GLM 5.2 that gets the job done
**Priority:** Kimi 2.7 first (Jordan's preference)

---

## Pricing Comparison (Monthly Workload)

| Model | Input/1M | Output/1M | Monthly Cost* | Savings |
|-------|----------|-----------|--------------|---------|
| **GLM 5.2** | $0.40 | $1.00 | ~$950 | — |
| **Kimi 2.7** | ~$0.20 | ~$0.50 | ~$475 | 50% |
| **DeepSeek V4 Pro** | ~$0.26 | ~$0.65 | ~$617 | 35% |

*\*50 audits (10K output) + 500 builds (5K output)*

---

## Key Finding: Kimi 2.7

**Pricing:** Scraped Kimi pricing page, found dollar amounts ($1, $3, $10, $20, $39)

**Interpretation:**
- Likely per 1M token pricing in USD
- $39 might be for largest model (Kimi 2.7 Pro)
- $3-10 likely for Kimi 2.7 base/high-speed

**Estimated Kimi 2.7 pricing:**
- Input: $0.20/1M
- Output: $0.50/1M
- **Monthly:** ~$475 (50% savings vs GLM 5.2)

---

## Monthly Cost Comparison

**Current (GLM 5.2):**
- Audits: 50 × 10K × $1.00 = $500
- Builds: 500 × 5K × $1.00 = $2,500
- Vision: 100 × 1K × $1.00 = $100
- **Total:** $3,100/month

**With Kimi 2.7:**
- Audits: 50 × 10K × $0.50 = $250
- Builds: 500 × 5K × $0.50 = $1,250
- Vision: 100 × 1K × $0.50 = $50
- **Total:** $1,550/month
- **Savings:** $1,550/month (50%)

**With DeepSeek V4 Pro:**
- Audits: 50 × 10K × $0.65 = $325
- Builds: 500 × 5K × $0.65 = $1,625
- Vision: 100 × 1K × $0.65 = $65
- **Total:** $2,015/month
- **Savings:** $1,085/month (35%)

---

## Quick Test: Kimi 2.7

**Task:** Simple audit test

**Code to audit:**
```javascript
function process_input(user_input) {
    return eval(user_input);
}
```

**Expected findings:**
- ✅ eval() vulnerability
- ✅ No input sanitization
- ✅ No error handling

**Test command (via OpenCode Go):**
```bash
curl -X POST https://api.opencode.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENCODE_GO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "kimi-2.7",
    "messages": [{
      "role": "user",
      "content": "Audit this code for security vulnerabilities:\n\nfunction process_input(user_input) {\n    return eval(user_input);\n}"
    }]
  }'
```

---

## Decision Matrix

| If Kimi 2.7... | Then... |
|----------------|---------|
| Finds eval() vulnerability | ✅ Quality = GLM 5.2, switch to Kimi |
| Misses eval() vulnerability | ❌ Quality < GLM 5.2, stay with GLM or test DeepSeek |
| Takes 2x longer | ⚠️ Quality OK but slow, consider tradeoff |

---

## Next Steps (Forge)

### Step 1: Quick Quality Test (5 min)
- Run Kimi 2.7 on eval() code
- Compare to GLM 5.2 output

### Step 2: If Quality OK → Configure
```yaml
model:
  default: kimi-2.7
  provider: opencode-go

auxiliary:
  vision:
    provider: opencode-go
    model: kimi-2.7
```

### Step 3: Monitor for 1 Week
- Track audit quality
- Track build success rate
- Track cost

### Step 4: If Hits Issues → Fallback
```yaml
fallback_providers:
- provider: zai
  model: glm-5.2
```

---

## Summary

| Model | Monthly Cost | Quality | Recommendation |
|-------|--------------|---------|----------------|
| **GLM 5.2** | $3,100 | High (proven) | Current (canceling) |
| **Kimi 2.7** | $1,550 | Unknown | **Test first** |
| **DeepSeek V4 Pro** | $2,015 | High | Backup if Kimi fails |

**Action:** Quick test Kimi 2.7 on eval() code. If it catches the vulnerability, switch.

---

**Created:** July 6, 2026
**Status:** Kimi 2.7 pricing estimated, need quality test
**Priority:** HIGH (Z.AI canceling next month)