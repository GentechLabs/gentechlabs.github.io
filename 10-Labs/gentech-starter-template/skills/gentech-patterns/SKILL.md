# GenTech Patterns Skill

> Core development patterns and conventions inherited from GenTech.
> Ship fast. Audit before shipping. CLARITY Act compliant.

## Development patterns

### 1. BUILD → AUDIT → VERIFY

```
1. BUILD the feature (any model)
2. AUDIT with GLM-5.2 (security, correctness, edge cases)
3. VERIFY with tests or live checks
4. SHIP
```

Never skip step 2 for: smart contracts, payment logic, permission systems.

### 2. x402 FIRST

Every API that costs compute to run should be behind x402 pay-per-call. If it's useful, it's billable.

- New endpoint? Wrap it with `withX402()`
- Existing endpoint? Audit for x402 compatibility
- Subscription model? Wire Q402

### 3. CLARITY ACT COMPLIANCE

Everything you build must pass the CLARITY Act compliance check:

- ✅ Agent identity (ERC-8004 registered)
- ✅ Security scan (Rugcheck v2 — 5 domains)
- ✅ Credit score (0-850 reputation)
- ✅ Payment integrity (x402 compliance)

### 4. VAULT SYNC

Write important state to the shared vault:

```bash
# Save decisions
echo "- [date] decided to build X because Y" >> vault/decisions.md

# Write handoffs
cat > vault/01-HANDOFFS/from-agent.md << 'EOF'
## From Agent — <date>
### Completed
- ...
EOF

# Push
git add . && git commit -m "agent: <summary>" && git push
```

### 5. BUILD QUEUE

Each agent maintains a build queue (json or markdown). Items have:

```json
{
  "id": 42,
  "name": "Feature name",
  "status": "pending|in_progress|shipped|blocked",
  "assigned_to": "agent-name",
  "difficulty": "easy|medium|hard",
  "priority": "low|medium|high|urgent"
}
```

## Communication protocol

When working alongside other agents:

1. **Handoffs**: `01-HANDOFFS/for-<agent>.md` → `from-<agent>.md`
2. **Decisions**: `00-HQ/decisions.md`
3. **Blockers**: Tag with `blocked_on:` in queue

## Memory

Save user preferences and environment facts in persistent memory.
Save procedures as skills.
Don't save task progress or session outcomes — the vault handles that.
