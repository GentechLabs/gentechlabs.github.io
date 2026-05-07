# Smart Routing v2 — Execution Pattern (from 2026-05-07 session)

## Trigger
Jordan shares a link, image, or external reference in HQ.

## Flow
1. **Mess Hall entry** — Create `11-Mess Hall/YYYY-MM-DD/{topic}.md` with the shared content
2. **Delegate to specialists** — Use `delegate_task` to spawn parallel subagent analyses
3. **Consolidate** — Merge specialist takes into one unified HQ brief
4. **Deliver** — Post consolidated brief to Jordan in HQ

## delegate_task Template

```python
delegate_task(tasks=[
    {
        "goal": "You are YoYo, the DeFi/Strategies specialist for GenTech Labs. "
                "Analyze [shared content]. Provide [X] bullet points on [angle]. "
                "Be concise.",
        "toolsets": ["web"]  # or [] for analysis-only
    },
    {
        "goal": "You are DMOB, the Code/Engineering specialist for GenTech Labs. "
                "Analyze [shared content]. Provide [X] bullet points on [angle]. "
                "Be concise.",
        "toolsets": []  # or ["web"] if research needed
    }
])
```

## Pitfalls

1. **Never answer solo first** — Jordan explicitly corrected this. Smart Routing v2 is mandatory when he shares links.
2. **Subagent interruption** — If delegate_task returns `status: "interrupted"`, retry once. If interrupted again, do the analysis yourself and note the interruption.
3. **Mess Hall file + delegation in parallel** — Don't wait for the file write to complete before delegating. Do both simultaneously.
4. **Keep briefs tight** — Jordan values concise, actionable output. 3-4 bullet points per specialist max.

## Mess Hall Entry Template

```markdown
# Mess Hall: [Topic]

**Link:** [URL]
**Shared by:** Jordan
**Time:** YYYY-MM-DD

## Content
[Raw tweet/link content]

## Routing
- **YoYo:** [angle]
- **DMOB:** [angle]
- **Desmond:** [angle]

## Status: Awaiting specialist input
```

## Consolidated HQ Brief Template

```markdown
**HQ Brief — [Topic]** 🧠

**Bottom line:** [One sentence]

**Key takeaways:**
- [Bullet 1]
- [Bullet 2]
- [Bullet 3]

Mess Hall logged. [Question or next step]
```
