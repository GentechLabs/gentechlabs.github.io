# Bug report — `coinbase/cdp-sdk` (Python SDK v1.47.1)

## Issue 1: `swap()` returns `executed: true` even when the on-chain tx reverts

**Severity:** High — misleads callers into believing a trade succeeded when it reverted.

### Summary
`EvmServerAccount.swap()` (via `send_swap_transaction`) returns an `AccountSwapResult` with `transaction_hash` and the executor treats it as success, but the SDK **never checks the transaction receipt**. A swap that reverts on-chain returns the same `executed: true` + hash as one that succeeds. The only reliable signal is reading the receipt yourself and checking `status == 0x1`.

### Repro (Base mainnet)
1. Fund a CDP EVM server account with USDC (native token), but **do not** grant the Permit2 contract (`0x000000000022D473030F116dDEE9F6B43aC78BA3`) any allowance for that USDC.
2. Call `account.swap(AccountSwapOptions(network="base", from_token=USDC, to_token=cbBTC, from_amount="5000000", ...))`.
3. The call returns `executed: true` with a `transaction_hash`.
4. `w3.eth.get_transaction_receipt(hash)["status"]` → `0` (reverted), revert reason `TRANSFER_FROM_FAILED`.
5. Token balances are unchanged — the "successful" swap moved nothing.

### Expected
The SDK should either:
- **Reject the swap before submission** by checking the wallet's USDC → Permit2 allowance (return a clear "allowance required" error), OR
- **Expose a confirmed/settled status** field that reflects the receipt (`status == 0x1`), so callers don't mistake broadcast for settlement.

### Why this bites real users
Automated agent treasuries (which are exactly what CDP Server Wallets target) act on `executed: true`. A silent revert makes the agent believe it opened a position it didn't — a serious accounting/custody failure mode.

### Context
- SDK: `cdp-sdk` 1.47.1 (Python)
- Network: Base mainnet
- Swap path used: `EvmServerAccount.swap()` → `send_swap_transaction()` with inline `InlineSendSwapTransactionOptions`

---

## Issue 2 (minor, CLI): `--dry-run` cannot be disabled from the CLI

`gta_coinbase_leg.py` (our executor wrapper) exposes `--dry-run` with `default=True`, but there is no `--no-dry-run` flag. Running with any flag to disable it errors:
```
gta_coinbase_leg.py: error: unrecognized arguments: --no-dry-run
```
Real execution therefore requires calling `run_spot_leg(dry_run=False)` programmatically — it is impossible to execute a real swap from the command line as the CLI is written.

---

## Note (for the maintainers)
Not a bug in the SDK, just confirming the right contract: the wallet secret is a **DER PKCS#8 EC P-256 (secp256r1)** key (`base64.b64decode` → `load_der_private_key`, decodes to ~138 bytes starting `MIGH…`), *not* the 88-char Ed25519 format used by `CDP_API_KEY_SECRET`. It may be worth documenting this distinction in the auth docs, since a copied Ed25519 API-secret value stores cleanly but fails wallet auth.
