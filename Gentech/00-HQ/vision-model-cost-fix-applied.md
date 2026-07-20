# Vision Model Cost Fix — Applied 2026-07-06

## Issue

**Problem:** Vision tasks using GLM 5.2 (full model) → $125/month vision cost

**Root cause:** `auxiliary.vision` configured with expensive model

```yaml
# BEFORE (EXPENSIVE)
auxiliary:
  vision:
    provider: zai
    model: glm-5.2  # $1.00/1M output tokens
```

## Fix Applied

```bash
hermes config set auxiliary.vision.provider opencode-go
hermes config set auxiliary.vision.model deepseek-v4-flash
```

```yaml
# AFTER (95% CHEAPER)
auxiliary:
  vision:
    provider: opencode-go
    model: deepseek-v4-flash  # $0.05/1M output tokens
```

## Verification

✅ Config updated:
```bash
$ grep -A5 "auxiliary:" /root/.hermes/profiles/gentech/config.yaml
auxiliary:
  vision:
    provider: opencode-go
    model: deepseek-v4-flash
    base_url: ''
```

⚠️ **NOT VERIFIED:** OpenCode Go endpoint may still be wrong (`https://api.opencode.com` doesn't resolve)

**Test command:**
```bash
curl -X POST https://api.opencode.com/v1/vision \
  -H "Authorization: Bearer $OPENCODE_GO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-v4-flash",
    "image": "base64-encoded-image",
    "prompt": "Describe this image"
  }'
```

## Expected Savings

| Metric | Before | After | Savings |
|--------|--------|-------|---------|
| Model | GLM 5.2 | DeepSeek V4 Flash | 95% |
| Output cost | $1.00/1M | $0.05/1M | $0.95/1M |
| Monthly vision | $125 | $6.25 | **$118.75** |

## Blockers

1. ❌ **OpenCode Go endpoint wrong:** `https://api.opencode.com` → NXDOMAIN
2. ❌ **ZAI out of credits:** Can't fall back to GLM 5.2 if fix fails
3. ⚠️ **No vision test:** Can't verify fix without valid endpoint

## Recommendations

### Short Term (Today)
1. Test vision task with DeepSeek V4 Flash if endpoint works
2. If endpoint fails, keep current config and test Ollama Cloud instead

### Long Term (This Week)
1. Get correct OpenCode Go endpoint from documentation
2. Sign up for Ollama Cloud ($20/month unlimited)
3. Test Kimi 2.7 or DeepSeek V4 Pro for quality
4. Migrate all models to cheaper provider
5. Cancel Z.AI subscription (currently out of credits anyway)

---

**Applied by:** Gentech
**Date:** July 6, 2026, 21:15 UTC
**Status:** Config updated, not verified