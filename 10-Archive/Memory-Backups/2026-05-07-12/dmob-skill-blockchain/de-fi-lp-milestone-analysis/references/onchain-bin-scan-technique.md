# On-Chain Bin Scan Technique for LFJ Positions

## Purpose

Determine the ACTUAL on-chain LP position range by querying `balanceOf` across a wide range of bins, bypassing any config files. This is the only way to get ground truth when configs may be stale.

## When to Use

- Config range values look wrong (price seems in-range but position is 100% USDC, or vice versa)
- After any rebalance that may not have been recorded in configs
- When `lp-position-reader.py` output seems inconsistent with market conditions
- Before updating config files — always verify first

## Constants

```python
POOL_ADDRESS = "0x864d4e5Ee7318e97483DB7EB0912E09F161516EA"  # LFJ AVAX/USDC 5bps
WALLET = "[REDACTED_WALLET]"        # Jordan's wallet
RPC = "https://api.avax.network/ext/bc/C/rpc"
SELECTOR = "0x00fdd58e"  # balanceOf(address,uint256) — NOT 0xc8f32345
BIN_STEP = 10  # 10bps per bin
```

## Core Script

```python
import math, json, requests

POOL_ADDRESS = "0x864d4e5Ee7318e97483DB7EB0912E09F161516EA"
WALLET = "[REDACTED_WALLET]"
RPC = "https://api.avax.network/ext/bc/C/rpc"
SELECTOR = "0x00fdd58e"  # balanceOf(address,uint256)

active_bin = 8363224  # Get from get_active_bin() or pool contract
price = 9.58          # Current AVAX price
bin_step = 10
log_step = math.log(1 + bin_step / 10000)

def bin_to_price(bin_id):
    return price * math.pow(1 + bin_step / 10000, bin_id - active_bin)

user_hex = WALLET[2:].lower().zfill(64)

def query_bin(bin_id):
    bin_hex = format(bin_id, "064x")
    data = SELECTOR + user_hex + bin_hex
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_call",
        "params": [{"to": POOL_ADDRESS, "data": data}, "latest"],
        "id": 1
    }
    r = requests.post(RPC, json=payload, timeout=10)
    result = r.json()
    if "result" in result and result["result"] != "0x":
        return int(result["result"], 16)
    return 0

# Query WIDE range (price 9.00 to 9.80) — do NOT use config range
bin_low = active_bin - int(round(math.log(price / 9.00) / log_step))
bin_high = active_bin + int(round(math.log(9.80 / price) / log_step))

bins_with_shares = []
for bin_id in range(bin_low, bin_high + 1):
    shares = query_bin(bin_id)
    if shares > 0:
        bp = bin_to_price(bin_id)
        side = "below" if bin_id < active_bin else ("above" if bin_id > active_bin else "active")
        bins_with_shares.append({"bin_id": bin_id, "shares": shares, "price": round(bp, 4), "side": side})

if bins_with_shares:
    first = bins_with_shares[0]
    last = bins_with_shares[-1]
    print(f"ACTUAL ON-CHAIN RANGE: ${first['price']} - ${last['price']}")
    print(f"Bins: {len(bins_with_shares)} ({len([b for b in bins_with_shares if b['side']=='below'])} below / {len([b for b in bins_with_shares if b['side']=='active'])} active / {len([b for b in bins_with_shares if b['side']=='above'])} above)")
```

## Pitfalls

- The selector is `0x00fdd58e`, NOT `0xc8f32345` (which is ERC-721 balanceOf). LFJ bins use a different contract interface.
- Query a WIDE range (at least +/- $0.50 from current price). If you only query the range from the config, and the config is wrong, you will miss bins where shares actually exist.
- Bin price calculation: `price * (1 + bin_step/10000)^(bin_id - active_bin)`. The active_bin price is the current market price.
- The active bin itself may or may not have shares depending on whether the position range includes it.
- RPC calls are sequential in this script. For faster execution, use batch JSON-RPC calls.

## Reading the Output

- If shares are concentrated BELOW the active bin: position is USDC-heavy, price is near/above top of range
- If shares are concentrated ABOVE the active bin: position is AVAX-heavy, price is near/below bottom of range
- If balanced (roughly equal below/above): position is centered in range
- The first and last bins with shares define the effective range boundaries
