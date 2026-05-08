---
name: implementing
domain: red-teaming
tags:
- implementing
- class-level
- umbrella
status: active
version: 1.0.0
description: Consolidated umbrella for implementing-* skills.
---
## Included Capabilities

### implementing-identity-verification-for-zero-trust
Implement continuous identity verification for zero trust using phishing-resistant MFA (FIDO2/WebAuthn), risk-based conditional access, and identity governance aligned with the CISA Zero Trust Maturity Model.
- **Full reference:** `references/implementing-identity-verification-for-zero-trust/SKILL.md`
- **Execution scripts:** `scripts/implementing-identity-verification-for-zero-trust/`

### implementing-continuous-security-validation-with-bas
Deploy Breach and Attack Simulation tools to continuously validate security control effectiveness by safely emulating real-world attack techniques across the kill chain.
- **Full reference:** `references/implementing-continuous-security-validation-with-bas/SKILL.md`
- **Execution scripts:** `scripts/implementing-continuous-security-validation-with-bas/`

### implementing-rsa-key-pair-management
RSA (Rivest-Shamir-Adleman) is the most widely deployed asymmetric cryptographic algorithm, used for digital signatures, key exchange, and encryption. This skill covers generating, storing, rotating,
- **Full reference:** `references/implementing-rsa-key-pair-management/SKILL.md`
- **Execution scripts:** `scripts/implementing-rsa-key-pair-management/`

### implementing-proofpoint-email-security-gateway
Deploy and configure Proofpoint Email Protection as a secure email gateway to detect and block phishing, malware, BEC, and spam before messages reach user inboxes.
- **Full reference:** `references/implementing-proofpoint-email-security-gateway/SKILL.md`
- **Execution scripts:** `scripts/implementing-proofpoint-email-security-gateway/`

### implementing-web-application-logging-with-modsecurity
Configure ModSecurity WAF with OWASP Core Rule Set (CRS) for web application logging, tune rules to reduce false positives, analyze audit logs for attack detection, and implement custom SecRules for application-specific threats. The analyst configures SecRuleEngine, SecAuditEngine, and CRS paranoia levels to balance security coverage with operational stability. Activates for requests involving WAF configuration, ModSecurity rule tuning, web application audit logging, or CRS deployment.

- **Full reference:** `references/implementing-web-application-logging-with-modsecurity/SKILL.md`
- **Execution scripts:** `scripts/implementing-web-application-logging-with-modsecurity/`

### implementing-diamond-model-analysis
The Diamond Model of Intrusion Analysis provides a structured framework for analyzing cyber intrusions by examining four core features - Adversary, Capability, Infrastructure, and Victim. This skill covers implementing the Diamond Model programmatically to classify and correlate intrusion events, build activity threads, and generate pivot-ready intelligence.
- **Full reference:** `references/implementing-diamond-model-analysis/SKILL.md`
- **Execution scripts:** `scripts/implementing-diamond-model-analysis/`

### implementing-zero-trust-dns-with-nextdns
Implement NextDNS as a zero trust DNS filtering layer with encrypted resolution, threat intelligence blocking, privacy protection, and organizational policy enforcement across all endpoints.
- **Full reference:** `references/implementing-zero-trust-dns-with-nextdns/SKILL.md`
- **Execution scripts:** `scripts/implementing-zero-trust-dns-with-nextdns/`

### implementing-dmarc-dkim-spf-email-security
SPF, DKIM, and DMARC form the three pillars of email authentication. Together they prevent domain spoofing, validate message integrity, and define policies for handling unauthenticated mail. Proper im
- **Full reference:** `references/implementing-dmarc-dkim-spf-email-security/SKILL.md`
- **Execution scripts:** `scripts/implementing-dmarc-dkim-spf-email-security/`

### implementing-microsegmentation-with-guardicore
Implementing microsegmentation using Akamai Guardicore Segmentation to map application dependencies, create granular network policies, visualize east-west traffic flows, and enforce least-privilege communication between workloads across data centers and cloud.

- **Full reference:** `references/implementing-microsegmentation-with-guardicore/SKILL.md`
- **Execution scripts:** `scripts/implementing-microsegmentation-with-guardicore/`

### implementing-mitre-attack-coverage-mapping
Implement MITRE ATT&CK coverage mapping to identify detection gaps, prioritize rule development, and measure SOC detection maturity against adversary techniques.
- **Full reference:** `references/implementing-mitre-attack-coverage-mapping/SKILL.md`
- **Execution scripts:** `scripts/implementing-mitre-attack-coverage-mapping/`

### implementing-llm-guardrails-for-security
Implements input and output validation guardrails for LLM-powered applications to prevent prompt injection, data leakage, toxic content generation, and hallucinated outputs. Builds a security validation pipeline using NVIDIA NeMo Guardrails Colang definitions, custom Python validators for PII detection and content policy enforcement, and the Guardrails AI framework for structured output validation. The guardrails system intercepts both user inputs (blocking injection attempts, stripping PII, enforcing topic boundaries) and model outputs (detecting hallucinations, filtering toxic content, validating JSON schema compliance). Activates for requests involving LLM output validation, AI content filtering, guardrail implementation, or LLM safety enforcement.

- **Full reference:** `references/implementing-llm-guardrails-for-security/SKILL.md`
- **Execution scripts:** `scripts/implementing-llm-guardrails-for-security/`

### implementing-siem-use-case-tuning
Tune SIEM detection rules to reduce false positives by analyzing alert volumes, creating whitelists, adjusting thresholds, and measuring detection efficacy metrics in Splunk and Elastic
- **Full reference:** `references/implementing-siem-use-case-tuning/SKILL.md`
- **Execution scripts:** `scripts/implementing-siem-use-case-tuning/`

### implementing-zero-trust-in-cloud
This skill guides organizations through implementing zero trust architecture in cloud environments following NIST SP 800-207 and Google BeyondCorp principles. It covers identity-centric access controls, micro-segmentation, continuous verification, device trust assessment, and deploying Identity-Aware Proxy to eliminate implicit network trust in AWS, Azure, and GCP environments.

- **Full reference:** `references/implementing-zero-trust-in-cloud/SKILL.md`
- **Execution scripts:** `scripts/implementing-zero-trust-in-cloud/`

### implementing-velociraptor-for-ir-collection
Deploy and configure Velociraptor for scalable endpoint forensic artifact collection during incident response using VQL queries, hunts, and pre-built artifact packs across Windows, Linux, and macOS environments.
- **Full reference:** `references/implementing-velociraptor-for-ir-collection/SKILL.md`
- **Execution scripts:** `scripts/implementing-velociraptor-for-ir-collection/`

### implementing-kubernetes-network-policy-with-calico
Implement Kubernetes network segmentation using Calico NetworkPolicy and GlobalNetworkPolicy for zero-trust pod-to-pod communication.
- **Full reference:** `references/implementing-kubernetes-network-policy-with-calico/SKILL.md`
- **Execution scripts:** `scripts/implementing-kubernetes-network-policy-with-calico/`

### implementing-ransomware-kill-switch-detection
Detects and exploits ransomware kill switch mechanisms including mutex-based execution guards, domain-based kill switches, and registry-based termination checks. Implements proactive mutex vaccination and kill switch domain monitoring to prevent ransomware from executing. Activates for requests involving ransomware kill switch analysis, mutex vaccination, WannaCry-style domain kill switches, or malware execution guard detection.

- **Full reference:** `references/implementing-ransomware-kill-switch-detection/SKILL.md`
- **Execution scripts:** `scripts/implementing-ransomware-kill-switch-detection/`

### implementing-vulnerability-management-with-greenbone
Deploy and operate Greenbone/OpenVAS vulnerability management using the python-gvm library to create scan targets, execute vulnerability scans, and parse scan reports via GMP protocol.
- **Full reference:** `references/implementing-vulnerability-management-with-greenbone/SKILL.md`
- **Execution scripts:** `scripts/implementing-vulnerability-management-with-greenbone/`

### implementing-runtime-application-self-protection
Deploy Runtime Application Self-Protection (RASP) agents to detect and block attacks from within application runtime, covering OpenRASP integration, attack pattern detection, and security policy configuration for Java and Python web applications.
- **Full reference:** `references/implementing-runtime-application-self-protection/SKILL.md`
- **Execution scripts:** `scripts/implementing-runtime-application-self-protection/`

### implementing-security-chaos-engineering
Implements security chaos engineering experiments that deliberately disable or degrade security controls to verify detection and response capabilities. Tests WAF bypass, firewall rule removal, log pipeline disruption, and EDR disablement scenarios using boto3 and subprocess. Use when validating SOC detection coverage and resilience.

- **Full reference:** `references/implementing-security-chaos-engineering/SKILL.md`
- **Execution scripts:** `scripts/implementing-security-chaos-engineering/`

### implementing-delinea-secret-server-for-pam
Implements Delinea Secret Server for privileged access management (PAM) including secret vault configuration, role-based access policies, automated password rotation, session recording, and integration with Active Directory and cloud platforms. Activates for requests involving PAM deployment, privileged credential vaulting, secret server administration, or password rotation automation.

- **Full reference:** `references/implementing-delinea-secret-server-for-pam/SKILL.md`
- **Execution scripts:** `scripts/implementing-delinea-secret-server-for-pam/`

### implementing-soar-automation-with-phantom
Implements Security Orchestration, Automation, and Response (SOAR) workflows using Splunk SOAR (formerly Phantom) to automate alert triage, IOC enrichment, containment actions, and incident response playbooks. Use when SOC teams need to reduce manual analyst work, standardize response procedures, or integrate multiple security tools into automated workflows.

