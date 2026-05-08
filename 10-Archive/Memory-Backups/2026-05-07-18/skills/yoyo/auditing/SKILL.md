---
name: auditing
domain: red-teaming
tags:
- class-level
- auditing
- umbrella
status: active
version: 1.0.0
description: Consolidated umbrella for auditing-* skills.
---
## Included Capabilities

### auditing-azure-active-directory-configuration
Auditing Microsoft Entra ID (Azure Active Directory) configuration to identify risky authentication policies, overly permissive role assignments, stale accounts, conditional access gaps, and guest user risks using AzureAD PowerShell, Microsoft Graph API, and ScoutSuite.

- **Full reference:** `references/auditing-azure-active-directory-configuration/SKILL.md`
- **Execution scripts:** `scripts/auditing-azure-active-directory-configuration/`

### auditing-cloud-with-cis-benchmarks
This skill details how to conduct cloud security audits using Center for Internet Security benchmarks for AWS, Azure, and GCP. It covers interpreting CIS Foundations Benchmark controls, running automated assessments with tools like Prowler and ScoutSuite, remediating failed controls, and maintaining continuous compliance monitoring against CIS v5 for AWS, v4 for Azure, and v4 for GCP.

- **Full reference:** `references/auditing-cloud-with-cis-benchmarks/SKILL.md`
- **Execution scripts:** `scripts/auditing-cloud-with-cis-benchmarks/`

### auditing-gcp-iam-permissions
Auditing Google Cloud Platform IAM permissions to identify overly permissive bindings, primitive role usage, service account key proliferation, and cross-project access risks using gcloud CLI, Policy Analyzer, and IAM Recommender.

- **Full reference:** `references/auditing-gcp-iam-permissions/SKILL.md`
- **Execution scripts:** `scripts/auditing-gcp-iam-permissions/`

### auditing-kubernetes-cluster-rbac
Auditing Kubernetes cluster RBAC configurations to identify overly permissive roles, wildcard permissions, dangerous ClusterRoleBindings, service account abuse, and privilege escalation paths using kubectl, rbac-tool, KubiScan, and Kubeaudit.

- **Full reference:** `references/auditing-kubernetes-cluster-rbac/SKILL.md`
- **Execution scripts:** `scripts/auditing-kubernetes-cluster-rbac/`

### auditing-aws-s3-bucket-permissions
Systematically audit AWS S3 bucket permissions to identify publicly accessible buckets, overly permissive ACLs, misconfigured bucket policies, and missing encryption settings using AWS CLI, S3audit, and Prowler to enforce least-privilege data access controls.

- **Full reference:** `references/auditing-aws-s3-bucket-permissions/SKILL.md`
- **Execution scripts:** `scripts/auditing-aws-s3-bucket-permissions/`

### auditing-tls-certificate-transparency-logs
Monitors Certificate Transparency (CT) logs to detect unauthorized certificate issuance, discover subdomains via CT data, and alert on suspicious certificate activity for owned domains. Uses the crt.sh API and direct CT log querying based on RFC 6962 to build continuous monitoring pipelines that catch rogue certificates, track CA behavior, and map the external attack surface. Activates for requests involving certificate transparency monitoring, CT log auditing, subdomain discovery via certificates, or certificate issuance alerting.

- **Full reference:** `references/auditing-tls-certificate-transparency-logs/SKILL.md`
- **Execution scripts:** `scripts/auditing-tls-certificate-transparency-logs/`

### auditing-terraform-infrastructure-for-security
Auditing Terraform infrastructure-as-code for security misconfigurations using Checkov, tfsec, Terrascan, and OPA/Rego policies to detect overly permissive IAM policies, public resource exposure, missing encryption, and insecure defaults before cloud deployment.

- **Full reference:** `references/auditing-terraform-infrastructure-for-security/SKILL.md`
- **Execution scripts:** `scripts/auditing-terraform-infrastructure-for-security/`