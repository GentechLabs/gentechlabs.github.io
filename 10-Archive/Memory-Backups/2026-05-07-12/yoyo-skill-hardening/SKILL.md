---
name: hardening
domain: red-teaming
tags:
- hardening
- class-level
- umbrella
status: active
version: 1.0.0
description: Consolidated umbrella for hardening-* skills.
---
## Included Capabilities

### hardening-docker-containers-for-production
Hardening Docker containers for production involves applying security best practices aligned with CIS Docker Benchmark v1.8.0 to minimize attack surface, prevent privilege escalation, and enforce leas
- **Full reference:** `references/hardening-docker-containers-for-production/SKILL.md`
- **Execution scripts:** `scripts/hardening-docker-containers-for-production/`

### hardening-docker-daemon-configuration
Harden the Docker daemon by configuring daemon.json with user namespace remapping, TLS authentication, rootless mode, and CIS benchmark controls.
- **Full reference:** `references/hardening-docker-daemon-configuration/SKILL.md`
- **Execution scripts:** `scripts/hardening-docker-daemon-configuration/`

### hardening-windows-endpoint-with-cis-benchmark
Hardens Windows endpoints using CIS (Center for Internet Security) Benchmark recommendations to reduce attack surface, enforce security baselines, and meet compliance requirements. Use when deploying new Windows workstations or servers, remediating audit findings, or establishing organization-wide security baselines. Activates for requests involving Windows hardening, CIS benchmarks, GPO security baselines, or endpoint configuration compliance.

- **Full reference:** `references/hardening-windows-endpoint-with-cis-benchmark/SKILL.md`
- **Execution scripts:** `scripts/hardening-windows-endpoint-with-cis-benchmark/`

### hardening-linux-endpoint-with-cis-benchmark
Hardens Linux endpoints using CIS Benchmark recommendations for Ubuntu, RHEL, and CentOS to reduce attack surface, enforce security baselines, and meet compliance requirements. Use when deploying new Linux servers, remediating audit findings, or establishing security baselines for Linux infrastructure. Activates for requests involving Linux hardening, CIS benchmarks for Linux, server security baselines, or Linux configuration compliance.

- **Full reference:** `references/hardening-linux-endpoint-with-cis-benchmark/SKILL.md`
- **Execution scripts:** `scripts/hardening-linux-endpoint-with-cis-benchmark/`