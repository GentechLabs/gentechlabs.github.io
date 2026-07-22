## 🤖 Forge Execution Protocol (Active Jul 5, 2026 — Updated Jul 8)

### SINGLE SOURCE OF TRUTH
The build queue lives at `/root/vaults/gentech/scripts/build_queue.json` v3.0.
- **Forge** reads the JSON directly — items with `assigned_to: forge` and `status: pending` are his active queue
- **No separate handoff documents needed** — handoff is the JSON itself
- **Status changes** flow back through the JSON: Forge updates his items' status as he completes them
- `build-queue.md` is a human-readable view, auto-generated from the JSON

### BUILD → AUDIT Pipeline

| Phase | Model | Provider | Purpose |
|-------|-------|----------|---------|
| **BUILD** | DeepSeek V4 Flash | Nous Research | First pass: code, docs, integration |
| **AUDIT + FIX** | GLM-5.2 (`z-ai/glm-5.2`) | Nous Research | Review quality, fix issues found, produce final artifact |

### Cost Strategy
- **Primary**: DeepSeek V4 Flash (free via Nous sub) — BUILD phase
- **Audit**: GLM-5.2 via Nous — AUDIT phase (complex tasks only)
- **Fallback**: Ollama Cloud GLM-4.7 (renews tomorrow) — BUILD + AUDIT

### Token Tracking Template

Every task in the build queue should include:

```yaml
cost:
  estimate: $X.XX
  model: glm-5.2
  tokens: ~XXX,XXX
  forge_threshold: YES/NO  # NO = Jordan-only (browser tasks)
complexity: Simple/Medium/Complex
```

| Complexity | Cost | Tokens | Examples |
|-----------|------|--------|---------|
| **Simple** | < $0.10 | < 50K | Quick configs, research |
| **Medium** | $0.10-0.30 | 50K-200K | BNPL integration, platform research, MCP integration |
| **Complex** | $0.30-1.00 | 200K-800K | Smart contracts, full builds, GLM-5.2 audits |

### Forge Threshold
- **NO** = Jordan-only (strategic, outreach, hackathon submissions, browser tasks)
- **YES** = Forge/Gentech (technical builds, infrastructure, documentation)

### Workflow

```
1. BUILD (DeepSeek V4 Flash)
   → Execute task
   → Output: draft artifact

2. AUDIT + FIX (GLM-5.2)
   → Review draft for quality + security
   → Apply fixes directly
   → Output: final artifact

3. TEST (forge / pytest)
   → Verify fixes didn't break anything
   → Output: passing tests

4. SYNC (git)
   → git add + commit + push
   → Copy to Obsidian vault if needed
```
