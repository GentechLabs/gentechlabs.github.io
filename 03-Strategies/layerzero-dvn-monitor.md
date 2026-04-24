     1|# LayerZero DVN Security Monitor
     2|
     3|## 2026-04-23
     4|- **Key Findings**: 
     5|    - LayerZero Labs published a detailed "KelpDAO Incident Statement" (April 19, 2026) regarding a ~$290M exploit.
     6|    - The attack was an RPC-spoofing and DDoS attack likely by Lazarus Group (TraderTraitor), targeting the LayerZero Labs DVN's downstream RPC infrastructure.
     7|    - The vulnerability was realized only because KelpDAO used a **1-of-1 DVN configuration** (LayerZero Labs as sole verifier), contradicting the protocol's recommended multi-DVN redundancy model.
     8|    - LayerZero Labs has deprecated affected RPC nodes, replaced them, and is now actively reaching out to all 1/1 configurations to migrate to multi-DVN setups.
     9|    - No protocol-level "mandatory" DVN changes were announced, but the "Integrations Checklist" is being heavily emphasized as the standard.
    10|- **Risk Level**: Unchanged (The protocol itself remains modular; the risk is shifted to application-level configuration).
    11|- **Action Items**: 
    12|    - Verify all Gentech-linked integrations are NOT using 1/1 DVN configurations.
    13|    - Audit DVN diversity (ensure no single provider is a systemic dependency).
    14|    - Monitor for any formal "security standard" mandates that might emerge from the community or Labs.
    15|

# LayerZero DVN Security Monitor Report - 2026-04-24

**Date Checked:** 2026-04-24
**Risk Level:** Unchanged (High for 1/1 configs, Low for multi-DVN)

## Key Findings
- **Incident Status:** The KelpDAO exploit ($290M) was confirmed to be an RPC-spoofing attack targeting the LayerZero Labs DVN, likely by Lazarus Group (TraderTraitor).
- **Root Cause:** Attackers poisoned downstream RPC infrastructure and used DDoS to force failover to malicious nodes.
- **Protocol Response:** LayerZero Labs has deprecated the affected RPC nodes and resumed DVN operations. They maintain that the protocol itself was not exploited, but rather the infrastructure upon which the DVN relied.
- **Security Standards:** LayerZero is actively urging all applications with 1/1 DVN configurations to migrate to multi-DVN setups. They reiterate that no single DVN should be a unilateral point of trust.
- **Contagion:** LayerZero claims zero contagion to other assets/applications, as the exploit specifically targeted KelpDAO's rsETH 1/1 configuration.
- **Industry Context:** This highlights a fundamental risk in off-chain RPC verification shared by many bridges and services.

## Action Items
- [ ] Monitor LayerZero's official channels for any mandatory DVN configuration updates or new minimum security standards.
- [ ] Verify if any Gentech-related integrations are using 1/1 DVN setups; if so, migrate to multi-DVN immediately.
- [ ] Track any competitive responses from Wormhole/Axelar regarding their own RPC dependency risks.
