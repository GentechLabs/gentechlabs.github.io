# Handoff to Treasury — $33 in `0xF9dc...734` needs a spend path (Aug 22, 2026)

**From:** Gentech (HQ) → **To:** Treasury agent
**Priority:** High — Jordan wants this money moved to his Coinbase (same way yesterday's $43 moved).

## The money (verified on-chain)
Wallet `0xF9dcBFF7EdDd76c58412fd46f4160c96312ce734` (~**$33.63** total):
- BSC: ~$12.47 BNB + ~$4.95 USD1 (World Liberty)
- Celo: ~$8.07 USDC + ~$0.43 CELO
- Base: ~$3.88 USDC + ~$1.50 ETH
- Arbitrum: ~$2.31 ETH

## The rail it came from
This is the **x402 `payTo` settlement address** configured across our gateway manifests (receive-only). Your own logs already state it: *"treasury X402_PAYTO... is receive-only, no signing key"* and *"there's no signing key behind the treasury address."*

## The blocker
Jordan has the private key for the wallet **he** created (`0x7ebff...96a`, the signer — key on disk, verified). But `0xF9dc...734` is a different address — a receive-only `payTo` settlement point. Neither HQ nor CDP has a key for it (CDP `get_account` → 404, not CDP-managed). Jordan only holds keys for wallets he personally made.

## Your investigation (Treasury owns this)
1. **Where did `0xF9dc...734` originate?** Trace the session/script that first configured it as `payTo`. Was it ever a signing key, or always a plain receive address?
2. **Was a key EVER generated for it?** Check your profile's session history, `.blockrun/`, `.hermes/profiles/gentech-treasury/secure/`, and git history around when the x402 gateway payTo was set.
3. **If no key exists:** the money is stuck unless Jordan can (a) recover/export the key from whatever tool made it, or (b) re-point the payTo to a wallet he controls AND sweep. Give Jordan the exact recovery path.
4. **If a key DOES exist:** hand it back to Gentech (HQ) with the location and I'll sweep all ~$33 to Coinbase like yesterday's $43.

## Hard rule going forward (Jordan, Aug 22)
Whenever we create a wallet/rail, **auto-generate AND store the private keys automatically** — Jordan has no control over that. Never leave a funded wallet keyless. This wallet is exactly the failure case that rule prevents.

## Reporting
Reply with findings + the payTo's origin. If you recover a key, drop it in a `secure/` file (chmod 600) and tell me the path — do NOT paste it in group chat.
