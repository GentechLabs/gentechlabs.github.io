# Second Brain Contribution Rules

All Gentech agents (Gentech, YoYo, Dmob, Desmond) can contribute to the Obsidian vault at `/root/Documents/Obsidian Vault`.

## When to Contribute

Agents should write to the vault when:
- **Discovering new information** — market research, technical findings, security alerts
- **Having ideas** — project ideas, improvements, connections between topics
- **Completing work** — log what was done, results, lessons learned
- **Finding issues** — bugs, risks, opportunities worth noting
- **Learning something** — new tools, techniques, patterns discovered during work

## Where to Write

| Content Type | Folder | Example |
|-------------|--------|---------|
| Research findings | `03-Strategies/` | Market analysis, protocol deep-dives |
| Technical notes | `02-Labs/` | Setup guides, troubleshooting, architecture |
| Ideas & concepts | `07-Ideas/` | New project ideas, feature requests |
| Daily logs | `08-Activity log/` | What happened today, decisions made |
| Security findings | `06-Security/` | Vulnerability reports, audit notes |
| Learning notes | `05-Learning/` | Course notes, tutorials, skill progress |
| Entertainment/brand | `04-Entertainment/` | Brand assets, social content ideas |
| Agency planning | `01-Agency/` | Team coordination, goals, roadmap |

## Note Format

Use this template for new notes:

```markdown
# [Title]

**Author:** [Agent Name]  
**Date:** YYYY-MM-DD  
**Tags:** #tag1 #tag2

## Summary
Brief description of what this is about.

## Details
The actual content.

## Action Items
- [ ] Any follow-up needed
- [ ] Who should act on this

## Related
Links to other notes or resources.
```

## Rules

1. **Don't overwrite existing notes** — append or create new files
2. **Use descriptive filenames** — `YYYY-MM-DD-Topic.md` for daily logs, descriptive names for others
3. **Tag your notes** — use #tags for discoverability
4. **Cross-reference** — link to related notes using [[wikilinks]]
5. **Be concise** — bullet points over paragraphs
6. **Mark action items** — use `- [ ]` for tasks that need follow-up
7. **The vault syncs to Jordan's PC** — he'll see everything you write

## Automated Review

A cron job reviews the vault every 2 days and reports:
- Action items that need attention
- Outdated content for cleanup
- Upcoming deadlines
- Completed work that should be marked done
