---
name: building
domain: red-teaming
tags:
- class-level
- building
- umbrella
status: active
version: 1.0.0
description: Consolidated umbrella for building-* skills.
---
## Included Capabilities

### building-automated-malware-submission-pipeline
Builds an automated malware submission and analysis pipeline that collects suspicious files from endpoints and email gateways, submits them to sandbox environments and multi-engine scanners, and generates verdicts with IOCs for SIEM integration. Use when SOC teams need to scale malware analysis beyond manual sandbox submissions for high-volume alert triage.

- **Full reference:** `references/building-automated-malware-submission-pipeline/SKILL.md`
- **Execution scripts:** `scripts/building-automated-malware-submission-pipeline/`

### building-soc-escalation-matrix
Build a structured SOC escalation matrix defining severity tiers, response SLAs, escalation paths, and notification procedures for security incidents.
- **Full reference:** `references/building-soc-escalation-matrix/SKILL.md`
- **Execution scripts:** `scripts/building-soc-escalation-matrix/`

### building-incident-response-dashboard
Builds real-time incident response dashboards in Splunk, Elastic, or Grafana to provide SOC analysts and leadership with situational awareness during active incidents, tracking affected systems, containment status, IOC spread, and response timeline. Use when IR teams need unified visibility during incident coordination and post-incident reporting.

- **Full reference:** `references/building-incident-response-dashboard/SKILL.md`
- **Execution scripts:** `scripts/building-incident-response-dashboard/`

### building-devsecops-pipeline-with-gitlab-ci
Design and implement a comprehensive DevSecOps pipeline in GitLab CI/CD integrating SAST, DAST, container scanning, dependency scanning, and secret detection.
- **Full reference:** `references/building-devsecops-pipeline-with-gitlab-ci/SKILL.md`
- **Execution scripts:** `scripts/building-devsecops-pipeline-with-gitlab-ci/`

### building-ioc-enrichment-pipeline-with-opencti
OpenCTI is an open-source platform for managing cyber threat intelligence knowledge, built on STIX 2.1 as its native data model. This skill covers building an automated IOC enrichment pipeline using O
- **Full reference:** `references/building-ioc-enrichment-pipeline-with-opencti/SKILL.md`
- **Execution scripts:** `scripts/building-ioc-enrichment-pipeline-with-opencti/`

### building-ransomware-playbook-with-cisa-framework
Builds a structured ransomware incident response playbook aligned with the CISA StopRansomware Guide and NIST Cybersecurity Framework. Covers preparation, detection, containment, eradication, recovery, and post-incident phases with actionable checklists. Activates for requests involving ransomware response planning, CISA compliance, incident response playbook creation, or ransomware preparedness assessment.

- **Full reference:** `references/building-ransomware-playbook-with-cisa-framework/SKILL.md`
- **Execution scripts:** `scripts/building-ransomware-playbook-with-cisa-framework/`

### building-ioc-defanging-and-sharing-pipeline
Build an automated pipeline to defang indicators of compromise (URLs, IPs, domains, emails) for safe sharing and distribute them in STIX format through TAXII feeds and threat intelligence platforms.
- **Full reference:** `references/building-ioc-defanging-and-sharing-pipeline/SKILL.md`
- **Execution scripts:** `scripts/building-ioc-defanging-and-sharing-pipeline/`

### building-role-mining-for-rbac-optimization
Apply bottom-up and top-down role mining techniques to discover optimal RBAC roles from existing user-permission assignments, reducing role explosion and enforcing least privilege.
- **Full reference:** `references/building-role-mining-for-rbac-optimization/SKILL.md`
- **Execution scripts:** `scripts/building-role-mining-for-rbac-optimization/`

### building-threat-hunt-hypothesis-framework
Build a systematic threat hunt hypothesis framework that transforms threat intelligence, attack patterns, and environmental data into testable hunting hypotheses.
- **Full reference:** `references/building-threat-hunt-hypothesis-framework/SKILL.md`
- **Execution scripts:** `scripts/building-threat-hunt-hypothesis-framework/`

### building-vulnerability-aging-and-sla-tracking
Implement a vulnerability aging dashboard and SLA tracking system to measure remediation performance against severity-based timelines and drive accountability.
- **Full reference:** `references/building-vulnerability-aging-and-sla-tracking/SKILL.md`
- **Execution scripts:** `scripts/building-vulnerability-aging-and-sla-tracking/`

### building-threat-intelligence-feed-integration
Builds automated threat intelligence feed integration pipelines connecting STIX/TAXII feeds, open-source threat intel, and commercial TI platforms into SIEM and security tools for real-time IOC matching and alerting. Use when SOC teams need to operationalize threat intelligence by automating feed ingestion, normalization, scoring, and distribution to detection systems.

- **Full reference:** `references/building-threat-intelligence-feed-integration/SKILL.md`
- **Execution scripts:** `scripts/building-threat-intelligence-feed-integration/`

