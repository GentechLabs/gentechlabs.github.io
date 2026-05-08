---
name: executing
domain: red-teaming
tags:
- class-level
- executing
- umbrella
status: active
version: 1.0.0
description: Consolidated umbrella for executing-* skills.
---
## Included Capabilities

### executing-phishing-simulation-campaign
Executes authorized phishing simulation campaigns to assess an organization's susceptibility to email-based social engineering attacks. The tester designs realistic phishing scenarios, builds credential harvesting infrastructure, sends targeted phishing emails, and tracks open rates, click-through rates, and credential submission rates to measure human security awareness. Activates for requests involving phishing simulation, social engineering assessment, email security testing, or security awareness measurement.

- **Full reference:** `references/executing-phishing-simulation-campaign/SKILL.md`
- **Execution scripts:** `scripts/executing-phishing-simulation-campaign/`

### executing-active-directory-attack-simulation
Executes authorized attack simulations against Active Directory environments to identify misconfigurations, weak credentials, dangerous privilege paths, and exploitable trust relationships that could lead to domain compromise. The tester uses BloodHound for attack path analysis, Mimikatz for credential extraction, and Impacket for protocol-level attacks including Kerberoasting, AS-REP Roasting, and delegation abuse. Activates for requests involving Active Directory pentest, AD attack simulation, domain compromise testing, or Kerberos attack assessment.

- **Full reference:** `references/executing-active-directory-attack-simulation/SKILL.md`
- **Execution scripts:** `scripts/executing-active-directory-attack-simulation/`

### executing-red-team-engagement-planning
Red team engagement planning is the foundational phase that defines scope, objectives, rules of engagement (ROE), threat model selection, and operational timelines before any offensive testing begins.
- **Full reference:** `references/executing-red-team-engagement-planning/SKILL.md`
- **Execution scripts:** `scripts/executing-red-team-engagement-planning/`

### executing-red-team-exercise
Executes comprehensive red team exercises that simulate real-world adversary operations against an organization's people, processes, and technology. The red team operates with stealth as a primary objective, employing the full attack lifecycle from initial reconnaissance through objective completion while testing the organization's detection and response capabilities. This differs from penetration testing by focusing on adversary emulation rather than vulnerability identification. Activates for requests involving red team exercise, adversary simulation, adversary emulation, or full-scope offensive security assessment.

- **Full reference:** `references/executing-red-team-exercise/SKILL.md`
- **Execution scripts:** `scripts/executing-red-team-exercise/`