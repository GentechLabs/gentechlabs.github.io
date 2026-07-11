# GenTech V4 — Autonomous Agent Workflow

> Two agents. One queue. Zero idle time.
> Gentech 24/7 (VPS) · Forge heavy lifting (Desktop) · Jordan steering (Decisions)

---

## The Core Loop

```
┌──────────────────────────────────────────────────┐
│                  BUILD QUEUE                      │
│  build_queue.json — source of truth, sorted       │
│  Easy → Hard, priority, status, assigned_to       │
└────────────┬──────────────────────────┬───────────┘
             │                          │
     ┌───────▼───────┐         ┌───────▼───────┐
     │   GENTECH     │         │    FORGE      │
     │  24/7 VPS     │         │  Desktop/GPU  │
     │               │         │               │
     │ • MCP tools   │         │ • Local runs  │
     │ • API calls   │         │ • Heavy builds │
     │ • Research    │         │ • GPU work    │
     │ • Drafting    │         │ • UI testing  │
     │ • Cron jobs   │         │ • Game builds │
     └───────┬───────┘         └───────┬───────┘
             │                          │
             └──────────┬───────────────┘
                        │
              ┌─────────▼──────────┐
              │    STOPPING POINT  │
              │                    │
              │  Blocked?          │
              │  → Save to Mess    │
              │    Hall (brain)    │
              │  → Move to next    │
              │    task in queue   │
              │  → Wake-up Jordan  │
              │    when he's back  │
              └────────────────────┘
```

---

## The Build Queue (v4.0)

**Sorting:** Tasks are ordered Easy → Hard, then by priority. Easy wins first = momentum.

```json
{
  "items": [
    { "id": 38, "name": "Pika Subscription", "difficulty": "easy", "priority": "high" },
    { "id": 35, "name": "Circle Marketplace", "difficulty": "easy", "priority": "high" },
    { "id": 30, "name": "GoPlausible Auth", "difficulty": "easy", "priority": "high" },
    { "id": 34, "name": "Sourcegraph Drafting", "difficulty": "medium", "priority": "high" },
    { "id": 29, "name": "Algorand Mainnet Deploy", "difficulty": "medium", "priority": "urgent" },
    ...
  ]
}
```

**Statuses:**
- `pending` — Available for an agent to pick up
- `in_progress` — Currently being worked on by an agent
- `blocked` — Hit a stopping point (Jordan needed, missing resource, waiting)
- `completed` — Done
- `cancelled` — Won't do

**Assigned To:**
- `gentech` — VPS work, 24/7 capable
- `forge` — Desktop work, local runs, GPU
- `jordan` — Decisions, auth, submissions
- `auto` — Any available agent picks it up

---

## Autonomous Workflow (Gentech 24/7)

Every 30 minutes, Gentech runs the **Build Queue Tick**:

### Step 1: Check Queue
```python
queue = load_build_queue()
next_task = queue.find_next_available()
# available = status == "pending" AND assigned_to == "gentech" or "auto"
```

### Step 2: Pick by Difficulty
Sort available tasks: Easy → Medium → Hard.
```
Rule: Complete 1 easy task before starting 1 medium.
       Complete 2 medium tasks before starting 1 hard.
This keeps momentum high.
```

### Step 3: Work Until Stopping Point
Work on the task. Stopping points are:
- **Blocked** — Needs Jordan (auth, decision, wallet, submission)
- **Needs Forge** — Desktop-only work (GPU, local game build)
- **Needs Resource** — Missing API key, tool, credit
- **Complete** — Done

### Step 4: Save to Mess Hall (Brain)
At each stopping point, save a **brain note**:

```markdown
# Brain Note — 2026-07-10 14:30 UTC
# Task: #38 Pika Subscription

## What was done
- Researched Pika pricing ($8/mo Standard)
- Found Build-a-Brand, App Sizzle, Explainer skills
- Built Pika plugin for Agent Kit

## Stopping point
Jordan Needed → Sign up at pika.art/pricing

## Next steps when resumed
1. Run Build-a-Brand with GenTech product brief
2. Generate App Sizzle from GitHub URL
3. Create Explainer video

## State
- Plugin built ✅
- Account needed ❌
```

