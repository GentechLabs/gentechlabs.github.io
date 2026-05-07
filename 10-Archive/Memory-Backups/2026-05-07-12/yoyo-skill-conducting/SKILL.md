---
name: conducting
domain: red-teaming
tags:
- class-level
- umbrella
- conducting
status: active
version: 1.0.0
description: Consolidated umbrella for conducting-* skills.
---
## Included Capabilities

### conducting-social-engineering-pretext-call
Plan and execute authorized vishing (voice phishing) pretext calls to assess employee susceptibility to social engineering and evaluate security awareness controls.
- **Full reference:** `references/conducting-social-engineering-pretext-call/SKILL.md`
- **Execution scripts:** `scripts/conducting-social-engineering-pretext-call/`

### conducting-social-engineering-penetration-test
Design and execute a social engineering penetration test including phishing, vishing, smishing, and physical pretexting campaigns to measure human security resilience and identify training gaps.
- **Full reference:** `references/conducting-social-engineering-penetration-test/SKILL.md`
- **Execution scripts:** `scripts/conducting-social-engineering-penetration-test/`

### conducting-wireless-network-penetration-test
Conducts authorized wireless network penetration tests to assess the security of WiFi infrastructure by testing for weak encryption protocols, captive portal bypasses, evil twin attacks, WPA2/WPA3 handshake capture, rogue access point detection, and client-side attacks. The tester evaluates wireless authentication, network segmentation, and the effectiveness of wireless intrusion detection systems. Activates for requests involving wireless pentest, WiFi security assessment, WPA2/WPA3 testing, or rogue access point detection.

- **Full reference:** `references/conducting-wireless-network-penetration-test/SKILL.md`
- **Execution scripts:** `scripts/conducting-wireless-network-penetration-test/`

### conducting-cloud-incident-response
Responds to security incidents in cloud environments (AWS, Azure, GCP) by performing identity-based containment, cloud-native log analysis, resource isolation, and forensic evidence acquisition adapted for ephemeral cloud infrastructure. Activates for requests involving cloud incident response, AWS security incident, Azure compromise, GCP breach, cloud forensics, or cloud identity compromise.

- **Full reference:** `references/conducting-cloud-incident-response/SKILL.md`
- **Execution scripts:** `scripts/conducting-cloud-incident-response/`

### conducting-mobile-app-penetration-test
Conducts penetration testing of iOS and Android mobile applications following the OWASP Mobile Application Security Testing Guide (MASTG) to identify vulnerabilities in data storage, network communication, authentication, cryptography, and platform-specific security controls. The tester performs static analysis of application binaries, dynamic analysis at runtime, and API security testing to evaluate the complete mobile attack surface. Activates for requests involving mobile app pentest, iOS security assessment, Android security testing, or OWASP MASTG assessment.

- **Full reference:** `references/conducting-mobile-app-penetration-test/SKILL.md`
- **Execution scripts:** `scripts/conducting-mobile-app-penetration-test/`

### conducting-network-penetration-test
Conducts comprehensive network penetration tests against authorized target environments by performing host discovery, port scanning, service enumeration, vulnerability identification, and controlled exploitation to assess the security posture of network infrastructure. The tester follows PTES methodology from reconnaissance through post-exploitation and reporting. Activates for requests involving network pentest, infrastructure security assessment, internal network testing, or external perimeter testing.

- **Full reference:** `references/conducting-network-penetration-test/SKILL.md`
- **Execution scripts:** `scripts/conducting-network-penetration-test/`

### conducting-spearphishing-simulation-campaign
Spearphishing simulation is a targeted social engineering attack vector used by red teams to gain initial access. Unlike broad phishing campaigns, spearphishing uses OSINT-derived intelligence to craf
- **Full reference:** `references/conducting-spearphishing-simulation-campaign/SKILL.md`
- **Execution scripts:** `scripts/conducting-spearphishing-simulation-campaign/`

### conducting-cloud-penetration-testing
This skill outlines methodologies for performing authorized penetration testing against AWS, Azure, and GCP cloud environments. It covers understanding the shared responsibility model for testing scope, leveraging cloud-specific attack tools like Pacu and ScoutSuite, exploiting IAM misconfigurations, testing for SSRF to cloud metadata services, and reporting findings aligned to MITRE ATT&CK Cloud matrix.

- **Full reference:** `references/conducting-cloud-penetration-testing/SKILL.md`
- **Execution scripts:** `scripts/conducting-cloud-penetration-testing/`

### conducting-man-in-the-middle-attack-simulation
Simulates man-in-the-middle attacks using Ettercap, mitmproxy, and Bettercap in authorized environments to intercept, analyze, and modify network traffic for testing encryption enforcement, certificate validation, and detection capabilities.

- **Full reference:** `references/conducting-man-in-the-middle-attack-simulation/SKILL.md`
- **Execution scripts:** `scripts/conducting-man-in-the-middle-attack-simulation/`

