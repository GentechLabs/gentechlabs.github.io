---
name: performing
domain: red-teaming
tags:
- performing
- class-level
- umbrella
status: active
version: 1.0.0
description: Consolidated umbrella for performing-* skills.
---
## Included Capabilities

### performing-container-escape-detection
Detects container escape attempts by analyzing namespace configurations, privileged container checks, dangerous capability assignments, and host path mounts using the kubernetes Python client. Identifies CVE-2022-0492 style escapes via cgroup abuse. Use when auditing container security posture or investigating escape attempts.

- **Full reference:** `references/performing-container-escape-detection/SKILL.md`
- **Execution scripts:** `scripts/performing-container-escape-detection/`

### performing-ai-driven-osint-correlation
Use AI and LLM-based reasoning to correlate findings across multiple OSINT sources—username enumeration, email lookups, social media profiles, domain records, breach databases, and dark-web mentions—into unified intelligence profiles with confidence scoring and link analysis.
- **Full reference:** `references/performing-ai-driven-osint-correlation/SKILL.md`
- **Execution scripts:** `scripts/performing-ai-driven-osint-correlation/`

### performing-red-team-phishing-with-gophish
Automate GoPhish phishing simulation campaigns using the Python gophish library. Creates email templates with tracking pixels, configures SMTP sending profiles, builds target groups from CSV, launches campaigns, and analyzes results including open rates, click rates, and credential submission statistics for security awareness assessment.
- **Full reference:** `references/performing-red-team-phishing-with-gophish/SKILL.md`
- **Execution scripts:** `scripts/performing-red-team-phishing-with-gophish/`

### performing-privacy-impact-assessment
Automates the Privacy Impact Assessment (PIA) workflow including data flow mapping, privacy risk scoring matrices, GDPR Article 35 DPIA and CCPA/CPRA alignment checks, data inventory cataloging, and remediation tracking. Implements the NIST Privacy Framework PRAM methodology and ICO DPIA guidance for systematic identification and mitigation of privacy risks across processing activities. Use when conducting privacy assessments for new systems, evaluating regulatory compliance posture, or building automated privacy governance programs.

- **Full reference:** `references/performing-privacy-impact-assessment/SKILL.md`
- **Execution scripts:** `scripts/performing-privacy-impact-assessment/`

### performing-gcp-security-assessment-with-forseti
Performing comprehensive security assessments of Google Cloud Platform environments using Forseti Security, Security Command Center, and gcloud CLI to audit IAM policies, firewall rules, storage permissions, and compliance against CIS GCP Foundations Benchmark.

- **Full reference:** `references/performing-gcp-security-assessment-with-forseti/SKILL.md`
- **Execution scripts:** `scripts/performing-gcp-security-assessment-with-forseti/`

### performing-lateral-movement-with-wmiexec
Perform lateral movement across Windows networks using WMI-based remote execution techniques including Impacket wmiexec.py, CrackMapExec, and native WMI commands for stealthy post-exploitation during red team engagements.
- **Full reference:** `references/performing-lateral-movement-with-wmiexec/SKILL.md`
- **Execution scripts:** `scripts/performing-lateral-movement-with-wmiexec/`

### performing-s7comm-protocol-security-analysis
Perform security analysis of Siemens S7comm and S7CommPlus protocols used by SIMATIC S7 PLCs to identify vulnerabilities including replay attacks, integrity bypass, unauthorized CPU stop commands, and program download manipulation exploiting weaknesses in S7-300, S7-400, S7-1200, and S7-1500 controllers.

- **Full reference:** `references/performing-s7comm-protocol-security-analysis/SKILL.md`
- **Execution scripts:** `scripts/performing-s7comm-protocol-security-analysis/`

### performing-ot-vulnerability-scanning-safely
Perform vulnerability scanning in OT/ICS environments safely using passive monitoring, native protocol queries, and carefully controlled active scanning with Tenable OT Security to identify vulnerabilities without disrupting industrial processes or crashing legacy controllers.

- **Full reference:** `references/performing-ot-vulnerability-scanning-safely/SKILL.md`
- **Execution scripts:** `scripts/performing-ot-vulnerability-scanning-safely/`

### performing-disk-forensics-investigation
Conducts disk forensics investigations using forensic imaging, file system analysis, artifact recovery, and timeline reconstruction to support incident response cases. Utilizes tools such as FTK Imager, Autopsy, and The Sleuth Kit for evidence acquisition, deleted file recovery, and artifact examination. Activates for requests involving disk forensics, hard drive analysis, forensic imaging, file recovery, evidence acquisition, or digital forensic investigation.

- **Full reference:** `references/performing-disk-forensics-investigation/SKILL.md`
- **Execution scripts:** `scripts/performing-disk-forensics-investigation/`

### performing-content-security-policy-bypass
Analyze and bypass Content Security Policy implementations to achieve cross-site scripting by exploiting misconfigurations, JSONP endpoints, unsafe directives, and policy injection techniques.
- **Full reference:** `references/performing-content-security-policy-bypass/SKILL.md`
- **Execution scripts:** `scripts/performing-content-security-policy-bypass/`

### performing-network-traffic-analysis-with-zeek
Deploy Zeek network security monitor to capture, parse, and analyze network traffic metadata for threat detection, anomaly identification, and forensic investigation.
- **Full reference:** `references/performing-network-traffic-analysis-with-zeek/SKILL.md`
- **Execution scripts:** `scripts/performing-network-traffic-analysis-with-zeek/`

### performing-security-headers-audit
Auditing HTTP security headers including CSP, HSTS, X-Frame-Options, and cookie attributes to identify missing or misconfigured browser-level protections.
- **Full reference:** `references/performing-security-headers-audit/SKILL.md`
- **Execution scripts:** `scripts/performing-security-headers-audit/`

### performing-bandwidth-throttling-attack-simulation
Simulates bandwidth throttling and network degradation attacks using tc, iperf3, and Scapy in authorized environments to test quality-of-service controls, application resilience, and network monitoring detection of traffic manipulation attacks.

- **Full reference:** `references/performing-bandwidth-throttling-attack-simulation/SKILL.md`
- **Execution scripts:** `scripts/performing-bandwidth-throttling-attack-simulation/`

### performing-kerberoasting-attack
Kerberoasting is a post-exploitation technique that targets service accounts in Active Directory by requesting Kerberos TGS (Ticket Granting Service) tickets for accounts with Service Principal Names
- **Full reference:** `references/performing-kerberoasting-attack/SKILL.md`
- **Execution scripts:** `scripts/performing-kerberoasting-attack/`

### performing-iot-security-assessment
Performs comprehensive security assessments of IoT devices and their ecosystems by testing hardware interfaces, firmware, network communications, cloud APIs, and companion mobile applications. The tester uses firmware extraction and analysis, hardware debugging via UART and JTAG, network protocol analysis, and runtime exploitation to identify vulnerabilities across all layers of the IoT stack. Activates for requests involving IoT security testing, embedded device assessment, firmware security analysis, or smart device penetration testing.

- **Full reference:** `references/performing-iot-security-assessment/SKILL.md`
- **Execution scripts:** `scripts/performing-iot-security-assessment/`

### performing-ioc-enrichment-automation
Automates Indicator of Compromise (IOC) enrichment by orchestrating lookups across VirusTotal, AbuseIPDB, Shodan, MISP, and other intelligence sources to provide contextual scoring and disposition recommendations. Use when SOC analysts need rapid multi-source enrichment of IPs, domains, URLs, and file hashes during alert triage or incident investigation.

- **Full reference:** `references/performing-ioc-enrichment-automation/SKILL.md`
- **Execution scripts:** `scripts/performing-ioc-enrichment-automation/`

### performing-agentless-vulnerability-scanning
Configure and execute agentless vulnerability scanning using network protocols, cloud snapshot analysis, and API-based discovery to assess systems without installing endpoint agents.
- **Full reference:** `references/performing-agentless-vulnerability-scanning/SKILL.md`
- **Execution scripts:** `scripts/performing-agentless-vulnerability-scanning/`

### performing-web-application-firewall-bypass
Bypass Web Application Firewall protections using encoding techniques, HTTP method manipulation, parameter pollution, and payload obfuscation to deliver SQL injection, XSS, and other attack payloads past WAF detection rules.
- **Full reference:** `references/performing-web-application-firewall-bypass/SKILL.md`
- **Execution scripts:** `scripts/performing-web-application-firewall-bypass/`

### performing-threat-intelligence-sharing-with-misp
Use PyMISP to create, enrich, and share threat intelligence events on a MISP platform, including IOC management, feed integration, STIX export, and community sharing workflows.
- **Full reference:** `references/performing-threat-intelligence-sharing-with-misp/SKILL.md`
- **Execution scripts:** `scripts/performing-threat-intelligence-sharing-with-misp/`

### performing-network-traffic-analysis-with-tshark
Automate network traffic analysis using tshark and pyshark for protocol statistics, suspicious flow detection, DNS anomaly identification, and IOC extraction from PCAP files
- **Full reference:** `references/performing-network-traffic-analysis-with-tshark/SKILL.md`
- **Execution scripts:** `scripts/performing-network-traffic-analysis-with-tshark/`

### performing-subdomain-enumeration-with-subfinder
Enumerate subdomains of target domains using ProjectDiscovery's Subfinder passive reconnaissance tool to map the attack surface during security assessments.
- **Full reference:** `references/performing-subdomain-enumeration-with-subfinder/SKILL.md`
- **Execution scripts:** `scripts/performing-subdomain-enumeration-with-subfinder/`