- **Full reference:** `references/implementing-soar-automation-with-phantom/SKILL.md`
- **Execution scripts:** `scripts/implementing-soar-automation-with-phantom/`

### implementing-ot-incident-response-playbook
Develop and implement OT-specific incident response playbooks aligned with SANS PICERL framework, IEC 62443, and NIST SP 800-82 that address unique ICS challenges including safety-critical systems, limited downtime tolerance, and coordination between IT SOC, OT engineering, and plant operations teams.

- **Full reference:** `references/implementing-ot-incident-response-playbook/SKILL.md`
- **Execution scripts:** `scripts/implementing-ot-incident-response-playbook/`

### implementing-epss-score-for-vulnerability-prioritization
Integrate FIRST's Exploit Prediction Scoring System (EPSS) API to prioritize vulnerability remediation based on real-world exploitation probability within 30 days.
- **Full reference:** `references/implementing-epss-score-for-vulnerability-prioritization/SKILL.md`
- **Execution scripts:** `scripts/implementing-epss-score-for-vulnerability-prioritization/`

### implementing-security-monitoring-with-datadog
Implements security monitoring using Datadog Cloud SIEM, Cloud Security Management (CSM), and Workload Protection to detect threats, enforce compliance, and respond to security events across cloud and hybrid infrastructure. Covers Agent deployment, log source ingestion, detection rule creation, security dashboards, and automated notification workflows. Activates for requests involving Datadog security setup, Cloud SIEM configuration, CSM threat detection, or security monitoring dashboards.

- **Full reference:** `references/implementing-security-monitoring-with-datadog/SKILL.md`
- **Execution scripts:** `scripts/implementing-security-monitoring-with-datadog/`

### implementing-zero-knowledge-proof-for-authentication
Zero-Knowledge Proofs (ZKPs) allow a prover to demonstrate knowledge of a secret (such as a password or private key) without revealing the secret itself. This skill implements the Schnorr identificati
- **Full reference:** `references/implementing-zero-knowledge-proof-for-authentication/SKILL.md`
- **Execution scripts:** `scripts/implementing-zero-knowledge-proof-for-authentication/`

### implementing-envelope-encryption-with-aws-kms
Envelope encryption is a strategy where data is encrypted with a data encryption key (DEK), and the DEK itself is encrypted with a master key (KEK) managed by AWS KMS. This approach allows encrypting
- **Full reference:** `references/implementing-envelope-encryption-with-aws-kms/SKILL.md`
- **Execution scripts:** `scripts/implementing-envelope-encryption-with-aws-kms/`

### implementing-end-to-end-encryption-for-messaging
End-to-end encryption (E2EE) ensures that only the communicating parties can read messages, with no intermediary (including the server) able to decrypt them. This skill implements a simplified version
- **Full reference:** `references/implementing-end-to-end-encryption-for-messaging/SKILL.md`
- **Execution scripts:** `scripts/implementing-end-to-end-encryption-for-messaging/`

### implementing-github-advanced-security-for-code-scanning
Configure GitHub Advanced Security with CodeQL to perform automated static analysis and vulnerability detection across repositories at enterprise scale.
- **Full reference:** `references/implementing-github-advanced-security-for-code-scanning/SKILL.md`
- **Execution scripts:** `scripts/implementing-github-advanced-security-for-code-scanning/`

### implementing-container-image-minimal-base-with-distroless
Reduce container attack surface by building application images on Google distroless base images that contain only the application runtime with no shell, package manager, or unnecessary OS utilities.
- **Full reference:** `references/implementing-container-image-minimal-base-with-distroless/SKILL.md`
- **Execution scripts:** `scripts/implementing-container-image-minimal-base-with-distroless/`

### implementing-google-workspace-admin-security
Implements comprehensive Google Workspace security hardening including admin console configuration, phishing-resistant MFA enforcement, DLP policies, email authentication (SPF/DKIM/DMARC), OAuth app control, and external sharing restrictions. Activates for requests involving Google Workspace hardening, G Suite security configuration, or cloud office security administration.

- **Full reference:** `references/implementing-google-workspace-admin-security/SKILL.md`
- **Execution scripts:** `scripts/implementing-google-workspace-admin-security/`

### implementing-network-intrusion-prevention-with-suricata
Deploy and configure Suricata as a network intrusion prevention system with custom rules, Emerging Threats rulesets, and inline traffic inspection for real-time threat blocking.
- **Full reference:** `references/implementing-network-intrusion-prevention-with-suricata/SKILL.md`
- **Execution scripts:** `scripts/implementing-network-intrusion-prevention-with-suricata/`

### implementing-azure-ad-privileged-identity-management
Configure Microsoft Entra Privileged Identity Management to enforce just-in-time role activation, approval workflows, and access reviews for Azure AD privileged roles.
- **Full reference:** `references/implementing-azure-ad-privileged-identity-management/SKILL.md`
- **Execution scripts:** `scripts/implementing-azure-ad-privileged-identity-management/`

### implementing-data-loss-prevention-with-microsoft-purview
Implements data loss prevention policies using Microsoft Purview to protect sensitive information across Exchange Online, SharePoint, OneDrive, Teams, endpoint devices, and Power BI. The analyst configures sensitivity labels with encryption and content marking, creates DLP policies using built-in and custom sensitive information types with regex patterns, deploys endpoint DLP rules to control file operations on Windows and macOS devices, and monitors policy effectiveness through Activity Explorer and DLP alert management. Uses PowerShell cmdlets and the Microsoft Graph API for programmatic policy management. Activates for requests involving DLP policy creation, sensitivity label configuration, data classification, endpoint data protection, or Microsoft Purview compliance administration.

- **Full reference:** `references/implementing-data-loss-prevention-with-microsoft-purview/SKILL.md`
- **Execution scripts:** `scripts/implementing-data-loss-prevention-with-microsoft-purview/`

### implementing-jwt-signing-and-verification
JSON Web Tokens (JWT) defined in RFC 7519 are compact, URL-safe tokens used for authentication and authorization in web applications. This skill covers implementing secure JWT signing with HMAC-SHA256
- **Full reference:** `references/implementing-jwt-signing-and-verification/SKILL.md`
- **Execution scripts:** `scripts/implementing-jwt-signing-and-verification/`

### implementing-identity-governance-with-sailpoint
Deploy SailPoint IdentityNow or IdentityIQ for identity governance and administration. Covers identity lifecycle management, access request workflows, certification campaigns, role mining, SOD policy
- **Full reference:** `references/implementing-identity-governance-with-sailpoint/SKILL.md`
- **Execution scripts:** `scripts/implementing-identity-governance-with-sailpoint/`

### implementing-soar-playbook-for-phishing
Automate phishing incident response using Splunk SOAR REST API to create containers, add artifacts, and trigger playbooks
- **Full reference:** `references/implementing-soar-playbook-for-phishing/SKILL.md`
- **Execution scripts:** `scripts/implementing-soar-playbook-for-phishing/`

### implementing-dragos-platform-for-ot-monitoring
Deploy and configure the Dragos Platform for OT network monitoring, leveraging its 600+ industrial protocol parsers, intelligence-driven threat detection analytics, and asset visibility capabilities to protect ICS environments against threat groups like VOLTZITE, GRAPHITE, and BAUXITE.

- **Full reference:** `references/implementing-dragos-platform-for-ot-monitoring/SKILL.md`
- **Execution scripts:** `scripts/implementing-dragos-platform-for-ot-monitoring/`

### implementing-zero-trust-network-access-with-zscaler
Implement Zero Trust Network Access using Zscaler Private Access (ZPA) to replace traditional VPN with identity-based, context-aware access to private applications through the Zscaler Zero Trust Exchange.
- **Full reference:** `references/implementing-zero-trust-network-access-with-zscaler/SKILL.md`
- **Execution scripts:** `scripts/implementing-zero-trust-network-access-with-zscaler/`

### implementing-image-provenance-verification-with-cosign
Sign and verify container image provenance using Sigstore Cosign with keyless OIDC-based signing, attestations, and Kubernetes admission enforcement.
- **Full reference:** `references/implementing-image-provenance-verification-with-cosign/SKILL.md`
- **Execution scripts:** `scripts/implementing-image-provenance-verification-with-cosign/`

### implementing-api-gateway-security-controls
Implements security controls at the API gateway layer including authentication enforcement, rate limiting, request validation, IP allowlisting, TLS termination, and threat protection. The engineer configures API gateways (Kong, AWS API Gateway, Azure APIM, Apigee) to act as a centralized security enforcement point that validates, throttles, and monitors all API traffic before it reaches backend services. Activates for requests involving API gateway security, API management security, gateway authentication, or centralized API protection.

- **Full reference:** `references/implementing-api-gateway-security-controls/SKILL.md`
- **Execution scripts:** `scripts/implementing-api-gateway-security-controls/`

### implementing-vulnerability-sla-breach-alerting
Build automated alerting for vulnerability remediation SLA breaches with severity-based timelines, escalation workflows, and compliance reporting dashboards.
- **Full reference:** `references/implementing-vulnerability-sla-breach-alerting/SKILL.md`
- **Execution scripts:** `scripts/implementing-vulnerability-sla-breach-alerting/`

### implementing-anti-phishing-training-program
Security awareness training is the human layer of phishing defense. An effective anti-phishing training program combines regular simulations, interactive learning modules, metric tracking, and positiv
- **Full reference:** `references/implementing-anti-phishing-training-program/SKILL.md`
- **Execution scripts:** `scripts/implementing-anti-phishing-training-program/`

