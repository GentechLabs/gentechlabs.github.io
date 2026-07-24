# Quantum-Safe Agentic Treasury — Design Doc
**Status:** Draft
**Date:** 2026-07-23
**Author:** GenTech Labs

---

## 1. Thesis

The agentic treasury is the most valuable target in the agent economy. It holds keys, signs transactions, and manages funds autonomously. Current cryptographic assumptions (ECDSA, secp256k1, SHA-256) will be broken by a cryptographically-relevant quantum computer (CRQC).

**Timeline:** 1,200 logical qubits can break ECDSA. This is approaching engineering reality. 6.7M BTC ($600B) are currently vulnerable. End of 2026 is the projected date for Bitcoin social consensus on a quantum-resistant upgrade fork.

**Our position:** Build quantum-safe defaults into the treasury from day one — not as a future patch, but as a core architectural principle.

---

## 2. Threat Model

### 2.1 Quantum Threats

| Threat | Attack | Impact | Timeline |
|--------|--------|--------|----------|
| Shor's Algorithm | Factor ECDSA private key from public key | Full wallet drain | 1,200+ logical qubits |
| Grover's Algorithm | 2x speedup on SHA-256 preimage | Weakened hash security | Larger quantum computers |
| Harvest-Now-Decrypt-Later | Collect encrypted traffic today, decrypt later | Retroactive exposure | Already happening |
| Public Key Exposure | Any signed transaction reveals the public key | One transaction = wallet death | Every transaction today |

### 2.2 AI Training Data Threat

Frontier models (Kimi, Claude, GPT, Gemini) train on undisclosed datasets. The industry pattern is:

1. **Model A** claims unique training data
2. **Model B** is caught performing suspiciously well on Model A's benchmarks
3. Investigation reveals training data overlap
4. No legal recourse — training data provenance is unenforceable

**The implication for agent security:**
- If any frontier model has been trained on hacker forum data, dark web exploit code, or leaked vulnerability databases, it knows attack vectors no human auditor has catalogued
- An agent running on a frontier model could inadvertently be prompted to exploit these undocumented vectors
- The attack surface is invisible — we don't know what the models know

### 2.3 Combined Threat: Quantum + AI

The intersection is the real danger:

> An AI agent that knows undocumented vulnerabilities + a quantum computer that can break ECDSA = the ability to drain any wallet whose public key has been exposed, using attack patterns no human can predict or defend against.

---

## 3. Architecture

### 3.1 Hybrid Signing (Default)

Every treasury transaction uses dual signatures:

```
transaction = {
  payload: "...",
  sig_ecdsa: ECDSA_secp256k1(payload),     // current standard
  sig_pqc: SPHINCS+(payload),               // NIST standardized, stateless
  sig_lattice: CRYSTALS-Dilithium(payload)  // NIST standardized, efficient
}
```

**Verification:** A transaction is valid only if BOTH ECDSA AND at least one PQC signature verify.

**Migration path:** When ECDSA becomes unsafe, the treasury can drop ECDSA verification without changing the signing infrastructure — the PQC sigs are already there.

### 3.2 Fresh Address Per Transaction

Inspired by Taproot's key-spend path mitigation:

- No address is used more than once
- The treasury generates a fresh address for each outbound transaction
- Change addresses are swept to a cold-derived address
- This limits quantum exposure to the specific transaction window

### 3.3 Quantum Emergency Circuit

A circuit breaker that triggers automatically when:

**Trigger conditions:**
- NIST publishes a critical quantum advisory
- A major chain (Bitcoin, Ethereum) forks for quantum resistance
- A verified quantum attack on ECDSA is detected
- A frontier model exhibits unexplained key-recovery behavior

**Actions on trigger:**
1. Pause all outbound transactions
2. Sweep all funds to quantum-safe cold storage
3. Rotate all signing keys to hybrid PQC
4. Notify wallet owner via multiple channels
5. Generate post-mortem report

### 3.4 Model Behavior Monitoring

To address the AI training data threat:

- Treasury agents log ALL model interaction prompts and completions
- Anomaly detection flags prompts that attempt to extract key material, transaction patterns, or wallet addresses
- Suspicious model behavior triggers a human-in-the-loop gate
- Model version pinning — the treasury only runs on known-good model versions, never "auto-upgrade"

---

## 4. Implementation Phases

### Phase 1 — Foundation (Now)
- [ ] Hybrid signing support in treasury (ECDSA + SPHINCS+)
- [ ] Fresh address generation per transaction
- [ ] Export logging for model interactions
- [ ] Quantum risk assessment document

### Phase 2 — Protection (Next 30 days)
- [ ] Quantum emergency circuit with auto-trigger
- [ ] Anomaly detection for model prompts
- [ ] Cold storage sweep mechanism
- [ ] Multi-signature wallet support (requires 2/3 PQC)

### Phase 3 — Hardening (60 days)
- [ ] Post-quantum TLS for all API calls
- [ ] Regular key rotation (hybrid keys rotated every 7 days)
- [ ] Third-party quantum security audit
- [ ] Public quantum readiness report

---

## 5. Market Positioning

This is the differentiator. No other agentic treasury is building quantum-safe defaults because no one else is thinking about it yet.

**Go-to-market message:**

> *"Most agent wallets will be vulnerable within 18 months. GenTech's treasury is quantum-safe from day one. Hybrid signatures, fresh addresses, automatic quantum circuit breaker. Your agents survive what comes next."*

**Target buyers:**
- DAO treasuries managing >$1M
- Crypto funds running automated trading agents
- x402 gateway operators
- Projects building on BitVM3 / Bitcoin L2s

---

## 6. Open Questions

1. **SPHINCS+ vs CRYSTALS-Dilithium** — Which PQC scheme for hybrid signing? SPHINCS+ is stateless (no secret state to leak) but signatures are large (17KB). Dilithium is smaller but stateful. SPHINCS+ is safer for agentic use.
2. **Gas cost increase** — Hybrid signatures add ~17KB per transaction. On L2s this is affordable ($0.01–$0.05). On L1 Ethereum it's $5–$20. Acceptable for high-value transactions only.
3. **Model monitoring overhead** — Logging every prompt adds storage costs. Estimated ~100MB/month for an active treasury. Trivial.

---

## 7. References

- NIST Post-Quantum Cryptography Standards (2024): CRYSTALS-Dilithium, Falcon, SPHINCS+
- BIP-360: Pay to Quantum Resistant Hash (P2QRH)
- Bitcoin 2026 quantum threat landscape: 6.7M BTC vulnerable
- Vitalik Buterin: Quantum Emergency Roadmap
- CLARITY Act (H.R. 3633): Digital asset regulatory framework
