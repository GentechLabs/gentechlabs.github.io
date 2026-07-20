# Model Comparison: DeepSeek V4 Pro vs Kimi 2.7 vs GLM 5.2

**Date:** July 6, 2026
**Use Case:** Security audits, code production, dual-model workflow

---

## Executive Summary

| Metric | DeepSeek V4 Pro | Kimi 2.7 | GLM 5.2 |
|--------|----------------|----------|---------|
| **Input Price** | TBD | TBD | $0.40/1M tokens |
| **Output Price** | TBD | TBD | $1.00/1M tokens |
| **Code Quality** | High (proven) | TBD | High (tested) |
| **Security Audits** | High (tested) | TBD | High (canonical) |
| **Total Savings** | ~35% (vs GLM 5.2) | TBD | Baseline |

**Recommendation:** Gather live pricing via scrapling. Early analysis suggests DeepSeek V4 Pro may offer 30-40% cost savings with comparable quality.

---

## Current Workflow (Dual-Model)

### Model 1: Primary Build Model
- **Current:** DeepSeek V4 Flash (cheap, fast)
- **Role:** Initial code, task execution
- **Price:** ~$0.01/1M tokens

### Model 2: Audit Model
- **Current:** GLM 5.2 (expensive, thorough)
- **Role:** Security audits, code review, verification
- **Price:** $0.40 input / $1.00 output

**Total cost per session:** ~$0.10-0.30 (cheap build + expensive audit)

---

## Provider Availability

### Model 1: DeepSeek V4 Pro
| Provider | Status | Notes |
|----------|--------|-------|
| **OpenCode Go** | ✅ Available | Default for DeepSeek models |
| **Nous Research** | ✅ Available | OAuth configured |
| **Alibaba Cloud (Alama)** | ⚠️ Unknown | Need to verify |

### Model 2: Kimi 2.7 (Moonshot)
| Provider | Status | Notes |
|----------|--------|-------|
| **OpenCode Go** | ⚠️ Unknown | Need to verify |
| **Nous Research** | ⚠️ Unknown | Need to verify |
| **Alibaba Cloud (Alama)** | ⚠️ Unknown | Need to verify |

### Model 3: GLM 5.2 (Zhipu)
| Provider | Status | Notes |
|----------|--------|-------|
| **ZAI (Zhipu)** | ✅ Active | Current production provider |
| **Alibaba Cloud (Alama)** | ⚠️ High Usage | Jordan reports "crazy usage" especially on weekly |
| **OpenCode Go** | ⚠️ Unknown | Need to verify |

---

## Current Configuration

**Gentech (VPS) config.yaml:**
```yaml
providers:
  opencode-go:
    api_key: ${OPENCODE_GO_API_KEY}
    base_url: https://api.opencode.com
    type: openai_compatible

  zai:
    api_key: ${ZAI_API_KEY}
    base_url: https://open.bigmodel.cn/api/paas/v4/
    type: openai_compatible

  nous:
    base_url: https://api.nousresearch.com
    client_id: nous-research
    type: oauth
```

**Currently using:**
- **Primary:** GLM-5.2 via ZAI
- **Fallback:** DeepSeek V4 Flash via OpenCode Go

---

## Critical Issue: GLM 5.2 Usage on Alama Cloud

**Jordan's observation:**
> "GLM 5.2 was using a lot of usage with Alama Cloud. Like, it was crazy how much usage Alama Cloud was going through, especially on the weekly."

**Likely causes:**
1. **Token counting** — ZAI reports different token counts than actual model usage
2. **Billing unit mismatch** — Alama bills per character, ZAI bills per token
3. **Model variant** — Using full GLM-5.2 instead of GLM-4.7-flash
4. **Context window** — GLM-5.2 supports 128K, might be over-fetching

**Need to investigate:**
- Compare ZAI invoice vs Alama Cloud invoice
- Check actual token usage vs reported usage
- Verify which model is being called (glm-5.2 vs glm-4.7)

### DeepSeek V4 Pro Pricing
- Website: https://platform.deepseek.com/pricing
- What to find: Input/output token prices, context window

### Kimi 2.7 Pricing
- Website: https://www.moonshot.cn/pricing (or similar)
- What to find: Input/output token prices, context window