### implementing-api-security-posture-management
Implement API Security Posture Management to continuously discover, classify, and score APIs based on risk while enforcing security policies across the API lifecycle.
- **Full reference:** `references/implementing-api-security-posture-management/SKILL.md`
- **Execution scripts:** `scripts/implementing-api-security-posture-management/`

### implementing-google-workspace-phishing-protection
Configure Google Workspace advanced phishing and malware protection settings including pre-delivery scanning, attachment protection, spoofing detection, and Enhanced Safe Browsing.
- **Full reference:** `references/implementing-google-workspace-phishing-protection/SKILL.md`
- **Execution scripts:** `scripts/implementing-google-workspace-phishing-protection/`

### implementing-syslog-centralization-with-rsyslog
Configure rsyslog for centralized log collection with TLS encryption, custom templates, and log rotation. Generates server and client configuration files with GnuTLS stream drivers, x509 certificate authentication, per-host log segregation, and reliable queue settings for high-availability syslog infrastructure.
- **Full reference:** `references/implementing-syslog-centralization-with-rsyslog/SKILL.md`
- **Execution scripts:** `scripts/implementing-syslog-centralization-with-rsyslog/`

### implementing-zero-trust-network-access
Implementing Zero Trust Network Access (ZTNA) in cloud environments by configuring identity-aware proxies, micro-segmentation, continuous verification with conditional access policies, and replacing traditional VPN-based access with BeyondCorp-style architectures across AWS, Azure, and GCP.

- **Full reference:** `references/implementing-zero-trust-network-access/SKILL.md`
- **Execution scripts:** `scripts/implementing-zero-trust-network-access/`

### implementing-semgrep-for-custom-sast-rules
Write custom Semgrep SAST rules in YAML to detect application-specific vulnerabilities, enforce coding standards, and integrate into CI/CD pipelines.
- **Full reference:** `references/implementing-semgrep-for-custom-sast-rules/SKILL.md`
- **Execution scripts:** `scripts/implementing-semgrep-for-custom-sast-rules/`

### implementing-mimecast-targeted-attack-protection
Deploy Mimecast Targeted Threat Protection including URL Protect, Attachment Protect, Impersonation Protect, and Internal Email Protect to defend against advanced phishing and spearphishing attacks.
- **Full reference:** `references/implementing-mimecast-targeted-attack-protection/SKILL.md`
- **Execution scripts:** `scripts/implementing-mimecast-targeted-attack-protection/`

### implementing-anti-ransomware-group-policy
Configures Windows Group Policy Objects (GPO) to prevent ransomware execution and limit its spread. Implements AppLocker rules, Software Restriction Policies, Controlled Folder Access, attack surface reduction rules, and network protection settings. Activates for requests involving Windows GPO hardening against ransomware, AppLocker configuration, Controlled Folder Access setup, or endpoint protection via Group Policy.

- **Full reference:** `references/implementing-anti-ransomware-group-policy/SKILL.md`
- **Execution scripts:** `scripts/implementing-anti-ransomware-group-policy/`

### implementing-conduit-security-for-ot-remote-access
Implement secure conduit architecture for OT remote access following IEC 62443 zones and conduits model, deploying jump servers, MFA-enabled gateways, session recording, and approval-based workflows to control vendor and engineer access to industrial control systems without exposing OT networks directly.

- **Full reference:** `references/implementing-conduit-security-for-ot-remote-access/SKILL.md`
- **Execution scripts:** `scripts/implementing-conduit-security-for-ot-remote-access/`

### implementing-secret-scanning-with-gitleaks
This skill covers implementing Gitleaks for detecting and preventing hardcoded secrets in git repositories. It addresses configuring pre-commit hooks, CI/CD pipeline integration, custom rule authoring for organization-specific secrets, baseline management for existing repositories, and remediation workflows for exposed credentials.

- **Full reference:** `references/implementing-secret-scanning-with-gitleaks/SKILL.md`
- **Execution scripts:** `scripts/implementing-secret-scanning-with-gitleaks/`

### implementing-mobile-application-management
Implements Mobile Application Management (MAM) policies to protect enterprise data on managed and unmanaged mobile devices through app-level controls including data loss prevention, selective wipe, app configuration, and containerization. Use when securing corporate apps on BYOD devices, implementing Intune App Protection Policies, or enforcing data separation between personal and work apps. Activates for requests involving MAM deployment, app protection policies, mobile containerization, or BYOD security.

- **Full reference:** `references/implementing-mobile-application-management/SKILL.md`
- **Execution scripts:** `scripts/implementing-mobile-application-management/`

### implementing-fuzz-testing-in-cicd-with-aflplusplus
Integrate AFL++ coverage-guided fuzz testing into CI/CD pipelines to discover memory corruption, input handling, and logic vulnerabilities in C/C++ and compiled applications.
- **Full reference:** `references/implementing-fuzz-testing-in-cicd-with-aflplusplus/SKILL.md`
- **Execution scripts:** `scripts/implementing-fuzz-testing-in-cicd-with-aflplusplus/`

### implementing-api-security-testing-with-42crunch
Implement comprehensive API security testing using the 42Crunch platform to perform static audit and dynamic conformance scanning of OpenAPI specifications.
- **Full reference:** `references/implementing-api-security-testing-with-42crunch/SKILL.md`
- **Execution scripts:** `scripts/implementing-api-security-testing-with-42crunch/`

### implementing-rapid7-insightvm-for-scanning
Deploy and configure Rapid7 InsightVM Security Console and Scan Engines for authenticated and unauthenticated vulnerability scanning across enterprise environments.
- **Full reference:** `references/implementing-rapid7-insightvm-for-scanning/SKILL.md`
- **Execution scripts:** `scripts/implementing-rapid7-insightvm-for-scanning/`

### implementing-deception-based-detection-with-canarytoken
Deploy and monitor Canary Tokens via the Thinkst Canary API for deception-based breach detection using web bug tokens, DNS tokens, document tokens, and AWS key tokens.
- **Full reference:** `references/implementing-deception-based-detection-with-canarytoken/SKILL.md`
- **Execution scripts:** `scripts/implementing-deception-based-detection-with-canarytoken/`

### implementing-cloud-vulnerability-posture-management
Implement Cloud Security Posture Management using AWS Security Hub, Azure Defender for Cloud, and open-source tools like Prowler and ScoutSuite for multi-cloud vulnerability detection.
- **Full reference:** `references/implementing-cloud-vulnerability-posture-management/SKILL.md`
- **Execution scripts:** `scripts/implementing-cloud-vulnerability-posture-management/`

### implementing-pam-for-database-access
Deploy privileged access management for database systems including Oracle, SQL Server, PostgreSQL, and MySQL. Covers session proxy configuration, credential vaulting, query auditing, dynamic credentia
- **Full reference:** `references/implementing-pam-for-database-access/SKILL.md`
- **Execution scripts:** `scripts/implementing-pam-for-database-access/`

### implementing-disk-encryption-with-bitlocker
Implements full disk encryption using Microsoft BitLocker on Windows endpoints to protect data at rest from unauthorized access in case of device loss or theft. Use when deploying encryption for compliance requirements, securing mobile workstations, or implementing data protection controls across the enterprise. Activates for requests involving BitLocker encryption, disk encryption, TPM configuration, or data-at-rest protection.

- **Full reference:** `references/implementing-disk-encryption-with-bitlocker/SKILL.md`
- **Execution scripts:** `scripts/implementing-disk-encryption-with-bitlocker/`

### implementing-hardware-security-key-authentication
Implements FIDO2/WebAuthn hardware security key authentication including registration ceremonies, authentication flows, YubiKey enrollment, and passkey migration strategies. Builds a complete relying party server using the python-fido2 library that supports cross-platform authenticators, resident key (discoverable credential) workflows, and user verification policies. Activates for requests involving FIDO2 implementation, WebAuthn registration, hardware security key enrollment, YubiKey integration, or passkey migration from password-based authentication.

- **Full reference:** `references/implementing-hardware-security-key-authentication/SKILL.md`
- **Execution scripts:** `scripts/implementing-hardware-security-key-authentication/`

### implementing-vulnerability-remediation-sla
Vulnerability remediation SLAs define mandatory timeframes for patching or mitigating identified vulnerabilities based on severity, asset criticality, and exploit availability. Effective SLA programs
- **Full reference:** `references/implementing-vulnerability-remediation-sla/SKILL.md`
- **Execution scripts:** `scripts/implementing-vulnerability-remediation-sla/`

### implementing-pod-security-admission-controller
Implement Kubernetes Pod Security Admission to enforce baseline and restricted security profiles at namespace level using built-in admission controller.
- **Full reference:** `references/implementing-pod-security-admission-controller/SKILL.md`
- **Execution scripts:** `scripts/implementing-pod-security-admission-controller/`

### implementing-digital-signatures-with-ed25519
Ed25519 is a high-performance digital signature algorithm using the Edwards curve Curve25519. It provides 128-bit security with 64-byte signatures and 32-byte keys, offering significant advantages ove
- **Full reference:** `references/implementing-digital-signatures-with-ed25519/SKILL.md`
- **Execution scripts:** `scripts/implementing-digital-signatures-with-ed25519/`

### implementing-network-policies-for-kubernetes
Kubernetes NetworkPolicies provide pod-level network segmentation by defining ingress and egress rules that control traffic flow between pods, namespaces, and external endpoints. Combined with CNI plu
- **Full reference:** `references/implementing-network-policies-for-kubernetes/SKILL.md`
- **Execution scripts:** `scripts/implementing-network-policies-for-kubernetes/`

