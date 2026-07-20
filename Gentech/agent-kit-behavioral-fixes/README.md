# Gentech Agent Kit — Behavioral Fixes v1.0

**Author:** Gentech Labs
**Date:** July 6, 2026
**License:** MIT

---

## What This Fixes

| Issue | Solution | Skill |
|-------|----------|-------|
| "Who am I?" confusion after gateway restart | Auto-wake on fresh sessions | session-startup |
| Messages get cut off mid-sentence | Enforce 1500-char limit | message-length-discipline |
| Duplicate research + unnecessary skill loading | Check vault first before external research | vault-first-research |

---

## Installation

### Prerequisites

- Skill files must be present in this package directory
- If installing from repository, ensure you cloned with submodules
- Hermes Agent profile directory exists at `~/.hermes/profiles/gentech/`

### Quick Install

```bash
cd /root/vaults/gentech/agent-kit-behavioral-fixes
bash install.sh
```

### Verify Installation

```bash
bash verify.sh
```

### Manual Install (Alternative)

If skills already exist in profile directory:

```bash
# Skills already exist at ~/.hermes/profiles/gentech/skills/
# Just run verify.sh to check installation
bash verify.sh
```

### Step 2: Configure Session Startup (Requires Gateway Integration)

**Note:** Session startup requires gateway-level integration. See `session-startup/SKILL.md` for implementation details.

**Manual setup:**

```python
# Create session-startup.py
import os
import time

MARKER_PATH = "~/.hermes/profiles/your-profile/.session-startup-marker"
GATEWAY_START = time.time()

def is_fresh_session():
    if not os.path.exists(os.path.expanduser(MARKER_PATH)):
        return True
    
    with open(os.path.expanduser(MARKER_PATH), 'r') as f:
        marker_ts = float(f.read().strip())
    
    return marker_ts < GATEWAY_START

# Then in your agent response handler:
if is_fresh_session():
    run_wake_up_protocol()
```

### Step 3: Configure Message Length Discipline

**Add to agent response handler:**

```python
def check_message_length(message: str, max_length: int = 1500) -> str:
    if len(message) <= max_length:
        return message
    
    # Truncate or split
    # See skill for implementation details
    return truncate_or_split(message, max_length)

# Before sending to user:
checked_message = check_message_length(response)
```

### Step 4: Configure Vault-First Research

**Add to all research workflows:**

```python
def check_vault_first(query: str) -> dict:
    # Search vault for existing research
    # See skill for implementation details
    pass

# Before web_search or skill_view:
vault_check = check_vault_first(query)
if not vault_check["found"]:
    # Only then proceed with external research
    web_search(query)
```

---

## Quick Start

### For Hermes Users (No Gateway Access)

If you can't modify gateway, implement **manual wake-up**:

1. **Start of every session**, run:
   ```
   Read 00-BRIEFING.md (identity)
   Read 00-Working-Memory.md (current state)
   Check handoffs folder for pending work
   ```

2. **Before every message**, check length:
   ```python
   if len(response) > 1500:
       truncate_or_split(response)
   ```

3. **Before every research**, check vault first:
   ```python
   if not in_vault(query):
       research_externally(query)
   ```

### For Gateway Owners (Full Integration)

1. Copy skills to profile
2. Implement session-startup.py
3. Add hooks to agent response handler
4. Test with manual trigger (see skill docs)

---

## Verification

### Test Session Startup

```bash
# Trigger fresh session
rm ~/.hermes/profiles/your-profile/.session-startup-marker

# Send message to agent
# Should see: "Back online. Build Queue: X. Ready to work."
```

### Test Message Length

```python
# Test length checker
msg = open('message.txt').read()
if len(msg) > 1500:
    print("❌ Too long")
```

### Test Vault-First Research

```python
# Test vault check
result = check_vault_first("Atelier marketplace")
# Expected: {"found": True, "source": "handoffs"}
```

---

## Skill Documentation

Each skill has full documentation:

| Skill | Documentation |
|-------|----------------|
| session-startup | [session-startup/SKILL.md](session-startup/SKILL.md) |
| message-length-discipline | [message-length-discipline/SKILL.md](message-length-discipline/SKILL.md) |
| vault-first-research | [vault-first-research/SKILL.md](vault-first-research/SKILL.md) |

---

## Pattern Reference

| Message Type | Max Chars | Split Strategy |
|--------------|-----------|----------------|
| Simple confirmation | 200 | No split needed |
| Status summary | 500 | No split needed |
| Detailed report | 1500 | Split by section |
| Multi-part checklist | 1000/part | Part 1 of 3... |

---

## Common Issues

### "Session startup doesn't trigger"

**Cause:** Gateway integration not configured

**Fix:** Implement session-startup.py in gateway startup handler

**Fallback:** Run manual wake-up at start of every session

### "Messages still getting cut off"

**Cause:** Message length check not in response handler

**Fix:** Add check_message_length() before sending to user

### "Still doing duplicate research"

**Cause:** Vault-first check not in research workflow

**Fix:** Add check_vault_first() before web_search or skill_view

---

## Integration With Other Skills

| This Skill | Pairs With |
|------------|------------|
| session-startup | wake-up-protocol, session-hygiene, agent-recovery |
| message-length-discipline | identity (frustration signal rule) |
| vault-first-research | pre-work-audit, session-hygiene |

---

## For Agent Kit v2 Distribution

To distribute as part of Agent Kit v2:

1. Package all 3 skills in `agent-kit/behavioral-fixes/`
2. Include installation script (`install.sh`)
3. Include verification script (`verify.sh`)
4. Document in Agent Kit README

---

## Version History

- **v1.0 (Jul 6, 2026):** Initial release
  - session-startup: Auto-wake on fresh sessions
  - message-length-discipline: 1500-char limit
  - vault-first-research: Check vault before external research

---

## License

MIT License — Free to use, modify, and distribute.

---

## Support

For questions or issues:
- Check skill documentation for troubleshooting
- See pattern reference tables for usage examples
- Refer to common issues section

**Built by Gentech Labs — Solo agent for GenTech Operations**