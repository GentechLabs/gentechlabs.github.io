---
name: configuring
domain: red-teaming
tags:
- class-level
- configuring
- umbrella
status: active
version: 1.0.0
description: Consolidated umbrella for configuring-* skills.
---
## Included Capabilities

### configuring-microsegmentation-for-zero-trust
Configure microsegmentation policies to enforce least-privilege workload-to-workload access using tools like VMware NSX, Illumio, and Calico, preventing lateral movement in zero trust architectures.
- **Full reference:** `references/configuring-microsegmentation-for-zero-trust/SKILL.md`
- **Execution scripts:** `scripts/configuring-microsegmentation-for-zero-trust/`

### configuring-windows-defender-advanced-settings
Configures Microsoft Defender for Endpoint (MDE) advanced protection settings including attack surface reduction rules, controlled folder access, network protection, and exploit protection. Use when hardening Windows endpoints beyond default Defender settings, deploying enterprise-grade endpoint protection, or meeting compliance requirements for advanced malware defense. Activates for requests involving Windows Defender configuration, ASR rules, MDE tuning, or Microsoft endpoint security.

- **Full reference:** `references/configuring-windows-defender-advanced-settings/SKILL.md`
- **Execution scripts:** `scripts/configuring-windows-defender-advanced-settings/`

### configuring-active-directory-tiered-model
Implement Microsoft's Enhanced Security Admin Environment (ESAE) tiered administration model for Active Directory. Covers Tier 0/1/2 separation, privileged access workstations (PAWs), administrative f
- **Full reference:** `references/configuring-active-directory-tiered-model/SKILL.md`
- **Execution scripts:** `scripts/configuring-active-directory-tiered-model/`

### configuring-ldap-security-hardening
Harden LDAP directory services against common attacks including credential harvesting, LDAP injection, anonymous binding, and channel binding bypass. Covers LDAPS enforcement, channel binding, LDAP si
- **Full reference:** `references/configuring-ldap-security-hardening/SKILL.md`
- **Execution scripts:** `scripts/configuring-ldap-security-hardening/`

### configuring-host-based-intrusion-detection
Configures host-based intrusion detection systems (HIDS) to monitor endpoint file integrity, system calls, and configuration changes for security violations. Use when deploying OSSEC, Wazuh, or AIDE for endpoint monitoring, building file integrity monitoring (FIM) policies, or meeting compliance requirements for change detection. Activates for requests involving HIDS configuration, file integrity monitoring, OSSEC/Wazuh deployment, or host-based detection.

- **Full reference:** `references/configuring-host-based-intrusion-detection/SKILL.md`
- **Execution scripts:** `scripts/configuring-host-based-intrusion-detection/`

### configuring-oauth2-authorization-flow
Configure secure OAuth 2.0 authorization flows including Authorization Code with PKCE, Client Credentials, and Device Authorization Grant. This skill covers flow selection, PKCE implementation, token
- **Full reference:** `references/configuring-oauth2-authorization-flow/SKILL.md`
- **Execution scripts:** `scripts/configuring-oauth2-authorization-flow/`

### configuring-identity-aware-proxy-with-google-iap
Configuring Google Cloud Identity-Aware Proxy (IAP) to enforce per-request identity verification for Compute Engine, App Engine, Cloud Run, and GKE services using access levels, context-aware policies, and programmatic access with service accounts.

- **Full reference:** `references/configuring-identity-aware-proxy-with-google-iap/SKILL.md`
- **Execution scripts:** `scripts/configuring-identity-aware-proxy-with-google-iap/`

### configuring-suricata-for-network-monitoring
Deploys and configures Suricata IDS/IPS with Emerging Threats rulesets, EVE JSON logging, and custom rules for real-time network traffic inspection, threat detection, and integration with SIEM platforms for centralized security monitoring.

- **Full reference:** `references/configuring-suricata-for-network-monitoring/SKILL.md`
- **Execution scripts:** `scripts/configuring-suricata-for-network-monitoring/`

