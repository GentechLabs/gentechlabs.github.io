# Auxiliary Provider Fallback Chain Behavior

## Context

When `auxiliary.<task>.provider: auto` is set (the default), Hermes uses `_resolve_auto()` from `agent/auxiliary_client.py` to select a backend for auxiliary tasks (vision, compression, web extraction, session search, etc.).

Understanding this chain is essential for:
- Debugging why vision tasks fail when the main model still works
- Designing cron-friendly configurations
- Intentional provider selection for reliability

## The Two-Step Resolution Algorithm

```python
# Simplified from _resolve_auto() in auxiliary_client.py

def _resolve_auto(main_runtime=None):
    # Step 1: Use main provider if it's configured and working
    main_provider = _read_main_provider()   # from config.yaml model.provider
    main_model = _read_main_model()         # from config.yaml model.default
    if main_provider and main_model and main_provider not in ("auto", ""):
        client = try_to_create_client(main_provider, main_model)
        if client is not None:
            return client, main_model   # ✅ SUCCESS — use main provider

    # Step 2: Fallback chain — try each until one works
    for label, try_fn in _get_provider_chain():
        client, model = try_fn()
        if client is not None:
            return client, model   # ✅ SUCCESS — first working provider

    return None, None  # ❌ Nothing available
```

### Step 1 — Main Provider Direct Use

If your config has:
```yaml
model:
  provider: opencode-go    # or any concrete provider (not "auto")
  default: stepfun/step-3.5-flash
```

Then **all** auxiliary tasks (including vision) will use OpenCode Go directly — **no fallback needed**.

This is the ideal state for cron reliability: pick an API-key provider and stick with it.

### Step 2 — Fallback Chain Order

If `model.provider: auto` (the Gentech default) or the main provider fails to initialize, the fallback chain runs:

1. **OpenRouter** — tries `OPENROUTER_API_KEY` if set
2. **Nous** — tries OAuth tokens (requires `hermes model` re-auth)
3. **Custom/local** — tries `OPENAI_BASE_URL` + `OPENAI_API_KEY` if configured
4. **API-key providers** — iterates all other providers in `HERMES_OVERLAYS`; first one with a valid env var wins

## The Vision Task Gotcha

**Scenario:** `model.provider: auto` with OPENCODE_GO_API_KEY available, but:

```yaml
auxiliary:
  vision:
    provider: nous   # ← explicit override
```

**What happens:**
- **Main provider resolution** (`_resolve_auto` Step 1): `auto` → falls through to Step 2 → OpenCode Go is selected ✅
- **Vision client resolution** (`resolve_provider_client("nous", ...)`: explicitly asks for `nous` → OAuth check → fails ❌

**Result:** Regular agent queries work; vision tasks fail with "Nous Portal not configured."

### Why explicit overrides bypass the main provider

The auxiliary-specific `provider` field is used directly in `resolve_provider_client(provider, ...)`. It does **not** go through `_resolve_auto()` unless set to `"auto"`.

From `agent/auxiliary_client.py` (auxiliary client factory):
```python
# For web_extract, compression, etc.
client, resolved = resolve_provider_client(
    configured_provider,   # could be "nous", "stepfun", "auto", ...
    configured_model or None,
    ...
)
```

So `provider: nous` will *always* try to useNous, regardless of what your main model uses.

## Diagnosing Which Provider Got Selected

### Check gateway logs
```bash
grep "Auxiliary auto-detect" ~/.hermes/logs/gateway.log | tail -10
```

Expected output:
```
Auxiliary auto-detect: using opencode-go (stepfun/step-3.5-flash)
```
or
```
Auxiliary auto-detect: using nous (google/gemini-3-flash-preview)
```

The provider name and model shown are what actually got chosen.

### Check current config
```bash
hermes config show | grep -A3 'auxiliary:'
```

Look for each `<task>.provider` setting.

### Runtime inspection (if tool available)
Some auxiliary clients expose their base URL:
```bash
hermes chat -q "What provider are you using for vision?" \
  --toolName=get_auxiliary_extra_body 2>/dev/null || true
```
(Only works if that tool is enabled and the agent is cooperative.)

## Fixing Mismatched Configurations

### Temporary fix — inherit main provider
If you need vision to work immediately and your main provider is healthy:
```bash
hermes config set auxiliary.vision.provider auto
hermes gateway restart   # or /reset in chat
```

Now vision uses the main provider (OpenCode Go in Gentech's case).

### Permanent fix for cron jobs — use API-key provider
```bash
# Set vision to StepFun (requires STEPFUN_API_KEY in .env)
hermes config set auxiliary.vision.provider stepfun
hermes config set auxiliary.vision.model stepfun/step-3.5-flash

# Or use OpenRouter (requires OPENROUTER_API_KEY)
hermes config set auxiliary.vision.provider openrouter
hermes config set auxiliary.vision.model google/gemini-3.1-flash
```

### Full switchaway from OAuth as main provider
```bash
# Run interactively
hermes model
# Select: OpenCode Go (or StepFun, DeepSeek, etc.)
# This updates config.yaml model.provider + model.default
```

After this, `model.provider` is concrete (not `auto`), so auxiliary `auto` tasks automatically use it without touching the fallback chain.

## Common Pitfalls

1. **"Main provider works but vision fails"** — caused by `auxiliary.vision.provider` set to an OAuth provider (nous). Change to `auto` or an API-key provider.

2. **"auto still picks Nous after OAuth logout"** — only happens if main provider is also `auto` AND all earlier fallbacks (OpenRouter, custom) fail. Ensure an API-key provider env var is set so the fallback chain terminates on a working provider.

3. **"Vision works manually but cron fails"** — manual chat inherits the TTY session's cached OAuth tokens; cron jobs run fresh and see expired tokens. Solution: don't use OAuth for cron-dependent features.

4. **"Provider keeps changing after config edit"** — the config file might be in the wrong profile. Check active profile with `hermes profile show`. Edit the correct `config.yaml` or use `--profile` flag.

5. **"Vision model not found after switching providers"** — each provider has its own model naming scheme:
   - Nous: `google/gemini-3-flash-preview`, `mistral-large-2`
   - StepFun: `stepfun/step-3.5-flash`
   - OpenCode Go: `kimi-k2.6`, `step-3.5-flash` (mapped internally)
   - OpenRouter: `anthropic/claude-sonnet-4`, `google/gemini-pro-1.5`
   Adjust `auxiliary.<task>.model` to match the provider's catalog.

## Reference: Provider Chain Definition

From `agent/auxiliary_client.py` → `_get_provider_chain()`:

```python
def _get_provider_chain():
    return [
        ("openrouter", _try_openrouter),
        ("nous", _try_nous),
        ("local/custom", _try_custom_endpoint),
        ("api-key", _resolve_api_key_provider),
    ]
```

Order is critical. OpenRouter gets first dibs after main provider;Nous is deliberately second (only OAuth-based aggregator). API-key providers are last, scanning all configured env vars.

## Related

- Main skill: `hermes-agent` → "Auxiliary provider fallback and OAuth dependencies"
- Non-interactive OAuth constraints: `references/oauth-non-interactive-constraints.md`
- Auth overlays: `/usr/local/lib/hermes-agent/hermes_cli/providers.py` → `HERMES_OVERLAYS`
- Resolution code: `agent/auxiliary_client.py` → `_resolve_auto()`, `resolve_provider_client()`
