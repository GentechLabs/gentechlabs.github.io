---
name: deploying
domain: red-teaming
tags:
- deploying
- class-level
- umbrella
status: active
version: 1.0.0
description: Consolidated umbrella for deploying-* skills.
---
## Included Capabilities

### deploying-osquery-for-endpoint-monitoring
Deploys and configures osquery for real-time endpoint monitoring using SQL-based queries to inspect running processes, open ports, installed software, and system configuration. Use when building visibility into endpoint state, threat hunting across fleet, or implementing compliance monitoring. Activates for requests involving osquery deployment, endpoint visibility, fleet management, or SQL-based endpoint querying.

- **Full reference:** `references/deploying-osquery-for-endpoint-monitoring/SKILL.md`
- **Execution scripts:** `scripts/deploying-osquery-for-endpoint-monitoring/`

### deploying-tailscale-for-zero-trust-vpn
Deploy and configure Tailscale as a WireGuard-based zero trust mesh VPN with identity-aware access controls, ACLs, and exit nodes for secure peer-to-peer connectivity.
- **Full reference:** `references/deploying-tailscale-for-zero-trust-vpn/SKILL.md`
- **Execution scripts:** `scripts/deploying-tailscale-for-zero-trust-vpn/`

### deploying-edr-agent-with-crowdstrike
Deploys and configures CrowdStrike Falcon EDR agents across enterprise endpoints to enable real-time threat detection, behavioral analysis, and automated response. Use when onboarding endpoints to EDR coverage, configuring detection policies, or integrating Falcon telemetry with SIEM platforms. Activates for requests involving CrowdStrike deployment, Falcon sensor installation, EDR policy configuration, or endpoint detection and response.

- **Full reference:** `references/deploying-edr-agent-with-crowdstrike/SKILL.md`
- **Execution scripts:** `scripts/deploying-edr-agent-with-crowdstrike/`

### deploying-active-directory-honeytokens
Deploys deception-based honeytokens in Active Directory including fake privileged accounts with AdminCount=1, fake SPNs for Kerberoasting detection (honeyroasting), decoy GPOs with cpassword traps, and fake BloodHound paths. Monitors Windows Security Event IDs 4769, 4625, 4662, 5136 for honeytoken interaction. Use when implementing AD deception defenses for detecting lateral movement, credential theft, and reconnaissance.

- **Full reference:** `references/deploying-active-directory-honeytokens/SKILL.md`
- **Execution scripts:** `scripts/deploying-active-directory-honeytokens/`

### deploying-software-defined-perimeter
Deploy a Software-Defined Perimeter using the CSA v2.0 specification with Single Packet Authorization, mutual TLS, and SDP controller/gateway configuration to enforce zero trust network access.
- **Full reference:** `references/deploying-software-defined-perimeter/SKILL.md`
- **Execution scripts:** `scripts/deploying-software-defined-perimeter/`

### deploying-cloudflare-access-for-zero-trust
Deploying Cloudflare Access with Cloudflare Tunnel to provide zero trust access to self-hosted and private applications, configuring identity-aware access policies, device posture checks, and WARP client enrollment for VPN replacement.

- **Full reference:** `references/deploying-cloudflare-access-for-zero-trust/SKILL.md`
- **Execution scripts:** `scripts/deploying-cloudflare-access-for-zero-trust/`

### deploying-decoy-files-for-ransomware-detection
Deploys canary files (honeytokens) across file systems to detect ransomware encryption activity in real time. Uses strategically placed decoy documents monitored via file integrity monitoring or OS-level watchdogs to trigger alerts when ransomware modifies or encrypts them. Activates for requests involving ransomware canary deployment, honeyfile setup, deception-based ransomware detection, or file integrity monitoring for encryption.

- **Full reference:** `references/deploying-decoy-files-for-ransomware-detection/SKILL.md`
- **Execution scripts:** `scripts/deploying-decoy-files-for-ransomware-detection/`

### deploying-ransomware-canary-files
Deploys and monitors ransomware canary files across critical directories using Python's watchdog library for real-time filesystem event detection. Places strategically named decoy files that mimic high-value targets (financial records, credentials, database exports) in locations ransomware typically enumerates first. Monitors for any read, modify, rename, or delete operations on canary files and triggers immediate alerts via email, Slack webhook, or syslog when interaction is detected, providing early warning before full encryption begins.

- **Full reference:** `references/deploying-ransomware-canary-files/SKILL.md`
- **Execution scripts:** `scripts/deploying-ransomware-canary-files/`

### deploying-palo-alto-prisma-access-zero-trust
Deploying Palo Alto Networks Prisma Access for SASE-based zero trust network access using GlobalProtect agents, ZTNA Connectors, security policy enforcement, and integration with Strata Cloud Manager for unified security management.

- **Full reference:** `references/deploying-palo-alto-prisma-access-zero-trust/SKILL.md`
- **Execution scripts:** `scripts/deploying-palo-alto-prisma-access-zero-trust/`