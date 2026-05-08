---
name: monitoring
domain: red-teaming
tags:
- monitoring
- class-level
- umbrella
status: active
version: 1.0.0
description: Consolidated umbrella for monitoring-* skills.
---
## Included Capabilities

### monitoring-darkweb-sources
Monitors dark web forums, marketplaces, paste sites, and ransomware leak sites for mentions of organizational assets, leaked credentials, threatened attacks, and threat actor communications to provide early warning intelligence. Use when establishing dark web monitoring coverage, investigating specific data breach claims, or enriching incident investigations with dark web context. Activates for requests involving dark web OSINT, leak site monitoring, credential exposure, Recorded Future dark web, or Tor hidden service intelligence.

- **Full reference:** `references/monitoring-darkweb-sources/SKILL.md`
- **Execution scripts:** `scripts/monitoring-darkweb-sources/`

### monitoring-scada-modbus-traffic-anomalies
Monitors Modbus TCP traffic on SCADA and ICS networks to detect anomalous function code usage, unauthorized register writes, and suspicious communication patterns. The analyst uses deep packet inspection with pymodbus, Scapy, and Zeek to baseline normal PLC/RTU communication behavior, then applies statistical and rule-based anomaly detection to identify reconnaissance, parameter manipulation, and denial-of-service attacks targeting Modbus devices on port 502. Activates for requests involving Modbus traffic analysis, SCADA network monitoring, ICS anomaly detection, PLC security monitoring, or OT network threat detection.

- **Full reference:** `references/monitoring-scada-modbus-traffic-anomalies/SKILL.md`
- **Execution scripts:** `scripts/monitoring-scada-modbus-traffic-anomalies/`