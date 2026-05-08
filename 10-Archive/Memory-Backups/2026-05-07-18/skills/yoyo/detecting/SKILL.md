---
name: detecting
domain: red-teaming
tags:
- detecting
- class-level
- umbrella
status: active
version: 1.0.0
description: Consolidated umbrella for detecting-* skills.
---
## Included Capabilities

### detecting-cloud-threats-with-guardduty
This skill teaches security teams how to deploy and operationalize Amazon GuardDuty for continuous threat detection across AWS accounts and workloads. It covers enabling protection plans for S3, EKS, EC2 runtime monitoring, and Lambda, interpreting finding severity levels, and building automated response workflows using EventBridge and Lambda.

- **Full reference:** `references/detecting-cloud-threats-with-guardduty/SKILL.md`
- **Execution scripts:** `scripts/detecting-cloud-threats-with-guardduty/`

### detecting-privilege-escalation-in-kubernetes-pods
Detect and prevent privilege escalation in Kubernetes pods by monitoring security contexts, capabilities, and syscall patterns with Falco and OPA policies.
- **Full reference:** `references/detecting-privilege-escalation-in-kubernetes-pods/SKILL.md`
- **Execution scripts:** `scripts/detecting-privilege-escalation-in-kubernetes-pods/`

### detecting-ai-model-prompt-injection-attacks
Detects prompt injection attacks targeting LLM-based applications using a multi-layered defense combining regex pattern matching for known attack signatures, heuristic scoring for structural anomalies, and transformer-based classification with DeBERTa models. The detector analyzes user inputs before they reach the LLM, flagging direct injections (system prompt overrides, role-play escapes, instruction hijacking) and indirect injections (encoded payloads, multi-language obfuscation, delimiter-based escapes). Based on the OWASP LLM Top 10 (LLM01:2025 Prompt Injection) and Simon Willison's prompt injection taxonomy. Activates for requests involving prompt injection detection, LLM input sanitization, AI security scanning, or prompt attack classification.

- **Full reference:** `references/detecting-ai-model-prompt-injection-attacks/SKILL.md`
- **Execution scripts:** `scripts/detecting-ai-model-prompt-injection-attacks/`

### detecting-aws-credential-exposure-with-trufflehog
Detecting exposed AWS credentials in source code repositories, CI/CD pipelines, and configuration files using TruffleHog, git-secrets, and AWS-native detection mechanisms to prevent credential theft and unauthorized account access.

- **Full reference:** `references/detecting-aws-credential-exposure-with-trufflehog/SKILL.md`
- **Execution scripts:** `scripts/detecting-aws-credential-exposure-with-trufflehog/`

### detecting-serverless-function-injection
Detects and prevents code injection attacks targeting serverless functions (AWS Lambda, Azure Functions, Google Cloud Functions) through event source poisoning, malicious layer injection, runtime command execution, and IAM privilege escalation via function modification. The analyst combines static analysis of function code, CloudTrail event correlation, runtime behavior monitoring, and IAM policy auditing to identify injection vectors across the expanded serverless attack surface including API Gateway, S3, SQS, DynamoDB Streams, and CloudWatch event triggers. Activates for requests involving Lambda security assessment, serverless injection detection, function event poisoning analysis, or serverless privilege escalation investigation.

- **Full reference:** `references/detecting-serverless-function-injection/SKILL.md`
- **Execution scripts:** `scripts/detecting-serverless-function-injection/`

### detecting-mobile-malware-behavior
Detects and analyzes malicious behavior in mobile applications through behavioral analysis, permission abuse detection, network traffic monitoring, and dynamic instrumentation. Use when analyzing suspicious mobile applications for data exfiltration, command-and-control communication, credential stealing, SMS interception, or other malware indicators. Activates for requests involving mobile malware analysis, app behavior monitoring, trojan detection, or suspicious app investigation.

- **Full reference:** `references/detecting-mobile-malware-behavior/SKILL.md`
- **Execution scripts:** `scripts/detecting-mobile-malware-behavior/`

### detecting-container-escape-attempts
Container escape is a critical attack technique where an adversary breaks out of container isolation to access the host system or other containers. Detection involves monitoring for escape indicators
- **Full reference:** `references/detecting-container-escape-attempts/SKILL.md`
- **Execution scripts:** `scripts/detecting-container-escape-attempts/`

### detecting-lateral-movement-in-network
Identifies lateral movement techniques in enterprise networks by analyzing authentication logs, network flows, SMB traffic, and RDP sessions using Zeek, Velociraptor, and SIEM correlation rules to detect attackers moving between systems.

- **Full reference:** `references/detecting-lateral-movement-in-network/SKILL.md`
- **Execution scripts:** `scripts/detecting-lateral-movement-in-network/`

### detecting-suspicious-oauth-application-consent
Detect risky OAuth application consent grants in Azure AD / Microsoft Entra ID using Microsoft Graph API, audit logs, and permission analysis to identify illicit consent grant attacks.
- **Full reference:** `references/detecting-suspicious-oauth-application-consent/SKILL.md`
- **Execution scripts:** `scripts/detecting-suspicious-oauth-application-consent/`