### performing-aws-privilege-escalation-assessment
Performing authorized privilege escalation assessments in AWS environments to identify IAM misconfigurations that allow users or roles to elevate their permissions using Pacu, CloudFox, Principal Mapper, and manual IAM policy analysis techniques.

- **Full reference:** `references/performing-aws-privilege-escalation-assessment/SKILL.md`
- **Execution scripts:** `scripts/performing-aws-privilege-escalation-assessment/`

### performing-bluetooth-security-assessment
Assess Bluetooth Low Energy device security by scanning, enumerating GATT services, and detecting vulnerabilities
- **Full reference:** `references/performing-bluetooth-security-assessment/SKILL.md`
- **Execution scripts:** `scripts/performing-bluetooth-security-assessment/`

### performing-oil-gas-cybersecurity-assessment
This skill covers conducting cybersecurity assessments specific to oil and gas facilities including upstream (exploration/production), midstream (pipeline/transport), and downstream (refining/distribution) operations. It addresses SCADA systems controlling pipeline operations, DCS for refinery process control, safety instrumented systems for hazardous processes, remote terminal units at unmanned wellhead sites, and compliance with API 1164, TSA Pipeline Security Directives, IEC 62443, and NIST Cybersecurity Framework for critical infrastructure.

- **Full reference:** `references/performing-oil-gas-cybersecurity-assessment/SKILL.md`
- **Execution scripts:** `scripts/performing-oil-gas-cybersecurity-assessment/`

### performing-service-account-audit
Audit service accounts across enterprise infrastructure to identify orphaned, over-privileged, and non-compliant accounts. This skill covers discovery of service accounts in Active Directory, cloud pl
- **Full reference:** `references/performing-service-account-audit/SKILL.md`
- **Execution scripts:** `scripts/performing-service-account-audit/`

### performing-indicator-lifecycle-management
Indicator lifecycle management tracks IOCs from initial discovery through validation, enrichment, deployment, monitoring, and eventual retirement. This skill covers implementing systematic processes f
- **Full reference:** `references/performing-indicator-lifecycle-management/SKILL.md`
- **Execution scripts:** `scripts/performing-indicator-lifecycle-management/`

### performing-thick-client-application-penetration-test
Conduct a thick client application penetration test to identify insecure local storage, hardcoded credentials, DLL hijacking, memory manipulation, and insecure API communication in desktop applications using dnSpy, Procmon, and Burp Suite.
- **Full reference:** `references/performing-thick-client-application-penetration-test/SKILL.md`
- **Execution scripts:** `scripts/performing-thick-client-application-penetration-test/`

### performing-privileged-account-access-review
Conduct systematic reviews of privileged accounts to validate access rights, identify excessive permissions, and enforce least privilege across PAM infrastructure.
- **Full reference:** `references/performing-privileged-account-access-review/SKILL.md`
- **Execution scripts:** `scripts/performing-privileged-account-access-review/`

### performing-container-image-hardening
This skill covers hardening container images by minimizing attack surface, removing unnecessary packages, implementing multi-stage builds, configuring non-root users, and applying CIS Docker Benchmark recommendations to produce secure production-ready images.

- **Full reference:** `references/performing-container-image-hardening/SKILL.md`
- **Execution scripts:** `scripts/performing-container-image-hardening/`

### performing-dynamic-analysis-of-android-app
Performs runtime dynamic analysis of Android applications using Frida, Objection, and Android Debug Bridge to observe application behavior during execution, intercept function calls, modify runtime values, and identify vulnerabilities that static analysis misses. Use when testing Android apps for runtime security flaws, hooking sensitive methods, bypassing client-side protections, or analyzing obfuscated applications. Activates for requests involving Android dynamic analysis, runtime hooking, Frida Android instrumentation, or live app behavior analysis.

- **Full reference:** `references/performing-dynamic-analysis-of-android-app/SKILL.md`
- **Execution scripts:** `scripts/performing-dynamic-analysis-of-android-app/`

### performing-http-parameter-pollution-attack
Execute HTTP Parameter Pollution attacks to bypass input validation, WAF rules, and security controls by injecting duplicate parameters that are processed differently by front-end and back-end systems.
- **Full reference:** `references/performing-http-parameter-pollution-attack/SKILL.md`
- **Execution scripts:** `scripts/performing-http-parameter-pollution-attack/`

### performing-physical-intrusion-assessment
Conduct authorized physical penetration testing using tailgating, badge cloning, lock bypassing, and rogue device deployment to evaluate facility security controls.
- **Full reference:** `references/performing-physical-intrusion-assessment/SKILL.md`
- **Execution scripts:** `scripts/performing-physical-intrusion-assessment/`

### performing-cloud-asset-inventory-with-cartography
Perform comprehensive cloud asset inventory and relationship mapping using Cartography to build a Neo4j security graph of infrastructure assets, IAM permissions, and attack paths across AWS, GCP, and Azure.
- **Full reference:** `references/performing-cloud-asset-inventory-with-cartography/SKILL.md`
- **Execution scripts:** `scripts/performing-cloud-asset-inventory-with-cartography/`

### performing-threat-landscape-assessment-for-sector
Conduct a sector-specific threat landscape assessment by analyzing threat actor targeting patterns, common attack vectors, and industry-specific vulnerabilities to inform organizational risk management.
- **Full reference:** `references/performing-threat-landscape-assessment-for-sector/SKILL.md`
- **Execution scripts:** `scripts/performing-threat-landscape-assessment-for-sector/`

### performing-paste-site-monitoring-for-credentials
Monitor paste sites like Pastebin and GitHub Gists for leaked credentials, API keys, and sensitive data dumps using automated scraping and keyword matching to detect breaches early.
- **Full reference:** `references/performing-paste-site-monitoring-for-credentials/SKILL.md`
- **Execution scripts:** `scripts/performing-paste-site-monitoring-for-credentials/`

### performing-entitlement-review-with-sailpoint-iiq
Performs entitlement review and access certification campaigns using SailPoint IdentityIQ including manager certifications, targeted entitlement reviews, role-based access validation, SOD violation remediation, and automated revocation workflows. Activates for requests involving access reviews, entitlement certifications, SailPoint IIQ governance, or periodic user access recertification.

- **Full reference:** `references/performing-entitlement-review-with-sailpoint-iiq/SKILL.md`
- **Execution scripts:** `scripts/performing-entitlement-review-with-sailpoint-iiq/`

### performing-file-carving-with-foremost
Recover files from disk images and unallocated space using Foremost's header-footer signature carving to extract evidence regardless of file system state.
- **Full reference:** `references/performing-file-carving-with-foremost/SKILL.md`
- **Execution scripts:** `scripts/performing-file-carving-with-foremost/`

### performing-automated-malware-analysis-with-cape
Deploy and operate CAPEv2 sandbox for automated malware analysis with behavioral monitoring, payload extraction, configuration parsing, and anti-evasion capabilities.
- **Full reference:** `references/performing-automated-malware-analysis-with-cape/SKILL.md`
- **Execution scripts:** `scripts/performing-automated-malware-analysis-with-cape/`

### performing-authenticated-vulnerability-scan
Authenticated (credentialed) vulnerability scanning uses valid system credentials to log into target hosts and perform deep inspection of installed software, patches, configurations, and security sett
- **Full reference:** `references/performing-authenticated-vulnerability-scan/SKILL.md`
- **Execution scripts:** `scripts/performing-authenticated-vulnerability-scan/`

### performing-directory-traversal-testing
Testing web applications for path traversal vulnerabilities that allow reading or writing arbitrary files on the server by manipulating file path parameters.
- **Full reference:** `references/performing-directory-traversal-testing/SKILL.md`
- **Execution scripts:** `scripts/performing-directory-traversal-testing/`

### performing-ssl-certificate-lifecycle-management
SSL/TLS certificate lifecycle management encompasses the full process of requesting, issuing, deploying, monitoring, renewing, and revoking X.509 certificates. Poor certificate management is a leading
- **Full reference:** `references/performing-ssl-certificate-lifecycle-management/SKILL.md`
- **Execution scripts:** `scripts/performing-ssl-certificate-lifecycle-management/`

### performing-ransomware-tabletop-exercise
Plans and facilitates tabletop exercises simulating ransomware incidents to test organizational readiness, decision-making, and communication procedures. Designs realistic scenarios based on current ransomware threat actors (LockBit, ALPHV/BlackCat, Cl0p), injects covering double extortion, backup destruction, and regulatory notification requirements. Evaluates participant responses against NIST CSF and CISA guidelines. Activates for requests involving ransomware tabletop, incident response exercise, or ransomware readiness drill.

- **Full reference:** `references/performing-ransomware-tabletop-exercise/SKILL.md`
- **Execution scripts:** `scripts/performing-ransomware-tabletop-exercise/`

### performing-access-recertification-with-saviynt
Configure and execute access recertification campaigns in Saviynt Enterprise Identity Cloud to validate user entitlements, revoke excessive access, and maintain compliance with SOX, SOC2, and HIPAA.
- **Full reference:** `references/performing-access-recertification-with-saviynt/SKILL.md`
- **Execution scripts:** `scripts/performing-access-recertification-with-saviynt/`

### performing-kubernetes-etcd-security-assessment
Assess the security posture of Kubernetes etcd clusters by evaluating encryption at rest, TLS configuration, access controls, backup encryption, and network isolation.
- **Full reference:** `references/performing-kubernetes-etcd-security-assessment/SKILL.md`
- **Execution scripts:** `scripts/performing-kubernetes-etcd-security-assessment/`

