<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
/**
 * GenTech x402 Gateway — v7.0.0
 * 
 * Cloudflare Worker that serves as the payment gateway for GenTech Labs APIs.
 * 
 * Flow:
 * 1. Agent hits a paid endpoint → returns 402 with payment requirements
 * 2. Agent includes X-Payment-Proof header → verifies on-chain
 * 3. On success → proxies to VPS backend service
 * 4. On failure → returns 402 again with error details
 * 
 * Architecture:
 * - Metadata routes handled directly (/health, /pricing, /openapi.json, /.well-known/)
 * - Paid routes require x402 payment, then proxy to VPS per service
 * - VPS hosts backend services on ports 8080-8091
 */

// ── Configuration ───────────────────────────────────────────────────────────
const CONFIG = {
  // Wallet
  PAYMENT_ADDRESS: '0x7EBff1DbD34172C5b55697654006C9642b5236a3',
  SOLANA_WALLET: '71Y3H36eb2WRGseYM9GwinjNawfMfAUbcof5eeWGoGSA',
  
  // USDC contracts
  USDC_BASE: '0x833589fCD6eDb6E08f4c7C32D4f71b54bDA02913',
  USDC_SOLANA: 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
  
  // Networks
  NETWORKS: ['base', 'solana', 'avalanche', 'bnb', 'okx'],
  
  // RPC endpoints for verification
  RPC_URLS: {
    base: 'https://mainnet.base.org',
    solana: 'https://api.mainnet-beta.solana.com',
  },
  
  // Timestamp tolerance (5 minutes)
  TIMESTAMP_WINDOW: 300,
  
  // VPS backend
  VPS_IP: '2.24.195.196',
  VPS_PORT: '80',
  
  // Backend service ports on VPS
  BACKEND_PORTS: {
    deals: 8080,
    prices: 8082,
    gas: 8084,
    security: 8086,
    rugcheck: 8088,
    defi: 8090,
    search: 8091,
  },
  
  // Version
  VERSION: '7.0.0',
};

// ── Pricing ─────────────────────────────────────────────────────────────────
const PRICING: Record<string, number> = {
  // Games
  '/v1/games/search': 0.005,
  '/v1/games/cheapest': 0.005,
  '/v1/games/{id}/news': 0.001,
  '/v1/games/{id}/release': 0.001,
  // Movies
  '/v1/movies/search': 0.005,
  '/v1/movies/cheapest': 0.005,
  '/v1/movies/{id}/details': 0.001,
  '/v1/movies/{id}/trailers': 0.001,
  // Market intelligence
  '/v1/intel/search': 0.005,
  '/v1/intel/cheapest': 0.005,
  // Airdrops
  '/v1/airdrops/check': 0.01,
  // Wallet analysis
  '/v1/wallet/analyze': 0.025,
  // NFT
  '/v1/nft/search': 0.005,
  // Token security
  '/v1/score/{mint}': 0.01,
  // Agent scan
  '/v1/agent/scan': 0.10,
};

// Pricing tier labels
const TIERS = {
  micro: { max: 0.001, label: '$0.001 — news, details, trailers' },
  standard: { max: 0.005, label: '$0.005 — search, cheapest, NFT, shipping' },
  premium: { max: 0.01, label: '$0.01 — airdrops, AI token risk' },
  pro: { max: 0.025, label: '$0.025 — AI wallet analytics' },
  ultra: { max: 0.10, label: '$0.10 — AI agent scan' },
};

// Free endpoints
const FREE_ROUTES = [
  '/health',
  '/pricing',
  '/openapi.json',
  '/.well-known/agent.json',
  '/.well-known/agent-card.json',
];

// ── Helpers ─────────────────────────────────────────────────────────────────

function getPrice(path: string): number {
  for (const [pattern, price] of Object.entries(PRICING)) {
    const regex = new RegExp('^' + pattern.replace(/\{id\}/g, '[^/]+').replace(/\{mint\}/g, '[^/]+') + '$');
    if (regex.test(path)) return price;
  }
  return 0;
}

function getTier(price: number): string {
  for (const [tier, config] of Object.entries(TIERS)) {
    if (price <= config.max) return tier;
  }
  return 'ultra';
}

function jsonResponse(body: any, status = 200, headers: Record<string, string> = {}): Response {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Payment-Proof, X-Payment-Token',
      ...headers,
    },
  });
}

// ── Payment Verification ────────────────────────────────────────────────────