### Step 5: Move to Next Task
Mark current task as `blocked` or `awaiting_jordan`, pick next available task.

```python
queue.update_task(task_id, status="awaiting_jordan", notes="Need Jordan to sign up")
queue.start_next_available()
```

---

## Forge Workflow (Desktop/Heavy Lifting)

Forge picks up tasks when he's running on desktop:

| Task Type | Why Forge | Example |
|-----------|-----------|---------|
| **GPU compute** | Desktop has GPU | Model training, video gen |
| **Local builds** | Needs local env | Game builds, emulator dev |
| **Heavy compilation** | VPS limited | Rust/C++ builds |
| **UI testing** | Needs browser | Meta Ray-Ban testing |
| **Large data processing** | VPS storage limited | Dataset prep |

**Forge's wake-up check:**
```python
# On wake-up, Forge checks:
1. Is there a handoff from Gentech? (handoffs/gentech-to-forge/)
2. Are there tasks assigned to forge in build queue?
3. Does any task need local desktop execution?

Forge picks the highest-priority forge task and works it.
Same stopping-point logic as Gentech.
```

---

## Jordan's Role

Jordan only touches:

| Action | When | Time |
|--------|------|------|
| **Sign up / Auth** | Account needed (Pika, Circle, GoPlausible) | 5-10 min |
| **Submit forms** | External applications (grants, jobs) | 10-15 min |
| **Decisions** | Technical direction, which grant, which job | 5 min |
| **Wallet actions** | Deploy, fund, approve transactions | 5-10 min |
| **Review** | Review what agents built | 10 min |

**Jordan's flow when he sits down:**
1. Open Telegram → Gentech has a summary ready
2. See `awaiting_jordan` tasks in build queue
3. Work through them in order (Gentech sorted them Easy→Hard)
4. Approve, submit, sign — then agents take it from there

---

## Wake-Up Protocol (For Jordan)

When Jordan reconnects, the workflow agent (Gentech) automatically delivers:

```
📋 **Build Queue Update**
  ✅ Completed since last session: 3 (Pika plugin, Algorand plugin, Sourcegraph draft)
  ⏳ In progress: 2
  👑 Awaiting Jordan: 4 (Pika signup, Circle app, GoPlausible, Sourcegraph submit)

📝 **Brain Notes** — 3 new entries in 11-Mess Hall/
  → #38 Pika — Need signup
  → #35 Circle — Need form submit
  → #29 Algorand — Need GoPlausible auth

🎯 **Recommended Order** (Easy → Hard):
  1. Pika signup (2 min)
  2. Circle form (5 min)
  3. GoPlausible Discord auth (5 min)
  4. Sourcegraph submit (10 min)
```

---

## Mess Hall Brain Structure

Each brain note goes to `11-Mess Hall/agent-brain/YYYY-MM-DD/`:

```
11-Mess Hall/agent-brain/
├── 2026-07-10/
│   ├── 001-task38-pika-subscription.md
│   ├── 002-task35-circle-marketplace.md
│   └── 003-task29-algorand-mainnet.md
├── 2026-07-09/
│   ├── 001-task33-sourcegraph-draft.md
│   └── 002-task30-goplausible-auth.md
└── INDEX.md  (auto-generated summary of all brain notes)
```

Each note contains:
- Task ID and name
- What was done
- Stopping point
- State dump (files modified, env vars needed, links)
- Next steps for resumption

---

## Execution Rules

1. **Gentech never waits.** If blocked, save brain note, move to next task.
2. **No task is left without a brain note.** Every stopping point gets documented.
3. **Easy tasks first.** Complete all easy tasks before starting medium. Complete 2 medium before starting hard.
4. **Forge picks up where Gentech stops.** If Gentech reaches a stopping point that needs desktop, Forge gets a handoff.
5. **Jordan never sees a cold queue.** When he reconnects, there's always a summary ready.
6. **Build queue is the source of truth.** `build_queue.json` is the single point of control.
7. **Cron tick runs every 30 min.** Gentech checks for new available tasks and works them.
8. **No task takes more than 1 hour without a brain note.** Long tasks checkpoint every 60 min.