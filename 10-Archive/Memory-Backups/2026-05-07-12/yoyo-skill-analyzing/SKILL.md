---
name: analyzing
domain: red-teaming
tags:
- analyzing
- class-level
- umbrella
status: active
version: 1.0.0
description: Consolidated umbrella for analyzing-* skills.
---
## Included Capabilities

### analyzing-security-logs-with-splunk
Leverages Splunk Enterprise Security and SPL (Search Processing Language) to investigate security incidents through log correlation, timeline reconstruction, and anomaly detection. Covers Windows event logs, firewall logs, proxy logs, and authentication data analysis. Activates for requests involving Splunk investigation, SPL queries, SIEM log analysis, security event correlation, or log-based incident investigation.

- **Full reference:** `references/analyzing-security-logs-with-splunk/SKILL.md`
- **Execution scripts:** `scripts/analyzing-security-logs-with-splunk/`

### analyzing-malicious-url-with-urlscan
URLScan.io is a free service for scanning and analyzing suspicious URLs. It captures screenshots, DOM content, HTTP transactions, JavaScript behavior, and network connections of web pages in an isolat
- **Full reference:** `references/analyzing-malicious-url-with-urlscan/SKILL.md`
- **Execution scripts:** `scripts/analyzing-malicious-url-with-urlscan/`

### analyzing-certificate-transparency-for-phishing
Monitor Certificate Transparency logs using crt.sh and Certstream to detect phishing domains, lookalike certificates, and unauthorized certificate issuance targeting your organization.
- **Full reference:** `references/analyzing-certificate-transparency-for-phishing/SKILL.md`
- **Execution scripts:** `scripts/analyzing-certificate-transparency-for-phishing/`

### analyzing-threat-actor-ttps-with-mitre-navigator
Map advanced persistent threat (APT) group tactics, techniques, and procedures (TTPs) to the MITRE ATT&CK framework using the ATT&CK Navigator and attackcti Python library. The analyst queries STIX/TAXII data for group-technique associations, generates Navigator layer files for visualization, and compares defensive coverage against adversary profiles. Activates for requests involving APT TTP mapping, ATT&CK Navigator layers, threat actor profiling, or MITRE technique coverage analysis.

- **Full reference:** `references/analyzing-threat-actor-ttps-with-mitre-navigator/SKILL.md`
- **Execution scripts:** `scripts/analyzing-threat-actor-ttps-with-mitre-navigator/`

### analyzing-windows-registry-for-artifacts
Extract and analyze Windows Registry hives to uncover user activity, installed software, autostart entries, and evidence of system compromise.
- **Full reference:** `references/analyzing-windows-registry-for-artifacts/SKILL.md`
- **Execution scripts:** `scripts/analyzing-windows-registry-for-artifacts/`

### analyzing-ransomware-leak-site-intelligence
Monitor and analyze ransomware group data leak sites (DLS) to track victim postings, extract threat intelligence on group tactics, and assess sector-specific ransomware risk for proactive defense.
- **Full reference:** `references/analyzing-ransomware-leak-site-intelligence/SKILL.md`
- **Execution scripts:** `scripts/analyzing-ransomware-leak-site-intelligence/`

### analyzing-linux-elf-malware
Analyzes malicious Linux ELF (Executable and Linkable Format) binaries including botnets, cryptominers, ransomware, and rootkits targeting Linux servers, containers, and cloud infrastructure. Covers static analysis, dynamic tracing, and reverse engineering of x86_64 and ARM ELF samples. Activates for requests involving Linux malware analysis, ELF binary investigation, Linux server compromise assessment, or container malware analysis.

- **Full reference:** `references/analyzing-linux-elf-malware/SKILL.md`
- **Execution scripts:** `scripts/analyzing-linux-elf-malware/`

### analyzing-ransomware-payment-wallets
Traces ransomware cryptocurrency payment flows using blockchain analysis tools such as Chainalysis Reactor, WalletExplorer, and blockchain.com APIs. Identifies wallet clusters, tracks fund movement through mixers and exchanges, and supports law enforcement attribution. Activates for requests involving ransomware payment tracing, bitcoin wallet analysis, cryptocurrency forensics, or blockchain intelligence gathering.

- **Full reference:** `references/analyzing-ransomware-payment-wallets/SKILL.md`
- **Execution scripts:** `scripts/analyzing-ransomware-payment-wallets/`

### analyzing-persistence-mechanisms-in-linux
Detect and analyze Linux persistence mechanisms including crontab entries, systemd service units, LD_PRELOAD hijacking, bashrc modifications, and authorized_keys backdoors using auditd and file integrity monitoring
- **Full reference:** `references/analyzing-persistence-mechanisms-in-linux/SKILL.md`
- **Execution scripts:** `scripts/analyzing-persistence-mechanisms-in-linux/`

