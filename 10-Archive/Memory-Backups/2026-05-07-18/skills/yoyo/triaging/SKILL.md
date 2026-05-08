---
name: triaging
domain: red-teaming
tags:
- class-level
- triaging
- umbrella
status: active
version: 1.0.0
description: Consolidated umbrella for triaging-* skills.
---
## Included Capabilities

### triaging-vulnerabilities-with-ssvc-framework
Triage and prioritize vulnerabilities using CISA's Stakeholder-Specific Vulnerability Categorization (SSVC) decision tree framework to produce actionable remediation priorities.
- **Full reference:** `references/triaging-vulnerabilities-with-ssvc-framework/SKILL.md`
- **Execution scripts:** `scripts/triaging-vulnerabilities-with-ssvc-framework/`

### triaging-security-incident
Performs initial triage of security incidents to determine severity, scope, and required response actions using the NIST SP 800-61r3 and SANS PICERL frameworks. Classifies incidents by type, assigns priority based on business impact, and routes to appropriate response teams. Activates for requests involving incident triage, security alert classification, severity assessment, incident prioritization, or initial incident analysis.

- **Full reference:** `references/triaging-security-incident/SKILL.md`
- **Execution scripts:** `scripts/triaging-security-incident/`

### triaging-security-incident-with-ir-playbook
Classify and prioritize security incidents using structured IR playbooks to determine severity, assign response teams, and initiate appropriate response procedures.
- **Full reference:** `references/triaging-security-incident-with-ir-playbook/SKILL.md`
- **Execution scripts:** `scripts/triaging-security-incident-with-ir-playbook/`

### triaging-security-alerts-in-splunk
Triages security alerts in Splunk Enterprise Security by classifying severity, investigating notable events, correlating related telemetry, and making escalation or closure decisions using SPL queries and the Incident Review dashboard. Use when SOC analysts face queued alerts from correlation searches, need to prioritize investigation order, or must document triage decisions for handoff to Tier 2/3 analysts.

- **Full reference:** `references/triaging-security-alerts-in-splunk/SKILL.md`
- **Execution scripts:** `scripts/triaging-security-alerts-in-splunk/`