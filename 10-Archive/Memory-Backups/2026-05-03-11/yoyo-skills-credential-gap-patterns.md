# Credential Gap Patterns — Session 2026-05-02

These error signatures were identified during the multi-agent health check. Each pattern correlates to a specific missing/invalid API key or configuration.

## Pattern A: Anthropic/Claude Credential Missing (DMOB)

**Error signature:**
```
RuntimeError: No Anthropic credentials found. Set ANTHROPIC_TOKEN or ANTHROPIC_API_KEY, run 'claude setup-token', or authenticate with 'claude /login'.
```

**Associated failure:** Cron job "Defi Milestone" crashes; agent logs show repeated `AuthError`.

**Trigger grep:**
```bash
grep -i "No Anthropic credentials found" /root/.hermes/profiles/*/logs/agent.log
```

**Fix recipe:**
```bash
# Option 1 — set token directly in profile .env
echo "ANTHROPIC_API_KEY=sk-ant-..." >> /root/.hermes/profiles/dmob/home/.env

# Option 2 — interactive setup
hermes --profile dmob auth anthropic
```

**Verification:**
```bash
# After restart, grep should return empty
grep -i "No Anthropic credentials" /root/.hermes/profiles/dmob/logs/agent.log
```

---

## Pattern B: ElevenLabs TTS 401 — Invalid API Key (Desmond)

**Error signature:**
```
elevenlabs.core.api_error.ApiError: status_code: 401, body: {'detail': {'status': 'invalid_api_key', 'message': 'Invalid API key'}}
```

**Associated failure:** Text-to-speech generation fails; Desmond cannot send voice replies. Error count in agent.log exceeds 100 quickly.

**Trigger grep:**
```bash
grep -c "elevenlabs.*401\|Invalid API key" /root/.hermes/profiles/desmond/logs/agent.log
```

**Fix recipe:**
```bash
# Set ELEVENLABS_API_KEY in Desmond's .env
echo "ELEVENLABS_API_KEY=$(cat /secure/keys/elevenlabs)" >> /root/.hermes/profiles/desmond/home/.env

# Restart Desmond gateway
hermes gateway stop --profile desmond && hermes gateway run --replace --profile desmond
```

**Verification:**
```bash
# TTS test — should produce audio file, no 401
hermes tts "test" --profile desmond
```

---

## Pattern C: Provider API Key Unset (Gentech)

**Error signature:**
```
RuntimeError: Provider 'opencode-go' is set in config.yaml but no API key was found. Set the OPENCODE_GO_API_KEY environment variable, or switch to a different provider with `hermes model`.
```

**Associated failure:** Gateway exits with code 1 repeatedly; systemd Restart=on-failure cycle if enabled; agent floods logs with connection fallback attempts.

**Trigger grep:**
```bash
grep -E "Provider '.*' is set in config.yaml but no API key was found" /root/.hermes/profiles/*/logs/*.log
```

**Fix recipe:**
```bash
# Either set the missing key
echo "OPENCODE_GO_API_KEY=og-..." >> /root/.hermes/profiles/gentech/home/.env

# Or switch provider to one with a key present
hermes model --profile gentech set stepfun/step-3.5-flash
```

**Verification:**
```bash
# Check gateway stays up > 5 minutes without "Exiting with code 1"
tail -f /root/.hermes/profiles/gentech/logs/gateway.log
```

---

## Pattern D: `.env` and `config.yaml` Completely Missing (All Agents)

**Symptom:** All four agents show zero `.env` and zero `config.yaml` in their profile `home/` directories. This indicates profile directory corruption or incomplete restore.

**Trigger check:**
```bash
for agent in yoyo dmob desmond gentech; do
  test -f /root/.hermes/profiles/$agent/home/.env && echo OK || echo "$agent .env MISSING"
  test -f /root/.hermes/profiles/$agent/home/.config/hermes/config.yaml && echo OK || echo "$agent config.yaml MISSING"
done
```

**Fix recipe:** Reconstruct from vault backups or redeploy profiles. DO NOT proceed without baseline config; all agents will fail.

---

## Cross-Pattern Notes

- Credential gaps cascade: missing key → repeated errors → gateway instability → Telegram disconnects → cron job failures.
- Always fix credential gaps BEFORE investigating secondary symptoms (Telegram drops, connection errors).
- After key injection, monitor for 10–15 minutes to ensure error flood subsides; use `tail -f agent.log` to watch real-time error rate decay.