### analyzing-network-traffic-for-incidents
Analyzes network traffic captures and flow data to identify adversary activity during security incidents, including command-and-control communications, lateral movement, data exfiltration, and exploitation attempts. Uses Wireshark, Zeek, and NetFlow analysis techniques. Activates for requests involving network traffic analysis, packet capture investigation, PCAP analysis, network forensics, C2 traffic detection, or exfiltration detection.

- **Full reference:** `references/analyzing-network-traffic-for-incidents/SKILL.md`
- **Execution scripts:** `scripts/analyzing-network-traffic-for-incidents/`

### analyzing-active-directory-acl-abuse
Detect dangerous ACL misconfigurations in Active Directory using ldap3 to identify GenericAll, WriteDACL, and WriteOwner abuse paths
- **Full reference:** `references/analyzing-active-directory-acl-abuse/SKILL.md`
- **Execution scripts:** `scripts/analyzing-active-directory-acl-abuse/`

### analyzing-sbom-for-supply-chain-vulnerabilities
Parses Software Bill of Materials (SBOM) in CycloneDX and SPDX JSON formats to identify supply chain vulnerabilities by correlating components against the NVD CVE database via the NVD 2.0 API. Builds dependency graphs, calculates risk scores, identifies transitive vulnerability paths, and generates compliance reports. Activates for requests involving SBOM analysis, software composition analysis, supply chain security assessment, dependency vulnerability scanning, CycloneDX/SPDX parsing, or CVE correlation.

- **Full reference:** `references/analyzing-sbom-for-supply-chain-vulnerabilities/SKILL.md`
- **Execution scripts:** `scripts/analyzing-sbom-for-supply-chain-vulnerabilities/`

### analyzing-windows-prefetch-with-python
Parse Windows Prefetch files using the windowsprefetch Python library to reconstruct application execution history, detect renamed or masquerading binaries, and identify suspicious program execution patterns.
- **Full reference:** `references/analyzing-windows-prefetch-with-python/SKILL.md`
- **Execution scripts:** `scripts/analyzing-windows-prefetch-with-python/`

### analyzing-cobalt-strike-beacon-configuration
Extract and analyze Cobalt Strike beacon configuration from PE files and memory dumps to identify C2 infrastructure, malleable profiles, and operator tradecraft.
- **Full reference:** `references/analyzing-cobalt-strike-beacon-configuration/SKILL.md`
- **Execution scripts:** `scripts/analyzing-cobalt-strike-beacon-configuration/`

### analyzing-macro-malware-in-office-documents
Analyzes malicious VBA macros embedded in Microsoft Office documents (Word, Excel, PowerPoint) to identify download cradles, payload execution, persistence mechanisms, and anti-analysis techniques. Uses olevba, oledump, and VBA deobfuscation to extract the attack chain. Activates for requests involving Office macro analysis, VBA malware investigation, maldoc analysis, or document-based threat examination.

- **Full reference:** `references/analyzing-macro-malware-in-office-documents/SKILL.md`
- **Execution scripts:** `scripts/analyzing-macro-malware-in-office-documents/`

### analyzing-kubernetes-audit-logs
Parses Kubernetes API server audit logs (JSON lines) to detect exec-into-pod, secret access, RBAC modifications, privileged pod creation, and anonymous API access. Builds threat detection rules from audit event patterns. Use when investigating Kubernetes cluster compromise or building k8s-specific SIEM detection rules.

- **Full reference:** `references/analyzing-kubernetes-audit-logs/SKILL.md`
- **Execution scripts:** `scripts/analyzing-kubernetes-audit-logs/`

### analyzing-threat-intelligence-feeds
Analyzes structured and unstructured threat intelligence feeds to extract actionable indicators, adversary tactics, and campaign context. Use when ingesting commercial or open-source CTI feeds, evaluating feed quality, normalizing data into STIX 2.1 format, or enriching existing IOCs with campaign attribution. Activates for requests involving ThreatConnect, Recorded Future, Mandiant Advantage, MISP, AlienVault OTX, or automated feed aggregation pipelines.

- **Full reference:** `references/analyzing-threat-intelligence-feeds/SKILL.md`
- **Execution scripts:** `scripts/analyzing-threat-intelligence-feeds/`

### analyzing-malware-persistence-with-autoruns
Use Sysinternals Autoruns to systematically identify and analyze malware persistence mechanisms across registry keys, scheduled tasks, services, drivers, and startup locations on Windows systems.
- **Full reference:** `references/analyzing-malware-persistence-with-autoruns/SKILL.md`
- **Execution scripts:** `scripts/analyzing-malware-persistence-with-autoruns/`