### detecting-rootkit-activity
Detects rootkit presence on compromised systems by identifying hidden processes, hooked system calls, modified kernel structures, hidden files, and covert network connections using memory forensics, cross-view detection, and integrity checking techniques. Activates for requests involving rootkit detection, hidden process discovery, kernel integrity checking, or system call hook analysis.

- **Full reference:** `references/detecting-rootkit-activity/SKILL.md`
- **Execution scripts:** `scripts/detecting-rootkit-activity/`

### detecting-insider-threat-behaviors
Detect insider threat behavioral indicators including unusual data access, off-hours activity, mass file downloads, privilege abuse, and resignation-correlated data theft.
- **Full reference:** `references/detecting-insider-threat-behaviors/SKILL.md`
- **Execution scripts:** `scripts/detecting-insider-threat-behaviors/`

### detecting-credential-dumping-techniques
Detect LSASS credential dumping, SAM database extraction, and NTDS.dit theft using Sysmon Event ID 10, Windows Security logs, and SIEM correlation rules
- **Full reference:** `references/detecting-credential-dumping-techniques/SKILL.md`
- **Execution scripts:** `scripts/detecting-credential-dumping-techniques/`

### detecting-shadow-api-endpoints
Discover and inventory shadow API endpoints that operate outside documented specifications using traffic analysis, code scanning, and API discovery platforms.
- **Full reference:** `references/detecting-shadow-api-endpoints/SKILL.md`
- **Execution scripts:** `scripts/detecting-shadow-api-endpoints/`

### detecting-supply-chain-attacks-in-ci-cd
Scans GitHub Actions workflows and CI/CD pipeline configurations for supply chain attack vectors including unpinned actions, script injection via expressions, dependency confusion, and secrets exposure. Uses PyGithub and YAML parsing for automated audit. Use when hardening CI/CD pipelines or investigating compromised build systems.

- **Full reference:** `references/detecting-supply-chain-attacks-in-ci-cd/SKILL.md`
- **Execution scripts:** `scripts/detecting-supply-chain-attacks-in-ci-cd/`

### detecting-bluetooth-low-energy-attacks
Detects and analyzes Bluetooth Low Energy (BLE) security attacks including sniffing, replay attacks, GATT enumeration abuse, and Man-in-the-Middle interception. Uses Ubertooth One and nRF52840 sniffers for packet capture, the bleak Python library for GATT service enumeration, and crackle for BLE encryption cracking. Use when assessing IoT device BLE security, monitoring for BLE-based attacks on wireless infrastructure, or performing authorized BLE penetration testing. Activates for requests involving BLE security assessment, Ubertooth sniffing, GATT enumeration, or BLE replay detection.

- **Full reference:** `references/detecting-bluetooth-low-energy-attacks/SKILL.md`
- **Execution scripts:** `scripts/detecting-bluetooth-low-energy-attacks/`

### detecting-privilege-escalation-attempts
Detect privilege escalation attempts including token manipulation, UAC bypass, unquoted service paths, kernel exploits, and sudo/doas abuse across Windows and Linux.
- **Full reference:** `references/detecting-privilege-escalation-attempts/SKILL.md`
- **Execution scripts:** `scripts/detecting-privilege-escalation-attempts/`

### detecting-wmi-persistence
Detect WMI event subscription persistence by analyzing Sysmon Event IDs 19, 20, and 21 for malicious EventFilter, EventConsumer, and FilterToConsumerBinding creation.
- **Full reference:** `references/detecting-wmi-persistence/SKILL.md`
- **Execution scripts:** `scripts/detecting-wmi-persistence/`

### detecting-dns-exfiltration-with-dns-query-analysis
Detect data exfiltration through DNS tunneling by analyzing query entropy, subdomain length, query volume, TXT record abuse, and response payload sizes using passive DNS monitoring.
- **Full reference:** `references/detecting-dns-exfiltration-with-dns-query-analysis/SKILL.md`
- **Execution scripts:** `scripts/detecting-dns-exfiltration-with-dns-query-analysis/`

### detecting-shadow-it-cloud-usage
Detect unauthorized SaaS and cloud service usage (shadow IT) by analyzing proxy logs, DNS query logs, and netflow data using Python pandas for traffic pattern analysis and domain classification.
- **Full reference:** `references/detecting-shadow-it-cloud-usage/SKILL.md`
- **Execution scripts:** `scripts/detecting-shadow-it-cloud-usage/`

### detecting-evasion-techniques-in-endpoint-logs
Detects defense evasion techniques used by adversaries in endpoint logs including log tampering, timestomping, process injection, and security tool disabling. Use when investigating suspicious endpoint behavior, building detection rules for evasion tactics, or conducting threat hunting for stealthy adversary activity. Activates for requests involving evasion detection, defense evasion analysis, log tampering detection, or MITRE ATT&CK TA0005.

- **Full reference:** `references/detecting-evasion-techniques-in-endpoint-logs/SKILL.md`
- **Execution scripts:** `scripts/detecting-evasion-techniques-in-endpoint-logs/`

