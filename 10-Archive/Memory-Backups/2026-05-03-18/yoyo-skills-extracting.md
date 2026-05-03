---
name: extracting
domain: red-teaming
tags:
- class-level
- umbrella
- extracting
status: active
version: 1.0.0
description: Consolidated umbrella for extracting-* skills.
---
## Included Capabilities

### extracting-iocs-from-malware-samples
Extracts indicators of compromise (IOCs) from malware samples including file hashes, network indicators (IPs, domains, URLs), host artifacts (file paths, registry keys, mutexes), and behavioral patterns for threat intelligence sharing and detection rule creation. Activates for requests involving IOC extraction, threat indicator harvesting, malware indicator collection, or building detection content from samples.

- **Full reference:** `references/extracting-iocs-from-malware-samples/SKILL.md`
- **Execution scripts:** `scripts/extracting-iocs-from-malware-samples/`

### extracting-memory-artifacts-with-rekall
Uses Rekall memory forensics framework to analyze memory dumps for process hollowing, injected code via VAD anomalies, hidden processes, and rootkit detection. Applies plugins like pslist, psscan, vadinfo, malfind, and dlllist to extract forensic artifacts from Windows memory images. Use during incident response memory analysis.

- **Full reference:** `references/extracting-memory-artifacts-with-rekall/SKILL.md`
- **Execution scripts:** `scripts/extracting-memory-artifacts-with-rekall/`

### extracting-windows-event-logs-artifacts
Extract, parse, and analyze Windows Event Logs (EVTX) using Chainsaw, Hayabusa, and EvtxECmd to detect lateral movement, persistence, and privilege escalation.
- **Full reference:** `references/extracting-windows-event-logs-artifacts/SKILL.md`
- **Execution scripts:** `scripts/extracting-windows-event-logs-artifacts/`

### extracting-browser-history-artifacts
Extract and analyze browser history, cookies, cache, downloads, and bookmarks from Chrome, Firefox, and Edge for forensic evidence of user web activity.
- **Full reference:** `references/extracting-browser-history-artifacts/SKILL.md`
- **Execution scripts:** `scripts/extracting-browser-history-artifacts/`

### extracting-config-from-agent-tesla-rat
Extract embedded configuration from Agent Tesla RAT samples including SMTP/FTP/Telegram exfiltration credentials, keylogger settings, and C2 endpoints using .NET decompilation and memory analysis.
- **Full reference:** `references/extracting-config-from-agent-tesla-rat/SKILL.md`
- **Execution scripts:** `scripts/extracting-config-from-agent-tesla-rat/`

### extracting-credentials-from-memory-dump
Extract cached credentials, password hashes, Kerberos tickets, and authentication tokens from memory dumps using Volatility and Mimikatz for forensic investigation.
- **Full reference:** `references/extracting-credentials-from-memory-dump/SKILL.md`
- **Execution scripts:** `scripts/extracting-credentials-from-memory-dump/`