async function verifyPayment(proof: any, requiredAmount: number, env: any): Promise<{ valid: boolean; error?: string; tx?: any }> {
  try {
    // 1. Validate proof format
    if (!proof.signature || !proof.sender || !proof.timestamp || !proof.amount || !proof.nonce) {
      return { valid: false, error: 'Missing required fields (signature, sender, timestamp, amount, nonce)' };
    }

    // 2. Check timestamp window
    const now = Math.floor(Date.now() / 1000);
    if (Math.abs(now - proof.timestamp) > CONFIG.TIMESTAMP_WINDOW) {
      return { valid: false, error: `Payment proof expired (must be within ${CONFIG.TIMESTAMP_WINDOW / 60} minutes)` };
    }

    // 3. Check idempotency — if this tx hash was already verified, return cached result
    if (env?.NONCE_STORE) {
      const cached = await env.NONCE_STORE.get('tx:' + proof.signature);
      if (cached) {
        const cachedResult = JSON.parse(cached);
        if (cachedResult.amount >= requiredAmount) {
          return { valid: true, tx: cachedResult };
        }
      }
    }

    // 4. Verify on Base mainnet via RPC — fetch tx first
    const txResponse = await fetch(CONFIG.RPC_URLS.base, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0', id: 1,
        method: 'eth_getTransactionByHash',
        params: [proof.signature],
      }),
    });
    const txData: any = await txResponse.json();
    if (!txData.result) return { valid: false, error: 'Transaction not found on Base blockchain' };

    const tx = txData.result;

    // 5. Verify chainId is Base mainnet (8453 = 0x2105)
    if (tx.chainId !== '0x2105') {
      return { valid: false, error: `Wrong chain: expected Base mainnet (chainId 8453), got ${parseInt(tx.chainId || '0x0', 16)}` };
    }

    // 6. Verify it's a USDC transfer to the correct contract
    if (tx.to?.toLowerCase() !== CONFIG.USDC_BASE.toLowerCase()) {
      return { valid: false, error: 'Transaction not to USDC contract on Base' };
    }

    // 7. Verify sender matches — tx.from is recovered by the node from the signature
    if (tx.from?.toLowerCase() !== proof.sender.toLowerCase()) {
      return { valid: false, error: 'Sender mismatch' };
    }

    // 8. Fetch receipt to confirm success
    const receiptResponse = await fetch(CONFIG.RPC_URLS.base, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0', id: 2,
        method: 'eth_getTransactionReceipt',
        params: [proof.signature],
      }),
    });
    const receiptData: any = await receiptResponse.json();
    if (!receiptData.result) return { valid: false, error: 'Transaction receipt not found (transaction may be pending)' };
    if (!receiptData.result.blockHash) return { valid: false, error: 'Transaction not yet mined (no blockHash)' };
    if (receiptData.result.status !== '0x1') return { valid: false, error: 'Transaction failed on-chain (receipt status != success)' };

    // 9. Parse Transfer event logs from receipt for amount + recipient
    // This is more secure than decoding tx.input — logs are emitted by the canonical USDC contract
    const transferLog = receiptData.result.logs?.find((log: any) => {
      // Transfer event: Transfer(address indexed from, address indexed to, uint256 value)
      // topic0 = keccak256("Transfer(address,address,uint256)")
      return log.topics?.[0]?.toLowerCase() === '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
        && log.address?.toLowerCase() === CONFIG.USDC_BASE.toLowerCase();
    });

    if (!transferLog) return { valid: false, error: 'No USDC Transfer event found in transaction logs' };

    // Extract `to` from topics[2] (indexed parameter, 32 bytes, right-padded address)
    const logTo = '0x' + transferLog.topics[2].slice(-40);
    if (logTo.toLowerCase() !== CONFIG.PAYMENT_ADDRESS.toLowerCase()) {
      return { valid: false, error: `Transfer recipient mismatch (got ${logTo})` };
    }

    // Extract value from log data (uint256, 32 bytes)
    const logAmount = Number(BigInt('0x' + transferLog.data.slice(0, 66))) / 1_000_000;

    if (logAmount < requiredAmount) {
      return { valid: false, error: `Insufficient payment: ${logAmount.toFixed(6)} USDC transferred, ${requiredAmount.toFixed(6)} required` };
    }

    // 10. Mark as used for idempotency + replay protection (if KV available)
    if (env?.NONCE_STORE) {
      const result = { tx: proof.signature, from: tx.from, amount: logAmount, verified: now };
      await env.NONCE_STORE.put('tx:' + proof.signature, JSON.stringify(result), { expirationTtl: 86400 });
      await env.NONCE_STORE.put(proof.nonce, proof.signature, { expirationTtl: 86400 });
    }

    return { valid: true, tx: { hash: proof.signature, from: tx.from, amount: logAmount } };
  } catch (err: any) {
    return { valid: false, error: 'Verification error: ' + err.message };
  }
}

// ── Route Handlers ──────────────────────────────────────────────────────────

