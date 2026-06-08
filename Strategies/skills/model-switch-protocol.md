# Model Switch Protocol — Nous → OpenCode

## Description
One-time reminder for model provider refresh token expiration with fallback to OpenCode to prevent agent downtime.

## Current Cron Job
- **ID:** `1aa83242d9ca`
- **Name:** Model Switch Reminder —Nous → OpenCode
- **Schedule:** `once at 2026-04-23 10:00` (single run)

## Prompt Refactoring

### Before (Shell commands in prompt)
```
Steps:
1. Ensure OpenCode CLI installed: `npm install -g @openrouter/opencode-cli`
2. Ensure OPENROUTER_API_KEY is set in ~/.hermes/.env
3. Switch provider config to use OpenCode/Qwen
4. Verify with `hermes status`
```

### After (Clean human-readable prompt)

You are the Gentech DevOps Agent. Run the **model provider rotation reminder**.

**Task:**
Check if the Nous Portal refresh token is near expiry and prepare a fallback to OpenCode if needed.

**Execution:**
1. Verify the current model provider configuration in `~/.hermes/config.yml`
2. Check if `OPENROUTER_API_KEY` is set in `~/.hermes/.env`
3. Report the current status:
   - **Green:** Nous provider active, token valid for >24h → deliver nothing
   - **Yellow:** Token expires within 24h → report: "Nou\n[truncated]
   - **Red:** Token expired → switch to OpenCode/Qwen, verify, and report success

**Output Format:**
- Only deliver if action is needed (Yellow or Red)
- Single-paragraph summary for Telegram: status, action taken, next check date

> **Note:** This is a one-time check. After execution, the job is complete. No follow-up needed.