### detecting-fileless-malware-techniques
Detects and analyzes fileless malware that operates entirely in memory using PowerShell, WMI, .NET reflection, registry-resident payloads, and living-off-the-land binaries (LOLBins) without writing traditional executable files to disk. Activates for requests involving fileless threat detection, in-memory malware investigation, LOLBin abuse analysis, or WMI persistence examination.

- **Full reference:** `references/detecting-fileless-malware-techniques/SKILL.md`
- **Execution scripts:** `scripts/detecting-fileless-malware-techniques/`

### detecting-anomalous-authentication-patterns
Detects anomalous authentication patterns using UEBA analytics, statistical baselines, and machine learning models to identify impossible travel, credential stuffing, brute force, password spraying, and compromised account behaviors across authentication logs. Activates for requests involving authentication anomaly detection, login behavior analysis, UEBA implementation, or suspicious sign-in investigation.

- **Full reference:** `references/detecting-anomalous-authentication-patterns/SKILL.md`
- **Execution scripts:** `scripts/detecting-anomalous-authentication-patterns/`

### detecting-command-and-control-over-dns
Detects command-and-control (C2) communications tunneled through DNS protocol including DNS tunneling tools (Iodine, dnscat2, dns2tcp, Cobalt Strike DNS beacon), domain generation algorithms (DGA), encoded payload delivery via TXT/CNAME records, and DNS beaconing patterns. Covers Shannon entropy analysis of query subdomains, statistical anomaly detection, ML-based DGA classification, passive DNS correlation, and Zeek/Suricata signature development. Activates for requests involving DNS-based C2 detection, DNS tunnel identification, suspicious DNS traffic investigation, or DGA domain classification.

- **Full reference:** `references/detecting-command-and-control-over-dns/SKILL.md`
- **Execution scripts:** `scripts/detecting-command-and-control-over-dns/`

### detecting-ransomware-precursors-in-network
Detects early-stage ransomware indicators in network traffic before encryption begins, including initial access broker activity, command-and-control beaconing, credential harvesting, reconnaissance scanning, and staging behavior. Uses network detection tools (Zeek, Suricata, Arkime), SIEM correlation rules, and threat intelligence feeds to identify ransomware precursor patterns such as Cobalt Strike beacons, Mimikatz network signatures, and RDP brute-force attempts. Activates for requests involving pre-ransomware detection, network-based ransomware indicators, or early warning ransomware monitoring.

- **Full reference:** `references/detecting-ransomware-precursors-in-network/SKILL.md`
- **Execution scripts:** `scripts/detecting-ransomware-precursors-in-network/`

### detecting-insider-threat-with-ueba
Implement User and Entity Behavior Analytics using Elasticsearch/OpenSearch to build behavioral baselines, calculate anomaly scores, perform peer group analysis, and detect insider threat indicators such as data exfiltration, privilege abuse, and unauthorized access patterns.
- **Full reference:** `references/detecting-insider-threat-with-ueba/SKILL.md`
- **Execution scripts:** `scripts/detecting-insider-threat-with-ueba/`

### detecting-service-account-abuse
Detect abuse of service accounts through anomalous interactive logons, privilege escalation, lateral movement, and unauthorized access patterns.
- **Full reference:** `references/detecting-service-account-abuse/SKILL.md`
- **Execution scripts:** `scripts/detecting-service-account-abuse/`

### detecting-network-scanning-with-ids-signatures
Detect network reconnaissance and port scanning using Suricata and Snort IDS signatures, threshold-based detection rules, and traffic anomaly analysis to identify Nmap, Masscan, and custom scanning activity.
- **Full reference:** `references/detecting-network-scanning-with-ids-signatures/SKILL.md`
- **Execution scripts:** `scripts/detecting-network-scanning-with-ids-signatures/`

### detecting-kerberoasting-attacks
Detect Kerberoasting attacks by monitoring for anomalous Kerberos TGS requests targeting service accounts with SPNs for offline password cracking.
- **Full reference:** `references/detecting-kerberoasting-attacks/SKILL.md`
- **Execution scripts:** `scripts/detecting-kerberoasting-attacks/`

### detecting-t1003-credential-dumping-with-edr
Detect OS credential dumping techniques targeting LSASS memory, SAM database, NTDS.dit, and cached credentials using EDR telemetry, Sysmon process access monitoring, and Windows security event correlation.
- **Full reference:** `references/detecting-t1003-credential-dumping-with-edr/SKILL.md`
- **Execution scripts:** `scripts/detecting-t1003-credential-dumping-with-edr/`

### detecting-fileless-attacks-on-endpoints
Detects fileless malware and in-memory attacks that execute entirely in RAM without writing persistent files to disk, evading traditional antivirus. Use when building detections for PowerShell-based attacks, reflective DLL injection, WMI persistence, and registry-resident malware. Activates for requests involving fileless malware detection, in-memory attacks, PowerShell exploitation, or living-off-the-land techniques.

- **Full reference:** `references/detecting-fileless-attacks-on-endpoints/SKILL.md`
- **Execution scripts:** `scripts/detecting-fileless-attacks-on-endpoints/`