### performing-log-source-onboarding-in-siem
Perform structured log source onboarding into SIEM platforms by configuring collectors, parsers, normalization, and validation for complete security visibility.
- **Full reference:** `references/performing-log-source-onboarding-in-siem/SKILL.md`
- **Execution scripts:** `scripts/performing-log-source-onboarding-in-siem/`

### performing-user-behavior-analytics
Performs User and Entity Behavior Analytics (UEBA) to detect anomalous user activities including impossible travel, unusual access patterns, privilege abuse, and insider threats using SIEM-based behavioral baselines and statistical analysis. Use when SOC teams need to identify compromised accounts or insider threats through deviation from established behavioral norms.

- **Full reference:** `references/performing-user-behavior-analytics/SKILL.md`
- **Execution scripts:** `scripts/performing-user-behavior-analytics/`

### performing-privilege-escalation-assessment
Performs privilege escalation assessments on compromised Linux and Windows systems to identify paths from low-privilege access to root or SYSTEM-level control. The tester enumerates misconfigurations, vulnerable services, kernel exploits, SUID binaries, unquoted service paths, and credential stores to demonstrate the full impact of an initial compromise. Activates for requests involving privilege escalation testing, local exploitation, post-compromise escalation, or OS-level security assessment.

- **Full reference:** `references/performing-privilege-escalation-assessment/SKILL.md`
- **Execution scripts:** `scripts/performing-privilege-escalation-assessment/`

### performing-authenticated-scan-with-openvas
Configure and execute authenticated vulnerability scans using OpenVAS/Greenbone Vulnerability Management with SSH and SMB credentials for comprehensive host-level assessment.
- **Full reference:** `references/performing-authenticated-scan-with-openvas/SKILL.md`
- **Execution scripts:** `scripts/performing-authenticated-scan-with-openvas/`

### performing-graphql-introspection-attack
Performs GraphQL introspection attacks to extract the full API schema including types, queries, mutations, subscriptions, and field definitions from GraphQL endpoints. The tester uses introspection queries to map the attack surface, identifies sensitive fields and mutations, tests for query depth and complexity limits, and exploits GraphQL-specific vulnerabilities including batching attacks, alias-based brute force, and nested query DoS. Activates for requests involving GraphQL security testing, introspection attack, GraphQL enumeration, or GraphQL API penetration testing.

- **Full reference:** `references/performing-graphql-introspection-attack/SKILL.md`
- **Execution scripts:** `scripts/performing-graphql-introspection-attack/`

### performing-docker-bench-security-assessment
Docker Bench for Security is an open-source script that checks dozens of common best practices around deploying Docker containers in production. Based on the CIS Docker Benchmark, it audits host confi
- **Full reference:** `references/performing-docker-bench-security-assessment/SKILL.md`
- **Execution scripts:** `scripts/performing-docker-bench-security-assessment/`

### performing-soc-tabletop-exercise
Performs tabletop exercises for SOC teams simulating security incidents through discussion-based scenarios to test incident response procedures, communication workflows, and decision-making under pressure without impacting production systems. Use when organizations need to validate IR playbooks, train analysts, or meet compliance requirements for incident response testing.

- **Full reference:** `references/performing-soc-tabletop-exercise/SKILL.md`
- **Execution scripts:** `scripts/performing-soc-tabletop-exercise/`

### performing-open-source-intelligence-gathering
Open Source Intelligence (OSINT) gathering is the first active phase of a red team engagement, where operators collect publicly available information about the target organization to identify attack s
- **Full reference:** `references/performing-open-source-intelligence-gathering/SKILL.md`
- **Execution scripts:** `scripts/performing-open-source-intelligence-gathering/`

### performing-arp-spoofing-attack-simulation
Simulates ARP spoofing attacks in authorized lab or pentest environments using arpspoof, Ettercap, and Scapy to demonstrate man-in-the-middle risks, test network detection capabilities, and validate ARP inspection countermeasures.

- **Full reference:** `references/performing-arp-spoofing-attack-simulation/SKILL.md`
- **Execution scripts:** `scripts/performing-arp-spoofing-attack-simulation/`

### performing-web-application-scanning-with-nikto
Nikto is an open-source web server and web application scanner that tests against over 7,000 potentially dangerous files/programs, checks for outdated versions of over 1,250 servers, and identifies ve
- **Full reference:** `references/performing-web-application-scanning-with-nikto/SKILL.md`
- **Execution scripts:** `scripts/performing-web-application-scanning-with-nikto/`

### performing-sqlite-database-forensics
Perform forensic analysis of SQLite databases to recover deleted records from freelists and WAL files, decode encoded timestamps, and extract evidence from browser history, messaging apps, and mobile device databases.
- **Full reference:** `references/performing-sqlite-database-forensics/SKILL.md`
- **Execution scripts:** `scripts/performing-sqlite-database-forensics/`

### performing-service-account-credential-rotation
Automate credential rotation for service accounts across Active Directory, cloud platforms, and application databases to eliminate stale secrets and reduce compromise risk.
- **Full reference:** `references/performing-service-account-credential-rotation/SKILL.md`
- **Execution scripts:** `scripts/performing-service-account-credential-rotation/`

### performing-ssrf-vulnerability-exploitation
Test for Server-Side Request Forgery vulnerabilities by probing cloud metadata endpoints, internal network services, and protocol handlers through user-controllable URL parameters. Tests AWS/GCP/Azure metadata APIs (169.254.169.254), internal port scanning via HTTP, URL scheme bypass techniques, and DNS rebinding detection.
- **Full reference:** `references/performing-ssrf-vulnerability-exploitation/SKILL.md`
- **Execution scripts:** `scripts/performing-ssrf-vulnerability-exploitation/`

### performing-dns-tunneling-detection
Detects DNS tunneling by computing Shannon entropy of DNS query names, analyzing query length distributions, inspecting TXT record payloads, and identifying high subdomain cardinality. Uses scapy for packet capture analysis and statistical methods to distinguish legitimate DNS from covert channels. Use when hunting for data exfiltration.

- **Full reference:** `references/performing-dns-tunneling-detection/SKILL.md`
- **Execution scripts:** `scripts/performing-dns-tunneling-detection/`

### performing-wifi-password-cracking-with-aircrack
Captures WPA/WPA2 handshakes and performs offline password cracking using aircrack-ng, hashcat, and dictionary attacks during authorized wireless security assessments to evaluate passphrase strength and wireless network security posture.

- **Full reference:** `references/performing-wifi-password-cracking-with-aircrack/SKILL.md`
- **Execution scripts:** `scripts/performing-wifi-password-cracking-with-aircrack/`

### performing-kubernetes-cis-benchmark-with-kube-bench
Audit Kubernetes cluster security posture against CIS benchmarks using kube-bench with automated checks for control plane, worker nodes, and RBAC.
- **Full reference:** `references/performing-kubernetes-cis-benchmark-with-kube-bench/SKILL.md`
- **Execution scripts:** `scripts/performing-kubernetes-cis-benchmark-with-kube-bench/`

### performing-threat-modeling-with-owasp-threat-dragon
Use OWASP Threat Dragon to create data flow diagrams, identify threats using STRIDE and LINDDUN methodologies, and generate threat model reports for secure design review.
- **Full reference:** `references/performing-threat-modeling-with-owasp-threat-dragon/SKILL.md`
- **Execution scripts:** `scripts/performing-threat-modeling-with-owasp-threat-dragon/`

### performing-ssl-tls-security-assessment
Assess SSL/TLS server configurations using the sslyze Python library to evaluate cipher suites, certificate chains, protocol versions, HSTS headers, and known vulnerabilities like Heartbleed and ROBOT.
- **Full reference:** `references/performing-ssl-tls-security-assessment/SKILL.md`
- **Execution scripts:** `scripts/performing-ssl-tls-security-assessment/`

### performing-gcp-penetration-testing-with-gcpbucketbrute
Perform GCP security testing using GCPBucketBrute for storage bucket enumeration, gcloud IAM privilege escalation path analysis, and service account permission auditing
- **Full reference:** `references/performing-gcp-penetration-testing-with-gcpbucketbrute/SKILL.md`
- **Execution scripts:** `scripts/performing-gcp-penetration-testing-with-gcpbucketbrute/`

### performing-log-analysis-for-forensic-investigation
Collect, parse, and correlate system, application, and security logs to reconstruct events and establish timelines during forensic investigations.
- **Full reference:** `references/performing-log-analysis-for-forensic-investigation/SKILL.md`
- **Execution scripts:** `scripts/performing-log-analysis-for-forensic-investigation/`

### performing-network-forensics-with-wireshark
Capture and analyze network traffic using Wireshark and tshark to reconstruct network events, extract artifacts, and identify malicious communications.
- **Full reference:** `references/performing-network-forensics-with-wireshark/SKILL.md`
- **Execution scripts:** `scripts/performing-network-forensics-with-wireshark/`

### performing-active-directory-vulnerability-assessment
Assess Active Directory security posture using PingCastle, BloodHound, and Purple Knight to identify misconfigurations, privilege escalation paths, and attack vectors.
- **Full reference:** `references/performing-active-directory-vulnerability-assessment/SKILL.md`
- **Execution scripts:** `scripts/performing-active-directory-vulnerability-assessment/`

### performing-ransomware-response
Executes a structured ransomware incident response from initial detection through containment, forensic analysis, decryption assessment, recovery, and post-incident hardening. Addresses ransom negotiation considerations, backup integrity verification, and regulatory notification requirements. Activates for requests involving ransomware response, ransomware recovery, crypto-ransomware, data encryption attack, ransom payment decision, or ransomware containment.

