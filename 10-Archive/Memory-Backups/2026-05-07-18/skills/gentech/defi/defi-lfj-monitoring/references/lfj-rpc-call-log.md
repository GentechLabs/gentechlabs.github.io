# LFJ RPC Call Log — 2026-05-02 Session

**Pool**: `0x864d4e5ee7318e97483db7eb0912e09f161516ea`  
**RPC Endpoint**: `https://api.avax.network/ext/bc/C/rpc`  
**Session Goal**: Fetch on-chain position data when external APIs unavailable

---

## Call 1: Connectivity Test

**Method**: `eth_blockNumber`  
**Payload**: `{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}`  
**Response**: `{"jsonrpc":"2.0","id":1,"result":"0x50a7c1e"}` → block 84433754  
**Status**: ✅ Connected

---

## Call 2: `activeId()` — Get Current Active Bin

**Selector**: `0xdbe65edc` (no 0x prefix in calldata)  
**Raw Call**: `{"to":"0x864d4e5ee7318e97483db7eb0912e09f161516ea","data":"0xdbe65edc"}`  
**Response**: `0x00000000000000000000000000000000000000000000000000000000007f9cab`  
**Parsed**: `int("7f9cab", 16)` = 8363179  
**Interpretation**: Current active trading bin is 8363179

---

## Call 3: `balanceOf(wallet, binId)` — Scan User Positions

**Selector**: `0x00fdd58e`  
**Call pattern**: `selector + address[32] + binId[32]` (all big-endian, left-padded zeros)

**Example** (bin 8363157):
```
data: 0x00fdd58e
      [address as 32-byte hex] → [REDACTED_WALLET]
      [binId as 32-byte hex]  → 0x000000000000000000000000000000000000000000000000000000000031a405
```
**Response (bin 8363157)**: `0x0000022f9720978c21a55e2b0000000` (truncated in transcript) → parsed to `149886948901471345170371` shares  
**Interpretation**: Position active across bins 8363157–8363202 (46 bins total)

---

## Call 4: `totalSupply(binId)` — Pool Share Total Per Bin

**Selector**: `0xbd85b039`  
**Call pattern**: `selector + binId[32]`

**Example** (bin 8363157):
```
data: 0xbd85b039
      [binId] → 0x000000000000000000000000000000000000000000000000000000000031a405
```
**Response**: `0x000000000000000000000746402734798824939220212528` → `746402734798824939220212528` total shares  
**Share %**: `149886948901471345170371 / 746402734798824939220212528 × 100 ≈ 0.0201%`

**Aggregate across all 46 bins**:
```
User total shares: 41,514,769,358,024,808,643,213,648
Pool total shares (scanned bins only): 275,285,433,606,788,311,234,559,988,533
Weighted avg share_pct: ~0.0151%
```

---

## Call 5: `getReserves()` — Pool Reserves (Attempted)

**Selector**: `0x0902f1ac`  
**Expected return**: `(uint112 reserve0, uint112 reserve1, uint32 activeId)` → encoded as 3× uint256 (96 bytes)

**Response**: `0x0000000000000000000000000000000000000000000053751077ddd4235e5996000000000000000000000000000000000000000000000000000000438c93d82e`  
**Parse issue**: Response 128 hex chars (64 bytes) — truncated or different ABI than expected. Abandoned in favor of vault-reported token balances.

---

## Call 6: `tokenX()` / `tokenY()` — Token Addresses

**Selectors**: `0x05e8746d` (tokenX), `0xda10610c` (tokenY)  
**Results**:
```
tokenX: 0xb31f66aa3c1e785363f0875a1b74e27b85fd66c7  (WAVAX)
tokenY: 0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e  (USDC)
```
**Status**: ✅ Confirmed

---

## Call 7: `binStep` — Pool Configuration