function handleHealth(): Response {
  return jsonResponse({
    status: 'ok',
    service: 'gentech-x402-gateway',
    version: CONFIG.VERSION,
    networks: CONFIG.NETWORKS,
    token: 'USDC',
    multichain: true,
    wallets: {
      base: CONFIG.PAYMENT_ADDRESS.slice(0, 12) + '...',
      solana: CONFIG.SOLANA_WALLET.slice(0, 12) + '...',
    },
    paid_endpoints: Object.keys(PRICING).length,
    free_endpoints: FREE_ROUTES,
    facilitator: 'x402.org',
    timestamp: new Date().toISOString(),
  });
}

function handlePricing(): Response {
  return jsonResponse({
    service: 'GenTech Labs x402 Gateway (AI-Powered, Multichain)',
    version: CONFIG.VERSION,
    networks: CONFIG.NETWORKS.map(n => n === 'base' ? 'Base mainnet' : n === 'solana' ? 'Solana mainnet' : n.charAt(0).toUpperCase() + n.slice(1)),
    token: 'USDC',
    multichain: true,
    tiers: Object.fromEntries(Object.entries(TIERS).map(([k, v]) => [k, v.label])),
    total_endpoints: Object.keys(PRICING).length,
    payment_address: CONFIG.PAYMENT_ADDRESS,
    solana_address: CONFIG.SOLANA_WALLET,
    usdc_base: CONFIG.USDC_BASE,
    facilitator: 'x402.org',
    payment_protocol: 'x402',
    docs_url: 'https://gentech-x402-gateway.jordanjones0902.workers.dev/openapi.json',
  });
}

function handleOpenAPI(): Response {
  // Simplified OpenAPI spec for discovery
  const paths: any = {};
  for (const [route, price] of Object.entries(PRICING)) {
    paths[route] = {
      get: {
        summary: `GenTech API - ${route.split('/').pop()}`,
        description: `x402 paid endpoint. Cost: $${price.toFixed(3)} USDC. Payment via X-Payment-Proof header.`,
        parameters: [
          { name: 'X-Payment-Proof', in: 'header', required: true, schema: { type: 'string' }, description: 'Base64-encoded x402 payment proof' },
        ],
        responses: {
          '200': { description: 'Successful response' },
          '402': { description: 'Payment required' },
        },
      },
    };
  }

  return jsonResponse({
    openapi: '3.0.0',
    info: {
      title: 'GenTech x402 Gateway',
      version: CONFIG.VERSION,
      description: '16 AI-powered API endpoints. Pay per call via x402 USDC on Base, Solana, Avalanche, BNB, or OKX.',
    },
    servers: [{ url: 'https://api.gentechlabs.net' }],
    paths,
  });
}

function handleAgentCard(): Response {
  return jsonResponse({
    name: 'GenTech x402 Gateway',
    description: '16 AI-powered API endpoints. Multichain: pay per call via x402 USDC on Base, Solana, Avalanche, BNB, or OKX.',
    version: CONFIG.VERSION,
    url: 'https://gentech-x402-gateway.jordanjones0902.workers.dev',
    provider: { organization: 'GenTech Labs', url: 'https://gentechlabs.net' },
    documentationUrl: 'https://gentech-x402-gateway.jordanjones0902.workers.dev/openapi.json',
    capabilities: { streaming: false, pushNotifications: false, stateTransitionHistory: false },
    payment: {
      protocol: 'x402',
      networks: CONFIG.NETWORKS,
      token: 'USDC',
      facilitator: 'x402.org',
      paymentAddress: CONFIG.PAYMENT_ADDRESS,
    },
  });
}

// ── VPS Proxy ───────────────────────────────────────────────────────────────

async function proxyToVPS(path: string, request: Request): Promise<Response> {
  const url = new URL(`http://${CONFIG.VPS_IP}:${CONFIG.VPS_PORT}${path}`);
  const proxyRequest = new Request(url, request);
  proxyRequest.headers.set('Host', 'api.gentechlabs.net');
  proxyRequest.headers.set('X-Forwarded-Proto', 'https');
  proxyRequest.headers.set('X-Forwarded-For', request.headers.get('CF-Connecting-IP') || '');

  try {
    const response = await fetch(proxyRequest);
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Payment-Proof, X-Payment-Token',
    };
    const newResponse = new Response(response.body, response);
    Object.entries(corsHeaders).forEach(([k, v]) => newResponse.headers.set(k, v));
    return newResponse;
  } catch {
    return jsonResponse({ error: 'backend_unreachable', message: 'API backend temporarily unavailable' }, 502);
  }
}

// ── Main Request Handler ────────────────────────────────────────────────────

