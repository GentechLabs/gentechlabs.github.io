---
name: deobfuscating
domain: red-teaming
tags:
- deobfuscating
- class-level
- umbrella
status: active
version: 1.0.0
description: Consolidated umbrella for deobfuscating-* skills.
---
## Included Capabilities

### deobfuscating-powershell-obfuscated-malware
Systematically deobfuscate multi-layer PowerShell malware using AST analysis, dynamic tracing, and tools like PSDecode and PowerDecode to reveal hidden payloads and C2 infrastructure.
- **Full reference:** `references/deobfuscating-powershell-obfuscated-malware/SKILL.md`
- **Execution scripts:** `scripts/deobfuscating-powershell-obfuscated-malware/`

### deobfuscating-javascript-malware
Deobfuscates malicious JavaScript code used in web-based attacks, phishing pages, and dropper scripts by reversing encoding layers, eval chains, string manipulation, and control flow obfuscation to reveal the original malicious logic. Activates for requests involving JavaScript malware analysis, script deobfuscation, web skimmer analysis, or obfuscated dropper investigation.

- **Full reference:** `references/deobfuscating-javascript-malware/SKILL.md`
- **Execution scripts:** `scripts/deobfuscating-javascript-malware/`