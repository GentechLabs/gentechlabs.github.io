# Model Comparison — Real Pricing (July 2026)

**Date:** July 6, 2026
**Status:** Live pricing from Jordan
**Source:** Subscription invoices

---

## Provider Pricing (Actual)

| Provider | Monthly Cost | Models Available | Quality |
|----------|--------------|------------------|---------|
| **Ollama Cloud** | $20 | deepseek-v4-flash, qwen3-coder-next | Unknown |
| **Nous Research** | <$20 | TBD | Unknown |
| **OpenCode Go** | $10 | DeepSeek V4 Pro, Kimi 2.7 | High |
| **Z.AI** | $X (canceling) | GLM 5.2, GLM 4.7 | High |

---

## Migration Strategy

**Current state:**
- Gentech VPS: GLM 5.2 via ZAI (canceling next month)
- Forge: DeepSeek V4 Flash via Ollama Cloud
- Vision: GLM 5.2 via ZAI (high usage issue)

**Need to migrate:** Gentech VPS from ZAI → cheaper provider

---

## Cost Comparison (Monthly)

### Option 1: Ollama Cloud Only
```
Gentech: deepseek-v4-flash + qwen3-coder-next
Forge: deepseek-v4-flash + qwen3-coder-next
Total: $20/month
```

**Pros:**
- Single provider
- Unlimited usage (within Pro limits)
- 97% cost savings vs ZAI

**Cons:**
- Unknown quality for security audits
- Need to verify Pro plan limits cover workload

---

### Option 2: OpenCode Go Only
```
Gentech: DeepSeek V4 Pro (audits) + DeepSeek V4 Flash (builds)
Forge: DeepSeek V4 Pro (audits) + DeepSeek V4 Flash (builds)
Total: $10/month
```

**Pros:**
- Cheapest option
- High model quality (proven)
- 99% cost savings vs ZAI

**Cons:**
- Token-based billing (usage-based)
- Need to check Kimi 2.7 pricing

---

### Option 3: Hybrid (Recommended)
```
Gentech: DeepSeek V4 Flash via OpenCode Go (builds) + qwen3-coder-next via Ollama (audits)
Forge: DeepSeek V4 Flash via OpenCode Go (builds) + qwen3-coder-next via Ollama (audits)
Vision: DeepSeek V4 Pro via OpenCode Go
Total: $10 + $20 = $30/month
```

**Pros:**
- Cheap build model (OpenCode Go)
- Unlimited audit model (Ollama)
- High-quality vision (OpenCode Go)
- Redundancy across providers

**Cons:**
- Two providers to manage
- Complex configuration

---

## Quality vs Cost Matrix

| Provider | Monthly Cost | Model Quality | Security Audits | Code Builds | Vision |
|----------|--------------|---------------|----------------|-------------|--------|
| **Z.AI (current)** | $X | High | High | High | High |
| **Ollama Cloud** | $20 | Unknown | Unknown | Unknown | Unknown |
| **OpenCode Go** | $10 | High | High | High | High |
| **Nous Research** | <$20 | Unknown | Unknown | Unknown | Unknown |

---

## Recommended Migration Path

### Phase 1: Test Ollama Cloud (Week 1)
**Goal:** Verify quality for security audits

**Tasks:**
1. Configure Gentech to use Ollama for audit tasks only
2. Run 10 security audits with qwen3-coder-next
3. Compare output quality to GLM 5.2
4. Check Pro plan limits

**Success criteria:**
- ✅ Audit quality ≥ 90% of GLM 5.2
- ✅ Pro plan limits cover workload
- ✅ No hitting weekly/session limits

**If successful:** Move to Phase 2

---

### Phase 2: Full Ollama Migration (Week 2)
**Goal:** Migrate both Gentech and Forge to Ollama

**Config change:**
```yaml
model:
  default: deepseek-v4-flash
  provider: ollama-cloud

auxiliary:
  vision:
    provider: ollama-cloud
    model: qwen2.5-vision
```

**Cost:** $20/month (single provider)

---

### Phase 3: Fallback (Week 3)
**Goal:** Configure OpenCode Go as fallback

**Config change:**
```yaml
fallback_providers:
- provider: opencode-go
  model: deepseek-v4-flash
```

**Total cost:** $20 (primary) + $10 (fallback) = $30/month

---

## OpenCode Go Investigation (Forge Task)

**Need to verify:**
1. DeepSeek V4 Pro pricing (per 1M tokens)
2. Kimi 2.7 pricing (per 1M tokens)
3. Monthly cost estimate for 50 audits + 500 builds

**Estimated costs (conservative):**
- DeepSeek V4 Pro: $0.26 input / $0.65 output
- Kimi 2.7: $0.20 input / $0.50 output (estimated)

**Monthly calculation:**
- Audits: 50 × 10K output × $0.65/M = $32.50
- Builds: 500 × 5K output × $0.65/M = $162.50
- **Total:** $195/month (token-based)
- **+ Subscription:** $10/month
- **Grand Total:** $205/month

**Ollama is still cheaper:** $20 vs $205

---

## Decision Framework

### If Ollama Quality ≥ GLM 5.2
**Recommendation:** Migrate to Ollama Cloud
- Cost: $20/month
- Savings: ~$930/month vs ZAI

### If Ollama Quality < GLM 5.2
**Recommendation:** Use OpenCode Go
- Cost: $205/month
- Savings: ~$745/month vs ZAI

### If Ollama Hits Pro Limits
**Recommendation:** Hybrid + OpenCode Go fallback
- Cost: $30/month
- Redundancy ensures no downtime

---

## Urgent Action Items

**Before Z.AI cancellation (next month):**

1. **Week 1:** Test Ollama quality (Forge task)
   - Run 10 audit tests
   - Compare to GLM 5.2
   - Check Pro limits

2. **Week 2:** Configure new provider (Forge task)
   - Update config.yaml
   - Test all endpoints
   - Monitor usage

3. **Week 3:** Cancel Z.AI subscription
   - Verify no billing overlaps
   - Confirm new provider stable

---

## Configuration Templates

### Ollama Cloud Only
```yaml
model:
  default: deepseek-v4-flash
  provider: ollama-cloud

providers:
  ollama-cloud:
    base_url: https://ollama.com/v1
    api_key: ${OLLAMA_API_KEY}
    type: openai_compatible

auxiliary:
  vision:
    provider: ollama-cloud
    model: qwen2.5-vision
```

### OpenCode Go Only
```yaml
model:
  default: deepseek-v4-flash
  provider: opencode-go

providers:
  opencode-go:
    api_key: ${OPENCODE_GO_API_KEY}
    base_url: https://api.opencode.com
    type: openai_compatible

auxiliary:
  vision:
    provider: opencode-go
    model: deepseek-v4-pro
```

### Hybrid (Ollama + OpenCode Go)
```yaml
model:
  default: deepseek-v4-flash
  provider: ollama-cloud

providers:
  ollama-cloud:
    base_url: https://ollama.com/v1
    api_key: ${OLLAMA_API_KEY}
    type: openai_compatible

  opencode-go:
    api_key: ${OPENCODE_GO_API_KEY}
    base_url: https://api.opencode.com
    type: openai_compatible

fallback_providers:
- provider: opencode-go
  model: deepseek-v4-flash

auxiliary:
  vision:
    provider: opencode-go
    model: deepseek-v4-pro
```

---

**Created:** July 6, 2026
**Status:** Real pricing received, need quality testing
**Priority:** CRITICAL (Z.AI canceling next month)
**Deadline:** 3 weeks to migrate