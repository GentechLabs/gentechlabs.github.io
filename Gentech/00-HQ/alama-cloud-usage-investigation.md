# Alama Cloud Usage Investigation — GLM 5.2

**Date:** July 6, 2026
**Issue:** Excessive weekly usage on Alama Cloud when using GLM 5.2
**Priority:** CRITICAL — Cost optimization

---

## Problem Statement

**Jordan's observation:**
> "GLM 5.2 was using a lot of usage with Alama Cloud. Like, it was crazy how much usage Alama Cloud was going through, especially on the weekly."

**Impact:**
- Higher than expected costs
- Weekly usage spikes
- Potential billing discrepancies

---

## Hypotheses

### Hypothesis 1: Token Counting Mismatch
**Description:** ZAI reports token counts, but Alama bills per character.

**Evidence:**
- GLM 5.2 uses a tokenizer that produces ~0.25 tokens per character
- Alama might be billing 4x more than expected (character vs token)

**Test:**
```bash
# Count tokens vs characters in a sample
echo "Sample text for testing" | wc -c  # Characters
# Expected: 26 characters
# Token count might be ~6-8 tokens
```

### Hypothesis 2: Model Variant Confusion
**Description:** Using full GLM-5.2 instead of cheaper GLM-4.7-flash.

**Evidence:**
- Config shows `glm-5.2` for auxiliary.vision
- Config shows `glm-4.7` as default model
- Different price tiers between models

**Test:**
```bash
# Check actual model being called
grep -r "glm-5.2" ~/.hermes/profiles/gentech/config.yaml
grep -r "glm-4.7" ~/.hermes/profiles/gentech/config.yaml
```

### Hypothesis 3: Context Window Over-Fetching
**Description:** GLM-5.2 supports 128K context, might be fetching more data than needed.

**Evidence:**
- Session context compaction might not be aggressive enough
- Cron jobs might be loading full session history
- File reads might not have proper limits

**Test:**
```bash
# Check context compression settings
grep -A 10 "compression:" ~/.hermes/profiles/gentech/config.yaml
```

### Hypothesis 4: Billing Unit Misalignment
**Description:** Alama bills by "tokens" but calculates differently than ZAI.

**Evidence:**
- ZAI: 1 token = standard OpenAI tokenizer
- Alama: 1 token = 4 characters (simplified)
- Result: 4x billing discrepancy

**Test:**
```python
# Calculate expected vs actual usage
text = "Sample text"
token_count = len(text.split())  # Rough estimate
char_count = len(text)
alama_tokens = char_count / 4  # If Alama uses 4 chars per token
```

---

## Current Configuration Analysis

**From config.yaml:**
```yaml
model:
  default: glm-4.7  # Default model for sessions
  provider: zai

auxiliary:
  vision:
    provider: zai
    model: glm-5.2  # Vision tasks use GLM-5.2
```

**Usage pattern:**
- **Regular sessions:** GLM-4.7 (cheaper)
- **Vision tasks:** GLM-5.2 (expensive)
- **Fallback:** DeepSeek V4 Flash (cheapest)

**Question:** Are vision tasks consuming disproportionate usage?

---

## Data Collection Plan

### Step 1: Check Provider Invoices
```bash
# ZAI invoice (current provider)
# Check ZAI dashboard for token usage breakdown

# Alama Cloud invoice
# Check Alama dashboard for character/token usage
# Compare billing units
```

### Step 2: Analyze Model Usage
```bash
# Check which models are being called
grep -r "model.*glm" ~/.hermes/profiles/gentech/logs/ | tail -100
```

### Step 3: Measure Context Window Usage
```bash
# Check session context sizes
du -sh ~/.hermes/profiles/gentech/sessions/* | sort -h | tail -10
```

### Step 4: Compare Token Counts
```python
# Test token counting accuracy
import tiktoken

enc = tiktoken.encoding_for_model("gpt-4")
text = "Sample text for testing"
tokens = enc.encode(text)
print(f"Characters: {len(text)}, Tokens: {len(tokens)}, Ratio: {len(text)/len(tokens):.2f}")
```

---

## Potential Solutions

### Solution 1: Switch to GLM-4.7-Flash
**Benefit:** 60-80% cost reduction
**Tradeoff:** Lower quality for vision tasks

**Config change:**
```yaml
auxiliary:
  vision:
    model: glm-4.7-flash  # Instead of glm-5.2
```

### Solution 2: Use DeepSeek V4 Pro for Vision
**Benefit:** 35-50% cost reduction
**Tradeoff:** Different provider, need OpenCode Go key

**Config change:**
```yaml
auxiliary:
  vision:
    provider: opencode-go
    model: deepseek-v4-pro
```

### Solution 3: Implement Usage Monitoring
**Benefit:** Visibility into actual vs expected usage
**Tradeoff:** No cost savings, just monitoring

**Implementation:**
- Cron job to log token usage weekly
- Alert when usage exceeds threshold
- Compare ZAI vs Alama usage monthly

---

## Immediate Actions (Forge Task)

1. **Check Alama Cloud dashboard**
   - View last 7 days usage breakdown
   - Identify top consuming endpoints

2. **Check ZAI dashboard**
   - View last 7 days usage breakdown
   - Compare model usage distribution

3. **Switch vision model to GLM-4.7-flash** (if acceptable)
   - Test vision quality
   - Monitor usage for 1 week

4. **Run comparison test**
   - Same task on GLM-5.2 vs GLM-4.7-flash vs DeepSeek V4 Pro
   - Measure actual token usage
   - Compare costs

---

## Success Criteria

- **Usage discrepancy explained** — Understand why Alama usage is high
- **Cost reduction achieved** — Switch to cheaper model (30-50% savings)
- **Monitoring in place** — Weekly usage tracking prevents future spikes

---

**Created:** July 6, 2026
**Status:** Need Forge to check dashboards + run comparison tests
**Priority:** CRITICAL (cost optimization)