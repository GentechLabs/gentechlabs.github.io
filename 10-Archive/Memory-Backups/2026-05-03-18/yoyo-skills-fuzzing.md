---
name: fuzzing
domain: red-teaming
tags:
- fuzzing
- class-level
- umbrella
status: active
version: 1.0.0
description: Consolidated umbrella for fuzzing-* skills.
---
## Included Capabilities

### fuzzing-dictionary
Fuzzing dictionaries guide fuzzers with domain-specific tokens. Use when fuzzing parsers, protocols, or format-specific code.

- **Full reference:** `references/fuzzing-dictionary/SKILL.md`
- **Execution scripts:** `scripts/fuzzing-dictionary/`

### fuzzing-obstacles
Techniques for patching code to overcome fuzzing obstacles. Use when checksums, global state, or other barriers block fuzzer progress.

- **Full reference:** `references/fuzzing-obstacles/SKILL.md`
- **Execution scripts:** `scripts/fuzzing-obstacles/`