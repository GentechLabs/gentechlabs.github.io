---
name: correlating
domain: red-teaming
tags:
- correlating
- class-level
- umbrella
status: active
version: 1.0.0
description: Consolidated umbrella for correlating-* skills.
---
## Included Capabilities

### correlating-threat-campaigns
Correlates disparate security incidents, IOCs, and adversary behaviors across time and organizations to identify unified threat campaigns, attribute them to common threat actors, and extract shared indicators for improved detection. Use when multiple incidents exhibit overlapping indicators, when sector-wide attack campaigns require cross-organizational analysis, or when building campaign-level intelligence products. Activates for requests involving campaign analysis, incident clustering, cross-organizational IOC correlation, or MISP correlation engine.

- **Full reference:** `references/correlating-threat-campaigns/SKILL.md`
- **Execution scripts:** `scripts/correlating-threat-campaigns/`

### correlating-security-events-in-qradar
Correlates security events in IBM QRadar SIEM using AQL (Ariel Query Language), custom rules, building blocks, and offense management to detect multi-stage attacks across network, endpoint, and application log sources. Use when SOC analysts need to investigate QRadar offenses, build correlation rules, or tune detection logic for reducing false positives.

- **Full reference:** `references/correlating-security-events-in-qradar/SKILL.md`
- **Execution scripts:** `scripts/correlating-security-events-in-qradar/`