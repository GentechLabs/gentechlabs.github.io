---
agent: watchdog
date: 2026-05-02
session: gentech-health-check-yoyo-dmob-desmond-outage
summary: |
  Discovered cascading gateway shutdowns across YoYo, DMOB, Desmond (13:38–15:38 UTC).
  Root causes identified: ElevenLabs TTS API key expiration → 401 errors → gateways exited cleanly → systemd did not auto-restart due to Restart=on-failure policy.
  Cron tick.locks stale, scheduled jobs queued but not executing.

key_findings:
  - "gateway_state.json shows 'running' but ps finds no process → stale state after crash"
  - "Clean exit (code=0) bypasses systemd Restart=on-failure → manual restart required"
  - "ElevenLabs TTS 401 cascades to all agents using tool → single point of failure"
  - ".tick.lock age >60s indicates hung cron; gateway restart needed"
  - "YAML config error 'mapping values are not allowed' from mixed indentation/tabs"

diagnostic_commands:
  process_check: |
    ps aux | grep -E 'hermes|yoyo|dmob|desmond|gentech' | grep -v grep
  systemd_status: |
    systemctl --user status hermes-gateway-*.service
    systemctl --user show hermes-gateway-yoyo.service -p NRestarts -p Restart -p ActiveEnterTimestamp
  gateway_state_inspect: |
    cat /root/.hermes/profiles/yoyo/gateway_state.json | head -20
  log_triage_agent: |
    tail -50 /root/.hermes/profiles/yoyo/logs/agent.log
    tail -50 /root/.hermes/profiles/yoyo/logs/gateway.log
  log_triage_global: |
    tail -20 /root/.hermes/logs/errors.log
  cron_lock_age: |
    stat /root/.hermes/profiles/yoyo/cron/.tick.lock
  manual_restart: |
    systemctl --user start hermes-gateway-yoyo.service
  reset_failed_and_start: |
    systemctl --user reset-failed hermes-gateway-yoyo.service
    systemctl --user start hermes-gateway-yoyo.service
  clear_stale_lock: |
    rm /root/.hermes/profiles/yoyo/cron/.tick.lock
  yaml_validate: |
    python3 -c "import yaml; yaml.safe_load(open('/root/.hermes/profiles/yoyo/config.yaml'))"

elevenlabs_tts_failure_signature:
  log_pattern: "ERROR tools.tts_tool: TTS generation failed (elevenlabs): status_code: 401"
  affected_files:
    - /root/.hermes/profiles/yoyo/.env (ELEVENLABS_API_KEY)
    - /root/.hermes/profiles/dmob/.env
    - /root/.hermes/profiles/desmond/.env
  recovery: |
    1. Update ELEVENLABS_API_KEY in each agent's .env from secure vault
    2. Restart each gateway: systemctl --user restart hermes-gateway-<agent>.service
    3. Verify by tailing logs for successful TTS call or absence of 401 errors

systemd_clean_exit_bypass:
  detail: |
    Restart=on-failure only triggers on non-zero exit codes. When gateways exit with code=0
    (planned shutdown, --replace takeover, or graceful SIGTERM handling), systemd does not restart.
  evidence:
    - yoyo: "code=exited, status=0/SUCCESS" after 2026-05-02T13:38:26 SIGTERM
    - dmob: "code=exited, status=0/SUCCESS" after 2026-05-02T15:38:37 clean shutdown
    - desmond: "code=killed, signal=HUP" (also bypasses restart)
  mitigation_options:
    - Manual: systemctl --user start hermes-gateway-<agent>.service
    - Automatic: Edit service file to Restart=always (caution: may restart during planned maintenance)
    - Watchdog: Add cron that checks gateway_state.json and starts if not running

yaml_config_error_fallback:
  warning_message: "Warning: Failed to load config.yaml — falling back to .env / gateway.json values"
  common_causes:
    - Tabs instead of spaces for indentation
    - Mixed quote styles causing parser ambiguity
    - Unquoted colons or special characters in values
    - Missing space after colon in key-value pairs
  fix_procedure: |
    1. Run yamllint on config.yaml
    2. Convert all indentation to 2-space soft tabs
    3. Ensure all string values are explicitly quoted (prefer double quotes)
    4. Validate with: python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"
  location: /root/.hermes/profiles/yoyo/config.yaml (line 130 showed "  region: ''" — valid but check surrounding context)

telegram_connection_verification:
  expected_pattern: "\[Telegram\] Connected to Telegram \(polling mode\)"
  location: gateway.log (tail -20)
  fallback_ips: "Auto-discovered Telegram fallback IPs: 149.154.167.220" (indicates network issues resolved)

auth_status_check:
  command: "cat /root/.hermes/profiles/yoyo/auth.json | jq '.providers[].expired'"
  healthy: "false or absent"
  expired: "true → run 'hermes model' to re-authenticate"

---
