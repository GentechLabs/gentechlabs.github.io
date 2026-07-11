# Model Config Status — July 6, 2026

## VPS (Gentech) — Current Configuration

**Primary model:** GLM 4.7
**Provider:** Z.AI
**Fallback:** OpenCode Go (DeepSeek V4 Flash)

**Vision model:** DeepSeek V4 Flash
**Provider:** OpenCode Go

---

## Test Results

### 1. Z.AI (GLM 4.7) — ❌ Out of Credits

**Error:**
```json
{
  "error": {
    "code": "1113",
    "message": "余额不足或无可用资源包,请充值。"
  }
}
```

**Translation:** "Insufficient balance or no available resource packages, please recharge."

**Status:** API key valid, but no credits available

---

### 2. OpenCode Go (DeepSeek V4 Flash) — ❌ Endpoint Wrong

**Config:**
```yaml
opencode-go:
  api_key: ${OPENCODE_GO_API_KEY}
  base_url: https://api.opencode.com
```

**Issue:** `api.opencode.com` → NXDOMAIN (doesn't resolve)

**Status:** Cannot test; incorrect endpoint

---

### 3. Ollama Cloud — ❌ Not Configured

**Desktop (Forge):** ✅ Active
**VPS (Gentech):** ❌ Missing API key

**Status:** Not available on VPS

---

## Options

### Option A: Recharge Z.AI

1. Recharge Z.AI account
2. Wait for credit propagation
3. Test again
4. **Pros:** No config changes
5. **Cons:** Billing hit ($3,100/month at current rates)

---

### Option B: Get Ollama Cloud API Key for VPS

1. Sign up for Ollama Cloud ($20/month)
2. Add API key to `~/.hermes/profiles/gentech/.env`:
   ```bash
   OLLAMA_API_KEY=your_api_key_here
   ```
3. Update config:
   ```bash
   hermes config set model default ollama-cloud
   hermes config set model provider ollama
   hermes config set model model llama-3.1-70b
   ```
4. **Pros:** Unlimited usage, flat $20/month
5. **Cons:** Need to sign up

---

### Option C: Fix OpenCode Go Endpoint

1. Find correct endpoint from OpenCode Go documentation
2. Update config:
   ```bash
   hermes config set providers.opencode-go.base_url https://correct-endpoint.com
   ```
3. Test with DeepSeek V4 Flash
4. **Pros:** Cheaper than Z.AI
5. **Cons:** Need documentation, token-based billing

---

## Current Blockers

| Issue | Impact | Action |
|-------|--------|--------|
| Z.AI out of credits | Cannot use GLM 4.7 | Recharge or switch |
| OpenCode Go endpoint wrong | Cannot use fallback | Find correct endpoint |
| No Ollama Cloud key | Cannot use VPS unlimited | Sign up or get key |

---

## Recommended Path

**For VPS (Gentech):**
1. **Immediate:** Get Ollama Cloud API key ($20/month)
2. **Setup:** Configure Ollama as primary provider
3. **Fallback:** Keep OpenCode Go configured (fix endpoint later)

**For Desktop (Forge):**
1. **Keep:** Ollama Cloud active
2. **Configure:** Kimi 2.7 for complex tasks (if available)

---

## Vision Model Status

**Current:** DeepSeek V4 Flash (via OpenCode Go)
**Issue:** Endpoint wrong, so vision tasks may fail

**If vision breaks:**
- Switch to Ollama Cloud for vision
- Or fix OpenCode Go endpoint first

---

**Updated:** July 6, 2026, 23:45 UTC
**Next action:** Get Ollama Cloud API key or recharge Z.AI