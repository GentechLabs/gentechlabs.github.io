---
name: hunting
domain: red-teaming
tags:
- class-level
- hunting
- umbrella
status: active
version: 1.0.0
description: Consolidated umbrella for hunting-* skills.
---
## Included Capabilities

### hunting-for-living-off-the-cloud-techniques
Hunt for adversary abuse of legitimate cloud services for C2, data staging, and exfiltration including abuse of Azure, AWS, GCP services, and SaaS platforms.
- **Full reference:** `references/hunting-for-living-off-the-cloud-techniques/SKILL.md`
- **Execution scripts:** `scripts/hunting-for-living-off-the-cloud-techniques/`

### hunting-for-data-exfiltration-indicators
Hunt for data exfiltration through network traffic analysis, detecting unusual data flows, DNS tunneling, cloud storage uploads, and encrypted channel abuse.
- **Full reference:** `references/hunting-for-data-exfiltration-indicators/SKILL.md`
- **Execution scripts:** `scripts/hunting-for-data-exfiltration-indicators/`

### hunting-for-suspicious-scheduled-tasks
Hunt for adversary persistence and execution via Windows scheduled tasks by analyzing task creation events, suspicious task properties, and unusual execution patterns that indicate T1053.005 abuse.
- **Full reference:** `references/hunting-for-suspicious-scheduled-tasks/SKILL.md`
- **Execution scripts:** `scripts/hunting-for-suspicious-scheduled-tasks/`

### hunting-advanced-persistent-threats
Proactively hunts for Advanced Persistent Threat (APT) activity within enterprise environments using hypothesis-driven searches across endpoint telemetry, network logs, and memory artifacts. Use when conducting scheduled threat hunting cycles, investigating anomalous behavior flagged by UEBA, or validating that known APT TTPs are not present in the environment. Activates for requests involving MITRE ATT&CK, Velociraptor, osquery, Zeek, or threat hunting playbooks.

- **Full reference:** `references/hunting-advanced-persistent-threats/SKILL.md`
- **Execution scripts:** `scripts/hunting-advanced-persistent-threats/`

### hunting-for-lolbins-execution-in-endpoint-logs
Hunt for adversary abuse of Living Off the Land Binaries (LOLBins) by analyzing endpoint process creation logs for suspicious execution patterns of legitimate Windows system binaries used for malicious purposes.
- **Full reference:** `references/hunting-for-lolbins-execution-in-endpoint-logs/SKILL.md`
- **Execution scripts:** `scripts/hunting-for-lolbins-execution-in-endpoint-logs/`

### hunting-for-unusual-service-installations
Detect suspicious Windows service installations (MITRE ATT&CK T1543.003) by parsing System event logs for Event ID 7045, analyzing service binary paths, and identifying indicators of persistence mechanisms.
- **Full reference:** `references/hunting-for-unusual-service-installations/SKILL.md`
- **Execution scripts:** `scripts/hunting-for-unusual-service-installations/`

### hunting-for-beaconing-with-frequency-analysis
Identify command-and-control beaconing patterns in network traffic by applying statistical frequency analysis, jitter calculation, and coefficient of variation scoring to detect periodic callbacks from compromised endpoints.
- **Full reference:** `references/hunting-for-beaconing-with-frequency-analysis/SKILL.md`
- **Execution scripts:** `scripts/hunting-for-beaconing-with-frequency-analysis/`

### hunting-for-ntlm-relay-attacks
Detect NTLM relay attacks by analyzing Windows Event 4624 logon type 3 with NTLMSSP authentication, identifying IP-to-hostname mismatches, Responder traffic signatures, SMB signing status, and suspicious authentication patterns across the domain.
- **Full reference:** `references/hunting-for-ntlm-relay-attacks/SKILL.md`
- **Execution scripts:** `scripts/hunting-for-ntlm-relay-attacks/`

### hunting-for-dns-tunneling-with-zeek
Detect DNS tunneling and data exfiltration by analyzing Zeek dns.log for high-entropy subdomain queries, excessive query volume, long query lengths, and unusual DNS record types indicating covert channel communication.
- **Full reference:** `references/hunting-for-dns-tunneling-with-zeek/SKILL.md`
- **Execution scripts:** `scripts/hunting-for-dns-tunneling-with-zeek/`

### hunting-for-lateral-movement-via-wmi
Detect WMI-based lateral movement by analyzing Windows Event ID 4688 process creation and Sysmon Event ID 1 for WmiPrvSE.exe child process patterns, remote process execution, and WMI event subscription persistence.
- **Full reference:** `references/hunting-for-lateral-movement-via-wmi/SKILL.md`
- **Execution scripts:** `scripts/hunting-for-lateral-movement-via-wmi/`

