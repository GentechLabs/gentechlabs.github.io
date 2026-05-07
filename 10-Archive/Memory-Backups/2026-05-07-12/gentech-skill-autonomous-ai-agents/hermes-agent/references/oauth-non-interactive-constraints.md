# OAuth Non-Interactive Constraints

## Problem

The `hermes model` command (OAuth device_code flow) **requires an interactive terminal** and cannot be run in non-interactive contexts:

```bash
# In a cron job or piped subprocess:
$ hermes model
Error: 'hermes model' requires an interactive terminal.
It cannot be run through a pipe or non-interactive subprocess.
Run it directly in your terminal instead.
```

This means:
- **Cron jobs cannot auto-renew OAuth tokens** — human intervention required
- **Automated maintenance scripts** must detect but not attempt to fix OAuth revocation
- **Scheduled vision tasks** fail if they depend on OAuth-based providers

## What actually happens

The `hermes model` command:
1. Opens a browser for the user to authenticate with the provider's OAuth portal
2. Waits for the user to complete the device_code flow
3. Stores the resulting tokens in `~/.hermes/auth.json` (or credential pool)

All three steps require a live TTY and user interaction. No headless alternative exists.

## Operational patterns

### Pattern 1 — Detect-only monitoring (cron-safe)

```bash
# Cron job: check OAuth health, report but don't fix
hermes status | grep -q "Refresh session has been revoked" && {
  echo "ALERT: Nous OAuth token revoked — manual 'hermes model' required"
  # Send notification to user (Telegram/Email)
  exit 1
}
```

### Pattern 2 — API-key fallback for zero-touch operation

Configure providers that use static API keys for auxiliary tasks:

```yaml
model:
  provider: opencode-go    # Uses OPENCODE_GO_API_KEY from .env
  default: kimi-k2.6

auxiliary:
  vision:
    provider: stepfun      # Uses STEPFUN_API_KEY — no OAuth
    model: stepfun/step-3.5-flash
```

Or use `auxiliary.vision.provider: auto` to inherit the main provider, which itself should be an API-key provider.

### Pattern 3 — Staggered manual re-auth

When managing multiple Hermes profiles (Gentech, YoYo, DMOB, Desmond):
- Flag all profiles as needing re-auth (OAuth revocation is fleet-wide)
- Re-authenticate one profile at a time manually
- Verify each before moving to the next
- Avoids coordinated downtime

## Provider auth type reference

| Provider | Auth type | Cron-friendly? |
|----------|-----------|----------------|
| OpenCode Go | API key (`OPENCODE_GO_API_KEY`) | ✅ Yes |
| StepFun | API key (`STEPFUN_API_KEY`) | ✅ Yes |
| OpenRouter | API key (`OPENROUTER_API_KEY`) | ✅ Yes |
| DeepSeek | API key (`DEEPSEEK_API_KEY`) | ✅ Yes |
| Nous Portal | OAuth device_code (`hermes model`) | ❌ No — needs TTY |
| OpenAI Codex | OAuth external | ❌ No |
| Qwen OAuth | OAuth external | ❌ No |
| MiniMax OAuth | OAuth external | ❌ No |

## Related

- Main skill section: `hermes-agent` → "Auxiliary provider fallback and OAuth dependencies"
- Recovery workflow: `references/brain-backup-credential-recovery.md` (for cascading Git failures)
- Provider auth types: `providers.py` → `HERMES_OVERLAYS[provider].auth_type`