### conducting-domain-persistence-with-dcsync
Perform DCSync attacks to replicate Active Directory credentials and establish domain persistence by extracting KRBTGT, Domain Admin, and service account hashes for Golden Ticket creation.
- **Full reference:** `references/conducting-domain-persistence-with-dcsync/SKILL.md`
- **Execution scripts:** `scripts/conducting-domain-persistence-with-dcsync/`

### conducting-external-reconnaissance-with-osint
Conducts external reconnaissance using Open Source Intelligence (OSINT) techniques to map an organization's external attack surface without directly interacting with target systems. The tester gathers information from public sources including DNS records, certificate transparency logs, search engines, social media, code repositories, and data breach databases to build a comprehensive target profile. Activates for requests involving OSINT reconnaissance, external footprinting, attack surface mapping, or passive information gathering.

- **Full reference:** `references/conducting-external-reconnaissance-with-osint/SKILL.md`
- **Execution scripts:** `scripts/conducting-external-reconnaissance-with-osint/`

### conducting-malware-incident-response
Responds to malware infections across enterprise endpoints by identifying the malware family, determining infection vectors, assessing spread, and executing eradication procedures. Covers the full lifecycle from detection through containment, analysis, removal, and recovery. Activates for requests involving malware response, malware eradication, trojan removal, worm containment, malware triage, or infected endpoint remediation.

- **Full reference:** `references/conducting-malware-incident-response/SKILL.md`
- **Execution scripts:** `scripts/conducting-malware-incident-response/`

### conducting-full-scope-red-team-engagement
Plan and execute a comprehensive red team engagement covering reconnaissance through post-exploitation using MITRE ATT&CK-aligned TTPs to evaluate an organization's detection and response capabilities.
- **Full reference:** `references/conducting-full-scope-red-team-engagement/SKILL.md`
- **Execution scripts:** `scripts/conducting-full-scope-red-team-engagement/`

### conducting-internal-network-penetration-test
Execute an internal network penetration test simulating an insider threat or post-breach attacker to identify lateral movement paths, privilege escalation vectors, and sensitive data exposure within the corporate network.
- **Full reference:** `references/conducting-internal-network-penetration-test/SKILL.md`
- **Execution scripts:** `scripts/conducting-internal-network-penetration-test/`

### conducting-phishing-incident-response
Responds to phishing incidents by analyzing reported emails, extracting indicators, assessing credential compromise, quarantining malicious messages across the organization, and remediating affected accounts. Covers email header analysis, URL/attachment sandboxing, and mailbox-wide purge operations. Activates for requests involving phishing response, email incident, credential phishing, spear phishing investigation, or phishing remediation.

- **Full reference:** `references/conducting-phishing-incident-response/SKILL.md`
- **Execution scripts:** `scripts/conducting-phishing-incident-response/`

### conducting-pass-the-ticket-attack
Pass-the-Ticket (PtT) is a lateral movement technique that uses stolen Kerberos tickets (TGT or TGS) to authenticate to services without knowing the user's password. By extracting Kerberos tickets fro
- **Full reference:** `references/conducting-pass-the-ticket-attack/SKILL.md`
- **Execution scripts:** `scripts/conducting-pass-the-ticket-attack/`

### conducting-internal-reconnaissance-with-bloodhound-ce
Conduct internal Active Directory reconnaissance using BloodHound Community Edition to map attack paths, identify privilege escalation chains, and discover misconfigurations in domain environments.
- **Full reference:** `references/conducting-internal-reconnaissance-with-bloodhound-ce/SKILL.md`
- **Execution scripts:** `scripts/conducting-internal-reconnaissance-with-bloodhound-ce/`

### conducting-post-incident-lessons-learned
Facilitate structured post-incident reviews to identify root causes, document what worked and failed, and produce actionable recommendations to improve future incident response.
- **Full reference:** `references/conducting-post-incident-lessons-learned/SKILL.md`
- **Execution scripts:** `scripts/conducting-post-incident-lessons-learned/`

### conducting-api-security-testing
Conducts security testing of REST, GraphQL, and gRPC APIs to identify vulnerabilities in authentication, authorization, rate limiting, input validation, and business logic. The tester uses the OWASP API Security Top 10 as the testing framework, combining Burp Suite interception with Postman collections and custom scripts to test endpoint security at every privilege level. Activates for requests involving API security testing, REST API pentest, GraphQL security assessment, or API vulnerability testing.

- **Full reference:** `references/conducting-api-security-testing/SKILL.md`
- **Execution scripts:** `scripts/conducting-api-security-testing/`

### conducting-memory-forensics-with-volatility
Performs memory forensics analysis using Volatility 3 to extract evidence of malware execution, process injection, network connections, and credential theft from RAM dumps captured during incident response. Covers memory acquisition, process analysis, DLL inspection, and malware detection. Activates for requests involving memory forensics, RAM analysis, Volatility framework, memory dump investigation, volatile evidence analysis, or live memory acquisition.

- **Full reference:** `references/conducting-memory-forensics-with-volatility/SKILL.md`
- **Execution scripts:** `scripts/conducting-memory-forensics-with-volatility/`