### hunting-for-dcom-lateral-movement
Hunt for DCOM-based lateral movement by detecting abuse of MMC20.Application, ShellBrowserWindow, and ShellWindows COM objects through Sysmon Event ID 1 (process creation) and Event ID 3 (network connection) correlation, WMI event analysis, RPC endpoint mapper traffic on port 135, and DCOM-specific parent-child process relationships.

- **Full reference:** `references/hunting-for-dcom-lateral-movement/SKILL.md`
- **Execution scripts:** `scripts/hunting-for-dcom-lateral-movement/`

### hunting-for-dns-based-persistence
Hunt for DNS-based persistence mechanisms including DNS hijacking, dangling CNAME records, wildcard DNS abuse, and unauthorized zone modifications using passive DNS databases, SecurityTrails API, and DNS audit log analysis.
- **Full reference:** `references/hunting-for-dns-based-persistence/SKILL.md`
- **Execution scripts:** `scripts/hunting-for-dns-based-persistence/`

### hunting-for-startup-folder-persistence
Detect T1547.001 startup folder persistence by monitoring Windows startup directories for suspicious file creation, analyzing autoruns entries, and using Python watchdog for real-time filesystem monitoring.
- **Full reference:** `references/hunting-for-startup-folder-persistence/SKILL.md`
- **Execution scripts:** `scripts/hunting-for-startup-folder-persistence/`

### hunting-for-persistence-mechanisms-in-windows
Systematically hunt for adversary persistence mechanisms across Windows endpoints including registry, services, startup folders, and WMI subscriptions.
- **Full reference:** `references/hunting-for-persistence-mechanisms-in-windows/SKILL.md`
- **Execution scripts:** `scripts/hunting-for-persistence-mechanisms-in-windows/`

### hunting-credential-stuffing-attacks
Detects credential stuffing attacks by analyzing authentication logs for login velocity anomalies, ASN diversity, password spray patterns, and geographic distribution of failed logins. Uses statistical analysis on Splunk or raw log data. Use when investigating account takeover campaigns or building detection rules for auth abuse.

- **Full reference:** `references/hunting-credential-stuffing-attacks/SKILL.md`
- **Execution scripts:** `scripts/hunting-credential-stuffing-attacks/`

### hunting-for-domain-fronting-c2-traffic
Detect domain fronting C2 traffic by analyzing SNI vs HTTP Host header mismatches in proxy logs and TLS certificate discrepancies using pyOpenSSL for certificate inspection
- **Full reference:** `references/hunting-for-domain-fronting-c2-traffic/SKILL.md`
- **Execution scripts:** `scripts/hunting-for-domain-fronting-c2-traffic/`

### hunting-for-unusual-network-connections
Hunt for unusual network connections by analyzing outbound traffic patterns, rare destinations, non-standard ports, and anomalous connection frequencies from endpoints.
- **Full reference:** `references/hunting-for-unusual-network-connections/SKILL.md`
- **Execution scripts:** `scripts/hunting-for-unusual-network-connections/`

### hunting-for-dcsync-attacks
Detect DCSync attacks by analyzing Windows Event ID 4662 for unauthorized DS-Replication-Get-Changes requests from non-domain-controller accounts.
- **Full reference:** `references/hunting-for-dcsync-attacks/SKILL.md`
- **Execution scripts:** `scripts/hunting-for-dcsync-attacks/`

### hunting-for-registry-run-key-persistence
Detect MITRE ATT&CK T1547.001 registry Run key persistence by analyzing Sysmon Event ID 13 logs and registry queries to identify malicious auto-start entries.
- **Full reference:** `references/hunting-for-registry-run-key-persistence/SKILL.md`
- **Execution scripts:** `scripts/hunting-for-registry-run-key-persistence/`

### hunting-for-registry-persistence-mechanisms
Hunt for registry-based persistence mechanisms including Run keys, Winlogon modifications, IFEO injection, and COM hijacking in Windows environments.
- **Full reference:** `references/hunting-for-registry-persistence-mechanisms/SKILL.md`
- **Execution scripts:** `scripts/hunting-for-registry-persistence-mechanisms/`

### hunting-for-living-off-the-land-binaries
Proactively hunt for adversary abuse of legitimate system binaries (LOLBins) to execute malicious payloads while evading detection.
- **Full reference:** `references/hunting-for-living-off-the-land-binaries/SKILL.md`
- **Execution scripts:** `scripts/hunting-for-living-off-the-land-binaries/`

### hunting-for-defense-evasion-via-timestomping
Detect NTFS timestamp manipulation (MITRE T1070.006) by comparing $STANDARD_INFORMATION vs $FILE_NAME timestamps in the MFT. Uses analyzeMFT and Python to identify files with anomalous temporal patterns indicating anti-forensic timestomping activity.

- **Full reference:** `references/hunting-for-defense-evasion-via-timestomping/SKILL.md`
- **Execution scripts:** `scripts/hunting-for-defense-evasion-via-timestomping/`