- **Full reference:** `references/performing-ransomware-response/SKILL.md`
- **Execution scripts:** `scripts/performing-ransomware-response/`

### performing-binary-exploitation-analysis
Analyze binary exploitation techniques including buffer overflows and ROP chains using pwntools Python library. Covers checksec analysis, gadget discovery with ROPgadget, and exploit development for CTF and authorized security assessments.

- **Full reference:** `references/performing-binary-exploitation-analysis/SKILL.md`
- **Execution scripts:** `scripts/performing-binary-exploitation-analysis/`

### performing-ot-vulnerability-assessment-with-claroty
This skill covers performing vulnerability assessments in OT environments using the Claroty xDome platform for comprehensive asset discovery, risk scoring, vulnerability correlation, and remediation prioritization. It addresses passive vulnerability identification through traffic analysis, active safe querying of OT devices, integration with CVE databases and ICS-CERT advisories, and risk-based prioritization that accounts for operational impact and compensating controls.

- **Full reference:** `references/performing-ot-vulnerability-assessment-with-claroty/SKILL.md`
- **Execution scripts:** `scripts/performing-ot-vulnerability-assessment-with-claroty/`

### performing-timeline-reconstruction-with-plaso
Build comprehensive forensic super-timelines using Plaso (log2timeline) to correlate events across file systems, logs, and artifacts into a unified chronological view.
- **Full reference:** `references/performing-timeline-reconstruction-with-plaso/SKILL.md`
- **Execution scripts:** `scripts/performing-timeline-reconstruction-with-plaso/`

### performing-brand-monitoring-for-impersonation
Monitor for brand impersonation attacks across domains, social media, mobile apps, and dark web channels to detect phishing campaigns, fake sites, and unauthorized brand usage targeting your organization.
- **Full reference:** `references/performing-brand-monitoring-for-impersonation/SKILL.md`
- **Execution scripts:** `scripts/performing-brand-monitoring-for-impersonation/`

### performing-ios-app-security-assessment
Performs comprehensive iOS application security assessments using Frida for dynamic instrumentation, Objection for runtime exploration, SSL pinning bypass for traffic interception, keychain extraction for credential analysis, and IPA static analysis for binary-level review. Use when conducting authorized iOS penetration tests, evaluating mobile app security posture against OWASP MASTG, or assessing iOS app data protection and transport security controls. Activates for requests involving iOS app pentesting, Frida-based iOS instrumentation, mobile app SSL pinning bypass, or IPA reverse engineering.

- **Full reference:** `references/performing-ios-app-security-assessment/SKILL.md`
- **Execution scripts:** `scripts/performing-ios-app-security-assessment/`

### performing-memory-forensics-with-volatility3-plugins
Analyze memory dumps using Volatility3 plugins to detect injected code, rootkits, credential theft, and malware artifacts in Windows, Linux, and macOS memory images.
- **Full reference:** `references/performing-memory-forensics-with-volatility3-plugins/SKILL.md`
- **Execution scripts:** `scripts/performing-memory-forensics-with-volatility3-plugins/`

### performing-static-malware-analysis-with-pe-studio
Performs static analysis of Windows PE (Portable Executable) malware samples using PEStudio to examine file headers, imports, strings, resources, and indicators without executing the binary. Identifies suspicious characteristics including packing, anti-analysis techniques, and malicious imports. Activates for requests involving static malware analysis, PE file inspection, Windows executable analysis, or pre-execution malware triage.

- **Full reference:** `references/performing-static-malware-analysis-with-pe-studio/SKILL.md`
- **Execution scripts:** `scripts/performing-static-malware-analysis-with-pe-studio/`

### performing-malware-hash-enrichment-with-virustotal
Enrich malware file hashes using the VirusTotal API to retrieve detection rates, behavioral analysis, YARA matches, and contextual threat intelligence for incident triage and IOC validation.
- **Full reference:** `references/performing-malware-hash-enrichment-with-virustotal/SKILL.md`
- **Execution scripts:** `scripts/performing-malware-hash-enrichment-with-virustotal/`

### performing-android-app-static-analysis-with-mobsf
Performs automated static analysis of Android applications using Mobile Security Framework (MobSF) to identify hardcoded secrets, insecure permissions, vulnerable components, weak cryptography, and code-level security flaws without executing the application. Use when assessing Android APK/AAB files for security vulnerabilities before deployment, during penetration testing, or as part of CI/CD security gates. Activates for requests involving Android static analysis, MobSF scanning, APK security assessment, or mobile application code review.

- **Full reference:** `references/performing-android-app-static-analysis-with-mobsf/SKILL.md`
- **Execution scripts:** `scripts/performing-android-app-static-analysis-with-mobsf/`

### performing-threat-emulation-with-atomic-red-team
Executes Atomic Red Team tests for MITRE ATT&CK technique validation using the atomic-operator Python framework. Loads test definitions from YAML atomics, runs attack simulations, and validates detection coverage. Use when testing SIEM detection rules, validating EDR coverage, or conducting purple team exercises.

- **Full reference:** `references/performing-threat-emulation-with-atomic-red-team/SKILL.md`
- **Execution scripts:** `scripts/performing-threat-emulation-with-atomic-red-team/`

### performing-cloud-log-forensics-with-athena
Uses AWS Athena to query CloudTrail, VPC Flow Logs, S3 access logs, and ALB logs for forensic investigation. Covers CREATE TABLE DDL with partition projection, forensic SQL queries for detecting unauthorized access, data exfiltration, lateral movement, and privilege escalation. Use when investigating AWS security incidents or building cloud-native forensic workflows at scale.

- **Full reference:** `references/performing-cloud-log-forensics-with-athena/SKILL.md`
- **Execution scripts:** `scripts/performing-cloud-log-forensics-with-athena/`

### performing-firmware-extraction-with-binwalk
Performs firmware image extraction and analysis using binwalk to identify embedded filesystems, compressed archives, bootloaders, kernel images, and cryptographic material. Covers entropy analysis for detecting encrypted or compressed regions, recursive extraction of nested archives, SquashFS/CramFS/JFFS2 filesystem mounting, and string analysis for credential and configuration discovery. Activates for requests involving firmware reverse engineering, IoT device analysis, embedded system security assessment, or router/camera firmware extraction.

- **Full reference:** `references/performing-firmware-extraction-with-binwalk/SKILL.md`
- **Execution scripts:** `scripts/performing-firmware-extraction-with-binwalk/`

### performing-threat-hunting-with-elastic-siem
Performs proactive threat hunting in Elastic Security SIEM using KQL/EQL queries, detection rules, and Timeline investigation to identify threats that evade automated detection. Use when SOC teams need to hunt for specific ATT&CK techniques, investigate anomalous behaviors, or validate detection coverage gaps using Elasticsearch and Kibana Security.

- **Full reference:** `references/performing-threat-hunting-with-elastic-siem/SKILL.md`
- **Execution scripts:** `scripts/performing-threat-hunting-with-elastic-siem/`

### performing-privilege-escalation-on-linux
Linux privilege escalation involves elevating from a low-privilege user account to root access on a compromised system. Red teams exploit misconfigurations, vulnerable services, kernel exploits, and w
- **Full reference:** `references/performing-privilege-escalation-on-linux/SKILL.md`
- **Execution scripts:** `scripts/performing-privilege-escalation-on-linux/`

### performing-supply-chain-attack-simulation
Simulate and detect software supply chain attacks including typosquatting detection via Levenshtein distance, dependency confusion testing against private registries, package hash verification with pip, and known vulnerability scanning with pip-audit.
- **Full reference:** `references/performing-supply-chain-attack-simulation/SKILL.md`
- **Execution scripts:** `scripts/performing-supply-chain-attack-simulation/`

### performing-active-directory-penetration-test
Conduct a focused Active Directory penetration test to enumerate domain objects, discover attack paths with BloodHound, exploit Kerberos weaknesses, escalate privileges via ADCS/DCSync, and demonstrate domain compromise.
- **Full reference:** `references/performing-active-directory-penetration-test/SKILL.md`
- **Execution scripts:** `scripts/performing-active-directory-penetration-test/`

### performing-api-security-testing-with-postman
Uses Postman to perform structured API security testing by building collections that test for OWASP API Security Top 10 vulnerabilities including authentication bypass, authorization flaws, injection, and data exposure. The tester creates environments with multiple user roles, writes test scripts for automated security validation, and integrates Postman with OWASP ZAP and Newman for CI/CD security testing. Activates for requests involving Postman security testing, API security collection, automated API testing, or OWASP API testing with Postman.

- **Full reference:** `references/performing-api-security-testing-with-postman/SKILL.md`
- **Execution scripts:** `scripts/performing-api-security-testing-with-postman/`

### performing-ssl-stripping-attack
Simulates SSL stripping attacks using sslstrip, Bettercap, and mitmproxy in authorized environments to test HSTS enforcement, certificate validation, and HTTPS upgrade mechanisms that protect users from downgrade attacks on encrypted connections.

- **Full reference:** `references/performing-ssl-stripping-attack/SKILL.md`
- **Execution scripts:** `scripts/performing-ssl-stripping-attack/`

### performing-hardware-security-module-integration
Integrate Hardware Security Modules (HSMs) using PKCS#11 interface for cryptographic key management, signing operations, and secure key storage with python-pkcs11, AWS CloudHSM, and YubiHSM2.
- **Full reference:** `references/performing-hardware-security-module-integration/SKILL.md`
- **Execution scripts:** `scripts/performing-hardware-security-module-integration/`

