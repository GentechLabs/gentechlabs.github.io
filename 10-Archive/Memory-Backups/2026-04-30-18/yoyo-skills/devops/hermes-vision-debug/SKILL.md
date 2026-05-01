---
name: hermes-vision-debug
description: Debug Hermes vision/photo analysis failures — trace the auxiliary client resolution chain, diagnose model normalization issues, and fix vision model routing for Nous Portal and other providers.
triggers:
  - vision analysis fails with 404
  - telegram photos not being analyzed
  - vision_analyze errors
  - image analysis returns empty or errors
---

# Hermes Vision Debugging

## Symptoms
- Telegram photos are received and cached (`~/.hermes/image_cache/`) but vision analysis fails
- `tools.vision_tools: Error analyzing image: Error code: 404` in `~/.hermes/logs/agent.log`
- `vision_analyze` tool returns errors or empty results

## Architecture
```
User sends photo → Telegram caches it → vision_analyze_tool()
  → async_call_llm(task="vision")
    → _resolve_task_provider_model("vision", ...)
    → resolve_vision_provider_client()
      → _PROVIDER_VISION_MODELS dict maps provider → vision model
      → _normalize_resolved_model() applies vendor prefix normalization
      → resolve_provider_client() creates the OpenAI client
```

## Key Files
- `agent/auxiliary_client.py` — provider resolution, `_PROVIDER_VISION_MODELS` dict, `_normalize_resolved_model()`
- `hermes_cli/model_normalize.py` — `normalize_model_for_provider()` adds vendor prefixes
- `tools/vision_tools.py` — `vision_analyze_tool()` entry point

## Debugging Steps

### 1. Check logs for the exact error
```bash
grep -i "vision\|photo\|image\|404" ~/.hermes/logs/agent.log | tail -20
grep -i "vision\|photo\|image" ~/.hermes/logs/errors.log | tail -20
```

### 2. Trace the vision model resolution
```python
from agent.auxiliary_client import resolve_vision_provider_client, _PROVIDER_VISION_MODELS
print('Vision model map:', _PROVIDER_VISION_MODELS)
provider, client, model = resolve_vision_provider_client()
print(f'Resolved: provider={provider}, model={model}, client={client is not None}')
```

### 3. Test the resolved model directly on the API
```python
from openai import OpenAI
from agent.auxiliary_client import _read_nous_auth, _nous_api_key, _nous_base_url

nous = _read_nous_auth()
client = OpenAI(api_key=_nous_api_key(nous), base_url=_nous_base_url())

# Test with a tiny base64 PNG
tiny_png = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=='
resp = client.chat.completions.create(
    model=model,
    messages=[{'role': 'user', 'content': [
        {'type': 'text', 'text': 'What color?'},
        {'type': 'image_url', 'image_url': {'url': f'data:image/png;base64,{tiny_png}'}}
    ]}],
    max_tokens=20
)
print(resp.choices[0].message.content)
```

### 4. Check for model name normalization issues
```python
from hermes_cli.model_normalize import normalize_model_for_provider
# Bare model names get vendor prefixes: "gemini-3-flash" → "google/gemini-3-flash"
print(normalize_model_for_provider('gemini-3-flash', 'nous'))
# Already-prefixed names pass through unchanged
print(normalize_model_for_provider('google/gemini-3-flash-preview', 'nous'))
```

## Known Bugs & Fixes

### Duplicate `_PROVIDER_VISION_MODELS` dict (syntax error)
The dict can end up defined twice, with the first never closing. Check for duplicate lines 198-199 in `auxiliary_client.py`. Remove the broken duplicate.

### Nous vision model normalization
- `gemini-3-flash` gets normalized to `google/gemini-3-flash` → **404 on Nous**
- `google/gemini-3-flash-preview` passes through normalization → **works on Nous**
- Fix: use `google/gemini-3-flash-preview` in `_PROVIDER_VISION_MODELS` for `nous`

### Model names that work on Nous Portal (tested)
| Model | Status |
|-------|--------|
| `gemini-3-flash` | ✅ bare name works |
| `google/gemini-3-flash-preview` | ✅ prefixed name works |
| `google/gemini-3-flash` | ❌ 404 — normalization artifact |
| `xiaomi/mimo-v2-omni` | ✅ works (returns None for some vision tasks) |

## After Fixing
Changes take effect on next Python import cycle. For live gateway sessions, the fix activates on next message. If needed: `hermes gateway restart` (may timeout if run from within the gateway session itself).