### building-vulnerability-scanning-workflow
Builds a structured vulnerability scanning workflow using tools like Nessus, Qualys, and OpenVAS to discover, prioritize, and track remediation of security vulnerabilities across infrastructure. Use when SOC teams need to establish recurring vulnerability assessment processes, integrate scan results with SIEM alerting, and build remediation tracking dashboards.

- **Full reference:** `references/building-vulnerability-scanning-workflow/SKILL.md`
- **Execution scripts:** `scripts/building-vulnerability-scanning-workflow/`

### building-patch-tuesday-response-process
Establish a structured operational process to triage, test, and deploy Microsoft Patch Tuesday security updates within risk-based remediation SLAs.
- **Full reference:** `references/building-patch-tuesday-response-process/SKILL.md`
- **Execution scripts:** `scripts/building-patch-tuesday-response-process/`

### building-threat-feed-aggregation-with-misp
Deploy MISP (Malware Information Sharing Platform) to aggregate, correlate, and distribute threat intelligence feeds from multiple sources for centralized IOC management and automated SIEM integration.
- **Full reference:** `references/building-threat-feed-aggregation-with-misp/SKILL.md`
- **Execution scripts:** `scripts/building-threat-feed-aggregation-with-misp/`

### building-threat-actor-profile-from-osint
Build comprehensive threat actor profiles using open-source intelligence (OSINT) techniques to document adversary motivations, capabilities, infrastructure, and TTPs for proactive defense.
- **Full reference:** `references/building-threat-actor-profile-from-osint/SKILL.md`
- **Execution scripts:** `scripts/building-threat-actor-profile-from-osint/`

### building-soc-playbook-for-ransomware
Builds a structured SOC incident response playbook for ransomware attacks covering detection, containment, eradication, and recovery phases with specific SIEM queries, isolation procedures, and decision trees. Use when SOC teams need formalized response procedures for ransomware incidents aligned to NIST SP 800-61 and MITRE ATT&CK ransomware techniques.

- **Full reference:** `references/building-soc-playbook-for-ransomware/SKILL.md`
- **Execution scripts:** `scripts/building-soc-playbook-for-ransomware/`

### building-cloud-siem-with-sentinel
This skill covers deploying Microsoft Sentinel as a cloud-native SIEM and SOAR platform for centralized security operations. It details configuring data connectors for multi-cloud log ingestion, writing KQL detection queries, building automated response playbooks with Logic Apps, and leveraging the Sentinel data lake for petabyte-scale threat hunting across AWS, Azure, and GCP security telemetry.

- **Full reference:** `references/building-cloud-siem-with-sentinel/SKILL.md`
- **Execution scripts:** `scripts/building-cloud-siem-with-sentinel/`

### building-attack-pattern-library-from-cti-reports
Extract and catalog attack patterns from cyber threat intelligence reports into a structured STIX-based library mapped to MITRE ATT&CK for detection engineering and threat-informed defense.
- **Full reference:** `references/building-attack-pattern-library-from-cti-reports/SKILL.md`
- **Execution scripts:** `scripts/building-attack-pattern-library-from-cti-reports/`

### building-malware-incident-communication-template
Build structured communication templates for malware incidents including stakeholder notifications, executive briefings, technical advisories, and regulatory disclosures with severity-based escalation procedures.
- **Full reference:** `references/building-malware-incident-communication-template/SKILL.md`
- **Execution scripts:** `scripts/building-malware-incident-communication-template/`

### building-threat-intelligence-enrichment-in-splunk
Build automated threat intelligence enrichment pipelines in Splunk Enterprise Security using lookup tables, modular inputs, and the Threat Intelligence Framework.
- **Full reference:** `references/building-threat-intelligence-enrichment-in-splunk/SKILL.md`
- **Execution scripts:** `scripts/building-threat-intelligence-enrichment-in-splunk/`

### building-c2-infrastructure-with-sliver-framework
Build and configure a resilient command-and-control infrastructure using BishopFox's Sliver C2 framework with redirectors, HTTPS listeners, and multi-operator support for authorized red team engagements.
- **Full reference:** `references/building-c2-infrastructure-with-sliver-framework/SKILL.md`
- **Execution scripts:** `scripts/building-c2-infrastructure-with-sliver-framework/`

### building-detection-rules-with-sigma
Builds vendor-agnostic detection rules using the Sigma rule format for threat detection across SIEM platforms including Splunk, Elastic, and Microsoft Sentinel. Use when creating portable detection logic from threat intelligence, mapping rules to MITRE ATT&CK techniques, or converting community Sigma rules into platform-specific queries using sigmac or pySigma backends.

- **Full reference:** `references/building-detection-rules-with-sigma/SKILL.md`
- **Execution scripts:** `scripts/building-detection-rules-with-sigma/`

