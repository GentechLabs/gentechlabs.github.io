# x402 Payment Security YARA Rules for NVIDIA SkillSpector

**Repository:** `10-Labs/skillspector-x402-yara-rules`

YARA rules for detecting security vulnerabilities in AI agent skills that implement or interact with the [x402 payment protocol](https://x402.org/) (HTTP 402 Payment Required).

## Overview

The x402 protocol revives the HTTP 402 status code to enable web-native micropayments across APIs, content, and AI agents. It combines synchronous HTTP authorization with asynchronous blockchain settlement, creating a cross-layer attack surface absent from conventional web and on-chain payments.

These rules are designed to be loaded via SkillSpector's `--yara-rules-dir` flag:

```bash
skillspector scan ./my-skill/ --yara-rules-dir ./x402-payment-security/
```

## Rule Categories

| Category | ID Prefix | Rules | Severity Range | Reference |
|---|---|---|---|---|
| Payment Replay & Idempotency | X402-RP | 3 | CRITICAL–HIGH | arXiv:2605.11781 §3.2 |
| Settlement Bypass & Grant-Before-Settle | X402-SB | 4 | CRITICAL–MEDIUM | arXiv:2605.11781 §3.1 |
| Cache Leakage & Header Confusion | X402-CL | 3 | HIGH–MEDIUM | arXiv:2605.11781 §3.3 |
| Payment Injection & Prompt Manipulation | X402-PI | 3 | CRITICAL–MEDIUM | AgentLISA PaymentShield |
| Facilitator & Discovery Manipulation | X402-FD | 2 | HIGH–MEDIUM | arXiv:2605.11781 §3.4 |
| Resource Binding & Authorization | X402-RB | 3 | HIGH–MEDIUM | arXiv:2605.11781 §4.6 |
| Protocol Implementation Flaws | X402-IF | 3 | CRITICAL–MEDIUM | x402 Spec, Halborn |
| Agent Wallet & Key Exposure | X402-WK | 2 | CRITICAL–MEDIUM | OWASP LLM Top 10 |
| Economic DoS & Budget Exhaustion | X402-ED | 2 | HIGH–MEDIUM | AgentLISA PaymentShield |
| Cross-SDK & Encoding Drift | X402-EDR | 1 | MEDIUM | arXiv:2605.11781 §5 |

**Total: 26 rules** (6 CRITICAL, 10 HIGH, 10 MEDIUM) across 10 security categories.

## Threat Model

These rules address the five attack classes identified in the formal security analysis of x402 (arXiv:2605.11781):

### Attack I: Settlement-Path Inconsistencies
- **I-A (Revert-Grant):** Optimistic execution grants resources before payment is final. Settlement failure leaves the attacker with unpaid service.
- **I-B (Settlement Preemption):** Caller-unbound Permit2 settlement lets an observer consume the payment authorization before the legitimate facilitator.

### Attack II: Replay & Idempotency
- Reusable X-PAYMENT payloads produce multiple HTTP-layer grants when the server does not atomically record payment identity. One payment can yield 248+ grants on live endpoints.

### Attack III: Web-Layer Handling
- **Cache Leakage:** Paid content served without `Cache-Control: no-store` leaks through CDN/proxy caches to unpaid clients.
- **Header Ambiguity:** Non-canonical X-PAYMENT parsing enables parser differential attacks.

### Attack IV: Server-Selection Manipulation
- Metadata gaming and Sybil flooding in Bazaar-style discovery steer agents toward malicious paid endpoints (up to 71.8% selection bias).

### Attack V: AI Agent-Specific
- Prompt injection in payment descriptions, recursive payment loops, and price manipulation targeting autonomous agents.

## Rule Format

Rules follow the NVIDIA SkillSpector YARA convention:

```yara
rule x402_<category>_<descriptor>
{
 meta:
   description = "..."
   category = "malware|hack_tool|exploit"
   severity = "CRITICAL|HIGH|MEDIUM"
   confidence = "0.XX"
   reference = "..."
 strings:
   ...
 condition:
   ...
}
```

- **Severity:** Maps to SkillSpector's severity scale (CRITICAL, HIGH, MEDIUM)
- **Category:** Maps to SkillSpector's pattern categories (malware, hack_tool, exploit)
- **Confidence:** 0.0–1.0 indicating likelihood of true positive

## Usage with SkillSpector

### Quick Start

```bash
# Clone the rules
git clone https://github.com/10-Labs/skillspector-x402-yara-rules.git

# Scan a skill with x402 rules
skillspector scan ./my-skill/ --yara-rules-dir ./skillspector-x402-yara-rules/

# Scan with all built-in rules plus x402 rules
skillspector scan ./my-skill/ --yara-rules-dir ./skillspector-x402-yara-rules/ --format sarif --output report.sarif
```

### CI/CD Integration (GitHub Actions)

```yaml
- name: Scan with x402 Payment Security Rules
  run: |
    git clone https://github.com/10-Labs/skillspector-x402-yara-rules.git
    skillspector scan ./skill/ \
      --yara-rules-dir ./skillspector-x402-yara-rules/ \
      --format sarif \
      --output x402-security-report.sarif
```

## Research Sources

1. **arXiv:2605.11781** — "Five Attacks on x402 Agentic Payment Protocol" (Li, Wang, Wang, 2026)
   - Formal security analysis with 25,000+ payment requests across 48 configurations
   - Identifies 11 vulnerabilities across 5 attack classes
2. **x402 Specification** — x402.org, docs.cdp.coinbase.com
3. **Halborn Security Analysis** — "x402 Explained: Security Risks & Controls for HTTP 402 Micropayments"
4. **AgentLISA PaymentShield** — "The Dawn of Agent Commerce Demands a New Security Paradigm"
5. **OWASP LLM Top 10** — Large Language Model Application Security

## License

Apache License 2.0 — see [LICENSE](LICENSE).

## Contributing

PRs welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
