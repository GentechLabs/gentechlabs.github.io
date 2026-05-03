---
name: integrating
domain: red-teaming
tags:
- class-level
- integrating
- umbrella
status: active
version: 1.0.0
description: Consolidated umbrella for integrating-* skills.
---
## Included Capabilities

### integrating-dast-with-owasp-zap-in-pipeline
This skill covers integrating OWASP ZAP (Zed Attack Proxy) for Dynamic Application Security Testing in CI/CD pipelines. It addresses configuring baseline, full, and API scans against running applications, interpreting ZAP findings, tuning scan policies, and establishing DAST quality gates in GitHub Actions and GitLab CI.

- **Full reference:** `references/integrating-dast-with-owasp-zap-in-pipeline/SKILL.md`
- **Execution scripts:** `scripts/integrating-dast-with-owasp-zap-in-pipeline/`

### integrating-sast-into-github-actions-pipeline
This skill covers integrating Static Application Security Testing (SAST) tools—CodeQL and Semgrep—into GitHub Actions CI/CD pipelines. It addresses configuring automated code scanning on pull requests and pushes, tuning rules to reduce false positives, uploading SARIF results to GitHub Advanced Security, and establishing quality gates that block merges when high-severity vulnerabilities are detected.

- **Full reference:** `references/integrating-sast-into-github-actions-pipeline/SKILL.md`
- **Execution scripts:** `scripts/integrating-sast-into-github-actions-pipeline/`