### performing-cryptographic-audit-of-application
A cryptographic audit systematically reviews an application's use of cryptographic primitives, protocols, and key management to identify vulnerabilities such as weak algorithms, insecure modes, hardco
- **Full reference:** `references/performing-cryptographic-audit-of-application/SKILL.md`
- **Execution scripts:** `scripts/performing-cryptographic-audit-of-application/`

### performing-linux-log-forensics-investigation
Perform forensic investigation of Linux system logs including syslog, auth.log, systemd journal, kern.log, and application logs to reconstruct user activity, detect unauthorized access, and establish event timelines on compromised Linux systems.
- **Full reference:** `references/performing-linux-log-forensics-investigation/SKILL.md`
- **Execution scripts:** `scripts/performing-linux-log-forensics-investigation/`

### performing-ot-network-security-assessment
This skill covers conducting comprehensive security assessments of Operational Technology (OT) networks including SCADA systems, DCS architectures, and industrial control system communication paths. It addresses the Purdue Reference Model layers, identifies IT/OT convergence risks, evaluates firewall rules between zones, and maps industrial protocol traffic (Modbus, DNP3, OPC UA, EtherNet/IP) to detect misconfigurations, unauthorized connections, and attack surfaces in critical infrastructure.

- **Full reference:** `references/performing-ot-network-security-assessment/SKILL.md`
- **Execution scripts:** `scripts/performing-ot-network-security-assessment/`

### performing-cloud-forensics-with-aws-cloudtrail
Perform forensic investigation of AWS environments using CloudTrail logs to reconstruct attacker activity, identify compromised credentials, and analyze API call patterns.
- **Full reference:** `references/performing-cloud-forensics-with-aws-cloudtrail/SKILL.md`
- **Execution scripts:** `scripts/performing-cloud-forensics-with-aws-cloudtrail/`

### performing-web-cache-deception-attack
Execute web cache deception attacks by exploiting path normalization discrepancies between CDN caching layers and origin servers to cache and retrieve sensitive authenticated content.
- **Full reference:** `references/performing-web-cache-deception-attack/SKILL.md`
- **Execution scripts:** `scripts/performing-web-cache-deception-attack/`

### performing-cloud-native-threat-hunting-with-aws-detective
Hunt for threats in AWS environments using Detective behavior graphs, entity investigation timelines, GuardDuty finding correlation, and automated entity profiling across IAM users, EC2 instances, and IP addresses.
- **Full reference:** `references/performing-cloud-native-threat-hunting-with-aws-detective/SKILL.md`
- **Execution scripts:** `scripts/performing-cloud-native-threat-hunting-with-aws-detective/`

### performing-dynamic-analysis-with-any-run
Performs interactive dynamic malware analysis using the ANY.RUN cloud sandbox to observe real-time execution behavior, interact with malware prompts, and capture process trees, network traffic, and system changes. Activates for requests involving interactive sandbox analysis, cloud-based malware detonation, real-time behavioral observation, or ANY.RUN usage.

- **Full reference:** `references/performing-dynamic-analysis-with-any-run/SKILL.md`
- **Execution scripts:** `scripts/performing-dynamic-analysis-with-any-run/`

### performing-external-network-penetration-test
Conduct a comprehensive external network penetration test to identify vulnerabilities in internet-facing infrastructure using PTES methodology, reconnaissance, scanning, exploitation, and reporting.
- **Full reference:** `references/performing-external-network-penetration-test/SKILL.md`
- **Execution scripts:** `scripts/performing-external-network-penetration-test/`

### performing-credential-access-with-lazagne
Extract stored credentials from compromised endpoints using the LaZagne post-exploitation tool to recover passwords from browsers, databases, system vaults, and applications during authorized red team operations.
- **Full reference:** `references/performing-credential-access-with-lazagne/SKILL.md`
- **Execution scripts:** `scripts/performing-credential-access-with-lazagne/`

### performing-purple-team-exercise
Performs purple team exercises by coordinating red team adversary emulation with blue team detection validation using MITRE ATT&CK-mapped attack scenarios, real-time detection testing, and collaborative gap remediation. Use when SOC teams need to validate detection capabilities, improve analyst skills, and close detection gaps through structured offensive-defensive collaboration.

- **Full reference:** `references/performing-purple-team-exercise/SKILL.md`
- **Execution scripts:** `scripts/performing-purple-team-exercise/`

### performing-wireless-security-assessment-with-kismet
Conduct wireless network security assessments using Kismet to detect rogue access points, hidden SSIDs, weak encryption, and unauthorized clients through passive RF monitoring.
- **Full reference:** `references/performing-wireless-security-assessment-with-kismet/SKILL.md`
- **Execution scripts:** `scripts/performing-wireless-security-assessment-with-kismet/`

### performing-network-packet-capture-analysis
Perform forensic analysis of network packet captures (PCAP/PCAPNG) using Wireshark, tshark, and tcpdump to reconstruct network communications, extract transferred files, identify malicious traffic, and establish evidence of data exfiltration or command-and-control activity.
- **Full reference:** `references/performing-network-packet-capture-analysis/SKILL.md`
- **Execution scripts:** `scripts/performing-network-packet-capture-analysis/`

### performing-container-security-scanning-with-trivy
Scan container images, filesystems, and Kubernetes manifests for vulnerabilities, misconfigurations, exposed secrets, and license compliance issues using Aqua Security Trivy with SBOM generation and CI/CD integration.
- **Full reference:** `references/performing-container-security-scanning-with-trivy/SKILL.md`
- **Execution scripts:** `scripts/performing-container-security-scanning-with-trivy/`

### performing-cloud-native-forensics-with-falco
Uses Falco YAML rules for runtime threat detection in containers and Kubernetes, monitoring syscalls for shell spawns, file tampering, network anomalies, and privilege escalation. Manages Falco rules via the Falco gRPC API and parses Falco alert output. Use when building container runtime security or investigating k8s cluster compromises.

- **Full reference:** `references/performing-cloud-native-forensics-with-falco/SKILL.md`
- **Execution scripts:** `scripts/performing-cloud-native-forensics-with-falco/`

### performing-privileged-account-discovery
Discover and inventory all privileged accounts across enterprise infrastructure including domain admins, local admins, service accounts, database admins, cloud IAM roles, and application admin account
- **Full reference:** `references/performing-privileged-account-discovery/SKILL.md`
- **Execution scripts:** `scripts/performing-privileged-account-discovery/`

### performing-cloud-incident-containment-procedures
Execute cloud-native incident containment across AWS, Azure, and GCP by isolating compromised resources, revoking credentials, preserving forensic evidence, and applying security group restrictions to prevent lateral movement.
- **Full reference:** `references/performing-cloud-incident-containment-procedures/SKILL.md`
- **Execution scripts:** `scripts/performing-cloud-incident-containment-procedures/`

### performing-packet-injection-attack
Crafts and injects custom network packets using Scapy, hping3, and Nemesis during authorized security assessments to test firewall rules, IDS detection, protocol handling, and network stack resilience against malformed and spoofed traffic.

- **Full reference:** `references/performing-packet-injection-attack/SKILL.md`
- **Execution scripts:** `scripts/performing-packet-injection-attack/`

### performing-adversary-in-the-middle-phishing-detection
Detect and respond to Adversary-in-the-Middle (AiTM) phishing attacks that use reverse proxy kits like EvilProxy, Evilginx, and Tycoon 2FA to bypass MFA and steal session tokens.
- **Full reference:** `references/performing-adversary-in-the-middle-phishing-detection/SKILL.md`
- **Execution scripts:** `scripts/performing-adversary-in-the-middle-phishing-detection/`

### performing-initial-access-with-evilginx3
Perform authorized initial access using EvilGinx3 adversary-in-the-middle phishing framework to capture session tokens and bypass multi-factor authentication during red team engagements.
- **Full reference:** `references/performing-initial-access-with-evilginx3/SKILL.md`
- **Execution scripts:** `scripts/performing-initial-access-with-evilginx3/`

### performing-api-inventory-and-discovery
Performs API inventory and discovery to identify all API endpoints in an organization's environment including documented, undocumented, shadow, zombie, and deprecated APIs. The tester uses passive traffic analysis, active scanning, DNS enumeration, JavaScript analysis, and cloud resource inventory to build a comprehensive API catalog. Maps to OWASP API9:2023 Improper Inventory Management. Activates for requests involving API discovery, shadow API detection, API inventory audit, or attack surface mapping.

- **Full reference:** `references/performing-api-inventory-and-discovery/SKILL.md`
- **Execution scripts:** `scripts/performing-api-inventory-and-discovery/`

### performing-dark-web-monitoring-for-threats
Dark web monitoring involves systematically scanning Tor hidden services, underground forums, paste sites, and dark web marketplaces to identify threats targeting an organization, including leaked cre
- **Full reference:** `references/performing-dark-web-monitoring-for-threats/SKILL.md`
- **Execution scripts:** `scripts/performing-dark-web-monitoring-for-threats/`

### performing-aws-account-enumeration-with-scout-suite
Perform comprehensive security posture assessment of AWS accounts using ScoutSuite to enumerate resources, identify misconfigurations, and generate actionable security reports.
- **Full reference:** `references/performing-aws-account-enumeration-with-scout-suite/SKILL.md`
- **Execution scripts:** `scripts/performing-aws-account-enumeration-with-scout-suite/`

