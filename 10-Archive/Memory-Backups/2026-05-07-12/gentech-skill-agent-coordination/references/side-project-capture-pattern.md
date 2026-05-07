# Side Project Capture Pattern — Reference

**Skill:** `agent-coordination` → Section 2.6

## When to Use

Jordan shares a new idea/feature during an active sprint and explicitly says:
- "this is like a side project"
- "add this to the to-do list"
- "but let's focus on [hackathon/milestone] first"
- "we can revisit this later"

## Vault Structure Conventions

### Idea Document Location
`07-Ideas/{slugified-name}.md`

**Template:**
```markdown
# 💡 Idea: {Title}

**Date:** YYYY-MM-DD
**Author:** {Name}
**Category:** {Premium/Feature/Side Project}

---

## The Concept

{2–3 sentence description}

## Why It's Unique

{Bullet points on differentiation}

## Architecture

```{flow or code block showing components}
```

## Value Prop

| Feature | Free | Premium/Paid |
|---------|------|--------------|
| ...     | ...  | ...          |

## Next Steps

- [ ] {Action item}
- [ ] {Action item}

## Status

Backlog — P{Priority} — Not in active sprint. Revisit after {deadline}.

---

## Tags
`#idea` `#{domain}` `#{tech}`
```

### Working Memory Backlog Section

**Location:** `00-Working-Memory.md`, after all critical incident sections, before closing `---`.

**Format:**
```markdown
## Side Projects (Backlog — Low Priority)

- [ ] {Project Name} — {One-line description} (P{Priority})
  - {Technical approach summary}
  - Vault: `07-Ideas/{file}.md`
  - {Timing note: "Explore post-{deadline}"}
```

**Important:** Keep this section at the **bottom** of the file so it never interferes with active sprint tracking. Checkboxes unchecked (`[ ]`).

## Status Message Template (Telegram)

```markdown
**Side Project Captured — {Name}**

{One-sentence summary of what was added}

**What's added:**
- Vault: `07-Ideas/{slug}.md` — {key sections added}
- Working Memory: `00-Working-Memory.md` → "Side Projects" backlog, priority P{Priority}

Priority remains locked on:
1. {Current Sprint Item 1}
2. {Current Sprint Item 2}

This is just the beginning — we'll revisit after {deadline}.
```

## Common Pitfalls

| Pitfall | Why it's bad | Fix |
|---------|--------------|-----|
| Adding side project to active sprint items in Working Memory | Blurs priority, risks distraction | Keep side projects in separate section with unchecked boxes |
| Posting lengthy idea debates to HQ | Noisy, breaks synthesis-first rule | Discuss in Mess Hall first, then capture in vault |
| Forgetting to reaffirm current priorities in status | Jordan may think priorities shifted | Always list active sprint items at bottom of confirmation |
| Delaying vault capture (relying on memory) | Ideas get lost, no single source of truth | Write to vault *before* sending Telegram status |

## Related Vault Paths

- Active sprint: `00-Working-Memory.md` (top sections only)
- Side projects: same file, bottom "Side Projects" section
- Idea details: `07-Ideas/{name}.md`
- Active project specs: `03-Projects/` or `02-Labs/`

## Example Session (May 3, 2026)

Jordan requested: Travel agent visual immersion concept (3D street-level preview, MapLib/Cesium, agent-narrated tours).

Actions taken:
1. Updated `07-Ideas/travel-agent-crypto-layer.md` with "Visual Immersion Layer" section
2. Added to Working Memory Side Projects section: P2, unchecked, with vault ref
3. Sent Telegram confirmation with priority re-affirmation (Solana Frontier P0, Kite AI P1)
4. No vault sync (ob not configured), but files written directly