### building-red-team-c2-infrastructure-with-havoc
Deploy and configure the Havoc C2 framework with teamserver, HTTPS listeners, redirectors, and Demon agents for authorized red team operations.
- **Full reference:** `references/building-red-team-c2-infrastructure-with-havoc/SKILL.md`
- **Execution scripts:** `scripts/building-red-team-c2-infrastructure-with-havoc/`

### building-identity-federation-with-saml-azure-ad
Establish SAML 2.0 identity federation between on-premises Active Directory and Azure AD (Microsoft Entra ID) for seamless cross-domain authentication and SSO to cloud applications.
- **Full reference:** `references/building-identity-federation-with-saml-azure-ad/SKILL.md`
- **Execution scripts:** `scripts/building-identity-federation-with-saml-azure-ad/`

### building-adversary-infrastructure-tracking-system
Build an automated system to track adversary infrastructure using passive DNS, certificate transparency, WHOIS data, and IP enrichment to map and monitor threat actor command-and-control networks.
- **Full reference:** `references/building-adversary-infrastructure-tracking-system/SKILL.md`
- **Execution scripts:** `scripts/building-adversary-infrastructure-tracking-system/`

### building-identity-governance-lifecycle-process
Builds comprehensive identity governance and lifecycle management processes including joiner-mover-leaver automation, role mining, access request workflows, periodic recertification, and orphaned account remediation using IGA platforms. Activates for requests involving identity lifecycle management, JML processes, role-based access provisioning, or identity governance program design.

- **Full reference:** `references/building-identity-governance-lifecycle-process/SKILL.md`
- **Execution scripts:** `scripts/building-identity-governance-lifecycle-process/`

### building-soc-metrics-and-kpi-tracking
Builds SOC performance metrics and KPI tracking dashboards measuring Mean Time to Detect (MTTD), Mean Time to Respond (MTTR), alert quality ratios, analyst productivity, and detection coverage using SIEM data. Use when SOC leadership needs operational visibility, continuous improvement tracking, or executive-level reporting on security operations effectiveness.

- **Full reference:** `references/building-soc-metrics-and-kpi-tracking/SKILL.md`
- **Execution scripts:** `scripts/building-soc-metrics-and-kpi-tracking/`

### building-vulnerability-dashboard-with-defectdojo
Deploy DefectDojo as a centralized vulnerability management dashboard with scanner integrations, deduplication, metrics tracking, and Jira ticketing workflows.
- **Full reference:** `references/building-vulnerability-dashboard-with-defectdojo/SKILL.md`
- **Execution scripts:** `scripts/building-vulnerability-dashboard-with-defectdojo/`

### building-incident-response-playbook
Designs and documents structured incident response playbooks that define step-by-step procedures for specific incident types aligned with NIST SP 800-61r3 and SANS PICERL frameworks. Covers playbook structure, decision trees, escalation criteria, RACI matrices, and integration with SOAR platforms. Activates for requests involving IR playbook creation, incident response procedure documentation, response runbook development, or SOAR playbook design.

- **Full reference:** `references/building-incident-response-playbook/SKILL.md`
- **Execution scripts:** `scripts/building-incident-response-playbook/`

### building-threat-intelligence-platform
Building a Threat Intelligence Platform (TIP) involves deploying and integrating multiple CTI tools into a unified system for collecting, analyzing, enriching, and disseminating threat intelligence. T
- **Full reference:** `references/building-threat-intelligence-platform/SKILL.md`
- **Execution scripts:** `scripts/building-threat-intelligence-platform/`

### building-phishing-reporting-button-workflow
Implement a phishing report button in email clients with automated triage workflow that analyzes user-reported suspicious emails and provides feedback to reporters.
- **Full reference:** `references/building-phishing-reporting-button-workflow/SKILL.md`
- **Execution scripts:** `scripts/building-phishing-reporting-button-workflow/`

### building-vulnerability-exception-tracking-system
Build a vulnerability exception and risk acceptance tracking system with approval workflows, compensating controls documentation, and expiration management.
- **Full reference:** `references/building-vulnerability-exception-tracking-system/SKILL.md`
- **Execution scripts:** `scripts/building-vulnerability-exception-tracking-system/`

### building-detection-rule-with-splunk-spl
Build effective detection rules using Splunk Search Processing Language (SPL) correlation searches to identify security threats in SOC environments.
- **Full reference:** `references/building-detection-rule-with-splunk-spl/SKILL.md`
- **Execution scripts:** `scripts/building-detection-rule-with-splunk-spl/`

### building-incident-timeline-with-timesketch
Build collaborative forensic incident timelines using Timesketch to ingest, normalize, and analyze multi-source event data for attack chain reconstruction and investigation documentation.
- **Full reference:** `references/building-incident-timeline-with-timesketch/SKILL.md`
- **Execution scripts:** `scripts/building-incident-timeline-with-timesketch/`