### performing-serverless-function-security-review
Performing security reviews of serverless functions across AWS Lambda, Azure Functions, and GCP Cloud Functions to identify overly permissive execution roles, insecure environment variables, injection vulnerabilities, and missing runtime protections.

- **Full reference:** `references/performing-serverless-function-security-review/SKILL.md`
- **Execution scripts:** `scripts/performing-serverless-function-security-review/`

### performing-graphql-depth-limit-attack
Execute and test GraphQL depth limit attacks using deeply nested recursive queries to identify denial-of-service vulnerabilities in GraphQL APIs.
- **Full reference:** `references/performing-graphql-depth-limit-attack/SKILL.md`
- **Execution scripts:** `scripts/performing-graphql-depth-limit-attack/`

### performing-soap-web-service-security-testing
Perform security testing of SOAP web services by analyzing WSDL definitions and testing for XML injection, XXE, WS-Security bypass, and SOAPAction spoofing.
- **Full reference:** `references/performing-soap-web-service-security-testing/SKILL.md`
- **Execution scripts:** `scripts/performing-soap-web-service-security-testing/`

### performing-cloud-penetration-testing-with-pacu
Performing authorized AWS penetration testing using Pacu, the open-source AWS exploitation framework, to enumerate IAM configurations, discover privilege escalation paths, test credential harvesting, and validate security controls through systematic attack simulation.

- **Full reference:** `references/performing-cloud-penetration-testing-with-pacu/SKILL.md`
- **Execution scripts:** `scripts/performing-cloud-penetration-testing-with-pacu/`

### performing-phishing-simulation-with-gophish
GoPhish is an open-source phishing simulation framework used by security teams to conduct authorized phishing awareness campaigns. It provides campaign management, email template creation, landing pag
- **Full reference:** `references/performing-phishing-simulation-with-gophish/SKILL.md`
- **Execution scripts:** `scripts/performing-phishing-simulation-with-gophish/`

### performing-post-quantum-cryptography-migration
Assesses organizational readiness for post-quantum cryptography migration per NIST FIPS 203/204/205 standards. Performs cryptographic inventory scanning to identify quantum-vulnerable algorithms (RSA, ECDH, ECDSA), evaluates hybrid TLS configurations with X25519MLKEM768, and validates CRYSTALS-Kyber (ML-KEM) and CRYSTALS-Dilithium (ML-DSA) readiness. Implements crypto-agility assessment using oqs-provider for OpenSSL. Use when planning or executing the transition from classical to post-quantum cryptographic algorithms across enterprise infrastructure.

- **Full reference:** `references/performing-post-quantum-cryptography-migration/SKILL.md`
- **Execution scripts:** `scripts/performing-post-quantum-cryptography-migration/`

### performing-blind-ssrf-exploitation
Detect and exploit blind Server-Side Request Forgery vulnerabilities using out-of-band techniques, DNS interactions, and timing analysis to access internal services and cloud metadata endpoints.
- **Full reference:** `references/performing-blind-ssrf-exploitation/SKILL.md`
- **Execution scripts:** `scripts/performing-blind-ssrf-exploitation/`

### performing-second-order-sql-injection
Detect and exploit second-order SQL injection vulnerabilities where malicious input is stored in a database and later executed in an unsafe SQL query during a different application operation.
- **Full reference:** `references/performing-second-order-sql-injection/SKILL.md`
- **Execution scripts:** `scripts/performing-second-order-sql-injection/`

### performing-memory-forensics-with-volatility3
Analyze volatile memory dumps using Volatility 3 to extract running processes, network connections, loaded modules, and evidence of malicious activity.
- **Full reference:** `references/performing-memory-forensics-with-volatility3/SKILL.md`
- **Execution scripts:** `scripts/performing-memory-forensics-with-volatility3/`

### performing-false-positive-reduction-in-siem
Perform systematic SIEM false positive reduction through rule tuning, threshold adjustment, correlation refinement, and threat intelligence enrichment to combat alert fatigue.
- **Full reference:** `references/performing-false-positive-reduction-in-siem/SKILL.md`
- **Execution scripts:** `scripts/performing-false-positive-reduction-in-siem/`

### performing-lateral-movement-detection
Detects lateral movement techniques including Pass-the-Hash, PsExec, WMI execution, RDP pivoting, and SMB-based spreading using SIEM correlation of Windows event logs, network flow data, and endpoint telemetry mapped to MITRE ATT&CK Lateral Movement (TA0008) techniques.

- **Full reference:** `references/performing-lateral-movement-detection/SKILL.md`
- **Execution scripts:** `scripts/performing-lateral-movement-detection/`

### performing-malware-ioc-extraction
Malware IOC extraction is the process of analyzing malicious software to identify actionable indicators of compromise including file hashes, network indicators (C2 domains, IP addresses, URLs), regist
- **Full reference:** `references/performing-malware-ioc-extraction/SKILL.md`
- **Execution scripts:** `scripts/performing-malware-ioc-extraction/`

### performing-wireless-network-penetration-test
Execute a wireless network penetration test to assess WiFi security by capturing handshakes, cracking WPA2/WPA3 keys, detecting rogue access points, and testing wireless segmentation using Aircrack-ng and related tools.
- **Full reference:** `references/performing-wireless-network-penetration-test/SKILL.md`
- **Execution scripts:** `scripts/performing-wireless-network-penetration-test/`

### performing-purple-team-atomic-testing
Executes Atomic Red Team tests mapped to MITRE ATT&CK techniques, performs coverage gap analysis across the ATT&CK matrix, and runs detection validation loops to measure blue team visibility. Covers Invoke-AtomicRedTeam PowerShell execution, ATT&CK Navigator layer generation for heatmaps, Sigma rule correlation, and continuous atomic testing pipelines. Activates for requests involving purple team exercises, atomic test execution, ATT&CK coverage assessment, detection engineering validation, or adversary emulation testing.

- **Full reference:** `references/performing-purple-team-atomic-testing/SKILL.md`
- **Execution scripts:** `scripts/performing-purple-team-atomic-testing/`

### performing-ip-reputation-analysis-with-shodan
Analyze IP address reputation using the Shodan API to identify open ports, running services, known vulnerabilities, and hosting context for threat intelligence enrichment and incident triage.
- **Full reference:** `references/performing-ip-reputation-analysis-with-shodan/SKILL.md`
- **Execution scripts:** `scripts/performing-ip-reputation-analysis-with-shodan/`

### performing-steganography-detection
Detect and extract hidden data embedded in images, audio, and other media files using steganalysis tools to uncover covert communication channels.
- **Full reference:** `references/performing-steganography-detection/SKILL.md`
- **Execution scripts:** `scripts/performing-steganography-detection/`

### performing-active-directory-bloodhound-analysis
Use BloodHound and SharpHound to enumerate Active Directory relationships and identify attack paths from compromised users to Domain Admin.
- **Full reference:** `references/performing-active-directory-bloodhound-analysis/SKILL.md`
- **Execution scripts:** `scripts/performing-active-directory-bloodhound-analysis/`

### performing-sca-dependency-scanning-with-snyk
This skill covers implementing Software Composition Analysis (SCA) using Snyk to detect vulnerable open-source dependencies in CI/CD pipelines. It addresses scanning package manifests and lockfiles, automated fix pull request generation, license compliance checking, continuous monitoring of deployed applications, and integration with GitHub, GitLab, and Jenkins pipelines.

- **Full reference:** `references/performing-sca-dependency-scanning-with-snyk/SKILL.md`
- **Execution scripts:** `scripts/performing-sca-dependency-scanning-with-snyk/`

### performing-insider-threat-investigation
Investigates insider threat incidents involving employees, contractors, or trusted partners who misuse authorized access to steal data, sabotage systems, or violate security policies. Combines digital forensics, user behavior analytics, and HR/legal coordination to build an evidence-based case. Activates for requests involving insider threat investigation, employee data theft, privilege misuse, user behavior anomaly, or internal threat detection.

- **Full reference:** `references/performing-insider-threat-investigation/SKILL.md`
- **Execution scripts:** `scripts/performing-insider-threat-investigation/`

### performing-firmware-malware-analysis
Analyzes firmware images for embedded malware, backdoors, and unauthorized modifications targeting routers, IoT devices, UEFI/BIOS, and embedded systems. Covers firmware extraction, filesystem analysis, binary reverse engineering, and bootkit detection. Activates for requests involving firmware security analysis, IoT malware investigation, UEFI rootkit detection, or embedded device compromise assessment.

- **Full reference:** `references/performing-firmware-malware-analysis/SKILL.md`
- **Execution scripts:** `scripts/performing-firmware-malware-analysis/`

### performing-api-fuzzing-with-restler
Uses Microsoft RESTler to perform stateful REST API fuzzing by automatically generating and executing test sequences that exercise API endpoints, discover producer-consumer dependencies between requests, and find security and reliability bugs. The tester compiles an OpenAPI specification into a RESTler fuzzing grammar, configures authentication, runs test/fuzz-lean/fuzz modes, and analyzes results for 500 errors, authentication bypasses, resource leaks, and payload injection vulnerabilities. Activates for requests involving API fuzzing, RESTler testing, stateful API testing, or automated API security scanning.

- **Full reference:** `references/performing-api-fuzzing-with-restler/SKILL.md`
- **Execution scripts:** `scripts/performing-api-fuzzing-with-restler/`

### performing-api-rate-limiting-bypass
Tests API rate limiting implementations for bypass vulnerabilities by manipulating request headers, IP addresses, HTTP methods, API versions, and encoding schemes to circumvent request throttling controls. The tester identifies rate limit headers, determines enforcement mechanisms, and attempts bypasses including X-Forwarded-For spoofing, parameter pollution, case variation, and endpoint path manipulation. Maps to OWASP API4:2023 Unrestricted Resource Consumption. Activates for requests involving rate limit bypass, API throttling evasion, brute force protection testing, or API abuse prevention assessment.