### implementing-network-segmentation-with-firewall-zones
Design and implement network segmentation using firewall security zones, VLANs, ACLs, and microsegmentation policies to restrict lateral movement and enforce least-privilege network access.
- **Full reference:** `references/implementing-network-segmentation-with-firewall-zones/SKILL.md`
- **Execution scripts:** `scripts/implementing-network-segmentation-with-firewall-zones/`

### implementing-aqua-security-for-container-scanning
Deploy Aqua Security's Trivy scanner to detect vulnerabilities, misconfigurations, secrets, and license issues in container images across CI/CD pipelines and registries.
- **Full reference:** `references/implementing-aqua-security-for-container-scanning/SKILL.md`
- **Execution scripts:** `scripts/implementing-aqua-security-for-container-scanning/`

### implementing-hashicorp-vault-dynamic-secrets
Implements HashiCorp Vault dynamic secrets engines for database credentials, AWS IAM keys, and PKI certificates with automatic generation, lease management, and credential rotation to eliminate static secrets in application configurations. Activates for requests involving Vault secrets engine configuration, dynamic database credentials, ephemeral cloud credentials, or automated secret rotation.

- **Full reference:** `references/implementing-hashicorp-vault-dynamic-secrets/SKILL.md`
- **Execution scripts:** `scripts/implementing-hashicorp-vault-dynamic-secrets/`

### implementing-log-forwarding-with-fluentd
Configure Fluentd and Fluent Bit for centralized log aggregation, routing, filtering, and enrichment across distributed infrastructure
- **Full reference:** `references/implementing-log-forwarding-with-fluentd/SKILL.md`
- **Execution scripts:** `scripts/implementing-log-forwarding-with-fluentd/`

### implementing-device-posture-assessment-in-zero-trust
Implementing device posture assessment as a zero trust access control by integrating endpoint health signals from CrowdStrike ZTA, Microsoft Intune, and Jamf into conditional access policies that enforce compliance before granting resource access.

- **Full reference:** `references/implementing-device-posture-assessment-in-zero-trust/SKILL.md`
- **Execution scripts:** `scripts/implementing-device-posture-assessment-in-zero-trust/`

### implementing-taxii-server-with-opentaxii
Deploy and configure an OpenTAXII server to share and consume STIX-formatted cyber threat intelligence using the TAXII 2.1 protocol for automated indicator exchange between organizations.
- **Full reference:** `references/implementing-taxii-server-with-opentaxii/SKILL.md`
- **Execution scripts:** `scripts/implementing-taxii-server-with-opentaxii/`

### implementing-aws-config-rules-for-compliance
Implementing AWS Config rules for continuous compliance monitoring of AWS resources, deploying managed and custom rules aligned to CIS and PCI DSS frameworks, configuring automatic remediation with SSM Automation, and aggregating compliance data across accounts.

- **Full reference:** `references/implementing-aws-config-rules-for-compliance/SKILL.md`
- **Execution scripts:** `scripts/implementing-aws-config-rules-for-compliance/`

### implementing-iso-27001-information-security-management
ISO/IEC 27001:2022 is the international standard for establishing, implementing, maintaining, and continually improving an Information Security Management System (ISMS). This skill covers the complete
- **Full reference:** `references/implementing-iso-27001-information-security-management/SKILL.md`
- **Execution scripts:** `scripts/implementing-iso-27001-information-security-management/`

### implementing-aws-security-hub-compliance
Implementing AWS Security Hub to aggregate security findings across AWS accounts, enable compliance standards like CIS AWS Foundations and PCI DSS, configure automated remediation with EventBridge and Lambda, and create custom security insights for organizational risk management.

- **Full reference:** `references/implementing-aws-security-hub-compliance/SKILL.md`
- **Execution scripts:** `scripts/implementing-aws-security-hub-compliance/`

### implementing-ticketing-system-for-incidents
Implements an integrated incident ticketing system connecting SIEM alerts to ServiceNow, Jira, or TheHive for structured incident tracking, SLA management, escalation workflows, and compliance documentation. Use when SOC teams need formalized incident lifecycle management with automated ticket creation, assignment routing, and resolution tracking.

- **Full reference:** `references/implementing-ticketing-system-for-incidents/SKILL.md`
- **Execution scripts:** `scripts/implementing-ticketing-system-for-incidents/`

### implementing-next-generation-firewall-with-palo-alto
Configure and deploy Palo Alto Networks next-generation firewalls with App-ID, User-ID, zone-based policies, SSL decryption, and threat prevention profiles for enterprise network security.
- **Full reference:** `references/implementing-next-generation-firewall-with-palo-alto/SKILL.md`
- **Execution scripts:** `scripts/implementing-next-generation-firewall-with-palo-alto/`

### implementing-passwordless-authentication-with-fido2
Deploy FIDO2/WebAuthn passwordless authentication using security keys and platform authenticators. Covers WebAuthn API integration, FIDO2 server configuration, passkey enrollment, biometric authentica
- **Full reference:** `references/implementing-passwordless-authentication-with-fido2/SKILL.md`
- **Execution scripts:** `scripts/implementing-passwordless-authentication-with-fido2/`

### implementing-email-sandboxing-with-proofpoint
Email sandboxing detonates suspicious attachments and URLs in isolated environments to detect zero-day malware and evasive phishing payloads. Proofpoint Targeted Attack Protection (TAP) is an industry
- **Full reference:** `references/implementing-email-sandboxing-with-proofpoint/SKILL.md`
- **Execution scripts:** `scripts/implementing-email-sandboxing-with-proofpoint/`

### implementing-immutable-backup-with-restic
Implements immutable backup strategy using restic with S3-compatible storage and object lock for ransomware-resistant data protection. Automates backup creation, integrity verification via restic check --read-data, snapshot retention policy enforcement, and restore testing. Integrates with AWS S3 Object Lock, MinIO, and Backblaze B2 for WORM (Write Once Read Many) storage that prevents backup deletion or encryption by ransomware actors.

- **Full reference:** `references/implementing-immutable-backup-with-restic/SKILL.md`
- **Execution scripts:** `scripts/implementing-immutable-backup-with-restic/`

### implementing-supply-chain-security-with-in-toto
Implement software supply chain integrity verification for container builds using the in-toto framework to create cryptographically signed attestations across CI/CD pipeline steps.
- **Full reference:** `references/implementing-supply-chain-security-with-in-toto/SKILL.md`
- **Execution scripts:** `scripts/implementing-supply-chain-security-with-in-toto/`

### implementing-ddos-mitigation-with-cloudflare
Configure Cloudflare DDoS protection with managed rulesets, rate limiting, WAF rules, Bot Management, and origin protection to mitigate volumetric, protocol, and application-layer attacks.
- **Full reference:** `references/implementing-ddos-mitigation-with-cloudflare/SKILL.md`
- **Execution scripts:** `scripts/implementing-ddos-mitigation-with-cloudflare/`

### implementing-zero-trust-with-beyondcorp
Deploy Google BeyondCorp Enterprise zero trust access controls using Identity-Aware Proxy (IAP), context-aware access policies, device trust validation, and Access Context Manager to enforce identity and posture-based access to GCP resources and internal applications.
- **Full reference:** `references/implementing-zero-trust-with-beyondcorp/SKILL.md`
- **Execution scripts:** `scripts/implementing-zero-trust-with-beyondcorp/`

### implementing-application-whitelisting-with-applocker
Implements application whitelisting using Windows AppLocker to restrict unauthorized software execution on endpoints, reducing attack surface from malware, unauthorized tools, and shadow IT. Use when enforcing application control policies, meeting compliance requirements for software restriction, or preventing execution of unsigned or untrusted binaries. Activates for requests involving AppLocker, application whitelisting, software restriction, or executable control.

- **Full reference:** `references/implementing-application-whitelisting-with-applocker/SKILL.md`
- **Execution scripts:** `scripts/implementing-application-whitelisting-with-applocker/`

### implementing-cloud-workload-protection
Implements cloud workload protection using boto3 and google-cloud APIs for runtime security monitoring, process anomaly detection, and file integrity checking on EC2/GCE instances. Scans for cryptomining, reverse shells, and unauthorized binaries. Use when building runtime security controls for cloud compute workloads.

- **Full reference:** `references/implementing-cloud-workload-protection/SKILL.md`
- **Execution scripts:** `scripts/implementing-cloud-workload-protection/`

### implementing-endpoint-detection-with-wazuh
Deploy and configure Wazuh SIEM/XDR for endpoint detection including agent management, custom decoder and rule XML creation, alert querying via the Wazuh REST API, and automated response actions.
- **Full reference:** `references/implementing-endpoint-detection-with-wazuh/SKILL.md`
- **Execution scripts:** `scripts/implementing-endpoint-detection-with-wazuh/`

### implementing-patch-management-workflow
Patch management is the systematic process of identifying, testing, deploying, and verifying software updates to remediate vulnerabilities across an organization's IT infrastructure. An effective patc
- **Full reference:** `references/implementing-patch-management-workflow/SKILL.md`
- **Execution scripts:** `scripts/implementing-patch-management-workflow/`

### implementing-secrets-management-with-vault
This skill covers deploying HashiCorp Vault for centralized secrets management across cloud environments, including dynamic secret generation for databases and cloud providers, transit encryption, PKI certificate management, and Kubernetes integration. It addresses eliminating hardcoded credentials from application code and CI/CD pipelines by implementing short-lived, automatically rotated secrets.

- **Full reference:** `references/implementing-secrets-management-with-vault/SKILL.md`
- **Execution scripts:** `scripts/implementing-secrets-management-with-vault/`

