---
name: scanning
domain: red-teaming
tags:
- scanning
- class-level
- umbrella
status: active
version: 1.0.0
description: Consolidated umbrella for scanning-* skills.
---
## Included Capabilities

### scanning-infrastructure-with-nessus
Tenable Nessus is the industry-leading vulnerability scanner used to identify security weaknesses across network infrastructure including servers, workstations, network devices, and operating systems.
- **Full reference:** `references/scanning-infrastructure-with-nessus/SKILL.md`
- **Execution scripts:** `scripts/scanning-infrastructure-with-nessus/`

### scanning-containers-with-trivy-in-cicd
This skill covers integrating Aqua Security's Trivy scanner into CI/CD pipelines for comprehensive container image vulnerability detection. It addresses scanning Docker images for OS package and application dependency CVEs, detecting misconfigurations in Dockerfiles, scanning filesystem and git repositories, and establishing severity-based quality gates that block deployment of vulnerable images.

- **Full reference:** `references/scanning-containers-with-trivy-in-cicd/SKILL.md`
- **Execution scripts:** `scripts/scanning-containers-with-trivy-in-cicd/`

### scanning-network-with-nmap-advanced
Performs advanced network reconnaissance using Nmap's scripting engine, timing controls, evasion techniques, and output parsing to discover hosts, enumerate services, detect vulnerabilities, and fingerprint operating systems across authorized target networks.

- **Full reference:** `references/scanning-network-with-nmap-advanced/SKILL.md`
- **Execution scripts:** `scripts/scanning-network-with-nmap-advanced/`

### scanning-docker-images-with-trivy
Trivy is a comprehensive open-source vulnerability scanner by Aqua Security that detects vulnerabilities in OS packages, language-specific dependencies, misconfigurations, secrets, and license violati
- **Full reference:** `references/scanning-docker-images-with-trivy/SKILL.md`
- **Execution scripts:** `scripts/scanning-docker-images-with-trivy/`

### scanning-container-images-with-grype
Scan container images for known vulnerabilities using Anchore Grype with SBOM-based matching and configurable severity thresholds.
- **Full reference:** `references/scanning-container-images-with-grype/SKILL.md`
- **Execution scripts:** `scripts/scanning-container-images-with-grype/`

### scanning-kubernetes-manifests-with-kubesec
Perform security risk analysis on Kubernetes resource manifests using Kubesec to identify misconfigurations, privilege escalation risks, and deviations from security best practices.
- **Full reference:** `references/scanning-kubernetes-manifests-with-kubesec/SKILL.md`
- **Execution scripts:** `scripts/scanning-kubernetes-manifests-with-kubesec/`