- **Full reference:** `references/performing-api-rate-limiting-bypass/SKILL.md`
- **Execution scripts:** `scripts/performing-api-rate-limiting-bypass/`

### performing-fuzzing-with-aflplusplus
Perform coverage-guided fuzzing of compiled binaries using AFL++ (American Fuzzy Lop Plus Plus) to discover memory corruption, crashes, and security vulnerabilities. The tester instruments target binaries with afl-cc/afl-clang-fast, manages input corpora with afl-cmin and afl-tmin, runs parallel fuzzing campaigns with afl-fuzz, and triages crashes using CASR or GDB scripts. Activates for requests involving binary fuzzing, crash discovery, coverage-guided testing, or AFL++ fuzzing campaigns.

- **Full reference:** `references/performing-fuzzing-with-aflplusplus/SKILL.md`
- **Execution scripts:** `scripts/performing-fuzzing-with-aflplusplus/`

### performing-deception-technology-deployment
Deploys deception technology including honeypots, honeytokens, and decoy systems to detect attackers who have bypassed perimeter defenses, providing high-fidelity alerts with near-zero false positive rates. Use when SOC teams need early warning of lateral movement, credential abuse, or internal reconnaissance by deploying convincing traps across the network.

- **Full reference:** `references/performing-deception-technology-deployment/SKILL.md`
- **Execution scripts:** `scripts/performing-deception-technology-deployment/`

### performing-malware-triage-with-yara
Performs rapid malware triage and classification using YARA rules to match file patterns, strings, byte sequences, and structural characteristics against known malware families and suspicious indicators. Covers rule writing, scanning, and integration with analysis pipelines. Activates for requests involving YARA rule creation, malware classification, pattern matching, sample triage, or signature-based detection.

- **Full reference:** `references/performing-malware-triage-with-yara/SKILL.md`
- **Execution scripts:** `scripts/performing-malware-triage-with-yara/`

### performing-dmarc-policy-enforcement-rollout
Execute a phased DMARC rollout from p=none monitoring through p=quarantine to p=reject enforcement, ensuring all legitimate email sources are authenticated before blocking unauthorized senders.
- **Full reference:** `references/performing-dmarc-policy-enforcement-rollout/SKILL.md`
- **Execution scripts:** `scripts/performing-dmarc-policy-enforcement-rollout/`

### performing-endpoint-forensics-investigation
Performs digital forensics investigation on compromised endpoints including memory acquisition, disk imaging, artifact analysis, and timeline reconstruction. Use when investigating security incidents, collecting evidence for legal proceedings, or analyzing endpoint compromise scope. Activates for requests involving endpoint forensics, memory analysis, disk forensics, or incident investigation.

- **Full reference:** `references/performing-endpoint-forensics-investigation/SKILL.md`
- **Execution scripts:** `scripts/performing-endpoint-forensics-investigation/`

### performing-threat-hunting-with-yara-rules
Use YARA pattern-matching rules to hunt for malware, suspicious files, and indicators of compromise across filesystems and memory dumps. Covers rule authoring, yara-python scanning, and integration with threat intel feeds.

- **Full reference:** `references/performing-threat-hunting-with-yara-rules/SKILL.md`
- **Execution scripts:** `scripts/performing-threat-hunting-with-yara-rules/`

### performing-access-review-and-certification
Conduct systematic access reviews and certifications to ensure users have appropriate access rights aligned with their roles. This skill covers review campaign design, reviewer selection, risk-based p
- **Full reference:** `references/performing-access-review-and-certification/SKILL.md`
- **Execution scripts:** `scripts/performing-access-review-and-certification/`

### performing-oauth-scope-minimization-review
Performs OAuth 2.0 scope minimization review to identify over-permissioned third-party application integrations, excessive API scopes, unused token grants, and risky OAuth consent patterns across identity providers and SaaS platforms. Activates for requests involving OAuth scope audit, API permission review, third-party app risk assessment, or consent grant minimization.

- **Full reference:** `references/performing-oauth-scope-minimization-review/SKILL.md`
- **Execution scripts:** `scripts/performing-oauth-scope-minimization-review/`

### performing-jwt-none-algorithm-attack
Execute and test the JWT none algorithm attack to bypass signature verification by manipulating the alg header field in JSON Web Tokens.
- **Full reference:** `references/performing-jwt-none-algorithm-attack/SKILL.md`
- **Execution scripts:** `scripts/performing-jwt-none-algorithm-attack/`

### performing-scada-hmi-security-assessment
Perform security assessments of SCADA Human-Machine Interface (HMI) systems to identify vulnerabilities in web-based HMIs, thin-client configurations, authentication mechanisms, and communication channels between HMI and PLCs, aligned with IEC 62443 and NIST SP 800-82 guidelines.

- **Full reference:** `references/performing-scada-hmi-security-assessment/SKILL.md`
- **Execution scripts:** `scripts/performing-scada-hmi-security-assessment/`

### performing-cloud-forensics-investigation
Conduct forensic investigations in cloud environments by collecting and analyzing logs, snapshots, and metadata from AWS, Azure, and GCP services.
- **Full reference:** `references/performing-cloud-forensics-investigation/SKILL.md`
- **Execution scripts:** `scripts/performing-cloud-forensics-investigation/`

### performing-malware-persistence-investigation
Systematically investigate all persistence mechanisms on Windows and Linux systems to identify how malware survives reboots and maintains access.
- **Full reference:** `references/performing-malware-persistence-investigation/SKILL.md`
- **Execution scripts:** `scripts/performing-malware-persistence-investigation/`

### performing-alert-triage-with-elastic-siem
Perform systematic alert triage in Elastic Security SIEM to rapidly classify, prioritize, and investigate security alerts for SOC operations.
- **Full reference:** `references/performing-alert-triage-with-elastic-siem/SKILL.md`
- **Execution scripts:** `scripts/performing-alert-triage-with-elastic-siem/`

### performing-ics-asset-discovery-with-claroty
Perform comprehensive ICS/OT asset discovery using Claroty xDome platform, leveraging passive monitoring, Claroty Edge active queries, and integration ecosystem to gain full visibility into industrial control system assets including PLCs, RTUs, HMIs, and network infrastructure across Purdue Model levels.

- **Full reference:** `references/performing-ics-asset-discovery-with-claroty/SKILL.md`
- **Execution scripts:** `scripts/performing-ics-asset-discovery-with-claroty/`

### performing-power-grid-cybersecurity-assessment
This skill covers conducting cybersecurity assessments of electric power grid infrastructure including generation facilities, transmission substations, distribution systems, and energy management system (EMS) control centers. It addresses NERC CIP compliance verification, substation automation security, IEC 61850 protocol analysis, synchrophasor (PMU) network security, and the unique threat landscape targeting power grid operations as demonstrated by Industroyer/CrashOverride and related attacks.

- **Full reference:** `references/performing-power-grid-cybersecurity-assessment/SKILL.md`
- **Execution scripts:** `scripts/performing-power-grid-cybersecurity-assessment/`

### performing-hash-cracking-with-hashcat
Hash cracking is an essential skill for penetration testers and security auditors to evaluate password strength. Hashcat is the world's fastest password recovery tool, supporting over 300 hash types w
- **Full reference:** `references/performing-hash-cracking-with-hashcat/SKILL.md`
- **Execution scripts:** `scripts/performing-hash-cracking-with-hashcat/`

### performing-endpoint-vulnerability-remediation
Performs vulnerability remediation on endpoints by prioritizing CVEs based on risk scoring, deploying patches, applying configuration changes, and validating fixes. Use when remediating findings from vulnerability scans, responding to critical CVE advisories, or maintaining endpoint compliance with patch management SLAs. Activates for requests involving vulnerability remediation, CVE patching, endpoint vulnerability management, or security fix deployment.

- **Full reference:** `references/performing-endpoint-vulnerability-remediation/SKILL.md`
- **Execution scripts:** `scripts/performing-endpoint-vulnerability-remediation/`

### performing-vulnerability-scanning-with-nessus
Performs authenticated and unauthenticated vulnerability scanning using Tenable Nessus to identify known vulnerabilities, misconfigurations, default credentials, and missing patches across network infrastructure, servers, and applications. The scanner correlates findings with CVE databases and CVSS scores to produce prioritized remediation guidance. Activates for requests involving vulnerability scanning, Nessus assessment, patch compliance checking, or automated vulnerability detection.

- **Full reference:** `references/performing-vulnerability-scanning-with-nessus/SKILL.md`
- **Execution scripts:** `scripts/performing-vulnerability-scanning-with-nessus/`

### performing-active-directory-compromise-investigation
Investigate Active Directory compromise by analyzing authentication logs, replication metadata, Group Policy changes, and Kerberos ticket anomalies to identify attacker persistence and lateral movement paths.
- **Full reference:** `references/performing-active-directory-compromise-investigation/SKILL.md`
- **Execution scripts:** `scripts/performing-active-directory-compromise-investigation/`

### performing-cve-prioritization-with-kev-catalog
Leverage the CISA Known Exploited Vulnerabilities catalog alongside EPSS and CVSS to prioritize CVE remediation based on real-world exploitation evidence.
- **Full reference:** `references/performing-cve-prioritization-with-kev-catalog/SKILL.md`
- **Execution scripts:** `scripts/performing-cve-prioritization-with-kev-catalog/`