### analyzing-memory-dumps-with-volatility
Analyzes RAM memory dumps from compromised systems using the Volatility framework to identify malicious processes, injected code, network connections, loaded modules, and extracted credentials. Supports Windows, Linux, and macOS memory forensics. Activates for requests involving memory forensics, RAM analysis, volatile data examination, process injection detection, or memory-resident malware investigation.

- **Full reference:** `references/analyzing-memory-dumps-with-volatility/SKILL.md`
- **Execution scripts:** `scripts/analyzing-memory-dumps-with-volatility/`

### analyzing-api-gateway-access-logs
Parses API Gateway access logs (AWS API Gateway, Kong, Nginx) to detect BOLA/IDOR attacks, rate limit bypass, credential scanning, and injection attempts. Uses pandas for statistical analysis of request patterns and anomaly detection. Use when investigating API abuse or building API-specific threat detection rules.

- **Full reference:** `references/analyzing-api-gateway-access-logs/SKILL.md`
- **Execution scripts:** `scripts/analyzing-api-gateway-access-logs/`

### analyzing-ethereum-smart-contract-vulnerabilities
Perform static and symbolic analysis of Solidity smart contracts using Slither and Mythril to detect reentrancy, integer overflow, access control, and other vulnerability classes before deployment to Ethereum mainnet.
- **Full reference:** `references/analyzing-ethereum-smart-contract-vulnerabilities/SKILL.md`
- **Execution scripts:** `scripts/analyzing-ethereum-smart-contract-vulnerabilities/`

### analyzing-supply-chain-malware-artifacts
Investigate supply chain attack artifacts including trojanized software updates, compromised build pipelines, and sideloaded dependencies to identify intrusion vectors and scope of compromise.
- **Full reference:** `references/analyzing-supply-chain-malware-artifacts/SKILL.md`
- **Execution scripts:** `scripts/analyzing-supply-chain-malware-artifacts/`

### analyzing-tls-certificate-transparency-logs
Queries Certificate Transparency logs via crt.sh and pycrtsh to detect phishing domains, unauthorized certificate issuance, and shadow IT. Monitors newly issued certificates for typosquatting and brand impersonation using Levenshtein distance. Use for proactive phishing domain detection and certificate monitoring.

- **Full reference:** `references/analyzing-tls-certificate-transparency-logs/SKILL.md`
- **Execution scripts:** `scripts/analyzing-tls-certificate-transparency-logs/`

### analyzing-linux-audit-logs-for-intrusion
Uses the Linux Audit framework (auditd) with ausearch and aureport utilities to detect intrusion attempts, unauthorized access, privilege escalation, and suspicious system activity. Covers audit rule configuration, log querying, timeline reconstruction, and integration with SIEM platforms. Activates for requests involving auditd analysis, Linux audit log investigation, ausearch queries, aureport summaries, or host-based intrusion detection on Linux.

- **Full reference:** `references/analyzing-linux-audit-logs-for-intrusion/SKILL.md`
- **Execution scripts:** `scripts/analyzing-linux-audit-logs-for-intrusion/`

### analyzing-ransomware-network-indicators
Identify ransomware network indicators including C2 beaconing patterns, TOR exit node connections, data exfiltration flows, and encryption key exchange via Zeek conn.log and NetFlow analysis
- **Full reference:** `references/analyzing-ransomware-network-indicators/SKILL.md`
- **Execution scripts:** `scripts/analyzing-ransomware-network-indicators/`

### analyzing-command-and-control-communication
Analyzes malware command-and-control (C2) communication protocols to understand beacon patterns, command structures, data encoding, and infrastructure. Covers HTTP, HTTPS, DNS, and custom protocol C2 analysis for detection development and threat intelligence. Activates for requests involving C2 analysis, beacon detection, C2 protocol reverse engineering, or command-and-control infrastructure mapping.

- **Full reference:** `references/analyzing-command-and-control-communication/SKILL.md`
- **Execution scripts:** `scripts/analyzing-command-and-control-communication/`

### analyzing-docker-container-forensics
Investigate compromised Docker containers by analyzing images, layers, volumes, logs, and runtime artifacts to identify malicious activity and evidence.
- **Full reference:** `references/analyzing-docker-container-forensics/SKILL.md`
- **Execution scripts:** `scripts/analyzing-docker-container-forensics/`

