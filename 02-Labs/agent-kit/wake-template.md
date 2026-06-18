# GenTech Agent Kit — Wake Template
# Copy this to your agent's wake-up protocol

## Morning Digest (run on session start)

### 1. Identity Restore
```bash
# Load agent identity
source ~/.hermes/profiles/{profile}/identity.sh
echo "Good morning. I am {agent_name}."
```

### 2. Mess Hall Check
```bash
# Read brainstorm ideas
cat ~/vault/{vault_name}/11-Mess\ Hall/ideas.md | head -50
```

**Prompt user with top 2-3 ideas:**
> "Morning — here's what's in the Mess Hall:
> 1. {idea_1_title} — {one_line_summary}
> 2. {idea_2_title} — {one_line_summary}
> 
> Want to work on any of these today?"

### 3. System Health
```bash
# Check wallet balance
# Check cron jobs
# Check vault sync status
```

### 4. Market Check (if DeFi enabled)
```bash
# Check portfolio positions
# Check pending alerts
# Check macro events
```

### 5. Task Queue
```bash
# Check for pending tasks from yesterday
# Check cron job outputs
# Check platform notifications (EvoMap, Hive, etc.)
```

---

## Mess Hall Workflow

**When brainstorming:**
1. Capture idea in `11-Mess Hall/ideas.md`
2. Add metadata: date, source, status, priority
3. Connect to existing ideas (see "Connection" field)
4. Mark as Milestone if it could become core product

**When waking up:**
1. Read Mess Hall ideas
2. Prompt user with top 2-3 (rotate based on priority)
3. Ask: "Want to work on any of these today?"

**When user adds an idea:**
1. Capture immediately
2. Connect to related ideas
3. Suggest next steps
4. Ask: "Want me to start researching/building this?"

---

## Template Variables

Replace these with your agent's values:
- `{profile}` — Hermes profile name (e.g., "gentech")
- `{vault_name}` — Obsidian vault name (e.g., "gentech")
- `{agent_name}` — Your agent's name

---

## Example Wake Prompt

```
Good morning. I am GenTech.

Here's what's in the Mess Hall:

1. 🏆 GenTech DeFi Model — Fine-tuned financial AI for external access
2. 💳 Sana Integration — Banking/card for agent earnings
3. 🔐 Agent Rug 2.0 — Security platform for agents

Want to work on any of these today?
```