### detecting-arp-poisoning-in-network-traffic
Detect and prevent ARP spoofing attacks using ARPWatch, Dynamic ARP Inspection, Wireshark analysis, and custom monitoring scripts to protect against man-in-the-middle interception.
- **Full reference:** `references/detecting-arp-poisoning-in-network-traffic/SKILL.md`
- **Execution scripts:** `scripts/detecting-arp-poisoning-in-network-traffic/`

### detecting-aws-iam-privilege-escalation
Detect AWS IAM privilege escalation paths using boto3 and Cloudsplaining policy analysis to identify overly permissive policies, dangerous permission combinations, and least-privilege violations
- **Full reference:** `references/detecting-aws-iam-privilege-escalation/SKILL.md`
- **Execution scripts:** `scripts/detecting-aws-iam-privilege-escalation/`

### detecting-email-forwarding-rules-attack
Detect malicious email forwarding rules created by adversaries to maintain persistent access to email communications for intelligence collection and BEC attacks.
- **Full reference:** `references/detecting-email-forwarding-rules-attack/SKILL.md`
- **Execution scripts:** `scripts/detecting-email-forwarding-rules-attack/`

### detecting-port-scanning-with-fail2ban
Configures Fail2ban with custom filters and actions to detect port scanning activity, SSH brute force attempts, and network reconnaissance, automatically banning offending IP addresses and alerting security teams to suspicious network probing.

- **Full reference:** `references/detecting-port-scanning-with-fail2ban/SKILL.md`
- **Execution scripts:** `scripts/detecting-port-scanning-with-fail2ban/`

### detecting-modbus-command-injection-attacks
Detect command injection attacks against Modbus TCP/RTU protocol in ICS environments by monitoring for unauthorized write operations, anomalous function codes, malformed frames, and deviations from established communication baselines using ICS-aware IDS and protocol deep packet inspection.

- **Full reference:** `references/detecting-modbus-command-injection-attacks/SKILL.md`
- **Execution scripts:** `scripts/detecting-modbus-command-injection-attacks/`

### detecting-qr-code-phishing-with-email-security
Detect and prevent QR code phishing (quishing) attacks that bypass traditional email security by embedding malicious URLs in QR code images within emails.
- **Full reference:** `references/detecting-qr-code-phishing-with-email-security/SKILL.md`
- **Execution scripts:** `scripts/detecting-qr-code-phishing-with-email-security/`

### detecting-oauth-token-theft
Detects and responds to OAuth token theft and replay attacks in cloud environments, focusing on Microsoft Entra ID (Azure AD) token protection, conditional access policies, and sign-in anomaly detection. Covers access token theft, refresh token replay, Primary Refresh Token (PRT) abuse, and pass-the-cookie attacks. Activates for requests involving OAuth token theft detection, token replay prevention, Azure AD conditional access token protection, or cloud identity attack investigation.

- **Full reference:** `references/detecting-oauth-token-theft/SKILL.md`
- **Execution scripts:** `scripts/detecting-oauth-token-theft/`

### detecting-suspicious-powershell-execution
Detect suspicious PowerShell execution patterns including encoded commands, download cradles, AMSI bypass attempts, and constrained language mode evasion.
- **Full reference:** `references/detecting-suspicious-powershell-execution/SKILL.md`
- **Execution scripts:** `scripts/detecting-suspicious-powershell-execution/`

### detecting-business-email-compromise-with-ai
Deploy AI and NLP-powered detection systems to identify business email compromise attacks by analyzing writing style, behavioral patterns, and contextual anomalies that evade traditional rule-based filters.
- **Full reference:** `references/detecting-business-email-compromise-with-ai/SKILL.md`
- **Execution scripts:** `scripts/detecting-business-email-compromise-with-ai/`

### detecting-aws-guardduty-findings-automation
Automate AWS GuardDuty threat detection findings processing using EventBridge and Lambda to enable real-time incident response, automatic quarantine of compromised resources, and security notification workflows.
- **Full reference:** `references/detecting-aws-guardduty-findings-automation/SKILL.md`
- **Execution scripts:** `scripts/detecting-aws-guardduty-findings-automation/`

### detecting-t1548-abuse-elevation-control-mechanism
Detect abuse of elevation control mechanisms including UAC bypass, sudo exploitation, and setuid/setgid manipulation by monitoring registry modifications, process elevation flags, and unusual parent-child process relationships.
- **Full reference:** `references/detecting-t1548-abuse-elevation-control-mechanism/SKILL.md`
- **Execution scripts:** `scripts/detecting-t1548-abuse-elevation-control-mechanism/`

### detecting-process-injection-techniques
Detects and analyzes process injection techniques used by malware including classic DLL injection, process hollowing, APC injection, thread hijacking, and reflective loading. Uses memory forensics, API monitoring, and behavioral analysis to identify injection artifacts. Activates for requests involving process injection detection, code injection analysis, hollowed process investigation, or in-memory threat detection.

- **Full reference:** `references/detecting-process-injection-techniques/SKILL.md`
- **Execution scripts:** `scripts/detecting-process-injection-techniques/`

### detecting-attacks-on-historian-servers
Detect cyber attacks targeting OT historian servers (OSIsoft PI, Ignition, Wonderware) that sit at the IT/OT boundary and serve as pivot points for lateral movement between enterprise and control networks, including data manipulation, unauthorized queries, and exploitation of historian-specific vulnerabilities.

