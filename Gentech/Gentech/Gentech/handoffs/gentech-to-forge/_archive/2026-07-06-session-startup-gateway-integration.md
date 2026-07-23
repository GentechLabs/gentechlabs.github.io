# Forge Handoff — Session-Startup Gateway Integration

**From:** Gentech (VPS)
**To:** Forge (Desktop)
**Created:** July 6, 2026
**Priority:** HIGH

---

## Problem

Jordan loses context when jumping between groups. Wake-up protocol doesn't auto-trigger, so brainstorming gets lost.

---

## Solution Installed ✅

**Behavioral Fixes v1.1** — 11 of 12 issues fixed:
- session-startup skill ✅
- message-length-discipline skill ✅
- vault-first-research skill ✅
- install.sh ✅
- verify.sh ✅
- README ✅

---

## What Forge Needs to Do

### Task 1: Configure Gateway Auto-Wake (15 min)

**File:** Gateway startup script (location depends on your Hermes setup)

**Action:** Reset session marker on gateway restart

```bash
# Add to gateway startup script
rm -f ~/.hermes/profiles/gentech/.session-startup-marker

# Or create fresh marker
echo "$(date +%s)" > ~/.hermes/profiles/gentech/.session-startup-marker
```

**Verification:**
```bash
# After gateway restart, check marker exists
ls -la ~/.hermes/profiles/gentech/.session-startup-marker
```

---

### Task 2: Configure First-Message Handler (30 min)

**Location:** Agent response handler (depends on your Hermes gateway configuration)

**Action:** Auto-wake on fresh sessions

```python
# At start of every message handler
from hermes_tools import read_file

def check_fresh_session():
    MARKER_PATH = "/root/.hermes/profiles/gentech/.session-startup-marker"
    GATEWAY_START = get_gateway_start_time()  # Implement this
    
    if not os.path.exists(MARKER_PATH):
        return True
    
    marker_ts = float(open(MARKER_PATH).read())
    return (GATEWAY_START - marker_ts) > 3600

def run_auto_wake():
    # Run wake-up protocol
    briefing = read_file("/root/vaults/gentech/00-BRIEFING.md")
    working_memory = read_file("/root/vaults/gentech/00-Working-Memory.md")
    
    # Check handoffs
    # Check deadlines
    # Format response
    
    return "Back online. Ready to work."

# In message handler:
if check_fresh_session():
    wake_up = run_auto_wake()
    # Prepend wake_up to agent response
```

---

### Task 3: Configure Session-Close Vault Save (30 min)

**Location:** Agent response handler / session manager

**Action:** Save context when session closes

```python
def on_session_close():
    # Save current context to vault
    working_memory = read_file("/root/vaults/gentech/00-Working-Memory.md")
    
    # Append session summary
    with open(working_memory, 'a') as f:
        f.write(f"\n## Session {datetime.now().isoformat()}\n")
        f.write("- Context saved automatically\n")
        f.write("- Next: [pending work]\n")
```

**Trigger:**
- Daily reset at 5:55 AM ET (already handled by session-hygiene cron)
- User sends `/new` command
- Context fills up (90%+ token limit)

---

### Task 4: Test in Production (20 min)

**Test 1: Fresh Session Wake-Up**
```bash
# Delete marker
rm ~/.hermes/profiles/gentech/.session-startup-marker

# Send message to agent
# Expected: "Back online. Ready to work." BEFORE normal response
```

**Test 2: Session Continuation**
```bash
# Send second message immediately
# Expected: No wake-up message (marker exists)
```

**Test 3: Context Persistence**
```bash
# Check 00-Working-Memory.md
# Expected: Latest session summary saved
```

---

## Files Modified by Gentech

1. `/root/vaults/gentech/agent-kit-behavioral-fixes/install.sh`
2. `/root/vaults/gentech/agent-kit-behavioral-fixes/verify.sh`
3. `/root/vaults/gentech/agent-kit-behavioral-fixes/README.md`
4. `/root/.hermes/profiles/gentech/skills/session-startup/SKILL.md`
5. `/root/.hermes/profiles/gentech/skills/message-length-discipline/SKILL.md`
6. `/root/.hermes/profiles/gentech/skills/vault-first-research/SKILL.md`

---

## Expected Outcome

After Forge configures gateway:
1. Fresh sessions auto-wake with identity context
2. Agent reads BRIEFING.md + Working Memory + handoffs
3. No more "who am I" confusion
4. Context saved automatically on session close
5. No more lost brainstorming

---

## Troubleshooting

**Issue:** Wake-up runs on every message

**Fix:** Check marker file logic — should only wake if marker < gateway_start or marker doesn't exist

**Issue:** Marker file corrupted

**Fix:** Run `bash /root/vaults/gentech/agent-kit-behavioral-fixes/verify.sh` — will recreate marker

**Issue:** No gateway access to configure auto-wake

**Fix:** Manual fallback — call wake-up protocol via `/wake-up` command when context lost

---

## Notes

- Session-startup skill has file locking (fcntl) for concurrent sessions
- extract_pending and extract_deadlines now have full implementations
- Vault-first-research has input validation (sanitize_query)
- Message-length-discipline has working split/truncate functions

---

**Created:** July 6, 2026
**Status:** Ready for Forge to implement
**Estimated time:** 95 minutes (1h 35m)