### implementing-aws-macie-for-data-classification
Implement Amazon Macie to automatically discover, classify, and protect sensitive data in S3 buckets using machine learning and pattern matching for PII, financial data, and credentials detection.
- **Full reference:** `references/implementing-aws-macie-for-data-classification/SKILL.md`
- **Execution scripts:** `scripts/implementing-aws-macie-for-data-classification/`

### implementing-api-key-security-controls
Implements secure API key generation, storage, rotation, and revocation controls to protect API authentication credentials from leakage, brute force, and abuse. The engineer designs API key formats with sufficient entropy, implements secure hashing for storage, enforces per-key scoping and rate limiting, monitors for leaked keys in public repositories, and builds key rotation workflows. Activates for requests involving API key management, API key security, key rotation policy, or API credential protection.

- **Full reference:** `references/implementing-api-key-security-controls/SKILL.md`
- **Execution scripts:** `scripts/implementing-api-key-security-controls/`

### implementing-cloud-waf-rules
This skill covers deploying and tuning Web Application Firewall rules on AWS WAF, Azure WAF, and Cloudflare to protect cloud-hosted applications against OWASP Top 10 attacks. It details configuring managed rule sets, creating custom rules for business logic protection, implementing rate limiting, deploying bot management, and reducing false positives through rule tuning and logging analysis.

- **Full reference:** `references/implementing-cloud-waf-rules/SKILL.md`
- **Execution scripts:** `scripts/implementing-cloud-waf-rules/`

### implementing-gcp-vpc-firewall-rules
Implementing and auditing GCP VPC firewall rules to enforce network segmentation, restrict ingress and egress traffic, apply hierarchical firewall policies across the organization, and monitor firewall rule effectiveness using VPC Flow Logs.

- **Full reference:** `references/implementing-gcp-vpc-firewall-rules/SKILL.md`
- **Execution scripts:** `scripts/implementing-gcp-vpc-firewall-rules/`

### implementing-ebpf-security-monitoring
Implements eBPF-based security monitoring using Cilium Tetragon for real-time process execution tracking, network connection observability, file access auditing, and runtime enforcement. Covers TracingPolicy CRD authoring with kprobe/tracepoint hooks, in-kernel filtering via matchArgs/matchBinaries selectors, JSON event export, and integration with SIEM pipelines. Use when building kernel-level runtime security observability for Linux hosts or Kubernetes clusters.

- **Full reference:** `references/implementing-ebpf-security-monitoring/SKILL.md`
- **Execution scripts:** `scripts/implementing-ebpf-security-monitoring/`

### implementing-rbac-hardening-for-kubernetes
Harden Kubernetes Role-Based Access Control by implementing least-privilege policies, auditing role bindings, eliminating cluster-admin sprawl, and integrating external identity providers.
- **Full reference:** `references/implementing-rbac-hardening-for-kubernetes/SKILL.md`
- **Execution scripts:** `scripts/implementing-rbac-hardening-for-kubernetes/`

### implementing-network-access-control-with-cisco-ise
Deploy Cisco Identity Services Engine for 802.1X wired and wireless authentication, MAC Authentication Bypass, posture assessment, and dynamic VLAN assignment for network access control.
- **Full reference:** `references/implementing-network-access-control-with-cisco-ise/SKILL.md`
- **Execution scripts:** `scripts/implementing-network-access-control-with-cisco-ise/`

### implementing-threat-modeling-with-mitre-attack
Implements threat modeling using the MITRE ATT&CK framework to map adversary TTPs against organizational assets, assess detection coverage gaps, and prioritize defensive investments. Use when SOC teams need to align detection engineering with threat landscape, conduct threat assessments for new environments, or justify security tool procurement.

- **Full reference:** `references/implementing-threat-modeling-with-mitre-attack/SKILL.md`
- **Execution scripts:** `scripts/implementing-threat-modeling-with-mitre-attack/`

### implementing-policy-as-code-with-open-policy-agent
This skill covers implementing Open Policy Agent (OPA) and Gatekeeper for policy-as-code enforcement in Kubernetes and CI/CD pipelines. It addresses writing Rego policies, deploying OPA Gatekeeper as a Kubernetes admission controller, testing policies in development, and integrating policy evaluation into deployment pipelines.

- **Full reference:** `references/implementing-policy-as-code-with-open-policy-agent/SKILL.md`
- **Execution scripts:** `scripts/implementing-policy-as-code-with-open-policy-agent/`

### implementing-stix-taxii-feed-integration
STIX (Structured Threat Information eXpression) and TAXII (Trusted Automated eXchange of Intelligence Information) are OASIS open standards for representing and transporting cyber threat intelligence.
- **Full reference:** `references/implementing-stix-taxii-feed-integration/SKILL.md`
- **Execution scripts:** `scripts/implementing-stix-taxii-feed-integration/`

### implementing-code-signing-for-artifacts
This skill covers implementing code signing for build artifacts to ensure integrity and authenticity throughout the software supply chain. It addresses signing binaries, packages, and containers using GPG, Sigstore, and platform-specific signing tools, establishing trust chains, and verifying signatures in deployment pipelines.

- **Full reference:** `references/implementing-code-signing-for-artifacts/SKILL.md`
- **Execution scripts:** `scripts/implementing-code-signing-for-artifacts/`

### implementing-mtls-for-zero-trust-services
Configures mutual TLS (mTLS) authentication between microservices using Python cryptography library for certificate generation and ssl module for TLS verification. Validates certificate chains, checks expiration, and audits mTLS deployment status. Use when implementing zero-trust service-to-service authentication.

- **Full reference:** `references/implementing-mtls-for-zero-trust-services/SKILL.md`
- **Execution scripts:** `scripts/implementing-mtls-for-zero-trust-services/`

### implementing-usb-device-control-policy
Implements USB device control policies to restrict unauthorized removable media access on endpoints, preventing data exfiltration and malware introduction via USB devices. Use when deploying device control via Group Policy, Intune, or EDR platforms to enforce USB restrictions. Activates for requests involving USB control, removable media policy, device control, or data loss prevention via USB.

- **Full reference:** `references/implementing-usb-device-control-policy/SKILL.md`
- **Execution scripts:** `scripts/implementing-usb-device-control-policy/`

### implementing-gcp-binary-authorization
Implement GCP Binary Authorization to enforce deploy-time security controls that ensure only trusted, attested container images are deployed to Google Kubernetes Engine and Cloud Run.
- **Full reference:** `references/implementing-gcp-binary-authorization/SKILL.md`
- **Execution scripts:** `scripts/implementing-gcp-binary-authorization/`

### implementing-zero-trust-for-saas-applications
Implementing zero trust access controls for SaaS applications using CASB, SSPM, conditional access policies, OAuth app governance, and session controls to enforce identity verification, device compliance, and data protection for cloud-hosted services.

- **Full reference:** `references/implementing-zero-trust-for-saas-applications/SKILL.md`
- **Execution scripts:** `scripts/implementing-zero-trust-for-saas-applications/`

### implementing-aws-iam-permission-boundaries
Configure IAM permission boundaries in AWS to delegate role creation to developers while enforcing maximum privilege limits set by the security team.
- **Full reference:** `references/implementing-aws-iam-permission-boundaries/SKILL.md`
- **Execution scripts:** `scripts/implementing-aws-iam-permission-boundaries/`

### implementing-siem-correlation-rules-for-apt
Write multi-event correlation rules that detect APT lateral movement by chaining Windows authentication events, process execution telemetry, and network connection logs across hosts. Uses Splunk SPL and Sigma rule format to correlate Event IDs 4624, 4648, 4688, and Sysmon Events 1/3 within sliding time windows to surface attack sequences invisible to single-event detections.
- **Full reference:** `references/implementing-siem-correlation-rules-for-apt/SKILL.md`
- **Execution scripts:** `scripts/implementing-siem-correlation-rules-for-apt/`

### implementing-cisa-zero-trust-maturity-model
Implement the CISA Zero Trust Maturity Model v2.0 across the five pillars of identity, devices, networks, applications, and data to achieve progressive organizational zero trust maturity.
- **Full reference:** `references/implementing-cisa-zero-trust-maturity-model/SKILL.md`
- **Execution scripts:** `scripts/implementing-cisa-zero-trust-maturity-model/`

### implementing-soar-playbook-with-palo-alto-xsoar
Implement automated incident response playbooks in Cortex XSOAR to orchestrate security workflows across SOC tools and reduce manual response time.
- **Full reference:** `references/implementing-soar-playbook-with-palo-alto-xsoar/SKILL.md`
- **Execution scripts:** `scripts/implementing-soar-playbook-with-palo-alto-xsoar/`

### implementing-api-rate-limiting-and-throttling
Implements API rate limiting and throttling controls using token bucket, sliding window, and fixed window algorithms to protect against brute force attacks, credential stuffing, resource exhaustion, and API abuse. The engineer configures per-user, per-IP, and per-endpoint rate limits using Redis-backed counters, API gateway plugins, or application middleware, and implements proper HTTP 429 responses with Retry-After headers. Activates for requests involving rate limiting implementation, API throttling setup, request quota management, or API abuse prevention.

- **Full reference:** `references/implementing-api-rate-limiting-and-throttling/SKILL.md`
- **Execution scripts:** `scripts/implementing-api-rate-limiting-and-throttling/`

