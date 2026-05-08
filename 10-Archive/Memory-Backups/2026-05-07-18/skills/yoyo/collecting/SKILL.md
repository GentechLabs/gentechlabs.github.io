---
name: collecting
domain: red-teaming
tags:
- class-level
- umbrella
- collecting
status: active
version: 1.0.0
description: Consolidated umbrella for collecting-* skills.
---
## Included Capabilities

### collecting-open-source-intelligence
Collects and synthesizes open-source intelligence (OSINT) about threat actors, malicious infrastructure, and attack campaigns using publicly available data sources, passive reconnaissance tools, and dark web monitoring. Use when investigating external threat actor infrastructure, performing pre-engagement reconnaissance for authorized red team assessments, or enriching CTI reports with publicly available adversary context. Activates for requests involving Maltego, Shodan, OSINT framework, SpiderFoot, or infrastructure reconnaissance.

- **Full reference:** `references/collecting-open-source-intelligence/SKILL.md`
- **Execution scripts:** `scripts/collecting-open-source-intelligence/`

### collecting-threat-intelligence-with-misp
MISP (Malware Information Sharing Platform) is an open-source threat intelligence platform for gathering, sharing, storing, and correlating Indicators of Compromise (IOCs) of targeted attacks, threat
- **Full reference:** `references/collecting-threat-intelligence-with-misp/SKILL.md`
- **Execution scripts:** `scripts/collecting-threat-intelligence-with-misp/`

### collecting-indicators-of-compromise
Systematically collects, categorizes, and distributes indicators of compromise (IOCs) during and after security incidents to enable detection, blocking, and threat intelligence sharing. Covers network, host, email, and behavioral indicators using STIX/TAXII formats and threat intelligence platforms. Activates for requests involving IOC collection, indicator extraction, threat indicator sharing, compromise indicators, STIX export, or IOC enrichment.

- **Full reference:** `references/collecting-indicators-of-compromise/SKILL.md`
- **Execution scripts:** `scripts/collecting-indicators-of-compromise/`

### collecting-volatile-evidence-from-compromised-host
Collect volatile forensic evidence from a compromised system following order of volatility, preserving memory, network connections, processes, and system state before they are lost.
- **Full reference:** `references/collecting-volatile-evidence-from-compromised-host/SKILL.md`
- **Execution scripts:** `scripts/collecting-volatile-evidence-from-compromised-host/`