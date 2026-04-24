---
name: gentech-labs-youtube-academy
description: "Structure GenTech Labs technical work into a branded weekly YouTube learning curriculum (Labs Academy)."
category: gentech
author: DMOB
date_created: "2026-04-24"
version: "1.0.0"
---

# GenTech Labs Academy Curriculum Builder

## Purpose
Turn raw technical outputs (audits, research, DeFi analysis) into a cohesive, professional YouTube/learning curriculum under the **Labs Academy** brand.

## Trigger
- Jordan asks to "make this into curriculum" or "Labs Academy" content
- New technical module ready for serialization into weekly lessons
- Need public-facing course map / syllabus from internal work

## Aesthetic Requirements
- **"Gritty B&W"** theme: monochrome palette, high contrast.
- No rainbow gradients. Think secure, austere, no-nonsense.
- Typography: bold sans-serif headers, monospaced code blocks.

## Curriculum Structure Template

### 1. Course Header
```
LABS ACADEMY // [SEASON/TOPIC]
[Module Number]: [Module Name]
Duration: ~[X] weeks
Level: Beginner | Intermediate | Advanced
Pre-reqs: [any]
```

### 2. Course Map (Per Module)
| Week | Topic | Deliverable | Instructor |
|------|-------|-------------|------------|
| 01 | [Title] | [Video / Handout / CTF] | [Agent] |
| 02 | ... | ... | ... |

### 3. Asset Generation Checklist
- [ ] Title cards (Gritty B&W)
- [ ] Lower thirds with agent names/roles
- [ ] Course map infographic (dark mode)
- [ ] Episode thumbnail template
- [ ] Companion Notion/Obsidian page with links

## Coordination Rules
1. **DMOB** (Security module): Extract findings → severity-ranked lessons → live exploit demos.
2. **YoYo** (DeFi module): Turn market analysis into case-study lessons → portfolio sim templates.
3. **Desmond** (Content polish): Branding, scripts, voiceover, thumbnail guidance.
4. **Green Room handoff**: Use `@YoYo @Desmond` when week map is ready for cross-review.

## Deliverable Format
- Obsidian note in `02-Labs/Academy/[Module]/`
- Summary posted to **HQ** when complete
- Canonical curriculum tracker as single Markdown table

## Example Module Template (copy/paste)
```markdown
## Module X: [Name]
### Learning Objectives
1. [Objective]
2. [Objective]

### Weekly Breakdown
#### Week 1: [Title]
- **Concept**: ...
- **Demo / Exercise**: ...
- **Homework**: ...

#### Week 2: ...
...
```