- **Full reference:** `references/detecting-attacks-on-historian-servers/SKILL.md`
- **Execution scripts:** `scripts/detecting-attacks-on-historian-servers/`

### detecting-azure-lateral-movement
Detect lateral movement in Azure AD/Entra ID environments using Microsoft Graph API audit logs, Azure Sentinel KQL hunting queries, and sign-in anomaly correlation to identify privilege escalation, token theft, and cross-tenant pivoting.
- **Full reference:** `references/detecting-azure-lateral-movement/SKILL.md`
- **Execution scripts:** `scripts/detecting-azure-lateral-movement/`

### detecting-ransomware-encryption-behavior
Detects ransomware encryption activity in real time using entropy analysis, file system I/O monitoring, and behavioral heuristics. Identifies mass file modification patterns, abnormal entropy spikes in written data, and suspicious process behavior characteristic of ransomware encryption routines. Activates for requests involving ransomware behavioral detection, entropy-based file monitoring, I/O anomaly detection, or real-time encryption activity alerting.

- **Full reference:** `references/detecting-ransomware-encryption-behavior/SKILL.md`
- **Execution scripts:** `scripts/detecting-ransomware-encryption-behavior/`

### detecting-lateral-movement-with-zeek
Detect lateral movement in network traffic using Zeek (formerly Bro) log analysis. Parses conn.log, smb_mapping.log, smb_files.log, dce_rpc.log, kerberos.log, and ntlm.log to identify SMB file transfers, NTLM account spray activity, remote service execution, and anomalous internal connections.

- **Full reference:** `references/detecting-lateral-movement-with-zeek/SKILL.md`
- **Execution scripts:** `scripts/detecting-lateral-movement-with-zeek/`

### detecting-living-off-the-land-with-lolbas
Detect Living Off the Land Binaries (LOLBins/LOLBAS) abuse including certutil, regsvr32, mshta, and rundll32 via process telemetry, Sigma rules, and parent-child process analysis
- **Full reference:** `references/detecting-living-off-the-land-with-lolbas/SKILL.md`
- **Execution scripts:** `scripts/detecting-living-off-the-land-with-lolbas/`

### detecting-broken-object-property-level-authorization
Detect and test for OWASP API3:2023 Broken Object Property Level Authorization vulnerabilities including excessive data exposure and mass assignment attacks.
- **Full reference:** `references/detecting-broken-object-property-level-authorization/SKILL.md`
- **Execution scripts:** `scripts/detecting-broken-object-property-level-authorization/`

### detecting-golden-ticket-attacks-in-kerberos-logs
Detect Golden Ticket attacks in Active Directory by analyzing Kerberos TGT anomalies including mismatched encryption types, impossible ticket lifetimes, non-existent accounts, and forged PAC signatures in domain controller event logs.
- **Full reference:** `references/detecting-golden-ticket-attacks-in-kerberos-logs/SKILL.md`
- **Execution scripts:** `scripts/detecting-golden-ticket-attacks-in-kerberos-logs/`

### detecting-exfiltration-over-dns-with-zeek
Detect DNS-based data exfiltration by analyzing Zeek dns.log for high-entropy subdomains and anomalous query patterns
- **Full reference:** `references/detecting-exfiltration-over-dns-with-zeek/SKILL.md`
- **Execution scripts:** `scripts/detecting-exfiltration-over-dns-with-zeek/`

### detecting-pass-the-hash-attacks
Detect Pass-the-Hash attacks by analyzing NTLM authentication patterns, identifying Type 3 logons with NTLM where Kerberos is expected, and correlating with credential dumping.
- **Full reference:** `references/detecting-pass-the-hash-attacks/SKILL.md`
- **Execution scripts:** `scripts/detecting-pass-the-hash-attacks/`

### detecting-process-hollowing-technique
Detect process hollowing (T1055.012) by analyzing memory-mapped sections, hollowed process indicators, and parent-child process anomalies in EDR telemetry.
- **Full reference:** `references/detecting-process-hollowing-technique/SKILL.md`
- **Execution scripts:** `scripts/detecting-process-hollowing-technique/`

### detecting-rdp-brute-force-attacks
Detect RDP brute force attacks by analyzing Windows Security Event Logs for failed authentication patterns (Event ID 4625), successful logons after failures (Event ID 4624), NLA failures, and source IP frequency analysis.
- **Full reference:** `references/detecting-rdp-brute-force-attacks/SKILL.md`
- **Execution scripts:** `scripts/detecting-rdp-brute-force-attacks/`

### detecting-stuxnet-style-attacks
This skill covers detecting sophisticated cyber-physical attacks that follow the Stuxnet attack pattern of modifying PLC logic while spoofing sensor readings to hide the manipulation from operators. It addresses PLC logic integrity monitoring, physics-based process anomaly detection, engineering workstation compromise indicators, USB-borne attack vectors, and multi-stage attack chain detection spanning IT-to-OT lateral movement through to process manipulation.

- **Full reference:** `references/detecting-stuxnet-style-attacks/SKILL.md`
- **Execution scripts:** `scripts/detecting-stuxnet-style-attacks/`

