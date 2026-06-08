# 🎬 Dmob → Desmond Content Pipeline

## How It Works

Dmob writes technical findings → Desmond translates into human content

## Content Types

| Dmob Output | Desmond Transforms Into |
|-------------|------------------------|
| Smart contract audit | 60-sec explainer video script |
| Vulnerability report | Thread breaking down the exploit |
| Code review / PR | Demo video showing the fix |
| Security finding | "What went wrong" case study |
| Gas optimization | Before/after comparison post |
| Token integration bug | Educational "how to avoid this" content |

## Video Formats (Desmond)

### 1. Security Explainer (60-90 sec)
```
HOOK: "This protocol lost $X million because of ONE line of code"
BODY: What happened, why it matters, what to watch for
CTA: "Follow for more DeFi security breakdowns"
```

### 2. Code Walkthrough (2-3 min)
```
SCREEN: Code snippet from Dmob's findings
NARRATION: "See this function? Here's why it's dangerous..."
VISUALS: Highlight the vulnerable line, show the exploit path
```

### 3. Before/After (30-45 sec)
```
LEFT: Vulnerable code
RIGHT: Fixed code
TEXT: "Dmob found this. Here's the fix."
```

### 4. Hot Take Reaction (60 sec)
```
FORMAT: Desmond reacting to Dmob's findings
STYLE: "So Dmob just audited this protocol and... 😬"
TONE: Informative but entertaining
```

## Script Template

```markdown
# Video Script: [Title]

**Source:** Dmob's [audit/review/finding] of [Protocol]
**Date:** YYYY-MM-DD
**Duration:** [X] seconds
**Platform:** TikTok / YouTube Shorts / Twitter

## Hook (first 3 seconds)
[Attention-grabbing line]

## Problem (10-15 seconds)
[What Dmob found, simplified]

## Why It Matters (10-15 seconds)
[Impact on regular users]

## Solution/Tip (10-15 seconds)
[What to do about it]

## CTA (3-5 seconds)
[Follow / Check the full audit / Link in bio]

## Notes for Production
- [Visual cues]
- [Code snippets to show]
- [Emphasis points]
```

## Trigger

Any vault note in `06-Security/` tagged with `#needs-content` triggers this pipeline. Desmond picks it up, writes a script, and puts it in `Entertainment/Scripts/`.

## Quality Bar

- Dmob's technical accuracy must be preserved
- Simplify without dumbing down
- Always credit the source (protocol, audit firm, etc.)
- Include risk level so viewers know severity
- Make it shareable — if someone wouldn't forward it, rewrite it