### analyzing-cloud-storage-access-patterns
Detect abnormal access patterns in AWS S3, GCS, and Azure Blob Storage by analyzing CloudTrail Data Events, GCS audit logs, and Azure Storage Analytics. Identifies after-hours bulk downloads, access from new IP addresses, unusual API calls (GetObject spikes), and potential data exfiltration using statistical baselines and time-series anomaly detection.
- **Full reference:** `references/analyzing-cloud-storage-access-patterns/SKILL.md`
- **Execution scripts:** `scripts/analyzing-cloud-storage-access-patterns/`

### analyzing-cobaltstrike-malleable-c2-profiles
Parse and analyze Cobalt Strike Malleable C2 profiles using dissect.cobaltstrike and pyMalleableC2 to extract C2 indicators, detect evasion techniques, and generate network detection signatures.
- **Full reference:** `references/analyzing-cobaltstrike-malleable-c2-profiles/SKILL.md`
- **Execution scripts:** `scripts/analyzing-cobaltstrike-malleable-c2-profiles/`

### analyzing-azure-activity-logs-for-threats
Queries Azure Monitor activity logs and sign-in logs via azure-monitor-query to detect suspicious administrative operations, impossible travel, privilege escalation, and resource modifications. Builds KQL queries for threat hunting in Azure environments. Use when investigating suspicious Azure tenant activity or building cloud SIEM detections.

- **Full reference:** `references/analyzing-azure-activity-logs-for-threats/SKILL.md`
- **Execution scripts:** `scripts/analyzing-azure-activity-logs-for-threats/`

### analyzing-bootkit-and-rootkit-samples
Analyzes bootkit and advanced rootkit malware that infects the Master Boot Record (MBR), Volume Boot Record (VBR), or UEFI firmware to gain persistence below the operating system. Covers boot sector analysis, UEFI module inspection, and anti-rootkit detection techniques. Activates for requests involving bootkit analysis, MBR malware investigation, UEFI persistence analysis, or pre-OS malware detection.

- **Full reference:** `references/analyzing-bootkit-and-rootkit-samples/SKILL.md`
- **Execution scripts:** `scripts/analyzing-bootkit-and-rootkit-samples/`

### analyzing-outlook-pst-for-email-forensics
Analyze Microsoft Outlook PST and OST files for email forensic evidence including message content, headers, attachments, deleted items, and metadata using libpff, pst-utils, and forensic email analysis tools for legal investigations and incident response.
- **Full reference:** `references/analyzing-outlook-pst-for-email-forensics/SKILL.md`
- **Execution scripts:** `scripts/analyzing-outlook-pst-for-email-forensics/`

### analyzing-campaign-attribution-evidence
Campaign attribution analysis involves systematically evaluating evidence to determine which threat actor or group is responsible for a cyber operation. This skill covers collecting and weighting attr
- **Full reference:** `references/analyzing-campaign-attribution-evidence/SKILL.md`
- **Execution scripts:** `scripts/analyzing-campaign-attribution-evidence/`

### analyzing-pdf-malware-with-pdfid
Analyzes malicious PDF files using PDFiD, pdf-parser, and peepdf to identify embedded JavaScript, shellcode, exploits, and suspicious objects without opening the document. Determines the attack vector and extracts embedded payloads for further analysis. Activates for requests involving PDF malware analysis, malicious document analysis, PDF exploit investigation, or suspicious attachment triage.

- **Full reference:** `references/analyzing-pdf-malware-with-pdfid/SKILL.md`
- **Execution scripts:** `scripts/analyzing-pdf-malware-with-pdfid/`

### analyzing-powershell-empire-artifacts
Detect PowerShell Empire framework artifacts in Windows event logs by identifying Base64 encoded launcher patterns, default user agents, staging URL structures, stager IOCs, and known Empire module signatures in Script Block Logging events.
- **Full reference:** `references/analyzing-powershell-empire-artifacts/SKILL.md`
- **Execution scripts:** `scripts/analyzing-powershell-empire-artifacts/`

### analyzing-ios-app-security-with-objection
Performs runtime mobile security exploration of iOS applications using Objection, a Frida-powered toolkit that enables security testers to interact with app internals without jailbreaking. Use when assessing iOS app security posture, bypassing client-side protections, dumping keychain items, inspecting filesystem storage, and evaluating runtime behavior. Activates for requests involving iOS security testing, Objection runtime analysis, Frida-based iOS assessment, or mobile runtime exploration.

- **Full reference:** `references/analyzing-ios-app-security-with-objection/SKILL.md`
- **Execution scripts:** `scripts/analyzing-ios-app-security-with-objection/`

