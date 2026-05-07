---
name: audit
domain: red-teaming
tags:
- audit
- class-level
- umbrella
status: active
version: 1.0.0
description: Consolidated umbrella for audit-* skills.
---
## Included Capabilities

### audit-prep-assistant
Prepares codebases for security review using Trail of Bits' checklist. Helps set review goals, runs static analysis tools, increases test coverage, removes dead code, ensures accessibility, and generates documentation (flowcharts, user stories, inline comments).
- **Full reference:** `references/audit-prep-assistant/SKILL.md`
- **Execution scripts:** `scripts/audit-prep-assistant/`

### audit-context-building
Enables ultra-granular, line-by-line code analysis to build deep architectural context before vulnerability or bug finding.
- **Full reference:** `references/audit-context-building/SKILL.md`
- **Execution scripts:** `scripts/audit-context-building/`

### audit-augmentation
Augments Trailmark code graphs with external audit findings from SARIF static analysis results and weAudit annotation files. Maps findings to graph nodes by file and line overlap, creates severity-based subgraphs, and enables cross-referencing findings with pre-analysis data (blast radius, taint, etc.). Use when projecting SARIF results onto a code graph, overlaying weAudit annotations, cross-referencing Semgrep or CodeQL findings with call graph data, or visualizing audit findings in the context of code structure.

- **Full reference:** `references/audit-augmentation/SKILL.md`
- **Execution scripts:** `scripts/audit-augmentation/`