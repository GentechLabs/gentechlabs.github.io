---
name: hackathon-content-curation
description: "Curate and enhance technical reference documents for hackathon submissions: add strategic framing, cross-link competitive analysis, maintain submission-ready materials."
tags:
  - hackathon
  - content
  - strategy
  - competitive-analysis
  - vault
  - documentation
triggers:
  - Jordan shares a technical article or deep dive for a hackathon project
  - Jordan shares a GitHub repo with structured data (e.g., bug bounty platforms, competitive datasets)
  - Reviewing reference material before a hackathon submission deadline
  - Adding strategic context to existing technical documents
  - Cross-linking competitive landscape with project docs
  - Maintaining hackathon submission materials over time
  - Extracting structured data from GitHub repos for hackathon use
---

# Hackathon Content Curation

Workflow for reviewing, enhancing, and maintaining technical reference documents for hackathon submissions. Adds strategic framing, cross-links competitive analysis, and keeps materials submission-ready.

## When to Use

- Jordan shares a technical article, deep dive, or reference doc for a hackathon project
- Need to add "Why This Matters" strategic framing to existing content
- Cross-linking a new document to competitive landscape, hackathon plan, or related notes
- Maintaining action items with deadlines across hackathon materials
- Reviewing a document before submission deadline

## Workflow

### 1. Read the Source Material

If the source is a **GitHub repo with structured data** (e.g., tables in README.md, CSV/TSV files), extract the raw data first:

```bash
curl -s https://raw.githubusercontent.com/[owner]/[repo]/main/README.md
```

Use `grep`, `awk`, or `pandoc` to isolate tables or structured sections. Example:

```bash
# Extract a Markdown table from README.md
curl -s https://raw.githubusercontent.com/disclose/bug-bounty-platforms/main/README.md | \
grep -A 100 "^| Platform Name" | head -n 20
```

Convert to CSV/TSV if needed for further analysis:

```bash
# Convert Markdown table to CSV
echo "$TABLE_MARKDOWN" | pandoc -f markdown -t csv -o extracted-table.csv
```

```bash
# Check what exists in the vault
find "$VAULT" -name "*keyword*" -type f

# Read the document to review
cat "$VAULT/path/to/document.md"
```

### 2. Pull Context from Vault

Gather related materials to cross-reference:

```bash
# Hackathon plan
cat "$VAULT/02-Labs/Hackathons/Active/[hackathon-name].md"

# Competitive landscape
cat "$VAULT/02-Labs/Hackathons/Active/ai-agent-payments-landscape.md"  # or similar

# Related deep dives / research
find "$VAULT" -name "*[related-topic]*" -type f
```

### 3. Add Strategic Framing

Insert a "Why This Matters" section near the top of the document:

```markdown
## Why This Matters (Strategic Context)

[1-2 sentences on the competitive advantage or market position]

**See:** `[[competitive-landscape-doc]]` for full breakdown.
```

**Rules:**
- Keep it tight — 3-5 sentences max
- Reference specific competitive data (cluster scores, competitor names, market gaps)
- Link to the source doc with wikilink syntax

### 4. Add Cross-Reference Tables

If the document describes a technical model, add a mapping table to the project's architecture:

```markdown
## How It Maps to [Project Name]

| [Source Model] | [Our Equivalent] | What It Does |
|----------------|------------------|--------------|
| Layer A | Our Component A | Description |
| Layer B | Our Component B | Description |
```

This shows judges/users that the technical model validates our approach.

### 5. Update Action Items with Deadlines

```markdown
## Action Items

- [ ] Task 1
- [ ] Task 2

> **Deadline:** [Date] — [X] days from today.
```

### 6. Add Cross-Links at Bottom

```markdown
**See also:**
- `[[hackathon-plan]]` — Main submission plan
- `[[competitive-landscape]]` — Full competitive breakdown
- `[[related-deep-dive]]` — Related technical reference
```

### 7. Provide Strategic Summary

After updating, summarize what was added and the strategic read for the user:

```markdown
**What I updated:**
- Added "Why This Matters" section with [specific competitive angle]
- Cross-linked to [related docs]
- Updated action items with deadline

**Strategic read:**
[1-2 sentences on why this strengthens the submission]
```

## Vault Organization

- **Hackathon plans:** `02-Labs/Hackathons/Active/`
- **Technical deep dives:** `02-Labs/` (project-specific) or `06-Content/` (reference)
- **Competitive landscape:** `02-Labs/Hackathons/Active/` or `06-Content/Competitive Analysis/`
- **Cross-reference in:** Hackathon plan notes with `See also:` links

### 8. Extract Structured Data from GitHub Repos

When the source material is a GitHub repo with structured data (e.g., tables in README.md, CSV/TSV files, or GitHub issues):

#### Steps:
1. **Fetch Raw Data**:
   ```bash
   curl -s https://raw.githubusercontent.com/[owner]/[repo]/main/README.md
   ```
   - Use `grep`/`awk`/`jq`/`pandoc` to extract tables or structured sections.

2. **Convert to Markdown/CSV**:
   - Use `pandoc` or Python (`tabulate`, `csvkit`) to reformat tables for vault use:
     ```bash
     echo "$TABLE_MARKDOWN" | pandoc -f markdown -t gfm -o extracted-table.md
     ```

3. **Add Strategic Framing**:
   - Insert a **"Key Insights"** section summarizing relevance to the hackathon.
   - Cross-link to competitive landscape docs.

4. **Save to Vault**:
   ```bash
   cat > "$VAULT/02-Labs/Hackathons/Active/[hackathon]/DATA-[dataset-name].md" << 'EOF'
   # [Dataset Name] — Curated Extract

   ## Key Insights
   [1-2 sentences on strategic relevance to the hackathon or project]

   ## Extracted Data
   [Table or structured data]

   **See also:**
   - [[competitive-landscape]]
   - [[hackathon-plan]]
   EOF
   ```

#### Example Triggers:
- "Extract the bug bounty platforms table from this GitHub repo."
- "Curate this dataset for the hackathon submission."
- "Add this GitHub table to the vault with strategic framing."

- **Don't fabricate competitive data.** Only reference what's actually in the vault or sourced from research.
- **Keep strategic sections tight.** Judges want substance, not fluff. 3-5 sentences max.
- **Use wikilinks consistently.** `[[Note Name]]` for vault cross-references.
- **Update action item deadlines.** Stale deadlines erode trust in the document.
- **Don't restructure unless asked.** Add sections, don't rewrite existing content.

## Example Trigger Phrases

- "Add this to the vault"
- "Review this deep dive"
- "What are we looking at next?"
- "Cross-link this with the hackathon plan"
- "Update the submission materials"

## Related Skills

- `hackathon-project-scaffold` — Build phase (this skill is the curation/maintenance phase)
- `hackathon-tech-stack-evaluation` — Pre-build evaluation (this skill enhances existing docs)
- `github-repo-content` — Generates social content from repos (this skill enhances reference material)
- `obsidian` — Basic vault operations (this skill provides the strategic workflow)
