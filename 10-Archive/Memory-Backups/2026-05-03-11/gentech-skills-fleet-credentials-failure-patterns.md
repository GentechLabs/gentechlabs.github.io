# Fleet-Wide Credential Failure Patterns

## Overview

When ALL agents exhibit the same provider error simultaneously, the root cause is almost always a shared credential issue, not per-agent misconfiguration.

## Canonical Patterns

### 1. ElevenLabs TTS Fleet-Wide Outage

**Error signature** (present in every agent's `errors.log`):
```text
elevenlabs.core.api_error.ApiError: status_code: 401, body: {'detail': {'status': 'invalid_api_key', 'message': 'Invalid API key'}}
File "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/elevenlabs/text_to_speech/client.py", line 223, in convert
```

**Detection**:
```bash
# Count 401 occurrences across all agent logs
grep -h "status_code: 401" ~/.hermes/profiles/*/logs/errors.log | wc -l
# Count agents affected
for agent in gentech yoyo dmob desmond; do
  if tail -50 ~/.hermes/profiles/$agent/logs/errors.log | grep -q "status_code: 401"; then
    echo "$agent: AFFECTED"
  fi
done
```

**Root causes**:
- API key expired or rotated in ElevenLabs dashboard
- Key revoked due to billing/billing alert
- Secrets file source-control sync replaced valid key with old placeholder
- Shared credential file (`~/.hermes/profiles/*/secrets/` or tool config) manually edited

**Remediation**:
1. Generate new ElevenLabs API key from dashboard
2. Replace in all agent secret locations (typically `~/.hermes/profiles/<agent>/secrets/elevenlabs` or environment `ELEVENLABS_API_KEY`)
3. Restart all gateways to clear cached auth:
   ```bash
   systemctl --user restart hermes-gateway-*
   ```
4. Validate: `tail -f ~/.hermes/profiles/<agent>/logs/errors.log` — no new 401s after first TTS call

---

### 2. Anthropic Credential Missing (DMOB-Specific but Repeatable)

**Error signature**:
```text
RuntimeError: No Anthropic credentials found. Set ANTHROPIC_TOKEN or ANTHROPIC_API_KEY...
```

**Detection**:
```bash
# Check DMOB .env for Anthropic keys
grep -E 'ANTHROPIC_(TOKEN|API_KEY)' ~/.hermes/profiles/dmob/.env
# If empty or commented, credential absent
```

**Root causes**:
- `.env` file truncated during backup/restore
- New agent profile created without copying base `.env` template
- Secrets rotation removed key without replacement

**Remediation**:
1. Obtain Anthropic API key from dashboard
2. Add to `~/.hermes/profiles/dmob/.env`:
   ```bash
   echo "ANTHROPIC_API_KEY=sk-ant-..." >> ~/.hermes/profiles/dmob/.env
   ```
3. Reload environment or restart DMOB gateway:
   ```bash
   systemctl --user restart hermes-gateway-dmob
   ```

---

## Shared Credential Source Checklist

If fleet-wide failure detected, audit these common shared sources:

| Location | Purpose | Check |
|----------|---------|-------|
| `~/.hermes/profiles/*/secrets/` | Agent-scoped secret files | `diff -r ~/.hermes/profiles/gentech/secrets ~/.hermes/profiles/yoyo/secrets` — should be identical for shared providers |
| `~/.hermes/profiles/*/.env` | Environment variables per profile | `grep -H 'ELEVENLABS\|ANTHROPIC\|OPENAI' ~/.hermes/profiles/*/.env` |
| `/usr/local/lib/hermes-agent/tools/*_tool.py` | Hardcoded defaults (rare) | `grep -n "api_key.*=" /usr/local/lib/hermes-agent/tools/tts_tool.py` |
| Orchestration-level secrets (if present) | Central secret store | Check vault or external secret manager used by deployment |

## Validation After Fix

1. Trigger a test TTS call on each agent (e.g., send a message that uses voice response)
2. Monitor error logs for 10 minutes:
   ```bash
   for agent in gentech yoyo dmob desmond; do
     echo "=== $agent ==="
     tail -30 ~/.hermes/profiles/$agent/logs/errors.log | grep -c "status_code: 401\|No Anthropic credentials"
   done
   ```
3. Expected: count = 0 for all agents

## Escalation

If credential rotation does not resolve:
- Check provider dashboard for additional restrictions (IP allowlist, region locks)
- Verify system clock is accurate (TLS handshake failures can masquerade as auth errors)
- Inspect network egress for firewall/proxy interference