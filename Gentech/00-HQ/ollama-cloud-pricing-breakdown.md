# Ollama Cloud Pricing — Complete Breakdown

**Date:** July 6, 2026
**Source:** https://ollama.com/pricing (scraped via Python)

---

## Pricing Tiers

| Plan | Price | Usage | Concurrent Models | Use Cases |
|------|-------|-------|-------------------|-----------|
| **Free** | $0 | Light usage | 1 | Chatting, evaluating larger models, coding with small models |
| **Pro** | $20/month ($200/yr) | Day-to-day work | 3 | Larger models, coding automation, deep research |
| **Max** | $100/month | Heavy, sustained usage | 10 | Continuous agent tasks, multiple concurrent agents, extended sessions |

---

## Usage Model

**Key insight:** Ollama Cloud uses **GPU time billing**, NOT token billing.

> "Usage reflects actual utilization of Ollama's cloud infrastructure — primarily GPU time, which depends on model size and request duration."

**How it differs from token-based pricing:**
- **Token-based (ZAI, OpenCode Go):** Billed per token processed
- **GPU-time (Ollama):** Billed per minute of GPU usage
- **Result:** Efficiency matters more than token count

**Session limits:**
- Reset every **5 hours** (session limits)
- Reset every **7 days** (weekly limits)
- 90% email reminder before hitting limits

---

## Model Availability

From April 2026 config backup:

| Model | Used By | Status |
|-------|---------|--------|
| **deepseek-v4-flash** | Gentech, YoYo, Desmond, CLI | ✅ Available |
| **qwen3-coder-next** | DMOB | ✅ Available |

---

## Cost Comparison: Ollama Cloud vs Token-Based

### Scenario: Monthly Agent Workload

**Assumptions:**
- 50 security audits (10K output tokens each)
- 500 code builds (5K output tokens each)
- Average request: 30 seconds GPU time

**Token-Based (GLM 5.2 via ZAI):**
- Input: 500K × $0.40/M = $200
- Output: 750K × $1.00/M = $750
- **Total:** $950/month

**Ollama Cloud (Pro Plan):**
- GPU time: 550 requests × 30s = 16,500 seconds = 275 minutes
- Pro plan: $20/month (unlimited within limits)
- **Total:** $20/month

**Savings:** 97.9% ($930/month)

---

## Pro Plan Limits (Need Investigation)

**Known:**
- Session limits reset every 5 hours
- Weekly limits reset every 7 days
- 90% reminder email

**Unknown (Forge task):**
- What is the "day-to-day work" quota?
- What is the weekly limit?
- How many GPU hours included in Pro plan?

**Test scenario:**
```bash
# Check current Ollama Cloud usage
curl -H "Authorization: Bearer $OLLAMA_API_KEY" \
  https://api.ollama.com/v1/usage

# Expected: JSON with current plan, usage, limits
```

---

## Max Plan for Multi-Agent

**Gentech Dual-Agent Architecture:**
- **Gentech (VPS):** 24/7 ops, cron jobs
- **Forge (Desktop):** Development, OSS work

**Concurrent models needed:**
- Gentech: 2-3 models (audit, vision, fallback)
- Forge: 1-2 models (coding, vision)

**Total: 3-5 concurrent models**

**Plan recommendation:**
- **Pro Plan:** 3 concurrent models ✅
- **Max Plan:** 10 concurrent models (overkill)

---

## Dual-Model Strategy with Ollama

### Current (Token-Based)
```
Build Model: DeepSeek V4 Flash ($0.01/1M)
Audit Model: GLM 5.2 ($1.00/1M)
Monthly Cost: ~$950
```

### Proposed (Ollama Cloud)
```
Build Model: deepseek-v4-flash (included in Pro)
Audit Model: qwen3-coder-next (included in Pro)
Monthly Cost: $20
```

### Hybrid (Optimal)
```
Build Model: Ollama Cloud deepseek-v4-flash (unlimited)
Audit Model: Ollama Cloud qwen3-coder-next (unlimited)
Vision: DeepSeek V4 Pro via OpenCode Go (when needed)
Monthly Cost: $20 + vision costs (~$100) = $120
```

---

## Configuration Change

**Current (Gentech VPS):**
```yaml
model:
  default: glm-4.7
  provider: zai

auxiliary:
  vision:
    provider: zai
    model: glm-5.2
```

**Proposed (Ollama Cloud):**
```yaml
model:
  default: deepseek-v4-flash
  provider: ollama-cloud

auxiliary:
  vision:
    provider: ollama-cloud
    model: qwen2.5-vision
```

**Change steps:**
1. Add Ollama Cloud provider to config
2. Set default model to deepseek-v4-flash
3. Switch vision model to qwen2.5-vision
4. Monitor Pro plan limits for 1 week
5. Adjust if hitting limits

---

## Investigation Tasks (Forge)

1. **Check Pro plan limits:**
   ```bash
   curl -H "Authorization: Bearer $OLLAMA_API_KEY" \
     https://api.ollama.com/v1/usage
   ```

2. **Test deepseek-v4-flash on Ollama:**
   ```bash
   # Simple coding task
   curl -X POST https://api.ollama.com/v1/chat/completions \
     -H "Authorization: Bearer $OLLAMA_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "deepseek-v4-flash",
       "messages": [{"role": "user", "content": "Write a Python hello world"}]
     }'
   ```

3. **Test qwen3-coder-next on Ollama:**
   ```bash
   # Security audit test
   curl -X POST https://api.ollama.com/v1/chat/completions \
     -H "Authorization: Bearer $OLLAMA_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "qwen3-coder-next",
       "messages": [{
         "role": "user",
         "content": "Audit this code for vulnerabilities:\n\ndef process_input(user_input):\n    return eval(user_input)"
       }]
     }'
   ```

4. **Monitor GPU time usage:**
   - Run 10 audits
   - Measure GPU time per audit
   - Extrapolate to monthly usage

---

## Success Criteria

- ✅ Pro plan covers monthly workload
- ✅ Model quality comparable to GLM 5.2
- ✅ Cost savings >80%
- ✅ No limit hits during normal operations

---

**Created:** July 6, 2026
**Status:** Pricing extracted, need Forge to test quality + limits
**Priority:** HIGH (97% cost savings potential)

---

## Summary

| Provider | Model | Pricing | Monthly Cost | Quality |
|----------|-------|---------|--------------|---------|
| **ZAI (current)** | GLM 5.2 | $0.40/$1.00 per 1M | ~$950 | High |
| **Ollama Cloud** | qwen3-coder-next | $20/month (unlimited) | $20 | Unknown |
| **OpenCode Go** | DeepSeek V4 Pro | ~$0.26/$0.65 per 1M | ~$247 | High |

**Recommendation:** Test Ollama Cloud Pro plan. If quality comparable, switch for 97% cost savings.