export default {
  async fetch(request: Request, env: any): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname;
    const method = request.method;

    // Handle CORS preflight
    if (method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Payment-Proof, X-Payment-Token',
          'Access-Control-Max-Age': '86400',
        },
      });
    }

    // ── Metadata Routes (always free) ──
    if (path === '/health') return handleHealth();
    if (path === '/pricing') return handlePricing();
    if (path === '/openapi.json') return handleOpenAPI();
    if (path === '/.well-known/agent.json' || path === '/.well-known/agent-card.json') return handleAgentCard();

    // ── Paid Endpoints ──
    const price = getPrice(path);
    if (price > 0) {
      // Check for payment proof header
      const proofHeader = request.headers.get('X-Payment-Proof');
      const tokenHeader = request.headers.get('X-Payment-Token');

      if (!proofHeader && !tokenHeader) {
        // Return 402 with payment requirements
        return jsonResponse({
          status: 402,
          title: 'Payment Required',
          detail: `This endpoint costs $${price.toFixed(3)} USDC. Include an x402 payment proof in the X-Payment-Proof header.`,
          payment: {
            protocol: 'x402',
            amount: price,
            currency: 'USDC',
            networks: CONFIG.NETWORKS,
            paymentAddress: CONFIG.PAYMENT_ADDRESS,
            usdcContract: CONFIG.USDC_BASE,
            rpcUrl: CONFIG.RPC_URLS.base,
            timestampWindow: CONFIG.TIMESTAMP_WINDOW,
            header: 'X-Payment-Proof',
            encoding: 'base64',
            proofStructure: {
              signature: 'Transaction hash (0x...)',
              sender: 'Payer address (0x...)',
              timestamp: 'Unix timestamp in seconds',
              amount: 'USDC amount as string',
              nonce: 'Unique nonce for replay protection',
            },
          },
        }, 402);
      }

      // Verify payment
      let proof: any;
      try {
        proof = JSON.parse(atob(proofHeader || ''));
      } catch {
        return jsonResponse({ status: 402, error: 'Invalid payment proof encoding (must be base64 JSON)' }, 402);
      }

      const result = await verifyPayment(proof, price, env);
      if (!result.valid) {
        return jsonResponse({
          status: 402,
          error: 'Payment verification failed',
          detail: result.error,
        }, 402);
      }

      // Payment verified — proxy to VPS backend
      const backendPath = path.replace('/v1', '/v1');
      return await proxyToVPS(backendPath, request);
    }

    // ── No matching route ──
    return jsonResponse({ error: 'not_found', message: `Endpoint not found: ${path}. Visit GET /health for available endpoints.` }, 404);
  },
=======
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
=======
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
>>>>>>> Stashed changes
=======
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
>>>>>>> Stashed changes
=======
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
>>>>>>> Stashed changes
=======
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
>>>>>>> Stashed changes
=======
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
>>>>>>> Stashed changes
=======
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
>>>>>>> Stashed changes
=======
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
>>>>>>> Stashed changes
=======
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
>>>>>>> Stashed changes
=======
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
>>>>>>> Stashed changes
=======
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
>>>>>>> Stashed changes
=======
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
>>>>>>> Stashed changes
=======
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
>>>>>>> Stashed changes
=======
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
>>>>>>> Stashed changes
=======
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
>>>>>>> Stashed changes
=======
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
>>>>>>> Stashed changes
=======
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
>>>>>>> Stashed changes
=======
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
>>>>>>> Stashed changes
=======
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
>>>>>>> Stashed changes
=======
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
>>>>>>> Stashed changes
=======
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
>>>>>>> Stashed changes
=======
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
>>>>>>> Stashed changes
=======
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
>>>>>>> Stashed changes
=======
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
>>>>>>> Stashed changes
    
    // Get VPS configuration from environment variables
    const vpsIP = env.VPS_IP || '2.24.195.196';
    const vpsPort = env.VPS_PORT || '80';
    
    // Route deals.gentechlabs.net and api.gentechlabs.net to VPS API server
    if (url.hostname === 'deals.gentechlabs.net' || 
        url.hostname === 'api.gentechlabs.net' ||
        url.hostname === 'gentechlabs.net' && (url.pathname.startsWith('/api') || url.pathname.startsWith('/v1'))) {
      
      const originUrl = new URL(request.url);
      originUrl.hostname = vpsIP;
      originUrl.port = vpsPort;
      
      // Forward request to VPS
      const originRequest = new Request(originUrl, request);
      
      try {
        const response = await fetch(originRequest);
        // Add CORS headers
        const corsHeaders = {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        };
        
        const newResponse = new Response(response.body, response);
        Object.entries(corsHeaders).forEach(([key, value]) => {
          newResponse.headers.set(key, value);
        });
        
        return newResponse;
      } catch (error) {
        return new Response('Origin unreachable', { status: 502 });
      }
    }
    
    // Default: pass through to existing backend
    return fetch(request);
  }
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
};