### detecting-dnp3-protocol-anomalies
Detect anomalies in DNP3 (Distributed Network Protocol 3) communications used in SCADA systems by monitoring for unauthorized control commands, firmware update attempts, protocol violations, and deviations from baseline traffic patterns using deep packet inspection and machine learning approaches.

- **Full reference:** `references/detecting-dnp3-protocol-anomalies/SKILL.md`
- **Execution scripts:** `scripts/detecting-dnp3-protocol-anomalies/`

### detecting-malicious-scheduled-tasks-with-sysmon
Detect malicious scheduled task creation and modification using Sysmon Event IDs 1 (Process Create for schtasks.exe), 11 (File Create for task XML), and Windows Security Event 4698/4702. The analyst correlates task creation with suspicious parent processes, public directory paths, and encoded command arguments to identify persistence and lateral movement via scheduled tasks. Activates for requests involving scheduled task detection, Sysmon persistence hunting, or T1053.005 Scheduled Task/Job analysis.

- **Full reference:** `references/detecting-malicious-scheduled-tasks-with-sysmon/SKILL.md`
- **Execution scripts:** `scripts/detecting-malicious-scheduled-tasks-with-sysmon/`

### detecting-container-escape-with-falco-rules
Detect container escape attempts in real-time using Falco runtime security rules that monitor syscalls, file access, and privilege escalation.
- **Full reference:** `references/detecting-container-escape-with-falco-rules/SKILL.md`
- **Execution scripts:** `scripts/detecting-container-escape-with-falco-rules/`

### detecting-dcsync-attack-in-active-directory
Detect DCSync attacks where adversaries abuse Active Directory replication privileges to extract password hashes by monitoring for non-domain-controller accounts requesting directory replication via DsGetNCChanges.
- **Full reference:** `references/detecting-dcsync-attack-in-active-directory/SKILL.md`
- **Execution scripts:** `scripts/detecting-dcsync-attack-in-active-directory/`

### detecting-typosquatting-packages-in-npm-pypi
Detects typosquatting attacks in npm and PyPI package registries by analyzing package name similarity using Levenshtein distance and other string metrics, examining publish date heuristics to identify recently created packages mimicking established ones, and flagging download count anomalies where suspicious packages have disproportionately low usage compared to their legitimate targets. The analyst queries the PyPI JSON API and npm registry API to gather package metadata for automated comparison. Activates for requests involving package typosquatting detection, dependency confusion analysis, malicious package identification, or software supply chain threat hunting in package registries.

- **Full reference:** `references/detecting-typosquatting-packages-in-npm-pypi/SKILL.md`
- **Execution scripts:** `scripts/detecting-typosquatting-packages-in-npm-pypi/`

### detecting-misconfigured-azure-storage
Detecting misconfigured Azure Storage accounts including publicly accessible blob containers, missing encryption settings, overly permissive SAS tokens, disabled logging, and network access violations using Azure CLI, PowerShell, and Microsoft Defender for Storage.

- **Full reference:** `references/detecting-misconfigured-azure-storage/SKILL.md`
- **Execution scripts:** `scripts/detecting-misconfigured-azure-storage/`

### detecting-network-anomalies-with-zeek
Deploys and configures Zeek (formerly Bro) network security monitor to passively analyze network traffic, generate structured logs, detect anomalous behavior, and create custom detection scripts for threat hunting and incident response.

- **Full reference:** `references/detecting-network-anomalies-with-zeek/SKILL.md`
- **Execution scripts:** `scripts/detecting-network-anomalies-with-zeek/`

### detecting-anomalies-in-industrial-control-systems
This skill covers deploying anomaly detection systems for industrial control environments using machine learning models trained on OT network baselines, physics-based process models, and behavioral analysis of industrial protocol communications. It addresses building normal behavior profiles for SCADA polling patterns, detecting deviations in Modbus/DNP3/OPC UA traffic, identifying rogue devices, and correlating network anomalies with physical process data from historians.

- **Full reference:** `references/detecting-anomalies-in-industrial-control-systems/SKILL.md`
- **Execution scripts:** `scripts/detecting-anomalies-in-industrial-control-systems/`

### detecting-dll-sideloading-attacks
Detect DLL side-loading attacks where adversaries place malicious DLLs alongside legitimate applications to hijack execution flow for defense evasion.
- **Full reference:** `references/detecting-dll-sideloading-attacks/SKILL.md`
- **Execution scripts:** `scripts/detecting-dll-sideloading-attacks/`

### detecting-mimikatz-execution-patterns
Detect Mimikatz execution through command-line patterns, LSASS access signatures, binary indicators, and in-memory detection of known modules.
- **Full reference:** `references/detecting-mimikatz-execution-patterns/SKILL.md`
- **Execution scripts:** `scripts/detecting-mimikatz-execution-patterns/`

### detecting-attacks-on-scada-systems
This skill covers detecting cyber attacks targeting Supervisory Control and Data Acquisition (SCADA) systems including man-in-the-middle attacks on industrial protocols, unauthorized command injection into PLCs, HMI compromise, historian data manipulation, and denial-of-service against control system communications. It leverages OT-specific intrusion detection systems, industrial protocol anomaly detection, and process data analytics to identify attacks that traditional IT security tools miss.

