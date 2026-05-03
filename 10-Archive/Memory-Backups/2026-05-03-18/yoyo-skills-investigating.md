---
name: investigating
domain: red-teaming
tags:
- investigating
- class-level
- umbrella
status: active
version: 1.0.0
description: Consolidated umbrella for investigating-* skills.
---
## Included Capabilities

### investigating-ransomware-attack-artifacts
Identify, collect, and analyze ransomware attack artifacts to determine the variant, initial access vector, encryption scope, and recovery options.
- **Full reference:** `references/investigating-ransomware-attack-artifacts/SKILL.md`
- **Execution scripts:** `scripts/investigating-ransomware-attack-artifacts/`

### investigating-phishing-email-incident
Investigates phishing email incidents from initial user report through header analysis, URL/attachment detonation, impacted user identification, and containment actions using SOC tools like Splunk, Microsoft Defender, and sandbox analysis platforms. Use when a reported phishing email requires full incident investigation to determine scope and impact.

- **Full reference:** `references/investigating-phishing-email-incident/SKILL.md`
- **Execution scripts:** `scripts/investigating-phishing-email-incident/`

### investigating-insider-threat-indicators
Investigates insider threat indicators including data exfiltration attempts, unauthorized access patterns, policy violations, and pre-departure behaviors using SIEM analytics, DLP alerts, and HR data correlation. Use when SOC teams receive insider threat referrals from HR, detect anomalous data movement by employees, or need to build investigation timelines for potential insider threats.

- **Full reference:** `references/investigating-insider-threat-indicators/SKILL.md`
- **Execution scripts:** `scripts/investigating-insider-threat-indicators/`