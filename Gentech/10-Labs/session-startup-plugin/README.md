# Hermes Plugin — Session Startup Auto-Wake

A lightweight Hermes plugin that:

1. **Resets the session marker** when the gateway restarts.
2. **Auto-wakes on the first user message** after a fresh session by prepending a wake-up prompt.
3. **Saves session context** to `00-Working-Memory.md` on session close.
4. Exposes a **`/wake-up`** slash-command fallback.

---

## Install

Copy the `gentech-session-startup/` directory into the Hermes profile's plugins folder:

```bash
# Forge (laptop)
cp -r 10-Labs/session-startup-plugin \
  ~/.hermes/profiles/gentech/plugins/gentech-session-startup

# Gentech (VPS)
cp -r 10-Labs/session-startup-plugin \
  /root/.hermes/profiles/gentech/plugins/gentech-session-startup
```

Then activate it in `~/.hermes/profiles/gentech/config.yaml`:

```yaml
plugins:
  - name: gentech-session-startup
    path: gentech-session-startup
```

---

## Marker Reset

Before launching Hermes, clear the marker:

```powershell
# Windows (Forge)
.\reset-marker.ps1
& "C:\Program Files\Hermes\Hermes.exe"
```

```bash
# Linux (VPS)
rm -f ~/.hermes/profiles/gentech/.session-startup-marker
hermes gateway start
```

---

## Files

| File | Purpose |
|---|---|
| `__init__.py` | Plugin entry point |
| `session_startup.py` | Hook implementations |
| `reset-marker.ps1` | Windows marker reset helper |
| `SKILL.md` | Plugin manifest |
| `README.md` | This file |

---

## Slash Commands

- `/wake-up` — manually triggers the wake-up prompt and refreshes the marker.

---

## Vault Save

On session end the plugin appends a brief summary to:

```
00-Working-Memory.md
```

Format:

```markdown
## Session Summary — 2026-07-06T23:10:00Z
- gateway: gentech
- messages: 42
- topics: x402 deploy, session plugin
```

---

## Verification

Run the built-in test harness:

```bash
cd ~/.hermes/profiles/gentech/plugins/gentech-session-startup
python -m pytest tests/
```

(If tests don't exist, the ad-hoc verification script under `tests/verify_plugin.py` can be added.)