- **Full reference:** `references/detecting-attacks-on-scada-systems/SKILL.md`
- **Execution scripts:** `scripts/detecting-attacks-on-scada-systems/`

### detecting-s3-data-exfiltration-attempts
Detecting data exfiltration attempts from AWS S3 buckets by analyzing CloudTrail S3 data events, VPC Flow Logs, GuardDuty findings, Amazon Macie alerts, and S3 access patterns to identify unauthorized bulk downloads and cross-account data transfers.

- **Full reference:** `references/detecting-s3-data-exfiltration-attempts/SKILL.md`
- **Execution scripts:** `scripts/detecting-s3-data-exfiltration-attempts/`

### detecting-sql-injection-via-waf-logs
Analyze WAF (ModSecurity/AWS WAF/Cloudflare) logs to detect SQL injection attack campaigns. Parses ModSecurity audit logs and JSON WAF event logs to identify SQLi patterns (UNION SELECT, OR 1=1, SLEEP(), BENCHMARK()), tracks attack sources, correlates multi-stage injection attempts, and generates incident reports with OWASP classification.
- **Full reference:** `references/detecting-sql-injection-via-waf-logs/SKILL.md`
- **Execution scripts:** `scripts/detecting-sql-injection-via-waf-logs/`

### detecting-beaconing-patterns-with-zeek
Performs statistical analysis of Zeek conn.log connection intervals to detect C2 beaconing patterns. Uses the ZAT library to load Zeek logs into Pandas DataFrames, calculates inter-arrival time standard deviation, and flags periodic connections with low jitter. Use when hunting for command-and-control callbacks in network data.

- **Full reference:** `references/detecting-beaconing-patterns-with-zeek/SKILL.md`
- **Execution scripts:** `scripts/detecting-beaconing-patterns-with-zeek/`

### detecting-compromised-cloud-credentials
Detecting compromised cloud credentials across AWS, Azure, and GCP by analyzing anomalous API activity, impossible travel patterns, unauthorized resource provisioning, and credential abuse indicators using GuardDuty, Defender for Identity, and SCC Event Threat Detection.

- **Full reference:** `references/detecting-compromised-cloud-credentials/SKILL.md`
- **Execution scripts:** `scripts/detecting-compromised-cloud-credentials/`

### detecting-ntlm-relay-with-event-correlation
Detect NTLM relay attacks through Windows Security Event correlation by analyzing Event 4624 LogonType 3 for IP-to-hostname mismatches, identifying Responder/LLMNR poisoning artifacts, auditing SMB and LDAP signing enforcement across the domain, and detecting NTLM downgrade attacks from NTLMv2 to NTLMv1 using event log analysis.

- **Full reference:** `references/detecting-ntlm-relay-with-event-correlation/SKILL.md`
- **Execution scripts:** `scripts/detecting-ntlm-relay-with-event-correlation/`

### detecting-golden-ticket-forgery
Detect Kerberos Golden Ticket forgery by analyzing Windows Event ID 4769 for RC4 encryption downgrades (0x17), abnormal ticket lifetimes, and krbtgt account anomalies in Splunk and Elastic SIEM
- **Full reference:** `references/detecting-golden-ticket-forgery/SKILL.md`
- **Execution scripts:** `scripts/detecting-golden-ticket-forgery/`

### detecting-modbus-protocol-anomalies
This skill covers detecting anomalies in Modbus/TCP and Modbus RTU communications in industrial control systems. It addresses function code monitoring, register range validation, timing analysis, unauthorized client detection, and deep packet inspection for malformed Modbus frames. The skill leverages Zeek with Modbus protocol analyzers, Suricata IDS with OT rules, and custom Python-based detection using Markov chain models for normal Modbus transaction sequences.

- **Full reference:** `references/detecting-modbus-protocol-anomalies/SKILL.md`
- **Execution scripts:** `scripts/detecting-modbus-protocol-anomalies/`

### detecting-email-account-compromise
Detect compromised O365 and Google Workspace email accounts by analyzing inbox rule creation, suspicious sign-in locations, mail forwarding rules, and unusual API access patterns via Microsoft Graph and audit logs.
- **Full reference:** `references/detecting-email-account-compromise/SKILL.md`
- **Execution scripts:** `scripts/detecting-email-account-compromise/`

### detecting-spearphishing-with-email-gateway
Spearphishing targets specific individuals using personalized, researched content that bypasses generic spam filters. Email security gateways (SEGs) like Microsoft Defender for Office 365, Proofpoint,
- **Full reference:** `references/detecting-spearphishing-with-email-gateway/SKILL.md`
- **Execution scripts:** `scripts/detecting-spearphishing-with-email-gateway/`

### detecting-lateral-movement-with-splunk
Detect adversary lateral movement across networks using Splunk SPL queries against Windows authentication logs, SMB traffic, and remote service abuse.
- **Full reference:** `references/detecting-lateral-movement-with-splunk/SKILL.md`
- **Execution scripts:** `scripts/detecting-lateral-movement-with-splunk/`