### implementing-attack-surface-management
Implements external attack surface management (EASM) using Shodan, Censys, and ProjectDiscovery tools (subfinder, httpx, nuclei) for asset discovery, subdomain enumeration, service fingerprinting, and exposure scoring. Includes a weighted risk scoring algorithm based on OWASP attack surface analysis methodology and the Relative Attack Surface Quotient (RSQ). Use when building continuous ASM programs or performing external reconnaissance for security assessments.

- **Full reference:** `references/implementing-attack-surface-management/SKILL.md`
- **Execution scripts:** `scripts/implementing-attack-surface-management/`

### implementing-attack-path-analysis-with-xm-cyber
Deploy XM Cyber's continuous exposure management platform to map attack paths, identify choke points, and prioritize the 2% of exposures that threaten critical assets.
- **Full reference:** `references/implementing-attack-path-analysis-with-xm-cyber/SKILL.md`
- **Execution scripts:** `scripts/implementing-attack-path-analysis-with-xm-cyber/`

### implementing-nerc-cip-compliance-controls
This skill covers implementing North American Electric Reliability Corporation Critical Infrastructure Protection (NERC CIP) compliance controls for Bulk Electric System (BES) cyber systems. It addresses asset categorization (CIP-002), electronic security perimeters (CIP-005), system security management (CIP-007), configuration management (CIP-010), supply chain risk management (CIP-013), and the 2025 updates including mandatory MFA for remote access and expanded low-impact asset requirements.

- **Full reference:** `references/implementing-nerc-cip-compliance-controls/SKILL.md`
- **Execution scripts:** `scripts/implementing-nerc-cip-compliance-controls/`

### implementing-bgp-security-with-rpki
Implement BGP route origin validation using RPKI with Route Origin Authorizations, RPKI-to-Router protocol, and ROV policies on Cisco and Juniper routers to prevent route hijacking.
- **Full reference:** `references/implementing-bgp-security-with-rpki/SKILL.md`
- **Execution scripts:** `scripts/implementing-bgp-security-with-rpki/`

### implementing-privileged-access-workstation
Design and implement Privileged Access Workstations (PAWs) with device hardening, just-in-time access, and integration with CyberArk or BeyondTrust for secure administrative operations.
- **Full reference:** `references/implementing-privileged-access-workstation/SKILL.md`
- **Execution scripts:** `scripts/implementing-privileged-access-workstation/`

### implementing-conditional-access-policies-azure-ad
Configure Microsoft Entra ID (Azure AD) Conditional Access policies for zero trust access control. Covers signal-based policy design, device compliance requirements, risk-based authentication, named l
- **Full reference:** `references/implementing-conditional-access-policies-azure-ad/SKILL.md`
- **Execution scripts:** `scripts/implementing-conditional-access-policies-azure-ad/`

### implementing-gdpr-data-subject-access-request
Automates GDPR Data Subject Access Request (DSAR) workflows including identity verification, PII discovery across databases and files using regex and NER, data mapping, response templating per Article 15 requirements, deadline tracking, and audit logging. Covers ICO/EDPB guidance compliance, exemption handling, and scalable batch processing. Use when building or auditing DSAR response capabilities under GDPR/UK GDPR.

- **Full reference:** `references/implementing-gdpr-data-subject-access-request/SKILL.md`
- **Execution scripts:** `scripts/implementing-gdpr-data-subject-access-request/`

### implementing-honeytokens-for-breach-detection
Deploys canary tokens and honeytokens (fake AWS credentials, DNS canaries, document beacons, database records) that trigger alerts when accessed by attackers. Uses the Canarytokens API and custom webhook integrations for breach detection. Use when building deception-based early warning systems for intrusion detection.

- **Full reference:** `references/implementing-honeytokens-for-breach-detection/SKILL.md`
- **Execution scripts:** `scripts/implementing-honeytokens-for-breach-detection/`

### implementing-network-access-control
Implements 802.1X port-based network access control using RADIUS authentication, PacketFence NAC, and switch configurations to enforce identity-based access policies, posture assessment, and automatic VLAN assignment for authorized devices.

- **Full reference:** `references/implementing-network-access-control/SKILL.md`
- **Execution scripts:** `scripts/implementing-network-access-control/`

### implementing-zero-standing-privilege-with-cyberark
Deploy CyberArk Secure Cloud Access to eliminate standing privileges in hybrid and multi-cloud environments using just-in-time access with time, entitlement, and approval controls.
- **Full reference:** `references/implementing-zero-standing-privilege-with-cyberark/SKILL.md`
- **Execution scripts:** `scripts/implementing-zero-standing-privilege-with-cyberark/`

### implementing-api-threat-protection-with-apigee
Implement API threat protection using Google Apigee policies including JSON/XML threat protection, OAuth 2.0, SpikeArrest, and Advanced API Security for OWASP Top 10 defense.
- **Full reference:** `references/implementing-api-threat-protection-with-apigee/SKILL.md`
- **Execution scripts:** `scripts/implementing-api-threat-protection-with-apigee/`

### implementing-privileged-session-monitoring
Implements privileged session monitoring and recording using Privileged Access Management (PAM) solutions, focusing on CyberArk Privileged Session Manager (PSM) and open-source alternatives. Covers session recording configuration, keystroke logging, real-time monitoring, risk-based session analysis, and compliance audit trail generation. Activates for requests involving privileged session recording, PAM session monitoring, CyberArk PSM configuration, administrator activity monitoring, or compliance session auditing.

- **Full reference:** `references/implementing-privileged-session-monitoring/SKILL.md`
- **Execution scripts:** `scripts/implementing-privileged-session-monitoring/`

### implementing-memory-protection-with-dep-aslr
Implements memory protection mechanisms including DEP (Data Execution Prevention), ASLR (Address Space Layout Randomization), CFG (Control Flow Guard), and other exploit mitigations to prevent memory corruption attacks. Use when hardening endpoints against buffer overflow exploits, ROP chains, and code injection. Activates for requests involving memory protection, exploit mitigation, DEP, ASLR, or CFG configuration.

- **Full reference:** `references/implementing-memory-protection-with-dep-aslr/SKILL.md`
- **Execution scripts:** `scripts/implementing-memory-protection-with-dep-aslr/`

### implementing-endpoint-dlp-controls
Implements endpoint Data Loss Prevention (DLP) controls to detect and prevent sensitive data exfiltration through email, USB, cloud storage, and printing. Use when deploying DLP agents, creating content inspection policies, or preventing unauthorized data movement from endpoints. Activates for requests involving DLP, data exfiltration prevention, content inspection, or sensitive data protection on endpoints.

- **Full reference:** `references/implementing-endpoint-dlp-controls/SKILL.md`
- **Execution scripts:** `scripts/implementing-endpoint-dlp-controls/`

### implementing-runtime-security-with-tetragon
Implement eBPF-based runtime security observability and enforcement in Kubernetes clusters using Cilium Tetragon for kernel-level threat detection and policy enforcement.
- **Full reference:** `references/implementing-runtime-security-with-tetragon/SKILL.md`
- **Execution scripts:** `scripts/implementing-runtime-security-with-tetragon/`

### implementing-opa-gatekeeper-for-policy-enforcement
Enforce Kubernetes admission policies using OPA Gatekeeper with ConstraintTemplates, Rego rules, and the Gatekeeper policy library.
- **Full reference:** `references/implementing-opa-gatekeeper-for-policy-enforcement/SKILL.md`
- **Execution scripts:** `scripts/implementing-opa-gatekeeper-for-policy-enforcement/`

### implementing-scim-provisioning-with-okta
Implement automated user provisioning and deprovisioning using SCIM 2.0 protocol with Okta as the identity provider.
- **Full reference:** `references/implementing-scim-provisioning-with-okta/SKILL.md`
- **Execution scripts:** `scripts/implementing-scim-provisioning-with-okta/`

### implementing-network-traffic-analysis-with-arkime
Deploy and query Arkime (formerly Moloch) for full packet capture network traffic analysis. Uses the Arkime API v3 to search sessions, download PCAPs, analyze connection patterns, detect beaconing behavior, and identify suspicious network flows. Monitors DNS queries, HTTP traffic, and TLS certificate anomalies across captured traffic.
- **Full reference:** `references/implementing-network-traffic-analysis-with-arkime/SKILL.md`
- **Execution scripts:** `scripts/implementing-network-traffic-analysis-with-arkime/`

### implementing-siem-use-cases-for-detection
Implements SIEM detection use cases by designing correlation rules, threshold alerts, and behavioral analytics mapped to MITRE ATT&CK techniques across Splunk, Elastic, and Sentinel. Use when SOC teams need to expand detection coverage, formalize use case lifecycle management, or build a detection library aligned to organizational threat profile.

- **Full reference:** `references/implementing-siem-use-cases-for-detection/SKILL.md`
- **Execution scripts:** `scripts/implementing-siem-use-cases-for-detection/`

### implementing-gcp-organization-policy-constraints
Implement GCP Organization Policy constraints to enforce security guardrails across the entire resource hierarchy, restricting risky configurations and ensuring compliance at organization, folder, and project levels.
- **Full reference:** `references/implementing-gcp-organization-policy-constraints/SKILL.md`
- **Execution scripts:** `scripts/implementing-gcp-organization-policy-constraints/`

### implementing-secrets-scanning-in-ci-cd
Integrate gitleaks and trufflehog into CI/CD pipelines to detect leaked secrets before deployment
- **Full reference:** `references/implementing-secrets-scanning-in-ci-cd/SKILL.md`
- **Execution scripts:** `scripts/implementing-secrets-scanning-in-ci-cd/`