### hunting-for-command-and-control-beaconing
Detect C2 beaconing patterns in network traffic using frequency analysis, jitter detection, and domain reputation to identify compromised endpoints communicating with adversary infrastructure.
- **Full reference:** `references/hunting-for-command-and-control-beaconing/SKILL.md`
- **Execution scripts:** `scripts/hunting-for-command-and-control-beaconing/`

### hunting-for-t1098-account-manipulation
Hunt for MITRE ATT&CK T1098 account manipulation including shadow admin creation, SID history injection, group membership changes, and credential modifications using Windows Security Event Logs.
- **Full reference:** `references/hunting-for-t1098-account-manipulation/SKILL.md`
- **Execution scripts:** `scripts/hunting-for-t1098-account-manipulation/`

### hunting-for-anomalous-powershell-execution
Hunt for malicious PowerShell activity by analyzing Script Block Logging (Event 4104), Module Logging (Event 4103), and process creation events. The analyst parses Windows Event Log EVTX files to detect obfuscated commands, AMSI bypass attempts, encoded payloads, credential dumping keywords, and suspicious download cradles. Activates for requests involving PowerShell threat hunting, script block analysis, encoded command detection, or AMSI bypass identification.

- **Full reference:** `references/hunting-for-anomalous-powershell-execution/SKILL.md`
- **Execution scripts:** `scripts/hunting-for-anomalous-powershell-execution/`

### hunting-for-spearphishing-indicators
Hunt for spearphishing campaign indicators across email logs, endpoint telemetry, and network data to detect targeted email attacks.
- **Full reference:** `references/hunting-for-spearphishing-indicators/SKILL.md`
- **Execution scripts:** `scripts/hunting-for-spearphishing-indicators/`

### hunting-for-supply-chain-compromise
Hunt for supply chain compromise indicators including trojanized software updates, compromised dependencies, unauthorized code modifications, and tampered build artifacts.
- **Full reference:** `references/hunting-for-supply-chain-compromise/SKILL.md`
- **Execution scripts:** `scripts/hunting-for-supply-chain-compromise/`

### hunting-for-process-injection-techniques
Detect process injection techniques (T1055) including CreateRemoteThread, process hollowing, and DLL injection via Sysmon Event IDs 8 and 10 and EDR process telemetry
- **Full reference:** `references/hunting-for-process-injection-techniques/SKILL.md`
- **Execution scripts:** `scripts/hunting-for-process-injection-techniques/`

### hunting-for-scheduled-task-persistence
Hunt for adversary persistence via Windows Scheduled Tasks by analyzing task creation events, suspicious task actions, and unusual scheduling patterns.
- **Full reference:** `references/hunting-for-scheduled-task-persistence/SKILL.md`
- **Execution scripts:** `scripts/hunting-for-scheduled-task-persistence/`

### hunting-for-webshell-activity
Hunt for web shell deployments on internet-facing servers by analyzing file creation in web directories, suspicious process spawning from web servers, and anomalous HTTP patterns.
- **Full reference:** `references/hunting-for-webshell-activity/SKILL.md`
- **Execution scripts:** `scripts/hunting-for-webshell-activity/`

### hunting-for-cobalt-strike-beacons
Detect Cobalt Strike beacon network activity using default TLS certificate signatures (serial 8BB00EE), JA3/JA3S/JARM fingerprints, HTTP C2 profile pattern matching, beacon jitter analysis, and named pipe detection via Zeek, Suricata, and Python PCAP analysis.
- **Full reference:** `references/hunting-for-cobalt-strike-beacons/SKILL.md`
- **Execution scripts:** `scripts/hunting-for-cobalt-strike-beacons/`

### hunting-for-persistence-via-wmi-subscriptions
Hunt for adversary persistence through Windows Management Instrumentation event subscriptions by monitoring WMI consumer, filter, and binding creation events that execute malicious code triggered by system events.
- **Full reference:** `references/hunting-for-persistence-via-wmi-subscriptions/SKILL.md`
- **Execution scripts:** `scripts/hunting-for-persistence-via-wmi-subscriptions/`

### hunting-for-data-staging-before-exfiltration
Detect data staging activity before exfiltration by monitoring for archive creation with 7-Zip/RAR, unusual temp folder access, large file consolidation, and staging directory patterns via EDR and process telemetry
- **Full reference:** `references/hunting-for-data-staging-before-exfiltration/SKILL.md`
- **Execution scripts:** `scripts/hunting-for-data-staging-before-exfiltration/`

### hunting-for-shadow-copy-deletion
Hunt for Volume Shadow Copy deletion activity that indicates ransomware preparation or anti-forensics by monitoring vssadmin, wmic, and PowerShell shadow copy commands.
- **Full reference:** `references/hunting-for-shadow-copy-deletion/SKILL.md`
- **Execution scripts:** `scripts/hunting-for-shadow-copy-deletion/`