### detecting-azure-service-principal-abuse
Detect and investigate Azure service principal abuse including privilege escalation, credential compromise, admin consent bypass, and unauthorized enumeration in Microsoft Entra ID environments.
- **Full reference:** `references/detecting-azure-service-principal-abuse/SKILL.md`
- **Execution scripts:** `scripts/detecting-azure-service-principal-abuse/`

### detecting-api-enumeration-attacks
Detect and prevent API enumeration attacks including BOLA and IDOR exploitation by monitoring sequential identifier access patterns and authorization failures.
- **Full reference:** `references/detecting-api-enumeration-attacks/SKILL.md`
- **Execution scripts:** `scripts/detecting-api-enumeration-attacks/`

### detecting-business-email-compromise
Business Email Compromise (BEC) is a sophisticated fraud scheme where attackers impersonate executives, vendors, or trusted partners to trick employees into transferring funds, sharing sensitive data,
- **Full reference:** `references/detecting-business-email-compromise/SKILL.md`
- **Execution scripts:** `scripts/detecting-business-email-compromise/`

### detecting-cryptomining-in-cloud
This skill teaches security teams how to detect and respond to unauthorized cryptocurrency mining operations in cloud environments. It covers identifying cryptomining indicators through compute usage anomalies, network traffic patterns to mining pools, GuardDuty CryptoCurrency findings, and runtime process monitoring on EC2, ECS, EKS, and Azure Automation workloads.

- **Full reference:** `references/detecting-cryptomining-in-cloud/SKILL.md`
- **Execution scripts:** `scripts/detecting-cryptomining-in-cloud/`

### detecting-insider-data-exfiltration-via-dlp
Detects insider data exfiltration by analyzing DLP policy violations, file access patterns, upload volume anomalies, and off-hours activity in endpoint and cloud logs. Uses pandas for behavioral analytics and statistical baselines. Use when investigating insider threats or building user behavior analytics for data loss prevention.

- **Full reference:** `references/detecting-insider-data-exfiltration-via-dlp/SKILL.md`
- **Execution scripts:** `scripts/detecting-insider-data-exfiltration-via-dlp/`

### detecting-living-off-the-land-attacks
Detect abuse of legitimate Windows binaries (LOLBins) used for living off the land attacks. Monitors process creation, command-line arguments, and parent-child relationships to identify suspicious LOLBin execution patterns.

- **Full reference:** `references/detecting-living-off-the-land-attacks/SKILL.md`
- **Execution scripts:** `scripts/detecting-living-off-the-land-attacks/`

### detecting-aws-cloudtrail-anomalies
Detect unusual API call patterns in AWS CloudTrail logs using boto3, statistical baselining, and behavioral analysis to identify credential compromise, privilege escalation, and unauthorized resource access.
- **Full reference:** `references/detecting-aws-cloudtrail-anomalies/SKILL.md`
- **Execution scripts:** `scripts/detecting-aws-cloudtrail-anomalies/`

### detecting-t1055-process-injection-with-sysmon
Detect process injection techniques (T1055) including classic DLL injection, process hollowing, and APC injection by analyzing Sysmon events for cross-process memory operations, remote thread creation, and anomalous DLL loading patterns.
- **Full reference:** `references/detecting-t1055-process-injection-with-sysmon/SKILL.md`
- **Execution scripts:** `scripts/detecting-t1055-process-injection-with-sysmon/`

### detecting-container-drift-at-runtime
Detect unauthorized modifications to running containers by monitoring for binary execution drift, file system changes, and configuration deviations from the original container image.
- **Full reference:** `references/detecting-container-drift-at-runtime/SKILL.md`
- **Execution scripts:** `scripts/detecting-container-drift-at-runtime/`

### detecting-deepfake-audio-in-vishing-attacks
Detects AI-generated deepfake audio used in voice phishing (vishing) attacks by extracting spectral features (MFCC, spectral centroid, spectral contrast, zero-crossing rate) and classifying samples with machine learning models. Supports batch analysis of audio files, generates confidence scores, and produces forensic reports. Activates for requests involving deepfake voice detection, vishing investigation, AI-generated speech analysis, voice cloning detection, or audio authenticity verification.

- **Full reference:** `references/detecting-deepfake-audio-in-vishing-attacks/SKILL.md`
- **Execution scripts:** `scripts/detecting-deepfake-audio-in-vishing-attacks/`

### detecting-azure-storage-account-misconfigurations
Audit Azure Blob and ADLS storage accounts for public access exposure, weak or long-lived SAS tokens, missing encryption at rest, disabled HTTPS-only traffic, and outdated TLS versions using the azure-mgmt-storage Python SDK.
- **Full reference:** `references/detecting-azure-storage-account-misconfigurations/SKILL.md`
- **Execution scripts:** `scripts/detecting-azure-storage-account-misconfigurations/`

### detecting-pass-the-ticket-attacks
Detect Kerberos Pass-the-Ticket (PtT) attacks by analyzing Windows Event IDs 4768, 4769, and 4771 for anomalous ticket usage patterns in Splunk and Elastic SIEM
- **Full reference:** `references/detecting-pass-the-ticket-attacks/SKILL.md`
- **Execution scripts:** `scripts/detecting-pass-the-ticket-attacks/`