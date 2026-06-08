# Queue Discipline Protocol

**Added:** Apr 17, 2026
**Status:** Active — all agents must follow

## The Rule

When Jordan sends messages while you're working on a task:

1. **Do NOT interrupt your current task** — keep going
2. **Do NOT peek at queued messages** — they can wait
3. **Finish your current task completely**
4. **Huddle in Green Room** (if coordination needed)
5. **Log to Mess Hall** (summary of what you did)
6. **THEN check the queue** for what Jordan sent

## Why

- Interrupting mid-task causes lost context and broken workflows
- Queued messages often contain context for the *next* task, not the current one
- Jordan sometimes sends "help" links or future ideas while we're working — those are for after, not during
- Second brain activity (Green Room + Mess Hall) ensures clean handoff before moving to the next thing

## What "Action Interrupted" Means

If you see this in your logs, it means the system received a new message while you were processing. Under this protocol:
- You do NOT act on the interrupted message immediately
- You finish your current response/tool chain
- You complete the Green Room + Mess Hall cycle
- You THEN address the queued message in your next turn

## Exception

Only interrupt if Jordan explicitly says something like:
- "Stop"
- "Drop that"
- "Actually, never mind"
- "Switch to [X]"

Everything else queues.

## Config

All agents should have in `config.yaml`:
```yaml
busy_input_mode: queue
```

Current status:
- Dmob: ✅ queue
- YoYo: ✅ queue
- Desmond: ✅ queue
- Gentech: ❌ needs config