### performing-vlan-hopping-attack
Simulates VLAN hopping attacks using switch spoofing and double tagging techniques in authorized environments to test VLAN segmentation effectiveness and validate switch port security configurations against Layer 2 bypass attacks.

- **Full reference:** `references/performing-vlan-hopping-attack/SKILL.md`
- **Execution scripts:** `scripts/performing-vlan-hopping-attack/`

### performing-asset-criticality-scoring-for-vulns
Develop and apply a multi-factor asset criticality scoring model to weight vulnerability prioritization based on business impact, data sensitivity, and operational importance.
- **Full reference:** `references/performing-asset-criticality-scoring-for-vulns/SKILL.md`
- **Execution scripts:** `scripts/performing-asset-criticality-scoring-for-vulns/`

### performing-mobile-app-certificate-pinning-bypass
Bypasses SSL/TLS certificate pinning implementations in Android and iOS applications to enable traffic interception during authorized security assessments. Covers OkHttp, TrustManager, NSURLSession, and third-party pinning library bypass techniques using Frida, Objection, and custom scripts. Activates for requests involving certificate pinning bypass, SSL pinning defeat, mobile TLS interception, or proxy-resistant app testing.

- **Full reference:** `references/performing-mobile-app-certificate-pinning-bypass/SKILL.md`
- **Execution scripts:** `scripts/performing-mobile-app-certificate-pinning-bypass/`

### performing-nist-csf-maturity-assessment
The NIST Cybersecurity Framework (CSF) 2.0, released in February 2024, provides a comprehensive taxonomy for managing cybersecurity risk through six core Functions - Govern, Identify, Protect, Detect, Respond, and Recover. This skill covers conducting a maturity assessment against the CSF using Implementation Tiers to measure organizational cybersecurity posture and create improvement roadmaps.
- **Full reference:** `references/performing-nist-csf-maturity-assessment/SKILL.md`
- **Execution scripts:** `scripts/performing-nist-csf-maturity-assessment/`

### performing-web-application-vulnerability-triage
Triage web application vulnerability findings from DAST/SAST scanners using OWASP risk rating methodology to separate true positives from false positives and prioritize remediation.
- **Full reference:** `references/performing-web-application-vulnerability-triage/SKILL.md`
- **Execution scripts:** `scripts/performing-web-application-vulnerability-triage/`

### performing-dns-enumeration-and-zone-transfer
Enumerates DNS records, attempts zone transfers, brute-forces subdomains, and maps DNS infrastructure during authorized reconnaissance to identify attack surface, misconfigurations, and information disclosure in target domains.

- **Full reference:** `references/performing-dns-enumeration-and-zone-transfer/SKILL.md`
- **Execution scripts:** `scripts/performing-dns-enumeration-and-zone-transfer/`

### performing-clickjacking-attack-test
Testing web applications for clickjacking vulnerabilities by assessing frame embedding controls and crafting proof-of-concept overlay attacks during authorized security assessments.
- **Full reference:** `references/performing-clickjacking-attack-test/SKILL.md`
- **Execution scripts:** `scripts/performing-clickjacking-attack-test/`

### performing-ssl-tls-inspection-configuration
Configure SSL/TLS inspection on network security devices to decrypt, inspect, and re-encrypt HTTPS traffic for threat detection while managing certificates, exemptions, and privacy compliance.
- **Full reference:** `references/performing-ssl-tls-inspection-configuration/SKILL.md`
- **Execution scripts:** `scripts/performing-ssl-tls-inspection-configuration/`

### performing-csrf-attack-simulation
Testing web applications for Cross-Site Request Forgery vulnerabilities by crafting forged requests that exploit authenticated user sessions during authorized security assessments.
- **Full reference:** `references/performing-csrf-attack-simulation/SKILL.md`
- **Execution scripts:** `scripts/performing-csrf-attack-simulation/`

### performing-cloud-storage-forensic-acquisition
Perform forensic acquisition and analysis of cloud storage services including Google Drive, OneDrive, Dropbox, and Box by collecting both API-based remote data and local sync client artifacts from endpoint devices.
- **Full reference:** `references/performing-cloud-storage-forensic-acquisition/SKILL.md`
- **Execution scripts:** `scripts/performing-cloud-storage-forensic-acquisition/`

### performing-windows-artifact-analysis-with-eric-zimmerman-tools
Perform comprehensive Windows forensic artifact analysis using Eric Zimmerman's open-source EZ Tools suite including KAPE, MFTECmd, PECmd, LECmd, JLECmd, and Timeline Explorer for parsing registry hives, prefetch files, event logs, and file system metadata.
- **Full reference:** `references/performing-windows-artifact-analysis-with-eric-zimmerman-tools/SKILL.md`
- **Execution scripts:** `scripts/performing-windows-artifact-analysis-with-eric-zimmerman-tools/`

### performing-soc2-type2-audit-preparation
Automates SOC 2 Type II audit preparation including gap assessment against AICPA Trust Services Criteria (CC1-CC9), evidence collection from cloud providers and identity systems, control testing validation, remediation tracking, and continuous compliance monitoring. Covers all five TSC categories (Security, Availability, Processing Integrity, Confidentiality, Privacy) with automated evidence gathering from AWS, Azure, GCP, Okta, GitHub, and Jira. Use when preparing for or maintaining SOC 2 Type II certification.

- **Full reference:** `references/performing-soc2-type2-audit-preparation/SKILL.md`
- **Execution scripts:** `scripts/performing-soc2-type2-audit-preparation/`

### performing-active-directory-forest-trust-attack
Enumerate and audit Active Directory forest trust relationships using impacket for SID filtering analysis, trust key extraction, cross-forest SID history abuse detection, and inter-realm Kerberos ticket assessment.
- **Full reference:** `references/performing-active-directory-forest-trust-attack/SKILL.md`
- **Execution scripts:** `scripts/performing-active-directory-forest-trust-attack/`

### performing-web-application-penetration-test
Performs systematic security testing of web applications following the OWASP Web Security Testing Guide (WSTG) methodology to identify vulnerabilities in authentication, authorization, input validation, session management, and business logic. The tester uses Burp Suite as the primary interception proxy alongside manual testing techniques to find flaws that automated scanners miss. Activates for requests involving web app pentest, OWASP testing, application security assessment, or web vulnerability testing.

- **Full reference:** `references/performing-web-application-penetration-test/SKILL.md`
- **Execution scripts:** `scripts/performing-web-application-penetration-test/`

### performing-yara-rule-development-for-detection
Develop precise YARA rules for malware detection by identifying unique byte patterns, strings, and behavioral indicators in executable files while minimizing false positives.
- **Full reference:** `references/performing-yara-rule-development-for-detection/SKILL.md`
- **Execution scripts:** `scripts/performing-yara-rule-development-for-detection/`

### performing-mobile-device-forensics-with-cellebrite
Acquire and analyze mobile device data using Cellebrite UFED and open-source tools to extract communications, location data, and application artifacts.
- **Full reference:** `references/performing-mobile-device-forensics-with-cellebrite/SKILL.md`
- **Execution scripts:** `scripts/performing-mobile-device-forensics-with-cellebrite/`

### performing-plc-firmware-security-analysis
This skill covers analyzing Programmable Logic Controller (PLC) firmware for security vulnerabilities including hardcoded credentials, insecure update mechanisms, backdoor functions, memory corruption flaws, and undocumented debug interfaces. It addresses firmware extraction from common PLC platforms (Siemens S7, Allen-Bradley, Schneider Modicon), static analysis of firmware images, dynamic analysis in emulated environments, and comparison against known-good baselines to detect tampering.

- **Full reference:** `references/performing-plc-firmware-security-analysis/SKILL.md`
- **Execution scripts:** `scripts/performing-plc-firmware-security-analysis/`

### performing-osint-with-spiderfoot
Automate OSINT collection using SpiderFoot REST API and CLI for target profiling, module-based reconnaissance, and structured result analysis across 200+ data sources
- **Full reference:** `references/performing-osint-with-spiderfoot/SKILL.md`
- **Execution scripts:** `scripts/performing-osint-with-spiderfoot/`

### performing-graphql-security-assessment
Assessing GraphQL API endpoints for introspection leaks, injection attacks, authorization flaws, and denial-of-service vulnerabilities during authorized security tests.
- **Full reference:** `references/performing-graphql-security-assessment/SKILL.md`
- **Execution scripts:** `scripts/performing-graphql-security-assessment/`

### performing-kubernetes-penetration-testing
Kubernetes penetration testing systematically evaluates cluster security by simulating attacker techniques against the API server, kubelet, etcd, pods, RBAC, network policies, and secrets. Using tools
- **Full reference:** `references/performing-kubernetes-penetration-testing/SKILL.md`
- **Execution scripts:** `scripts/performing-kubernetes-penetration-testing/`

### performing-web-cache-poisoning-attack
Exploiting web cache mechanisms to serve malicious content to other users by poisoning cached responses through unkeyed headers and parameters during authorized security tests.
- **Full reference:** `references/performing-web-cache-poisoning-attack/SKILL.md`
- **Execution scripts:** `scripts/performing-web-cache-poisoning-attack/`

### performing-red-team-with-covenant
Conduct red team operations using the Covenant C2 framework for authorized adversary simulation, including listener setup, grunt deployment, task execution, and lateral movement tracking.
- **Full reference:** `references/performing-red-team-with-covenant/SKILL.md`
- **Execution scripts:** `scripts/performing-red-team-with-covenant/`