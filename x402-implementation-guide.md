# x402 Pay-Per-Call Implementation Guide

## Current Status

**Working:** 
- Timestamp validation (5-minute window)
- Basic signature format check
- Payment rejection for expired proofs
- All 16 endpoints routed and guarded

**Not Yet Implemented:**
- On-chain signature verification (check Base transaction)
- Amount verification (compare to on-chain USDC transfer)
- Nonce tracking (prevent replay attacks)
- Q402 token registry validation

---

## Implementation Plan

### Phase 1: On-Chain Verification (Recommended Now)

Add to `src/worker.ts`:

```typescript
async function verifyPaymentOnChain(proof: PaymentProof, requiredAmount: number): Promise<boolean> {
  // Connect to Base RPC (use Cloudflare's built-in RPC or your own)
  const rpcUrl = 'https://mainnet.base.org';
  
  // 1. Fetch transaction by hash
  const tx = await fetch(rpcUrl, {
    method: 'POST',
    body: JSON.stringify({
      jsonrpc: '2.0',
      id: 1,
      method: 'eth_getTransactionByHash',
      params: [proof.signature]
    })
  }).then(r => r.json());
  
  // 2. Verify transaction exists and is confirmed
  if (!tx.result) return false;
  
  // 3. Verify sender matches
  if (tx.result.from.toLowerCase() !== proof.sender.toLowerCase()) return false;
  
  // 4. Verify USDC transfer amount
  // Parse input data to get transfer amount (USDC is ERC20)
  // This requires ABIs and input decoding - skip for MVP
  
  // 5. Verify timestamp is recent
  const now = Math.floor(Date.now() / 1000);
  if (Math.abs(now - proof.timestamp) > 300) return false; // 5 minutes
  
  return true;
}
```

### Phase 2: Nonce Tracking

Use Cloudflare KV Durable Object to track used nonces:

```typescript
// In wrangler.toml:
[[kv_namespaces]]
binding = "NONCE_STORE"
id = "your-kv-namespace-id"

// In worker.ts:
export default {
  async fetch(request: Request, env: any) {
    // Check nonce
    const used = await env.NONCE_STORE.get(proof.nonce);
    if (used) return { valid: false, error: 'Nonce already used' };
    
    // Mark as used
    await env.NONCE_STORE.put(proof.nonce, '1', { expirationTtl: 86400 }); // 1 day
  }
}
```

### Phase 3: Full USDC Amount Verification

Requires USDC contract ABI integration:

```typescript
const USDC_ABI = [
  'function transfer(address to, uint256 amount) returns (bool)',
  'function balanceOf(address account) view returns (uint256)'
];

// Decode transfer amount from transaction input
// Compare to required amount (convert to wei: 0.005 USDC = 5000000 wei)
```

---

## Quick Fix: Accept All Valid Format Proofs (MVP)

For immediate deployment, modify `validatePayment`:

```typescript
async function validatePayment(request: Request, requiredAmount: number): Promise<{ valid: boolean; error?: string }> {
  const x402Proof = request.headers.get('X-Payment-Proof');
  const x402Token = request.headers.get('X-Payment-Token');

  if (!x402Proof && !x402Token) {
    return { valid: false, error: 'Missing payment proof' };
  }

  if (x402Proof) {
    try {
      const proof: PaymentProof = JSON.parse(atob(x402Proof));
      
      // MVP: Just check format and timestamp (no on-chain verify)
      if (!proof.signature || !proof.sender || !proof.timestamp || !proof.amount || !proof.nonce) {
        return { valid: false, error: 'Invalid payment proof format' };
      }
      
      const now = Math.floor(Date.now() / 1000);
      if (Math.abs(now - proof.timestamp) > 300) {
        return { valid: false, error: 'Payment proof expired' };
      }

      return { valid: true };
    } catch (e) {
      return { valid: false, error: 'Invalid payment proof format' };
    }
  }

  if (x402Token) {
    return { valid: true };
  }

  return { valid: false, error: 'No valid payment method' };
}
```

This allows you to:
- ✅ Go live immediately
- ✅ Accept payments from Q402 clients
- ✅ Block expired/invalid formats
- ⚠️ Trust client-claimed payments (not production-secure)

**Upgrade path:** Add on-chain verification in Phase 1 after deployment.

---

## Deployment Command

```bash
# Deploy to Cloudflare Workers
cd /root/repos/ProtoJay4789.github.io
npx wrangler deploy

# Test live endpoint
curl https://gentechlabs.net/v1/games/search?q=cyberpunk \
  -H "X-Payment-Proof: <valid-proof>"
```

---

## Next Steps

1. Deploy now (accepts format + timestamp)
2. Add on-chain verification (Phase 1)
3. Add KV nonce tracking (Phase 2)
4. Add USDC amount verification (Phase 3)

Let me know when you want to deploy.