### implementing-log-integrity-with-blockchain
Build an append-only log integrity chain using SHA-256 hash chaining for tamper detection. Each log entry is hashed with the previous entry's hash to create a blockchain-like structure where modifying any entry invalidates all subsequent hashes. Implements log ingestion, chain verification, tamper detection with pinpoint identification, and periodic checkpoint anchoring to external timestamping services.
- **Full reference:** `references/implementing-log-integrity-with-blockchain/SKILL.md`
- **Execution scripts:** `scripts/implementing-log-integrity-with-blockchain/`

### implementing-api-abuse-detection-with-rate-limiting
Implement API abuse detection using token bucket, sliding window, and adaptive rate limiting algorithms to prevent DDoS, brute force, and credential stuffing attacks.
- **Full reference:** `references/implementing-api-abuse-detection-with-rate-limiting/SKILL.md`
- **Execution scripts:** `scripts/implementing-api-abuse-detection-with-rate-limiting/`

### implementing-security-information-sharing-with-stix2
Create, validate, and share STIX 2.1 threat intelligence objects using the stix2 Python library. Covers indicators, malware, campaigns, relationships, bundles, and TAXII 2.1 publishing.

- **Full reference:** `references/implementing-security-information-sharing-with-stix2/SKILL.md`
- **Execution scripts:** `scripts/implementing-security-information-sharing-with-stix2/`

### implementing-patch-management-for-ot-systems
This skill covers implementing a structured patch management program for OT/ICS environments where traditional IT patching approaches can cause process disruption or safety hazards. It addresses vendor compatibility testing, risk-based patch prioritization, staged deployment through test environments, maintenance window coordination, rollback procedures, and compensating controls when patches cannot be applied due to operational constraints or vendor restrictions.

- **Full reference:** `references/implementing-patch-management-for-ot-systems/SKILL.md`
- **Execution scripts:** `scripts/implementing-patch-management-for-ot-systems/`

### implementing-file-integrity-monitoring-with-aide
Configure AIDE (Advanced Intrusion Detection Environment) for file integrity monitoring including baseline creation, scheduled integrity checks, change detection, and alerting
- **Full reference:** `references/implementing-file-integrity-monitoring-with-aide/SKILL.md`
- **Execution scripts:** `scripts/implementing-file-integrity-monitoring-with-aide/`

### implementing-privileged-access-management-with-cyberark
Deploy CyberArk Privileged Access Management to discover, vault, rotate, and monitor privileged credentials across enterprise infrastructure. This skill covers vault architecture, session isolation, c
- **Full reference:** `references/implementing-privileged-access-management-with-cyberark/SKILL.md`
- **Execution scripts:** `scripts/implementing-privileged-access-management-with-cyberark/`

### implementing-network-deception-with-honeypots
Deploy and manage network honeypots using OpenCanary, T-Pot, or Cowrie to detect unauthorized access, lateral movement, and attacker reconnaissance.
- **Full reference:** `references/implementing-network-deception-with-honeypots/SKILL.md`
- **Execution scripts:** `scripts/implementing-network-deception-with-honeypots/`

### implementing-sigstore-for-software-signing
Implements Sigstore-based software signing and verification using Cosign keyless signing, Rekor transparency log verification, and Fulcio certificate authority integration to establish cryptographic provenance for container images, binaries, and software artifacts. The practitioner configures OIDC-based identity binding, verifies signing events against the Rekor transparency log, and integrates signing workflows into CI/CD pipelines. Activates for requests involving software supply chain signing, keyless container signing, Sigstore deployment, or artifact provenance verification.

- **Full reference:** `references/implementing-sigstore-for-software-signing/SKILL.md`
- **Execution scripts:** `scripts/implementing-sigstore-for-software-signing/`

### implementing-aws-nitro-enclave-security
Implements AWS Nitro Enclave-based confidential computing environments with cryptographic attestation, KMS policy integration using PCR-based condition keys, and secure vsock communication channels. The practitioner builds enclave images, configures attestation-aware KMS policies, validates attestation documents against the AWS Nitro PKI root of trust, and establishes isolated computation pipelines for processing sensitive data such as PII, cryptographic keys, and healthcare records. Activates for requests involving Nitro Enclave setup, enclave attestation validation, confidential computing on AWS, or KMS enclave policy configuration.

- **Full reference:** `references/implementing-aws-nitro-enclave-security/SKILL.md`
- **Execution scripts:** `scripts/implementing-aws-nitro-enclave-security/`

### implementing-cloud-dlp-for-data-protection
Implementing Cloud Data Loss Prevention (DLP) using Amazon Macie, Azure Information Protection, and Google Cloud DLP API to discover, classify, and protect sensitive data across cloud storage, databases, and data pipelines.

- **Full reference:** `references/implementing-cloud-dlp-for-data-protection/SKILL.md`
- **Execution scripts:** `scripts/implementing-cloud-dlp-for-data-protection/`

### implementing-network-traffic-baselining
Build network traffic baselines from NetFlow/IPFIX data using Python pandas for statistical analysis, z-score anomaly detection, and hourly/daily traffic pattern profiling
- **Full reference:** `references/implementing-network-traffic-baselining/SKILL.md`
- **Execution scripts:** `scripts/implementing-network-traffic-baselining/`

### implementing-container-network-policies-with-calico
Enforce Kubernetes network segmentation using Calico CNI network policies and global network policies to control pod-to-pod traffic, restrict egress, and implement zero-trust microsegmentation.
- **Full reference:** `references/implementing-container-network-policies-with-calico/SKILL.md`
- **Execution scripts:** `scripts/implementing-container-network-policies-with-calico/`

### implementing-saml-sso-with-okta
Implement SAML 2.0 Single Sign-On (SSO) using Okta as the Identity Provider (IdP). This skill covers end-to-end configuration of SAML authentication flows, attribute mapping, certificate management, a
- **Full reference:** `references/implementing-saml-sso-with-okta/SKILL.md`
- **Execution scripts:** `scripts/implementing-saml-sso-with-okta/`

### implementing-canary-tokens-for-network-intrusion
Deploys DNS, HTTP, and AWS API key canary tokens across network infrastructure to detect unauthorized access and lateral movement. Integrates with webhook alerting (Slack, Teams, email, generic HTTP) for real-time intrusion notifications. Provides automated token generation, placement strategies, and monitoring for enterprise network environments. Use when building deception-based network intrusion detection with Canarytokens.org and Thinkst Canary platforms.

- **Full reference:** `references/implementing-canary-tokens-for-network-intrusion/SKILL.md`
- **Execution scripts:** `scripts/implementing-canary-tokens-for-network-intrusion/`

### implementing-alert-fatigue-reduction
Implements strategies to reduce SOC alert fatigue by tuning detection rules, consolidating duplicate alerts, implementing risk-based alerting, and measuring alert quality metrics to maintain analyst effectiveness and prevent critical alert dismissal. Use when SOC teams face overwhelming alert volumes, high false positive rates, or declining analyst performance.

- **Full reference:** `references/implementing-alert-fatigue-reduction/SKILL.md`
- **Execution scripts:** `scripts/implementing-alert-fatigue-reduction/`

### implementing-just-in-time-access-provisioning
Implement Just-In-Time (JIT) access provisioning to eliminate standing privileges by granting temporary, time-bound access only when needed. This skill covers JIT architecture design, approval workflo
- **Full reference:** `references/implementing-just-in-time-access-provisioning/SKILL.md`
- **Execution scripts:** `scripts/implementing-just-in-time-access-provisioning/`

### implementing-purdue-model-network-segmentation
Implement network segmentation based on the Purdue Enterprise Reference Architecture (PERA) model to separate industrial control system networks into hierarchical security zones from Level 0 physical process through Level 5 enterprise, enforcing strict traffic control between OT and IT domains.

- **Full reference:** `references/implementing-purdue-model-network-segmentation/SKILL.md`
- **Execution scripts:** `scripts/implementing-purdue-model-network-segmentation/`

### implementing-infrastructure-as-code-security-scanning
This skill covers implementing automated security scanning for Infrastructure as Code (IaC) templates using tools like Checkov, tfsec, and KICS. It addresses detecting misconfigurations in Terraform, CloudFormation, Kubernetes manifests, and Helm charts before deployment, establishing policy-based governance, and integrating IaC scanning into CI/CD pipelines to prevent insecure cloud resource provisioning.

- **Full reference:** `references/implementing-infrastructure-as-code-security-scanning/SKILL.md`
- **Execution scripts:** `scripts/implementing-infrastructure-as-code-security-scanning/`

### implementing-aes-encryption-for-data-at-rest
AES (Advanced Encryption Standard) is a symmetric block cipher standardized by NIST (FIPS 197) used to protect classified and sensitive data. This skill covers implementing AES-256 encryption in GCM m
- **Full reference:** `references/implementing-aes-encryption-for-data-at-rest/SKILL.md`
- **Execution scripts:** `scripts/implementing-aes-encryption-for-data-at-rest/`

### implementing-ot-network-traffic-analysis-with-nozomi
Deploy Nozomi Networks Guardian sensors for passive OT network traffic analysis to achieve comprehensive asset visibility, real-time threat detection, and vulnerability assessment across industrial control systems without disrupting operations, leveraging behavioral anomaly detection and protocol-aware monitoring.

- **Full reference:** `references/implementing-ot-network-traffic-analysis-with-nozomi/SKILL.md`
- **Execution scripts:** `scripts/implementing-ot-network-traffic-analysis-with-nozomi/`

### implementing-api-schema-validation-security
Implement API schema validation using OpenAPI specifications and JSON Schema to enforce input/output contracts and prevent injection, data exposure, and mass assignment attacks.
- **Full reference:** `references/implementing-api-schema-validation-security/SKILL.md`
- **Execution scripts:** `scripts/implementing-api-schema-validation-security/`

