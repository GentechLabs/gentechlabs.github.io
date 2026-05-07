# LFJ V2.2 Pool Contract Interface — Working Functions

**Pool**: `0x864d4e5Ee7318e97483DB7EB0912E09F161516ea` (Avalanche C-Chain)
**Verified**: 2026-05-05 via direct RPC calls

## Confirmed Working Functions

| Selector | Function | Returns | Notes |
|----------|----------|---------|-------|
| `0xdbe65edc` | `activeId()` | `uint256` (active bin ID) | Always works |
| `0x00fdd58e` | `balanceOf(address, uint256)` | `uint256` (user shares in bin) | Requires EIP-55 checksummed addresses |
| `0xbd85b039` | `totalSupply(uint256)` | `uint256` (total shares in bin) | |
| `0x05e8746d` | `tokenX()` | `address` (WAVAX) | `0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7` |
| `0xda10610c` | `tokenY()` | `address` (USDC) | `0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E` |

## Confirmed REVERTING Functions

These do NOT exist on this contract:

| Selector Tried | Function | Result |
|----------------|----------|--------|
| `0xfc7c59eb` | `getBin(uint256)` | `execution reverted` |
| `0x2dea2e97` | `getBinReserves(uint256)` | `execution reverted` |
| `0xa83f7e4b` | `bins(uint256)` | `execution reverted` |
| `0x4903b0d1` | `binLevel(uint256)` | `execution reverted` |
| `0x70a08231` | `balanceOf(address)` (ERC20-style) | `execution reverted` |
| `0xf8b2cb4f` | `getBalance(address)` | `execution reverted` |

## ABI Encoding for balanceOf(address, uint256)

```python
from web3 import Web3

selector = bytes.fromhex("00fdd58e")
wallet_padded = Web3.to_checksum_address(WALLET).lower().replace("0x", "").zfill(64)
bin_padded = hex(bin_id).replace("0x", "").zfill(64)
calldata = selector + bytes.fromhex(wallet_padded + bin_padded)

result = w3.eth.call({"to": pool_address, "data": calldata})
user_shares = int.from_bytes(result, 'big')
```

**Critical**: Addresses MUST be checksummed via `Web3.to_checksum_address()` before use.

## Position Value Estimation (No Bin Reserves Available)

Since bin reserves cannot be read directly, use this approximation:

1. **Pool TVL**: Read ERC20 balances of WAVAX and USDC at the pool contract
2. **User share ratio**: `total_user_shares / total_pool_shares` (sample pool shares across ±200 bins)
3. **Estimate**: `pool_tvl * user_share_ratio`

Cross-validate with Routescan `tokentx`:
- Sum recent USDC deposits from wallet → pool
- Dust rewards from pool → wallet confirm active position

## Pool Parameters

- **binStep**: 10
- **Fee tier**: 5 bps (0.05%)
- **Shape**: Curve
- **Token0**: WAVAX (18 decimals)
- **Token1**: USDC (6 decimals)
- **Per-bin price multiplier**: 1.0001^10 ≈ 1.001005

## Reference: Routescan Token Transfer API

```
GET https://api.routescan.io/v2/network/mainnet/evm/43114/etherscan/api
  ?module=account&action=tokentx&address={WALLET}&page=1&offset=20&sort=desc
```

Response fields: `tokenName`, `tokenSymbol`, `tokenDecimal`, `value`, `from`, `to`, `timeStamp`, `blockNumber`

Use to:
- Verify position activity (deposits to pool = active)
- Detect dust fee rewards (tiny IN transfers from pool)
- Cross-validate on-chain scan results
