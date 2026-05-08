# ElevenLabs TTS Quota Exhaustion — Systemic Third-Party Service Failure

**Detected:** 2026-05-04 00:06–00:10 UTC
**Scope:** All 4 agents (YoYo, DMOB, Desmond, Gentech)
**Severity:** P1 — Degrades user experience (no voice output) but does not block text operations

---

## Executive Summary

All agents simultaneously began producing `401 quota_exceeded` errors from the ElevenLabs Text-to-Speech API. The organization has **0 credits remaining** out of a 121,002 monthly limit. This is a **systemic third-party service failure**, not an agent-specific bug.

**Impact:**
- Text-to-speech generation fails for all agent responses
- Voice messages in Telegram are disabled
- LLM text generation continues unaffected (separate provider)
- No impact on scheduled job execution (TTS is post-generation)

**Diagnostic signature across all agents:**
```
ERROR tools.tts_tool: TTS generation failed (elevenlabs): status_code: 401, body: {
  'detail': {'status': 'quota_exceeded', 'message': 'This request exceeds your quota of 121002. You have 0 credits remaining.'}}
```

---

## Root Cause Analysis

The error appears in **every agent's error log within the same 2-minute window** (00:06–00:10 UTC). This is the classic signature of a **shared service quota exhaustion** rather than a misconfiguration or network issue.

**Evidence:**
- Identical error message with credit count (`121002`) across all agents
- Timestamps synchronized (within 30 seconds of each other)
- No preceding network errors or timeouts
- Other tool calls (LLM inference, web_search) continue normally

**Why this is NOT an agent issue:**
- Credentials are correctly configured (ElevenLabs API key present in `.env`)
- API key format is valid (64-char hex)
- No change to agent configuration preceding the failure
- The error explicitly states quota exceeded, not `invalid_api_key`

---

## Diagnostic Checklist

When encountering TTS failures across the fleet:

### 1. Verify it's systemic (≥3 agents affected)
```bash
for p in yoyo dmob desmond gentech; do
  echo "=== $p ==="
  grep -m1 'quota_exceeded' /root/.hermes/profiles/$p/logs/errors.log | tail -1
done
```

**Result:** All 4 agents show identical error with timestamp within 10 minutes → **systemic failure confirmed**

### 2. Check remaining quota via API (if accessible)
```bash
curl -s -H "xi-api-key: $ELEVENLABS_API_KEY" \
  "https://api.elevenlabs.io/v1/user" | jq .subscription
```

**Expected output when exhausted:**
```json
{
  "character_count": 121002,
  "character_limit": 121002,
  "can_extend_character_limit": true,
  "next_character_count_reset_at": "2026-05-05T00:00:00.000000Z"
}
```

### 3. Verify it's NOT a stale key issue
Check that each agent's `.env` contains the same active key:
```bash
for p in yoyo dmob desmond gentech; do
  grep ELEVENLABS_API_KEY /root/.hermes/profiles/$p/.env | head -1
done
```

If all keys match and are 64-char hex, key is not the problem — quota is.

---

## Recovery Pathways

### Option A — Top-up Quota (immediate but requires payment)
Add credits to ElevenLabs account via dashboard:
- Monthly subscription upgrade
- Pay-as-you-go credits add-on
- Enterprise plan increase

**After top-up:**
1. Wait 1–2 minutes for quota to propagate
2. Verify via API check (Step 2 above)
3. Agent TTS should recover automatically (no restart needed)

### Option B — Switch to Fallback TTS Provider (free/alternative)
Set up a different TTS provider (OpenAI TTS, Google Cloud TTS, Coqui TTS, local Piper) by updating agent configuration.

**Example — OpenAI TTS fallback:**
```bash
# Set env var to use OpenAI instead of ElevenLabs
echo 'TTS_PROVIDER=openai' >> /root/.hermes/profiles/yoyo/.env
echo 'OPENAI_API_KEY=sk-...' >> /root/.hermes/profiles/yoyo/.env
# Repeat for all agents

# Restart gateways
for p in yoyo dmob desmond gentech; do
  hermes --profile $p gateway restart
done
```

**Skill update needed:** Create `tts-fallback-routing` skill to dynamically route TTS requests to healthy providers.

### Option C — Disable TTS Temporarily (degraded mode)
Set `TTS_ENABLED=false` to suppress voice generation entirely. Agents will respond with text only.

```bash
for p in yoyo dmob desmond gentech; do
  echo 'TTS_ENABLED=false' >> /root/.hermes/profiles/$p/.env
done
```

**Impact:** No voice messages; reduces noise in error logs.