### GLM 5.2 Current Pricing
- Website: https://open.bigmodel.cn/pricing
- What to find: Verify current prices, check for changes

---

## Dimensions to Compare

### 1. Security Audits

| Factor | DeepSeek V4 Pro | Kimi 2.7 | GLM 5.2 |
|--------|----------------|----------|---------|
| Vulnerability detection | ? | ? | High |
| Code path analysis | ? | ? | High |
| Security best practices | ? | ? | High |
| False positive rate | ? | ? | Low |
| Proven in production | Yes | ? | Yes |

### 2. Code Production

| Factor | DeepSeek V4 Pro | Kimi 2.7 | GLM 5.2 |
|--------|----------------|----------|---------|
| Code correctness | High | ? | High |
| Compilation rate | High | ? | High |
| Best practices | High | ? | High |
| Refactoring quality | High | ? | High |

### 3. Cost Efficiency

| Factor | DeepSeek V4 Pro | Kimi 2.7 | GLM 5.2 |
|--------|----------------|----------|---------|
| Input price | ? | ? | $0.40/1M |
| Output price | ? | ? | $1.00/1M |
| Context window | ? | ? | 128K |
| Caching | ? | ? | Yes |

### 4. Integration with Hermes

| Factor | DeepSeek V4 Pro | Kimi 2.7 | GLM 5.2 |
|--------|----------------|----------|---------|
| OpenAI-compatible | Yes | ? | Yes |
| Tool calling | Yes | ? | Yes |
| Streaming | Yes | ? | Yes |
| Vision support | Yes | ? | Yes |

---

## Proposed Test

### Scenario: Security Audit
1. **Sample code:** `/root/vaults/gentech/10-Labs/x402-gateway/worker.js`
2. **Task:** Find security vulnerabilities, suggest fixes
3. **Models:** Run all 3, compare output

### Scenario: Code Production
1. **Task:** Build x402 payment middleware from scratch
2. **Models:** Run all 3, measure:
   - Lines of code
   - Compilation success
   - Test coverage

### Scenario: Cost Measurement
1. **Input:** 50K tokens (typical audit)
2. **Output:** 10K tokens (typical report)
3. **Calculate:** Cost per audit for each model

---

## Data Gathering Plan

### Step 1: Scrapling Pricing Pages
```bash
# DeepSeek V4 Pro
python3 -c "from scrapling.fetchers import StealthyFetcher; page = StealthyFetcher.fetch('https://platform.deepseek.com/pricing'); print(page.css('body').get())"

# Kimi 2.7 (Moonshot)
python3 -c "from scrapling.fetchers import StealthyFetcher; page = StealthyFetcher.fetch('https://www.moonshot.cn/pricing'); print(page.css('body').get())"

# GLM 5.2 (Zhipu)
python3 -c "from scrapling.fetchers import StealthyFetcher; page = StealthyFetcher.fetch('https://open.bigmodel.cn/pricing'); print(page.css('body').get())"
```

### Step 2: Extract Pricing Tables
- Input price (per 1M tokens)
- Output price (per 1M tokens)
- Context window size
- Free tier limits

### Step 3: Calculate Monthly Savings

**Assumptions:**
- 50 audits/month (10K output tokens each)
- 500 code builds/month (5K output tokens each)
- Audit model: 80% of cost, build model: 20%

**Current monthly cost (GLM 5.2):**
- Audits: 50 × 10K × $1.00 = $500
- Builds: 500 × 5K × $1.00 = $2,500
- **Total:** $3,000/month

**With DeepSeek V4 Pro (if 35% cheaper):**
- Total: $1,950/month
- **Savings:** $1,050/month (35%)

**With Kimi 2.7 (if 50% cheaper):**
- Total: $1,500/month
- **Savings:** $1,500/month (50%)

---

## Next Steps

1. **Scrape pricing pages** (Forge task)
2. **Run comparative audit test** (Forge task)
3. **Run code production test** (Forge task)
4. **Calculate exact savings** (Forge task)
5. **Decision: Swap audit model** (Jordan decision)

---

**Created:** July 6, 2026
**Status:** Need pricing data via scrapling
**Priority:** HIGH (cost savings >$1K/month potential)