### analyzing-android-malware-with-apktool
Perform static analysis of Android APK malware samples using apktool for decompilation, jadx for Java source recovery, and androguard for permission analysis, manifest inspection, and suspicious API call detection.
- **Full reference:** `references/analyzing-android-malware-with-apktool/SKILL.md`
- **Execution scripts:** `scripts/analyzing-android-malware-with-apktool/`

### analyzing-indicators-of-compromise
Analyzes indicators of compromise (IOCs) including IP addresses, domains, file hashes, URLs, and email artifacts to determine maliciousness confidence, campaign attribution, and blocking priority. Use when triaging IOCs from phishing emails, security alerts, or external threat feeds; enriching raw IOCs with multi-source intelligence; or making block/monitor/whitelist decisions. Activates for requests involving VirusTotal, AbuseIPDB, MalwareBazaar, MISP, or IOC enrichment pipelines.

- **Full reference:** `references/analyzing-indicators-of-compromise/SKILL.md`
- **Execution scripts:** `scripts/analyzing-indicators-of-compromise/`

### analyzing-linux-system-artifacts
Examine Linux system artifacts including auth logs, cron jobs, shell history, and system configuration to uncover evidence of compromise or unauthorized activity.
- **Full reference:** `references/analyzing-linux-system-artifacts/SKILL.md`
- **Execution scripts:** `scripts/analyzing-linux-system-artifacts/`

### analyzing-office365-audit-logs-for-compromise
Parse Office 365 Unified Audit Logs via Microsoft Graph API to detect email forwarding rule creation, inbox delegation, suspicious OAuth app grants, and other indicators of account compromise.
- **Full reference:** `references/analyzing-office365-audit-logs-for-compromise/SKILL.md`
- **Execution scripts:** `scripts/analyzing-office365-audit-logs-for-compromise/`

### analyzing-malicious-pdf-with-peepdf
Perform static analysis of malicious PDF documents using peepdf, pdfid, and pdf-parser to extract embedded JavaScript, shellcode, and suspicious objects.
- **Full reference:** `references/analyzing-malicious-pdf-with-peepdf/SKILL.md`
- **Execution scripts:** `scripts/analyzing-malicious-pdf-with-peepdf/`

### analyzing-email-headers-for-phishing-investigation
Parse and analyze email headers to trace the origin of phishing emails, verify sender authenticity, and identify spoofing through SPF, DKIM, and DMARC validation.
- **Full reference:** `references/analyzing-email-headers-for-phishing-investigation/SKILL.md`
- **Execution scripts:** `scripts/analyzing-email-headers-for-phishing-investigation/`

### analyzing-network-packets-with-scapy
Craft, send, sniff, and dissect network packets using Scapy for protocol analysis, network reconnaissance, and traffic anomaly detection in authorized security testing
- **Full reference:** `references/analyzing-network-packets-with-scapy/SKILL.md`
- **Execution scripts:** `scripts/analyzing-network-packets-with-scapy/`

### analyzing-malware-family-relationships-with-malpedia
Use the Malpedia platform and API to research malware family relationships, track variant evolution, link families to threat actors, and integrate YARA rules for detection across malware lineages.
- **Full reference:** `references/analyzing-malware-family-relationships-with-malpedia/SKILL.md`
- **Execution scripts:** `scripts/analyzing-malware-family-relationships-with-malpedia/`

### analyzing-network-traffic-with-wireshark
Captures and analyzes network packet data using Wireshark and tshark to identify malicious traffic patterns, diagnose protocol issues, extract artifacts, and support incident response investigations on authorized network segments.

- **Full reference:** `references/analyzing-network-traffic-with-wireshark/SKILL.md`
- **Execution scripts:** `scripts/analyzing-network-traffic-with-wireshark/`

### analyzing-ransomware-encryption-mechanisms
Analyzes encryption algorithms, key management, and file encryption routines used by ransomware families to assess decryption feasibility, identify implementation weaknesses, and support recovery efforts. Covers AES, RSA, ChaCha20, and hybrid encryption schemes. Activates for requests involving ransomware cryptanalysis, encryption analysis, key recovery assessment, or ransomware decryption feasibility.

- **Full reference:** `references/analyzing-ransomware-encryption-mechanisms/SKILL.md`
- **Execution scripts:** `scripts/analyzing-ransomware-encryption-mechanisms/`

### analyzing-threat-actor-ttps-with-mitre-attack
MITRE ATT&CK is a globally-accessible knowledge base of adversary tactics, techniques, and procedures (TTPs) based on real-world observations. This skill covers systematically mapping threat actor beh
- **Full reference:** `references/analyzing-threat-actor-ttps-with-mitre-attack/SKILL.md`
- **Execution scripts:** `scripts/analyzing-threat-actor-ttps-with-mitre-attack/`