### implementing-gdpr-data-protection-controls
The General Data Protection Regulation (EU) 2016/679 (GDPR) is the EU's comprehensive data protection law governing the collection, processing, storage, and transfer of personal data. This skill cover
- **Full reference:** `references/implementing-gdpr-data-protection-controls/SKILL.md`
- **Execution scripts:** `scripts/implementing-gdpr-data-protection-controls/`

### implementing-beyondcorp-zero-trust-access-model
Implementing Google's BeyondCorp zero trust access model to eliminate implicit trust from the network perimeter, enforce identity-aware access controls using IAP, Access Context Manager, and Chrome Enterprise Premium for VPN-less secure application access.

- **Full reference:** `references/implementing-beyondcorp-zero-trust-access-model/SKILL.md`
- **Execution scripts:** `scripts/implementing-beyondcorp-zero-trust-access-model/`

### implementing-devsecops-security-scanning
Integrates Static Application Security Testing (SAST), Dynamic Application Security Testing (DAST), and Software Composition Analysis (SCA) into CI/CD pipelines using open-source tools. Covers Semgrep for SAST, Trivy for SCA and container scanning, OWASP ZAP for DAST, and Gitleaks for secrets detection. Activates for requests involving DevSecOps pipeline setup, automated security scanning in CI/CD, SAST/DAST/SCA integration, or shift-left security implementation.

- **Full reference:** `references/implementing-devsecops-security-scanning/SKILL.md`
- **Execution scripts:** `scripts/implementing-devsecops-security-scanning/`

### implementing-ics-firewall-with-tofino
Deploy and configure Tofino industrial firewalls from Belden/Hirschmann to protect SCADA systems and PLCs using deep packet inspection for OT protocols including Modbus, EtherNet/IP, OPC, and S7comm, enforcing granular access control between ICS security zones.

- **Full reference:** `references/implementing-ics-firewall-with-tofino/SKILL.md`
- **Execution scripts:** `scripts/implementing-ics-firewall-with-tofino/`

### implementing-cloud-trail-log-analysis
Implementing AWS CloudTrail log analysis for security monitoring, threat detection, and forensic investigation using Athena, CloudWatch Logs Insights, and SIEM integration to identify unauthorized access, privilege escalation, and suspicious API activity.

- **Full reference:** `references/implementing-cloud-trail-log-analysis/SKILL.md`
- **Execution scripts:** `scripts/implementing-cloud-trail-log-analysis/`

### implementing-network-segmentation-for-ot
This skill covers implementing network segmentation in Operational Technology environments using VLANs, industrial firewalls, data diodes, and software-defined networking. It addresses the Purdue Model-based segmentation strategy, migration from flat networks to segmented architectures without disrupting operations, configuring OT-aware firewalls with industrial protocol deep packet inspection, and validating segmentation effectiveness through traffic analysis.

- **Full reference:** `references/implementing-network-segmentation-for-ot/SKILL.md`
- **Execution scripts:** `scripts/implementing-network-segmentation-for-ot/`

### implementing-threat-intelligence-lifecycle-management
Implement a structured threat intelligence lifecycle encompassing planning, collection, processing, analysis, dissemination, and feedback stages to produce actionable intelligence for organizational decision-making.
- **Full reference:** `references/implementing-threat-intelligence-lifecycle-management/SKILL.md`
- **Execution scripts:** `scripts/implementing-threat-intelligence-lifecycle-management/`

### implementing-passwordless-auth-with-microsoft-entra
Implements passwordless authentication using Microsoft Entra ID with FIDO2 security keys, Windows Hello for Business, Microsoft Authenticator passkeys, and certificate-based authentication to eliminate password-based attacks. Activates for requests involving passwordless deployment, FIDO2 passkey configuration, phishing-resistant MFA, or Microsoft Entra authentication method policies.

- **Full reference:** `references/implementing-passwordless-auth-with-microsoft-entra/SKILL.md`
- **Execution scripts:** `scripts/implementing-passwordless-auth-with-microsoft-entra/`

### implementing-browser-isolation-for-zero-trust
Deploys remote browser isolation (RBI) as a core component of a Zero Trust architecture. Implements isolation policies with URL categorization and risk-based routing, content disarming and reconstruction (CDR) for file sanitization, data loss prevention controls within isolated sessions, and integration with Secure Web Gateway and ZTNA platforms. Based on Cloudflare Browser Isolation, Menlo Security, and Zscaler RBI approaches. Use when hardening web access against zero-day exploits, phishing, credential theft, and browser-based data exfiltration.

- **Full reference:** `references/implementing-browser-isolation-for-zero-trust/SKILL.md`
- **Execution scripts:** `scripts/implementing-browser-isolation-for-zero-trust/`

### implementing-ransomware-backup-strategy
Designs and implements a ransomware-resilient backup strategy following the 3-2-1-1-0 methodology (3 copies, 2 media types, 1 offsite, 1 immutable/air-gapped, 0 errors on restore verification). Configures backup schedules aligned to RPO/RTO requirements, implements backup credential isolation to prevent ransomware from compromising backup infrastructure, and establishes automated restore testing. Activates for requests involving ransomware backup planning, backup resilience, air-gapped backup design, or backup recovery point objective configuration.

- **Full reference:** `references/implementing-ransomware-backup-strategy/SKILL.md`
- **Execution scripts:** `scripts/implementing-ransomware-backup-strategy/`

### implementing-zero-trust-with-hashicorp-boundary
Implement HashiCorp Boundary for identity-aware zero trust infrastructure access management with dynamic credential brokering, session recording, and Vault integration.
- **Full reference:** `references/implementing-zero-trust-with-hashicorp-boundary/SKILL.md`
- **Execution scripts:** `scripts/implementing-zero-trust-with-hashicorp-boundary/`

### implementing-honeypot-for-ransomware-detection
Deploys canary files, honeypot shares, and decoy systems to detect ransomware activity at the earliest possible stage. Configures canary tokens embedded in strategic file locations that trigger alerts when ransomware attempts encryption, uses honeypot network shares that mimic high-value targets, and deploys Thinkst Canary appliances for comprehensive deception-based detection. Activates for requests involving ransomware honeypots, canary files, deception technology for ransomware, or early ransomware alerting.

- **Full reference:** `references/implementing-honeypot-for-ransomware-detection/SKILL.md`
- **Execution scripts:** `scripts/implementing-honeypot-for-ransomware-detection/`

### implementing-iec-62443-security-zones
This skill covers designing and implementing security zones and conduits for industrial automation and control systems (IACS) per IEC 62443-3-2. It addresses zone partitioning based on risk assessment, assigning Security Level targets (SL-T), designing conduit security controls, implementing microsegmentation with industrial firewalls, and validating zone architecture through traffic analysis and penetration testing against the Purdue Reference Model.

- **Full reference:** `references/implementing-iec-62443-security-zones/SKILL.md`
- **Execution scripts:** `scripts/implementing-iec-62443-security-zones/`

### implementing-google-workspace-sso-configuration
Configure SAML 2.0 single sign-on for Google Workspace with a third-party identity provider, enabling centralized authentication and enforcing organization-wide access policies.
- **Full reference:** `references/implementing-google-workspace-sso-configuration/SKILL.md`
- **Execution scripts:** `scripts/implementing-google-workspace-sso-configuration/`

### implementing-cloud-security-posture-management
Implementing Cloud Security Posture Management (CSPM) to continuously monitor multi-cloud environments for misconfigurations, compliance violations, and security risks using Prowler, ScoutSuite, AWS Security Hub, Azure Defender, and GCP Security Command Center.

- **Full reference:** `references/implementing-cloud-security-posture-management/SKILL.md`
- **Execution scripts:** `scripts/implementing-cloud-security-posture-management/`

### implementing-aws-security-hub
This skill covers deploying AWS Security Hub as a centralized cloud security posture management platform that aggregates findings from GuardDuty, Inspector, Macie, and third-party tools. It details enabling security standards like CIS AWS Foundations Benchmark, configuring automated remediation, and building executive dashboards for compliance tracking across multi-account AWS organizations.

- **Full reference:** `references/implementing-aws-security-hub/SKILL.md`
- **Execution scripts:** `scripts/implementing-aws-security-hub/`

### implementing-kubernetes-pod-security-standards
Pod Security Standards (PSS) define three levels of security policies -- Privileged, Baseline, and Restricted -- enforced by the Pod Security Admission (PSA) controller built into Kubernetes 1.25+. PS
- **Full reference:** `references/implementing-kubernetes-pod-security-standards/SKILL.md`
- **Execution scripts:** `scripts/implementing-kubernetes-pod-security-standards/`

### implementing-pci-dss-compliance-controls
PCI DSS 4.0.1 establishes 12 requirements across 6 control objectives for organizations that store, process, or transmit cardholder data. With PCI DSS 3.2.1 retiring April 2024 and 51 new requirements
- **Full reference:** `references/implementing-pci-dss-compliance-controls/SKILL.md`
- **Execution scripts:** `scripts/implementing-pci-dss-compliance-controls/`

### implementing-azure-defender-for-cloud
Implementing Microsoft Defender for Cloud to enable cloud security posture management, workload protection across VMs, containers, databases, and storage, configure security recommendations, and set up adaptive security controls with automated remediation.

- **Full reference:** `references/implementing-azure-defender-for-cloud/SKILL.md`
- **Execution scripts:** `scripts/implementing-azure-defender-for-cloud/`