### configuring-hsm-for-key-storage
Hardware Security Modules (HSMs) are tamper-resistant physical devices that safeguard cryptographic keys and perform cryptographic operations in a hardened environment. Keys stored in an HSM never lea
- **Full reference:** `references/configuring-hsm-for-key-storage/SKILL.md`
- **Execution scripts:** `scripts/configuring-hsm-for-key-storage/`

### configuring-zscaler-private-access-for-ztna
Configuring Zscaler Private Access (ZPA) to replace traditional VPN with zero trust network access by deploying App Connectors, defining application segments, configuring access policies based on user identity and device posture, and integrating with IdPs.

- **Full reference:** `references/configuring-zscaler-private-access-for-ztna/SKILL.md`
- **Execution scripts:** `scripts/configuring-zscaler-private-access-for-ztna/`

### configuring-certificate-authority-with-openssl
A Certificate Authority (CA) is the trust anchor in a PKI hierarchy, responsible for issuing, signing, and revoking digital certificates. This skill covers building a two-tier CA hierarchy (Root CA +
- **Full reference:** `references/configuring-certificate-authority-with-openssl/SKILL.md`
- **Execution scripts:** `scripts/configuring-certificate-authority-with-openssl/`

### configuring-pfsense-firewall-rules
Configures pfSense firewall rules, NAT policies, VPN tunnels, and traffic shaping to enforce network segmentation, control traffic flow, and protect internal network zones in enterprise and small-to-medium business environments.

- **Full reference:** `references/configuring-pfsense-firewall-rules/SKILL.md`
- **Execution scripts:** `scripts/configuring-pfsense-firewall-rules/`

### configuring-network-segmentation-with-vlans
Designs and implements VLAN-based network segmentation on managed switches to isolate network zones, enforce access control between segments, and reduce the attack surface by limiting lateral movement paths in enterprise network environments.

- **Full reference:** `references/configuring-network-segmentation-with-vlans/SKILL.md`
- **Execution scripts:** `scripts/configuring-network-segmentation-with-vlans/`

### configuring-multi-factor-authentication-with-duo
Deploy Cisco Duo multi-factor authentication across enterprise applications, VPN, RDP, and SSH access points. This skill covers Duo integration methods, adaptive authentication policies, device trust
- **Full reference:** `references/configuring-multi-factor-authentication-with-duo/SKILL.md`
- **Execution scripts:** `scripts/configuring-multi-factor-authentication-with-duo/`

### configuring-tls-1-3-for-secure-communications
TLS 1.3 (RFC 8446) is the latest version of the Transport Layer Security protocol, providing significant improvements over TLS 1.2 in both security and performance. It reduces handshake latency to 1-R
- **Full reference:** `references/configuring-tls-1-3-for-secure-communications/SKILL.md`
- **Execution scripts:** `scripts/configuring-tls-1-3-for-secure-communications/`

### configuring-snort-ids-for-intrusion-detection
Installs, configures, and tunes Snort 3 intrusion detection system to monitor network traffic for malicious activity using custom and community rulesets, preprocessors, and alert output plugins on authorized network segments.

- **Full reference:** `references/configuring-snort-ids-for-intrusion-detection/SKILL.md`
- **Execution scripts:** `scripts/configuring-snort-ids-for-intrusion-detection/`

### configuring-aws-verified-access-for-ztna
Configure AWS Verified Access to provide VPN-less zero trust network access to internal applications using identity and device posture verification with Cedar policy language.
- **Full reference:** `references/configuring-aws-verified-access-for-ztna/SKILL.md`
- **Execution scripts:** `scripts/configuring-aws-verified-access-for-ztna/`

### configuring-windows-event-logging-for-detection
Configures Windows Event Logging with advanced audit policies to generate high-fidelity security events for threat detection and forensic investigation. Use when enabling audit policies for logon events, process creation, privilege use, and object access to feed SIEM detection rules. Activates for requests involving Windows audit policy, event log configuration, security logging, or detection-oriented logging.

- **Full reference:** `references/configuring-windows-event-logging-for-detection/SKILL.md`
- **Execution scripts:** `scripts/configuring-windows-event-logging-for-detection/`