### analyzing-typosquatting-domains-with-dnstwist
Detect typosquatting, homograph phishing, and brand impersonation domains using dnstwist to generate domain permutations and identify registered lookalike domains targeting your organization.
- **Full reference:** `references/analyzing-typosquatting-domains-with-dnstwist/SKILL.md`
- **Execution scripts:** `scripts/analyzing-typosquatting-domains-with-dnstwist/`

### analyzing-packed-malware-with-upx-unpacker
Identifies and unpacks UPX-packed and other packed malware samples to expose the original executable code for static analysis. Covers both standard UPX unpacking and handling modified UPX headers that prevent automated decompression. Activates for requests involving malware unpacking, UPX decompression, packer removal, or preparing packed samples for analysis.

- **Full reference:** `references/analyzing-packed-malware-with-upx-unpacker/SKILL.md`
- **Execution scripts:** `scripts/analyzing-packed-malware-with-upx-unpacker/`

### analyzing-golang-malware-with-ghidra
Reverse engineer Go-compiled malware using Ghidra with specialized scripts for function recovery, string extraction, and type reconstruction in stripped Go binaries.
- **Full reference:** `references/analyzing-golang-malware-with-ghidra/SKILL.md`
- **Execution scripts:** `scripts/analyzing-golang-malware-with-ghidra/`

### analyzing-windows-amcache-artifacts
Parses and analyzes the Windows Amcache.hve registry hive to extract evidence of program execution, application installation, and driver loading for digital forensics investigations. Uses Eric Zimmerman's AmcacheParser and Timeline Explorer for artifact extraction, SHA-1 hash correlation with threat intel, and timeline reconstruction. Activates for requests involving Amcache forensics, program execution evidence, Windows artifact analysis, or application compatibility cache investigation.

- **Full reference:** `references/analyzing-windows-amcache-artifacts/SKILL.md`
- **Execution scripts:** `scripts/analyzing-windows-amcache-artifacts/`

### analyzing-heap-spray-exploitation
Detect and analyze heap spray attacks in memory dumps using Volatility3 plugins to identify NOP sled patterns, shellcode landing zones, and suspicious large allocations in process virtual address space.
- **Full reference:** `references/analyzing-heap-spray-exploitation/SKILL.md`
- **Execution scripts:** `scripts/analyzing-heap-spray-exploitation/`

### analyzing-memory-forensics-with-lime-and-volatility
Performs Linux memory acquisition using LiME (Linux Memory Extractor) kernel module and analysis with Volatility 3 framework. Extracts process lists, network connections, bash history, loaded kernel modules, and injected code from Linux memory images. Use when performing incident response on compromised Linux systems.

- **Full reference:** `references/analyzing-memory-forensics-with-lime-and-volatility/SKILL.md`
- **Execution scripts:** `scripts/analyzing-memory-forensics-with-lime-and-volatility/`

### analyzing-network-traffic-of-malware
Analyzes network traffic generated by malware during sandbox execution or live incident response to identify C2 protocols, data exfiltration channels, payload downloads, and lateral movement patterns using Wireshark, Zeek, and Suricata. Activates for requests involving malware network analysis, C2 traffic decoding, malware PCAP analysis, or network-based malware detection.

- **Full reference:** `references/analyzing-network-traffic-of-malware/SKILL.md`
- **Execution scripts:** `scripts/analyzing-network-traffic-of-malware/`

### analyzing-malware-sandbox-evasion-techniques
Detect sandbox evasion techniques in malware samples by analyzing timing checks, VM artifact queries, user interaction detection, and sleep inflation patterns from Cuckoo/AnyRun behavioral reports
- **Full reference:** `references/analyzing-malware-sandbox-evasion-techniques/SKILL.md`
- **Execution scripts:** `scripts/analyzing-malware-sandbox-evasion-techniques/`

### analyzing-slack-space-and-file-system-artifacts
Examine file system slack space, MFT entries, USN journal, and alternate data streams to recover hidden data and reconstruct file activity on NTFS volumes.
- **Full reference:** `references/analyzing-slack-space-and-file-system-artifacts/SKILL.md`
- **Execution scripts:** `scripts/analyzing-slack-space-and-file-system-artifacts/`

### analyzing-powershell-script-block-logging
Parse Windows PowerShell Script Block Logs (Event ID 4104) from EVTX files to detect obfuscated commands, encoded payloads, and living-off-the-land techniques. Uses python-evtx to extract and reconstruct multi-block scripts, applies entropy analysis and pattern matching for Base64-encoded commands, Invoke-Expression abuse, download cradles, and AMSI bypass attempts.
- **Full reference:** `references/analyzing-powershell-script-block-logging/SKILL.md`
- **Execution scripts:** `scripts/analyzing-powershell-script-block-logging/`