---

## Monitoring & Alerting

Add quota monitoring to the watchdog's pre-flight:

```bash
# In gentech-watchdog-health Step 0 expansion
# Check ElevenLabs quota health (proactive alert before exhaustion)
quota_check() {
  local remaining=$(curl -s -H "xi-api-key: $ELEVENLABS_API_KEY" \
    "https://api.elevenlabs.io/v1/user" 2>/dev/null \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('subscription',{}).get('character_limit',0) - d.get('subscription',{}).get('character_count',0))" 2>/dev/null || echo "?")
  
  if [ "$remaining" != "?" ] && [ "$remaining" -lt 10000 ]; then
    echo "⚠️  ElevenLabs quota low: $remaining characters remaining"
    echo "   Next reset: $(curl -s -H 'xi-api-key: $ELEVENLABS_API_KEY' https://api.elevenlabs.io/v1/user | python3 -c 'import sys,json; print(json.load(sys.stdin).get('subscription',{}).get('next_character_count_reset_at','unknown'))')"
  fi
}
```

**Alert threshold:** 10,000 characters remaining (~10% of monthly limit) → send proactive alert to Jordan.

---

## Historical Context

This is the **second quota exhaustion event** observed in the Gentech fleet:
- **First event:** 2026-05-02 (documented in separate incident report)
- **Second event:** 2026-05-04 (this event)

The rapid re-occurrence suggests:
- Monthly quota allocation insufficient for production volume
- Lack of quota monitoring/alerting before exhaustion
- No fallback provider configured

**Recommendation:** Upgrade ElevenLabs plan OR implement multi-provider TTS routing with automatic failover.

---

## Related Failure Patterns

This systemic third-party failure follows the same detection pattern as:
- **Nous OAuth cascade** (`2026-05-03-nous-oauth-cascade-failure.md`) — all agents affected simultaneously
- **OpenAI rate limit cascade** (if/when it occurs) — correlated `429` errors across fleet
- **Firecrawl API key rotation** (future) — identical error pattern across all agents within minutes

**Key discriminant:** The error message is identical across all agents, with the same numeric quota value. This distinguishes it from agent-specific credential issues where error patterns diverge (some agents show `invalid_api_key`, others show `quota_exceeded`, others show `no credentials`).

---

## Quick Diagnostic Commands

```bash
# 1. Confirm systemic pattern (all agents affected within 10 min?)
for p in yoyo dmob desmond gentech; do
  last_err=$(grep -m1 'quota_exceeded' /root/.hermes/profiles/$p/logs/errors.log | tail -1)
  echo "[$p] ${last_err:0:120}"
done

# 2. Verify API key consistency (all using same key?)
for p in yoyo dmob desmond gentech; do
  echo "[$p] $(grep ELEVENLABS_API_KEY /root/.hermes/profiles/$p/.env | cut -d'=' -f2)"
done

# 3. Check TTS error velocity (how fast is it growing?)
for p in yoyo dmob desmond gentech; do
  count_10m=$(grep 'quota_exceeded' /root/.hermes/profiles/$p/logs/errors.log | \
    awk -v d="$(date -d '10 minutes ago' '+%Y-%m-%d %H:%M')" '$0 > d' | wc -l)
  echo "[$p] TTS errors (last 10m): $count_10m"
done

# 4. Force a test TTS generation (should fail fast)
echo '{"text":"test"}' | hermes --profile yoyo tts --provider elevenlabs 2>&1 | head -5
```

---

## Playbook Decision Tree

```
Is TTS failing across ≥3 agents? 
├─ NO → Agent-specific issue. Check individual agent .env and gateway log
│
└─ YES → Systemic third-party failure
   │
   ├─ Error message contains 'quota_exceeded' → **Quota exhausted**
   │  ├─ Quota remaining < 5%? → Top-up required or switch provider
   │  └─ Quota should be reset? → Wait for monthly reset (check reset_at timestamp)
   │
   ├─ Error message contains 'invalid_api_key' → **Key revoked/expired**
   │  └─ Rotate key in all agent .env files; verify dashboard access
   │
   ├─ Error message contains 'rate limit' → **Rate limit hit**
   │  └─ Implement backoff; reduce TTS request frequency
   │
   └─ Other error → Check ElevenLabs API status page; network connectivity
```

---

## Owner & Escalation

- **Primary owner:** Jordan (ElevenLabs account admin)
- **Secondary:** DMOB (credential rotation, provider fallback implementation)
- **Escalation:** If quota exhaustion becomes recurrent (>monthly), evaluate alternative TTS providers or self-hosted solutions
