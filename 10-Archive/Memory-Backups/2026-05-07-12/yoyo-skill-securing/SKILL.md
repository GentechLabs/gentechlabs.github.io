---
name: securing
domain: red-teaming
tags:
- securing
- class-level
- umbrella
status: active
version: 1.0.0
description: Consolidated umbrella for securing-* skills.
---
## Included Capabilities

### securing-container-registry-images
Securing container registry images by implementing vulnerability scanning with Trivy and Grype, enforcing image signing with Cosign and Sigstore, configuring registry access controls, and building CI/CD pipelines that prevent deploying unscanned or unsigned images.

- **Full reference:** `references/securing-container-registry-images/SKILL.md`
- **Execution scripts:** `scripts/securing-container-registry-images/`

### securing-aws-lambda-execution-roles
Securing AWS Lambda execution roles by implementing least-privilege IAM policies, applying permission boundaries, restricting resource-based policies, using IAM Access Analyzer to validate permissions, and enforcing role scoping through SCPs.

- **Full reference:** `references/securing-aws-lambda-execution-roles/SKILL.md`
- **Execution scripts:** `scripts/securing-aws-lambda-execution-roles/`

### securing-azure-with-microsoft-defender
This skill instructs security practitioners on deploying Microsoft Defender for Cloud as a cloud-native application protection platform for Azure, multi-cloud, and hybrid environments. It covers enabling Defender plans for servers, containers, storage, and databases, configuring security recommendations, managing Secure Score, and integrating with the unified Defender portal for centralized threat management.

- **Full reference:** `references/securing-azure-with-microsoft-defender/SKILL.md`
- **Execution scripts:** `scripts/securing-azure-with-microsoft-defender/`

### securing-container-registry-with-harbor
Harbor is an open-source container registry that provides security features including vulnerability scanning (integrated Trivy), image signing (Notary/Cosign), RBAC, content trust policies, replicatio
- **Full reference:** `references/securing-container-registry-with-harbor/SKILL.md`
- **Execution scripts:** `scripts/securing-container-registry-with-harbor/`

### securing-api-gateway-with-aws-waf
Securing API Gateway endpoints with AWS WAF by configuring managed rule groups for OWASP Top 10 protection, creating custom rate limiting rules, implementing bot control, setting up IP reputation filtering, and monitoring WAF metrics for security effectiveness.

- **Full reference:** `references/securing-api-gateway-with-aws-waf/SKILL.md`
- **Execution scripts:** `scripts/securing-api-gateway-with-aws-waf/`

### securing-historian-server-in-ot-environment
This skill covers hardening and securing process historian servers (OSIsoft PI, Honeywell PHD, GE Proficy, AVEVA Historian) in OT environments. It addresses network placement across Purdue levels, access control for historian interfaces, data replication through DMZ using data diodes or PI-to-PI connectors, SQL injection prevention in historian queries, and integrity protection of process data used for safety analysis, regulatory reporting, and process optimization.

- **Full reference:** `references/securing-historian-server-in-ot-environment/SKILL.md`
- **Execution scripts:** `scripts/securing-historian-server-in-ot-environment/`

### securing-github-actions-workflows
This skill covers hardening GitHub Actions workflows against supply chain attacks, credential theft, and privilege escalation. It addresses pinning actions to SHA digests, minimizing GITHUB_TOKEN permissions, protecting secrets from exfiltration, preventing script injection in workflow expressions, and implementing required reviewers for workflow changes.

- **Full reference:** `references/securing-github-actions-workflows/SKILL.md`
- **Execution scripts:** `scripts/securing-github-actions-workflows/`

### securing-helm-chart-deployments
Secure Helm chart deployments by validating chart integrity, scanning templates for misconfigurations, and enforcing security contexts in Kubernetes releases.
- **Full reference:** `references/securing-helm-chart-deployments/SKILL.md`
- **Execution scripts:** `scripts/securing-helm-chart-deployments/`

### securing-kubernetes-on-cloud
This skill covers hardening managed Kubernetes clusters on EKS, AKS, and GKE by implementing Pod Security Standards, network policies, workload identity, RBAC scoping, image admission controls, and runtime security monitoring. It addresses cloud-specific security features including IRSA for EKS, Workload Identity for GKE, and Managed Identities for AKS.

- **Full reference:** `references/securing-kubernetes-on-cloud/SKILL.md`
- **Execution scripts:** `scripts/securing-kubernetes-on-cloud/`

### securing-remote-access-to-ot-environment
This skill covers implementing secure remote access to OT/ICS environments for operators, engineers, and vendors while preventing unauthorized access that could compromise industrial operations. It addresses jump server architecture, multi-factor authentication, session recording, privileged access management, vendor remote access controls, and compliance with IEC 62443 and NERC CIP-005 remote access requirements.

- **Full reference:** `references/securing-remote-access-to-ot-environment/SKILL.md`
- **Execution scripts:** `scripts/securing-remote-access-to-ot-environment/`

### securing-serverless-functions
This skill covers security hardening for serverless compute platforms including AWS Lambda, Azure Functions, and Google Cloud Functions. It addresses least privilege IAM roles, dependency vulnerability scanning, secrets management integration, input validation, function URL authentication, and runtime monitoring to protect against injection attacks, credential theft, and supply chain compromises.

- **Full reference:** `references/securing-serverless-functions/SKILL.md`
- **Execution scripts:** `scripts/securing-serverless-functions/`

### securing-aws-iam-permissions
This skill guides practitioners through hardening AWS Identity and Access Management configurations to enforce least privilege access across cloud accounts. It covers IAM policy scoping, permission boundaries, Access Analyzer integration, and credential rotation strategies to reduce the blast radius of compromised identities.

- **Full reference:** `references/securing-aws-iam-permissions/SKILL.md`
- **Execution scripts:** `scripts/securing-aws-iam-permissions/`