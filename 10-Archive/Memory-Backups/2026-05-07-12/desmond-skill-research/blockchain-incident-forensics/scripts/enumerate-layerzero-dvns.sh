#!/bin/bash
# enumerate-layerzero-dvns.sh — Query LayerZero DVN configurations for OApps
# Usage: ./enumerate-layerzero-dvns.sh <chain_id> <oapp_address> [destination_eid]
# Example: ./enumerate-layerzero-dvns.sh 1 0x85d456b2dff1fd8245387c0bfb64dfb700e98ef3 30111

set -euo pipefail

CHAIN_ID="${1:-1}"
OAPP_ADDR="${2:-}"
DEST_EID="${3:-}"

# Mainnet EndpointV2 addresses (from dvnstats config.yaml)
declare -A ENDPOINT_ADDR=(
  [1]="0x1a44076050125825900e736c501f859c50fE728c"      # Ethereum
  [10]="0x1a44076050125825900e736c501f859c50fE728c"     # Optimism (same endpoint)
  [56]="0x1a44076050125825900e736c501f859c50fE728c"     # BSC (same)
  [130]="0x6F475642a6e85809B1c36Fa62763669b1b48DD5B"    # Unichain
  [137]="0x1a44076050125825900e736c501f859c50fE728c"     # Polygon
  [8453]="0x1a44076050125825900e736c501f859c50fE728c"   # Base
  [42161]="0x3c4962Ff6258dcfCafD23a814237B7d6Eb712063"  # Arbitrum
)

# ReceiveUln302 addresses
declare -A ULN_ADDR=(
  [1]="0xc02Ab410f0734EFa3F14628780e6e695156024C2"
  [42161]="0x3c4962Ff6258dcfCafD23a814237B7d6Eb712063"
)

ENDPOINT="${ENDPOINT_ADDR[$CHAIN_ID]:-}"
ULN="${ULN_ADDR[$CHAIN_ID]:-}"

if [ -z "$ENDPOINT" ]; then
  echo "Error: Unknown chain ID $CHAIN_ID"
  echo "Known chains: ${!ENDPOINT_ADDR[@]}"
  exit 1
fi

# RPC endpoint (use public RPC or env var)
RPC_URL="${RPC_URL:-https://eth.llamarpc.com}"

# Check dependencies
if ! command -v cast &> /dev/null; then
  echo "Error: 'cast' (foundry) not found. Install: https://book.getfoundry.sh/"
  exit 1
fi

echo "=== LayerZero DVN Configuration Query ==="
echo "Chain ID: $CHAIN_ID"
echo "Endpoint: $ENDPOINT"
echo "ReceiveUln: $ULN"
echo "OApp: $OAPP_ADDR"
[ -n "$DEST_EID" ] && echo "Destination EID: $DEST_EID"
echo ""

if [ -z "$OAPP_ADDR" ]; then
  echo "Usage: $0 <chain_id> <oapp_address> [destination_eid]"
  echo ""
  echo "Examples:"
  echo "  $0 1 0x85d456b2dff1fd8245387c0bfb64dfb700e98ef3 30111  # rsETH on ETH → Arbitrum"
  echo "  $0 42161 0x85d456b2dff1fd8245387c0bfb64dfb700e98ef3    # rsETH on Arbitrum (any route)"
  echo ""
  echo "Known vulnerable OApps (from dvnstats census):"
  echo "  ZAI OFT Adapter (MAHA): 0x1920E9BD4f2ee03c04f4F8955e585bA9e52Fe06e"
  echo "  rsETH OFT (KelpDAO): 0x85d456b2dff1fd8245387c0bfb64dfb700e98ef3"
  exit 1
fi

# Build cast query
# First, get OAppUlnConfig for (oapp, eid) — requires calling ReceiveUln302.config()
# This requires decoding the (uint64,uint8,uint8,uint8,address[],address[]) tuple
# For simplicity, we call getConfig() on EndpointV2 which returns the merged effective config

echo "Querying EndpointV2.getConfig()..."

if [ -n "$DEST_EID" ]; then
  # Single route query
  echo "Fetching config for OApp=$OAPP_ADDR, eid=$DEST_EID"
  
  cast call "$ENDPOINT" \
    "getConfig(address,uint32)(uint64,uint8,uint8,uint8,address[],address[])" \
    "$OAPP_ADDR" "$DEST_EID" \
    --rpc-url "$RPC_URL" 2>/dev/null || {
      echo "Error: Query failed. Ensure RPC is reachable and contracts are verified."
      exit 1
    }
else
  # List all routes for this OApp (need to iterate common eids)
  echo "Fetching all route configs for OApp $OAPP_ADDR"
  
  # Common destination EIDs (from dvnstats config.yaml)
  EIDS=(1 10 56 130 137 42161 8453)
  
  for EID in "${EIDS[@]}"; do
    echo ""
    echo "--- eid=$EID ---"
    cast call "$ENDPOINT" \
      "getConfig(address,uint32)(uint64,uint8,uint8,uint8,address[],address[])" \
      "$OAPP_ADDR" "$EID" \
      --rpc-url "$RPC_URL" 2>/dev/null || {
        echo "(no config set for this route)"
      }
  done
fi

echo ""
echo "=== Interpretation ==="
echo "Return tuple: (confirmations, requiredDVNCount, optionalDVNCount,"
echo "               optionalDVNThreshold, requiredDVNs[], optionalDVNs[])"
echo ""
echo "Red flags:"
echo "  • requiredDVNCount == 255 → zero required DVNs (max vulnerability)"
echo "  • requiredDVNCount == 1   → 1-of-1 (single point of failure)"
echo "  • requiredDVNCount < requiredDVNs.length → mismatch"
echo "  • confirmations < 30      → low block confirmation window"
echo ""
echo "Secure pattern:"
echo "  • requiredDVNCount >= 2"
echo "  • requiredDVNCount == requiredDVNs.length"
echo "  • requiredDVNs has 3+ unique addresses"
echo "  • confirmations >= 50"
echo ""
echo "For live census, see: https://observatory.indexing.co/layerzero-dvn-census"
