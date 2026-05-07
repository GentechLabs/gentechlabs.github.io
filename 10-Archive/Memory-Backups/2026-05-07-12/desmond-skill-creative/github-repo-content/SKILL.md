---
name: github-repo-content
description: "Generate multi-platform content packages from GitHub repos: Twitter threads, LinkedIn posts, blog writeups, and deployment analysis."
tags: [content, github, social-media, creative, technical-analysis]
---

# GitHub Repo → Content Package

## When to Use

Use when a user shares a GitHub repo URL and wants content created about it — social media posts, blog writeups, or technical analysis. Also triggers when evaluating a new open-source tool for the team's stack.

## Workflow

### 1. Extract Repo Data

```bash
# Fetch README and repo metadata
gh repo view OWNER/REPO --json name,description,stargazerCount,forkCount,licenseInfo,primaryLanguage,url
gh api repos/OWNER/REPO/readme --jq '.content' | base64 -d
```

If `gh` isn't available, use `browser_navigate` to load the GitHub page and extract content.

### 2. Analyze & Categorize

Identify:
- **What it does** (1-2 sentences)
- **Core capabilities** (3-5 bullet points)
- **Tech stack** (language, dependencies, models)
- **Competitive edge** (what makes it unique vs alternatives)
- **Use cases** (practical applications)

### 3. Generate Content Package

Create a single markdown file in `06-Content/` with:

#### Twitter/X Thread (5-7 tweets)
- **Tweet 1 (Hook):** Star count + what makes it interesting + thread indicator
- **Tweet 2-4:** Features, architecture, competitive comparison
- **Tweet 5:** Use cases / practical applications
- **Tweet 6:** CTA with GitHub link

Rules:
- Each tweet ≤ 280 chars
- Use emojis sparingly for visual breaks
- Number format: 1️⃣ 2️⃣ 3️⃣ or • bullets
- Include the GitHub URL in final tweet

#### LinkedIn Post (professional tone)
- Opening hook (1-2 sentences)
- What it does (3-5 bullets)
- Why it matters (1 paragraph)
- Hashtags: #AI #OpenSource #[relevant tags]
- Link at bottom

#### Blog Post Draft (800-1200 words)
- Title with star count
- Introduction (what problem it solves)
- Features deep dive
- Architecture / how it works
- Competitive comparison
- Getting started section
- Bottom line / verdict

### 4. Deployment Analysis (if applicable)

If the tool requires infrastructure:
- Identify compute requirements (GPU, CPU, RAM)
- Compare hosting options (serverless vs on-demand vs free tier)
- Provide cost estimates at different usage levels
- Recommend approach based on team's current setup

### 5. Save to Vault

```
06-Content/{tool-name}-{org}.md
```

Include metadata header:
```markdown
# {Tool Name} by {Org} — Content Package
**Created:** {date}
**Source:** {GitHub URL}
**Stars:** {count} | **Forks:** {count} | **License:** {license} | **Language:** {lang}
```

## Pitfalls

- **Don't hallucinate features.** Only include what's actually in the README/docs.
- **Check star count accuracy.** Use `gh repo view` or scrape the page.
- **Platform tone matters.** Twitter = casual/punchy, LinkedIn = professional, Blog = analytical.
- **Include limitations.** Don't just hype — note what the tool *doesn't* do well.
- **Cost estimates are directional.** GPU pricing changes frequently. Note the date of estimates.

## Example Trigger Phrases

- "Analyze this repo" + GitHub URL
- "Create content about [tool name]"
- "What do you think about [GitHub project]?"
- "Write a thread about this"
- "Break down this repo for me"
