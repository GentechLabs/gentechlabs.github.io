# Quantum Risk Assessment — GenTech Treasury
**Date:** 2026-07-24
**Author:** GenTech Labs

## 1. Executive Summary

The GenTech Quantum-Safe Agentic Treasury has been built with post-quantum cryptography as a core architectural principle — not as a future patch. As of July 24, 2026, the treasury supports hybrid ECDSA (secp256k1) + SPHINCS+ (SLH-DSA, NIST standardized) dual signatures, fresh address generation per transaction, and a quantum emergency circuit breaker.

**Current risk level for most agent wallets:** CRITICAL within 18 months.
**GenTech Treasury risk level:** LOW — quantum-safe by design.

## 2. Quantum Threat Timeline

| Threat | Probability | Impact | Timeline |
|--------|------------|--------|----------|
| ECDSA broken by CRQC (1200+ logical qubits) | Medium-High | Full wallet drain | 2026-2028 |
| Harvest-Now-Decrypt-Later | Active today | Retroactive exposure | Ongoing |
| SHA-256 weakened by Grover's Algorithm | Low-Medium | Reduced security margin | 2028+ |
| AI-assisted vulnerability discovery | Medium | Unknown attack vectors | Active today |

## 3. Cryptographic Posture

### Current (As-Built)

| Scheme | Status | Quantum-Safe? | Notes |
|--------|--------|---------------|-------|
| ECDSA (secp256k1) | Production | No | Standard today, will fall |
| SPHINCS+ (SLH-DSA SHA2 128S) | Production | Yes | NIST standardized, stateless |
| Hybrid (ECDSA + SPHINCS+) | Production | Yes (redundant) | Both must verify |
| WOTS (Pure Python) | Dev/Test | Yes | Fallback when liboqs unavailable |

### Mitigation Strategy

1. **Hybrid signing** — Every transaction requires both ECDSA + SPHINCS+. When ECDSA falls, drop ECDSA verification.
2. **Fresh addresses** — No address used twice. Limits quantum exposure to single tx window.
3. **Emergency circuit** — Pauses outbound tx on quantum threat detection.
4. **Model logging** — All AI interactions logged, suspicious patterns flagged.

## 4. Key Findings

- **Signature sizes:** SPHINCS+ (SLH-DSA) signatures are ~7.9KB vs ECDSA's ~72 bytes. On L2s this costs ~$0.01-0.05 per tx. Acceptable for treasury operations.
- **liboqs compilation time:** ~5 minutes on first import. Acceptable for server deployments.
- **Pure Python fallback:** WOTS signatures are ~1.1KB but are one-time-use only. Suitable for dev/test.
- **No production key storage yet:** The current implementation generates fresh PQC keys per signing session. Persistent key storage needed for production (Phase 2).

## 5. Recommendations

1. Prioritize persistent SPHINCS+ key storage (encrypted keystore, not in-memory)
2. Add Dilithium as an additional PQC option (smaller signatures, stateful)
3. Implement automated key rotation every 7 days
4. Wire emergency circuit into live monitoring dashboard
5. Publish public quantum readiness report after Phase 2 complete
