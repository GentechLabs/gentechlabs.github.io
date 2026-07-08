---
name: gentech-session-startup
category: gentech
description: Forge gateway session-startup integration — auto-wake and context save
version: 1.0.0
platforms: [windows, linux, macos]
---

# GenTech Session-Startup Plugin

Auto-wake on first message after a fresh Hermes gateway session, and save
session summary to the GenTech vault on session close.

**Forge (laptop) specific.**

---

## Behavior

1. **Gateway start** → marker file is reset by companion startup script.
2. **First inbound message** → plugin detects missing/expired marker, prepends
   a wake-up prompt to the message text so the agent runs the wake-up protocol.
3. **Marker is then written** so subsequent messages in the same session skip
   the wake-up.
4. **Session end** → plugin appends a short session summary to the vault's
   working memory file.

---

## Files

- `plugins/gentech-session-startup/__init__.py` — plugin entry point
- `plugins/gentech-session-startup/session_startup.py` — core logic
- `plugins/gentech-session-startup/reset-marker.ps1` — Windows startup helper
- `plugins/gentech-session-startup/reset-marker.sh` — POSIX startup helper

---

## Windows Setup

Run once to enable:

```powershell
# Create plugin directory if needed
$plugins = "$env:LOCALAPPDATA\hermes\plugins\gentech-session-startup"
New-Item -ItemType Directory -Force -Path $plugins

# Copy plugin files (this plugin)
# Then set the vault path in config.yaml or env:
[Environment]::SetEnvironmentVariable("GENTECH_VAULT_DIR", "C:\Users\jhitm\Desktop\GenTech_Agency\gentech-vault-new", "User")

# Add reset-marker.ps1 to startup (Task Scheduler or shell profile)
```

---

## Manual Wake Trigger

If the plugin ever fails, send `/wake-up` — a fallback slash command that
forces the wake-up protocol regardless of marker state.

---

*Created: 2026-07-06 by Forge (kimi-k2.7-code)*