**Selector**: `0x37e69d4a`  
**Response**: None (call reverted or empty)  
**Known from vault config**: `binStep = 10`  
**Base price multiplier**: `1.0001 ** 10 ≈ 1.00100500670001` per bin

---

## External API Failures (Volume → Fee Estimation)

All volume endpoints returned no usable data:
- **DexScreener** `/latest/dex/pairs/avalanche/{pool}` → `volumeUsd.h24: None`
- **GeckoTerminal** `/api/v2/networks/avalanche/pools/{pool}` → 404
- **DefiLlama** `/pools/cross_pool` → 404 or 403
- **Lifinity API** `api.lifinity.fi/v1/pools/{pool}` → DNS resolution failure

**Fallback adopted**: Report `unavailable` with explanatory note; defer fee estimation until on-chain oracle configured or volume returns.

---

## Price Range Derivation (From Bin IDs)

Given:
- `active_bin = 8363179`
- `position_bins = [8363161, 8363202]` (min, max)
- `current_price = $9.16` (from DexScreener)
- `per_bin_multiplier = 1.0001 ** 10 ≈ 1.0010050067`

Compute:
```
min_offset = min_bin - active_bin = -18
max_offset = max_bin - active_bin = +23

min_price = 9.16 × (per_bin_multiplier ** -18) ≈ $8.9966
max_price = 9.16 × (per_bin_multiplier ** 23)  ≈ $9.3731
```
Rounded to vault precision: **$9.00–$9.37**

---

## Lessons for Future Sessions

1. **Always call `activeId()` first** — anchors all bin-based price math
2. **Never exponentiate large bin IDs directly** — Python `float` overflows at ~1e308; bin ~8.3M is enormous. Use **relative offsets** from active bin (offsets ~±50 safe)
3. **Scan ±50 bins around active** — captures full position with minimal calls
4. **Cache `totalSupply` results** — re-use across multiple bins with same total when scanning contiguous range
5. **Sequential calls preferred for >30 bins** — Avalanche public RPC returns HTTP 500 on batch requests >~30 items. For ±50 bin scans (101 calls), sequential is reliable (~20s). Batch only when <15 calls.
6. **If volume APIs fail 3 times in a row**, hardcode fallback: `fees_24h = "unavailable — external APIs unreachable"` rather than guessing
7. **Vault append must be atomic + de-dup** — double-run creates duplicate headers; use regex split + merge before write

---

## Call Template (Copy-Paste)

```python
import requests

RPC = 'https://api.avax.network/ext/bc/C/rpc'
POOL = '0x864d4e5ee7318e97483db7eb0912e09f161516ea'
WALLET = '[REDACTED_WALLET]'

def rpc_call(data, block='latest'):
    payload = {"jsonrpc":"2.0","id":1,"method":"eth_call",
               "params":[{"to":POOL,"data":data},block]}
    r = requests.post(RPC, json=payload, timeout=15).json()
    if 'error' in r: raise Exception(r['error'])
    return r['result']

# 1. activeId
active_hex = rpc_call('0xdbe65edc')
active_id = int(active_hex, 16)

# 2. Scan bins
wallet_int = int(WALLET, 16)
positions = {}
for offset in range(-50, 51):
    bin_id = active_id + offset
    data = '0x00fdd58e' + wallet_int.to_bytes(32,'big').hex() + bin_id.to_bytes(32,'big').hex()
    shares_hex = rpc_call(data)
    shares = int(shares_hex, 16)
    if shares > 0:
        positions[bin_id] = shares

# 3. Get totalSupply for each occupied bin
totals = {}
for bin_id in positions:
    data = '0xbd85b039' + bin_id.to_bytes(32,'big').hex()
    total_hex = rpc_call(data)
    totals[bin_id] = int(total_hex, 16)

# 4. Aggregate share_pct = sum(user) / sum(total) across bins
total_user = sum(positions.values())
total_pool = sum(totals.values())
share_pct = total_user / total_pool * 100
```