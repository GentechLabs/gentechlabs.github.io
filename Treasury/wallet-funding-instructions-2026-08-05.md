# Wallet Funding Instructions — Aug 5 (verified)

**Purpose:** Exact addresses, chains, and amounts for Jordan to fund the priority wallets from the grant.

---

## 🔴 1. CDP Server Account — Agentic Treasury live test (THE unlock)
- **Chain:** Base (mainnet, chain ID 8453)
- **Address:** `0x77C622D02A1518fC0FDcd83B8C28010FA5ebB7dE` ✅ VERIFIED (via CDP SDK `list_accounts`, matches brain `0x77C6…`)
- **Send:**
  - **~$25 USDC** (Base USDC — contract `0x833589fCD6eDb6E08f4c7C32D4f71b54bDA02913`)
  - **~$1 ETH** for gas (native Base ETH)
- **Unlocks:** First real x402 settlement → **Agentic.Market auto-indexes** ($52M+ TPV) + OpenDexter catalog. The "people use our rails" proof.
- **Note:** This account already holds 10.5 USDC + 0.0003 ETH (from Aug 4). Adding ~$25 USDC + ~$1 ETH tops it up for the live test.

---

## 🔴 2. KeeperHub Execution Wallet — hackathon live-tx (Aug 13 deadline)
- **Chain:** Base (mainnet, chain ID 8453)
- **Address:** `0x53A8DFA431D03A36499f9DB70AAFbb00C28308EA` ✅ (from brain, Aug 4)
- **Send:**
  - **~$15 ETH** (native Base ETH, for gas)
  - **~$10 USDC** (Base USDC)
- **Unlocks:** Live-tx link for KeeperHub judging (deadline Aug 13). Currently 0 ETH / 0 USDC.

---

## 🔴 3. Algorand Wallet — x402 Challenge mainnet payment
- **Chain:** Algorand (mainnet)
- **Address:** `6IXPRMSYQBZSP2KIPH6BQ7MP4XN7VP6MWGHCLLF52K5R4IYCPA74TU2MTI` ✅ (generated Aug 5, keys at /root/.algorand/)
- **Send:**
  - **~$5 ALGO** (native, for gas + opt-in fee)
  - **~$3 USDC** (ASA 31566704, 6 decimals)
- **IMPORTANT:** The address must **OPT-IN** to USDC ASA 31566704 before it can receive USDC. If sending USDC, ensure opt-in is done first (or send ALGO first, then I opt-in, then send USDC).
- **Unlocks:** Algorand x402 Challenge mainnet payment settlement.

---

## 🟡 4. Solana Keypair — Solana Homebase on-chain proof
- **Chain:** Solana (mainnet)
- **Address:** `BE815V7ojVz63PDxFFSEQyGSe5PZE2fAdKUU6Rd5pUvP` ✅ (jordan-personal wallet, /root/.gentech/wallets/)
- **Send:**
  - **~$2 SOL** (gas for Jupiter swaps)
  - **~$20 USDC** (Solana USDC)
- **Unlocks:** Solana Homebase on-chain proof (tranche-2 + Colosseum + Arc).

---

## Allocation summary (from ~$109 grant)
| Destination | Amount | Running |
|---|---|---|
| CDP Agentic Treasury | $26 | $26 |
| KeeperHub | $25 | $51 |
| Algorand | $8 | $59 |
| Solana keypair | $22 | $81 |
| Reserve (subs + buffer) | ~$28 | $109 |

**Priority order:** CDP ($26) first — it's the settlement unlock.