### analyzing-windows-event-logs-in-splunk
Analyzes Windows Security, System, and Sysmon event logs in Splunk to detect authentication attacks, privilege escalation, persistence mechanisms, and lateral movement using SPL queries mapped to MITRE ATT&CK techniques. Use when SOC analysts need to investigate Windows-based threats, build detection queries, or perform forensic timeline analysis of Windows endpoints and domain controllers.

- **Full reference:** `references/analyzing-windows-event-logs-in-splunk/SKILL.md`
- **Execution scripts:** `scripts/analyzing-windows-event-logs-in-splunk/`

### analyzing-mft-for-deleted-file-recovery
Analyze the NTFS Master File Table ($MFT) to recover metadata and content of deleted files by examining MFT record entries, $LogFile, $UsnJrnl, and MFT slack space using MFTECmd, analyzeMFT, and X-Ways Forensics.
- **Full reference:** `references/analyzing-mft-for-deleted-file-recovery/SKILL.md`
- **Execution scripts:** `scripts/analyzing-mft-for-deleted-file-recovery/`

### analyzing-web-server-logs-for-intrusion
Parse Apache and Nginx access logs to detect SQL injection attempts, local file inclusion, directory traversal, web scanner fingerprints, and brute-force patterns. Uses regex-based pattern matching against OWASP attack signatures, GeoIP enrichment for source attribution, and statistical anomaly detection for request frequency and response size outliers.
- **Full reference:** `references/analyzing-web-server-logs-for-intrusion/SKILL.md`
- **Execution scripts:** `scripts/analyzing-web-server-logs-for-intrusion/`

### analyzing-prefetch-files-for-execution-history
Parse Windows Prefetch files to determine program execution history including run counts, timestamps, and referenced files for forensic investigation.
- **Full reference:** `references/analyzing-prefetch-files-for-execution-history/SKILL.md`
- **Execution scripts:** `scripts/analyzing-prefetch-files-for-execution-history/`

### analyzing-linux-kernel-rootkits
Detect kernel-level rootkits in Linux memory dumps using Volatility3 linux plugins (check_syscall, lsmod, hidden_modules), rkhunter system scanning, and /proc vs /sys discrepancy analysis to identify hooked syscalls, hidden kernel modules, and tampered system structures.
- **Full reference:** `references/analyzing-linux-kernel-rootkits/SKILL.md`
- **Execution scripts:** `scripts/analyzing-linux-kernel-rootkits/`

### analyzing-network-covert-channels-in-malware
Detect and analyze covert communication channels used by malware including DNS tunneling, ICMP exfiltration, steganographic HTTP, and protocol abuse for C2 and data exfiltration.
- **Full reference:** `references/analyzing-network-covert-channels-in-malware/SKILL.md`
- **Execution scripts:** `scripts/analyzing-network-covert-channels-in-malware/`

### analyzing-network-flow-data-with-netflow
Parse NetFlow v9 and IPFIX records to detect volumetric anomalies, port scanning, data exfiltration, and C2 beaconing patterns. Uses the Python netflow library to decode flow records, builds traffic baselines, and applies statistical analysis to identify flows with abnormal byte counts, connection durations, and periodic timing patterns.
- **Full reference:** `references/analyzing-network-flow-data-with-netflow/SKILL.md`
- **Execution scripts:** `scripts/analyzing-network-flow-data-with-netflow/`

### analyzing-lnk-file-and-jump-list-artifacts
Analyze Windows LNK shortcut files and Jump List artifacts to establish evidence of file access, program execution, and user activity using LECmd, JLECmd, and manual binary parsing of the Shell Link Binary format.
- **Full reference:** `references/analyzing-lnk-file-and-jump-list-artifacts/SKILL.md`
- **Execution scripts:** `scripts/analyzing-lnk-file-and-jump-list-artifacts/`

### analyzing-disk-image-with-autopsy
Perform comprehensive forensic analysis of disk images using Autopsy to recover files, examine artifacts, and build investigation timelines.
- **Full reference:** `references/analyzing-disk-image-with-autopsy/SKILL.md`
- **Execution scripts:** `scripts/analyzing-disk-image-with-autopsy/`

### analyzing-windows-lnk-files-for-artifacts
Parse Windows LNK shortcut files to extract target paths, timestamps, volume information, and machine identifiers for forensic timeline reconstruction.
- **Full reference:** `references/analyzing-windows-lnk-files-for-artifacts/SKILL.md`
- **Execution scripts:** `scripts/analyzing-windows-lnk-files-for-artifacts/`

### analyzing-apt-group-with-mitre-navigator
Analyze advanced persistent threat (APT) group techniques using MITRE ATT&CK Navigator to create layered heatmaps of adversary TTPs for detection gap analysis and threat-informed defense.
- **Full reference:** `references/analyzing-apt-group-with-mitre-navigator/SKILL.md`
- **Execution scripts:** `scripts/analyzing-apt-group-with-mitre-navigator/`

### analyzing-dns-logs-for-exfiltration
Analyzes DNS query logs to detect data exfiltration via DNS tunneling, DGA domain communication, and covert C2 channels using entropy analysis, query volume anomalies, and subdomain length detection in SIEM platforms. Use when SOC teams need to identify DNS-based threats that bypass traditional network security controls.

- **Full reference:** `references/analyzing-dns-logs-for-exfiltration/SKILL.md`
- **Execution scripts:** `scripts/analyzing-dns-logs-for-exfiltration/`

### analyzing-windows-shellbag-artifacts
Analyze Windows Shellbag registry artifacts to reconstruct folder browsing activity, detect access to removable media and network shares, and establish user interaction with directories even after deletion using SBECmd and ShellBags Explorer.
- **Full reference:** `references/analyzing-windows-shellbag-artifacts/SKILL.md`
- **Execution scripts:** `scripts/analyzing-windows-shellbag-artifacts/`

### analyzing-usb-device-connection-history
Investigate USB device connection history from Windows registry, event logs, and setupapi logs to track removable media usage and potential data exfiltration.
- **Full reference:** `references/analyzing-usb-device-connection-history/SKILL.md`
- **Execution scripts:** `scripts/analyzing-usb-device-connection-history/`

### analyzing-uefi-bootkit-persistence
Analyzes UEFI bootkit persistence mechanisms including firmware implants in SPI flash, EFI System Partition (ESP) modifications, Secure Boot bypass techniques, and UEFI variable manipulation. Covers detection of known bootkit families (BlackLotus, LoJax, MosaicRegressor, MoonBounce, CosmicStrand), ESP partition forensic inspection, chipsec-based firmware integrity verification, and Secure Boot configuration auditing. Activates for requests involving UEFI malware analysis, firmware persistence investigation, boot chain integrity verification, or Secure Boot bypass detection.

- **Full reference:** `references/analyzing-uefi-bootkit-persistence/SKILL.md`
- **Execution scripts:** `scripts/analyzing-uefi-bootkit-persistence/`

### analyzing-cyber-kill-chain
Analyzes intrusion activity against the Lockheed Martin Cyber Kill Chain framework to identify which phases an adversary has completed, where defenses succeeded or failed, and what controls would have interrupted the attack at earlier phases. Use when conducting post-incident analysis, building prevention-focused security controls, or mapping detection gaps to kill chain phases. Activates for requests involving kill chain analysis, intrusion kill chain, attack phase mapping, or Lockheed Martin kill chain framework.

- **Full reference:** `references/analyzing-cyber-kill-chain/SKILL.md`
- **Execution scripts:** `scripts/analyzing-cyber-kill-chain/`

### analyzing-browser-forensics-with-hindsight
Analyze Chromium-based browser artifacts using Hindsight to extract browsing history, downloads, cookies, cached content, autofill data, saved passwords, and browser extensions from Chrome, Edge, Brave, and Opera for forensic investigation.
- **Full reference:** `references/analyzing-browser-forensics-with-hindsight/SKILL.md`
- **Execution scripts:** `scripts/analyzing-browser-forensics-with-hindsight/`

### analyzing-threat-landscape-with-misp
Analyze the threat landscape using MISP (Malware Information Sharing Platform) by querying event statistics, attribute distributions, threat actor galaxy clusters, and tag trends over time. Uses PyMISP to pull event data, compute IOC type breakdowns, identify top threat actors and malware families, and generate threat landscape reports with temporal trends.
- **Full reference:** `references/analyzing-threat-landscape-with-misp/SKILL.md`
- **Execution scripts:** `scripts/analyzing-threat-landscape-with-misp/`

### analyzing-malware-behavior-with-cuckoo-sandbox
Executes malware samples in Cuckoo Sandbox to observe runtime behavior including process creation, file system modifications, registry changes, network communications, and API calls. Generates comprehensive behavioral reports for malware classification and IOC extraction. Activates for requests involving dynamic malware analysis, sandbox detonation, behavioral analysis, or automated malware execution.

- **Full reference:** `references/analyzing-malware-behavior-with-cuckoo-sandbox/SKILL.md`
- **Execution scripts:** `scripts/analyzing-malware-behavior-with-cuckoo-sandbox/`