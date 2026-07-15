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
  '/.well-known/x402',
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
    const transferLog = receiptData.result.logs?.find((log: any) => {
      return log.topics?.[0]?.toLowerCase() === '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
        && log.address?.toLowerCase() === CONFIG.USDC_BASE.toLowerCase();
    });

    if (!transferLog) return { valid: false, error: 'No USDC Transfer event found in transaction logs' };

    const logTo = '0x' + transferLog.topics[2].slice(-40);
    if (logTo.toLowerCase() !== CONFIG.PAYMENT_ADDRESS.toLowerCase()) {
      return { valid: false, error: `Transfer recipient mismatch (got ${logTo})` };
    }

    const logAmount = Number(BigInt('0x' + transferLog.data.slice(0, 66))) / 1_000_000;

    if (logAmount < requiredAmount) {
      return { valid: false, error: `Insufficient payment: ${logAmount.toFixed(6)} USDC transferred, ${requiredAmount.toFixed(6)} required` };
    }

    // 10. Mark as used for idempotency
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
    docs_url: 'https://api.gentechlabs.net/openapi.json',
  });
}

/**
 * Endpoint metadata for OpenAPI spec generation.
 * Defines HTTP method, query parameters, and request body schemas with examples.
 */
interface EndpointMeta {
  method: 'get' | 'post';
  summary: string;
  description: string;
  queryParams?: { name: string; type: string; description: string; example?: string | number; required?: boolean }[];
  pathParams?: { name: string; type: string; description: string; example?: string }[];
  requestBody?: {
    required?: boolean;
    properties: { name: string; type: string; description: string; example: any; required?: boolean }[];
  };
}

const ENDPOINT_META: Record<string, EndpointMeta> = {
  '/v1/games/search': {
    method: 'get',
    summary: 'Search for game deals across stores',
    description: 'Search for the cheapest game deals across multiple stores. Returns title, sale price, normal price, store, and deal rating.',
    queryParams: [{ name: 'title', type: 'string', description: 'Game title to search for', example: 'Cyberpunk 2077', required: true }],
  },
  '/v1/games/cheapest': {
    method: 'get',
    summary: 'Get cheapest games on sale',
    description: 'List the cheapest game deals currently available. Filter by store, price range, or metacritic rating.',
    queryParams: [
      { name: 'store', type: 'string', description: 'Store filter (e.g. Steam, Epic, GOG)', example: 'Steam', required: false },
      { name: 'maxPrice', type: 'number', description: 'Maximum price in USD', example: 9.99, required: false },
    ],
  },
  '/v1/games/{id}/news': {
    method: 'get',
    summary: 'Get latest news for a game',
    description: 'Get the latest news articles, updates, and announcements for a specific game by its deal ID.',
    pathParams: [{ name: 'id', type: 'string', description: 'Game deal ID', example: 'MjE1NTE5' }],
  },
  '/v1/games/{id}/release': {
    method: 'get',
    summary: 'Get game release date info',
    description: 'Get release date, platforms, and availability information for a specific game.',
    pathParams: [{ name: 'id', type: 'string', description: 'Game deal ID', example: 'MjE1NTE5' }],
  },
  '/v1/movies/search': {
    method: 'get',
    summary: 'Search for movies and deals',
    description: 'Search for movies with available deals, including digital and physical copy pricing.',
    queryParams: [{ name: 'title', type: 'string', description: 'Movie title to search for', example: 'Dune: Part Two', required: true }],
  },
  '/v1/movies/cheapest': {
    method: 'get',
    summary: 'Get cheapest movies on sale',
    description: 'List the cheapest movie deals currently available across digital and physical retailers.',
    queryParams: [
      { name: 'genre', type: 'string', description: 'Movie genre filter', example: 'Sci-Fi', required: false },
      { name: 'maxPrice', type: 'number', description: 'Maximum price in USD', example: 14.99, required: false },
    ],
  },
  '/v1/movies/{id}/details': {
    method: 'get',
    summary: 'Get movie details',
    description: 'Get detailed information about a specific movie including synopsis, cast, runtime, and rating.',
    pathParams: [{ name: 'id', type: 'string', description: 'Movie deal ID', example: 'NzIwNjk=' }],
  },
  '/v1/movies/{id}/trailers': {
    method: 'get',
    summary: 'Get movie trailers',
    description: 'Get available trailers and video previews for a specific movie.',
    pathParams: [{ name: 'id', type: 'string', description: 'Movie deal ID', example: 'NzIwNjk=' }],
  },
  '/v1/intel/search': {
    method: 'get',
    summary: 'Market intelligence search',
    description: 'Search market intelligence data for trends, sentiment, and analysis across crypto and AI agent markets.',
    queryParams: [{ name: 'q', type: 'string', description: 'Search query for market intelligence', example: 'AI agent tokens', required: true }],
  },
  '/v1/intel/cheapest': {
    method: 'get',
    summary: 'Cheapest intelligence data',
    description: 'Get the cheapest available market intelligence data points and analysis snippets.',
    queryParams: [
      { name: 'category', type: 'string', description: 'Data category filter', example: 'defi', required: false },
      { name: 'limit', type: 'integer', description: 'Number of results to return', example: 10, required: false },
    ],
  },
  '/v1/airdrops/check': {
    method: 'post',
    summary: 'Check wallet for airdrop eligibility',
    description: 'Check if a wallet address is eligible for any tracked airdrops. Returns eligibility status, claimable amounts, and deadlines.',
    requestBody: {
      required: true,
      properties: [
        { name: 'address', type: 'string', description: 'Wallet address to check (EVM or Solana)', example: '0x7EBff1DbD34172C5b55697654006C9642b5236a3' },
        { name: 'chain', type: 'string', description: 'Blockchain to check (ethereum, solana, base)', example: 'base' },
      ],
    },
  },
  '/v1/wallet/analyze': {
    method: 'post',
    summary: 'Analyze a wallet portfolio',
    description: 'Analyze a wallet address for token holdings, portfolio value, risk score, and trading activity. Returns comprehensive analytics.',
    requestBody: {
      required: true,
      properties: [
        { name: 'address', type: 'string', description: 'Wallet address to analyze', example: '0x7EBff1DbD34172C5b55697654006C9642b5236a3' },
        { name: 'chain', type: 'string', description: 'Chain to analyze (ethereum, base, solana)', example: 'base' },
      ],
    },
  },
  '/v1/nft/search': {
    method: 'get',
    summary: 'Search NFTs by collection or trait',
    description: 'Search for NFTs across collections by name, collection address, or trait attributes. Returns floor prices and marketplace links.',
    queryParams: [
      { name: 'collection', type: 'string', description: 'Collection name or address', example: 'Bored Ape Yacht Club', required: true },
      { name: 'limit', type: 'integer', description: 'Max results to return', example: 20, required: false },
    ],
  },
  '/v1/score/{mint}': {
    method: 'get',
    summary: 'Get token security score',
    description: 'Get a detailed security risk score for a Solana token by its mint address. Analyzes liquidity, holders, mint authority, and known risk factors.',
    pathParams: [{ name: 'mint', type: 'string', description: 'Solana token mint address (base58)', example: 'So11111111111111111111111111111111111111112' }],
  },
  '/v1/agent/scan': {
    method: 'post',
    summary: 'Scan and evaluate AI agent',
    description: 'Scan and evaluate an AI agent by its wallet address or platform URL. Returns reputation score, transaction history, and risk assessment.',
    requestBody: {
      required: true,
      properties: [
        { name: 'address', type: 'string', description: 'Agent wallet address to scan', example: '0x742d35Cc6634C0532925a3b844Bc454e4438f44f' },
        { name: 'chain', type: 'string', description: 'Blockchain network', example: 'base' },
      ],
    },
  },
};

/**
 * Look up endpoint metadata by route pattern, with fuzzy fallback for path-variant routes.
 */
function getEndpointMeta(route: string): EndpointMeta {
  if (ENDPOINT_META[route]) return ENDPOINT_META[route];
  // Fallback: try to find a template-based match
  const base = route.split('/').slice(0, -1).join('/');
  for (const [pattern, meta] of Object.entries(ENDPOINT_META)) {
    const patternBase = pattern.split('/').slice(0, -1).join('/');
    if (base === patternBase && meta.pathParams) return meta;
  }
  // Ultimate fallback
  return {
    method: 'get',
    summary: `GenTech API - ${route.split('/').pop()}`,
    description: `x402 paid endpoint. Cost varies. Payment via X-Payment-Proof header.`,
  };
}

function handleOpenAPI(): Response {
  const paths: any = {};

  for (const [route, price] of Object.entries(PRICING)) {
    const meta = getEndpointMeta(route);
    const method = meta.method || 'get';

    // Build parameters array
    const parameters: any[] = [];

    // Add path parameters
    if (meta.pathParams) {
      for (const p of meta.pathParams) {
        parameters.push({
          name: p.name,
          in: 'path',
          required: true,
          schema: { type: p.type },
          description: p.description,
          example: p.example,
        });
      }
    }

    // Add query parameters
    if (meta.queryParams) {
      for (const p of meta.queryParams) {
        parameters.push({
          name: p.name,
          in: 'query',
          required: p.required || false,
          schema: { type: p.type },
          description: p.description,
          example: p.example,
        });
      }
    }

    // Build requestBody if applicable
    let requestBody: any = undefined;
    if (method === 'post' && meta.requestBody) {
      const properties: Record<string, any> = {};
      const required: string[] = [];
      for (const prop of meta.requestBody.properties) {
        properties[prop.name] = {
          type: prop.type,
          description: prop.description,
        };
        if (prop.required !== false) required.push(prop.name);
      }
      requestBody = {
        required: meta.requestBody.required ?? true,
        content: {
          'application/json': {
            schema: {
              type: 'object',
              ...(required.length > 0 ? { required } : {}),
              properties,
            },
            example: Object.fromEntries(
              meta.requestBody.properties.map(p => [p.name, p.example])
            ),
          },
        },
      };
    }

    // 402 response schema
    const paymentRequiredSchema = {
      type: 'object',
      properties: {
        status: { type: 'integer', example: 402 },
        title: { type: 'string', example: 'Payment Required' },
        detail: { type: 'string', example: `This endpoint costs $${price.toFixed(3)} USDC. Include a signed x402 payment in the X-Payment-Proof header.` },
        x402version: { type: 'string', example: 'x402-v2' },
        accepts: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              type: { type: 'string', example: 'x402' },
              scheme: { type: 'string', example: 'exact' },
              network: { type: 'string', example: 'eip155:8453' },
              amount: { type: 'string', example: String(price * 1_000_000) },
              asset: { type: 'string', example: '0x833589fcd6edb6e08f4c7c32d4f71b54bda02913' },
              payTo: { type: 'string', example: '0x7EBff1DbD34172C5b55697654006C9642b5236a3' },
              maxTimeoutSeconds: { type: 'integer', example: 60 },
            },
          },
        },
        instructions: {
          type: 'object',
          properties: {
            protocol: { type: 'string', example: 'x402' },
            header: { type: 'string', example: 'X-Payment-Proof' },
            encoding: { type: 'string', example: 'base64' },
            networks: { type: 'array', items: { type: 'string' }, example: ['base', 'solana', 'avalanche', 'bnb', 'okx'] },
            proofStructure: {
              type: 'object',
              properties: {
                signature: { type: 'string', example: '0xabc...' },
                sender: { type: 'string', example: '0xabc...' },
                timestamp: { type: 'integer', example: 1700000000 },
                amount: { type: 'string', example: '10000' },
                nonce: { type: 'string', example: 'uuid-or-random-string' },
              },
            },
          },
        },
      },
    };

    // Build operation entry
    const operation: any = {
      summary: meta.summary,
      description: `**x402 paid endpoint** — Cost: **$${price.toFixed(3)} USDC**. Send without X-Payment-Proof to receive 402 with payment instructions.`,
      parameters,
      responses: {
        '200': {
          description: 'Successful response — data returned after payment verification',
          content: {
            'application/json': {
              schema: { type: 'object' },
            },
          },
        },
        '402': {
          description: 'Payment required — includes x402 payment instructions and accepts[] array',
          content: {
            'application/json': {
              schema: paymentRequiredSchema,
            },
          },
        },
      },
    };

    if (requestBody) {
      operation.requestBody = requestBody;
    }

    // Security reference
    operation.security = [{ x402: [] }];

    paths[route] = { [method]: operation };
  }

  return jsonResponse({
    openapi: '3.0.0',
    info: {
      title: 'GenTech x402 Gateway',
      version: CONFIG.VERSION,
      description: '16 AI-powered API endpoints. Pay per call via x402 USDC on Base, Solana, Avalanche, BNB, or OKX. All paid endpoints require X-Payment-Proof header. Send without it to receive 402 + payment instructions.',
      'x-api-name': 'GenTech Labs x402 API',
      'x-payment-protocol': 'x402',
      'x-payment-token': 'USDC',
    },
    servers: [
      { url: 'https://api.gentechlabs.net', description: 'Production' },
    ],
    security: [{ x402: [] }],
    components: {
      securitySchemes: {
        x402: {
          type: 'apiKey',
          in: 'header',
          name: 'X-Payment-Proof',
          description: 'x402 payment proof (base64-encoded JSON with signature, sender, timestamp, amount, nonce). Obtain by sending USDC to 0x7EBff1DbD34172C5b55697654006C9642b5236a3 on Base.',
        },
      },
    },
    externalDocs: {
      description: 'x402 Protocol Specification',
      url: 'https://x402.org',
    },
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

// x402 v2 Discovery — /.well-known/x402
function handleX402Discovery(): Response {
  const resources: string[] = [];
  const resourceDetails: any[] = [];

  for (const [route, price] of Object.entries(PRICING)) {
    const name = `GenTech - ${route.split('/').pop() || 'endpoint'}`;
    resources.push(`https://api.gentechlabs.net${route}`);
    resourceDetails.push({
      url: `https://api.gentechlabs.net${route}`,
      name,
      description: `x402 paid endpoint. Cost: $${price.toFixed(3)} USDC. Payment via X-Payment-Proof header.`,
      price,
    });
  }

  return jsonResponse({
    version: 1,
    resources,
    resourceDetails,
    freeTier: {
      health: 'https://api.gentechlabs.net/health',
      pricing: 'https://api.gentechlabs.net/pricing',
      openapi: 'https://api.gentechlabs.net/openapi.json',
    },
    baseGateway: {
      enabled: true,
      network: 'eip155:8453',
      networkLabel: 'Base Mainnet',
      asset: CONFIG.USDC_BASE,
      assetLabel: 'USDC',
      payTo: CONFIG.PAYMENT_ADDRESS,
      gatewayUrl: 'https://api.gentechlabs.net',
      discoveryUrl: 'https://api.gentechlabs.net/.well-known/x402',
      openapiUrl: 'https://api.gentechlabs.net/openapi.json',
      facilitators: ['x402.org'],
    },
    instructions: `# GenTech Labs x402 Gateway\n\nPay-per-call API access via x402 protocol. USDC on Base, Solana, Avalanche, BNB, OKX.\n\n## Payment Flow\n1. Send request without payment → HTTP 402 with accepts[] and Payment-Required header.\n2. Sign USDC locally; retry with X-Payment-Proof header (base64 JSON).\n3. On success, backend response is returned.\n\n## Networks\n- Base (eip155:8453) — USDC\n- Solana (solana:mainnet) — USDC\n\n## Pricing\nTiers from $0.001 (micro) to $0.10 (ultra). See /pricing for full breakdown.`,
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
    if (path === '/.well-known/x402') return handleX402Discovery();

    // ── Paid Endpoints ──
    const price = getPrice(path);
    if (price > 0) {
      // Check for payment proof header
      const proofHeader = request.headers.get('X-Payment-Proof');
      const tokenHeader = request.headers.get('X-Payment-Token');

      if (!proofHeader && !tokenHeader) {
        // Return 402 with x402 v2 payment requirements
        const feeWei = Math.floor(price * 1_000_000).toString();
        
        const accepts = [{
          scheme: 'exact',
          network: 'eip155:8453',
          amount: feeWei,
          asset: CONFIG.USDC_BASE.toLowerCase(),
          payTo: CONFIG.PAYMENT_ADDRESS,
          maxTimeoutSeconds: 60,
        }];

        const paymentRequired = btoa(JSON.stringify({
          x402Version: 2,
          error: 'Payment required',
          resource: {
            url: `https://api.gentechlabs.net${path}`,
            description: `x402 paid endpoint. Cost: $${price.toFixed(3)} USDC. Payment via X-Payment-Proof header.`,
            mimeType: 'application/json',
            serviceName: 'GenTech Labs',
            tags: ['x402', 'api'],
          },
          accepts,
        }));

        return jsonResponse({
          status: 402,
          title: 'Payment Required',
          detail: `This endpoint costs $${price.toFixed(3)} USDC. Include a signed x402 payment in the X-Payment-Proof header.`,
          x402version: 'x402-v2',
          accepts: accepts.map(a => ({ type: 'x402', ...a })),
          network: 'eip155:8453',
          asset: CONFIG.USDC_BASE,
          amount: feeWei,
          payment_address: CONFIG.PAYMENT_ADDRESS,
          instructions: {
            protocol: 'x402',
            header: 'X-Payment-Proof',
            encoding: 'base64',
            networks: CONFIG.NETWORKS,
            timestampWindow: CONFIG.TIMESTAMP_WINDOW,
            proofStructure: {
              signature: 'Transaction hash (0x...)',
              sender: 'Payer address (0x...)',
              timestamp: 'Unix timestamp in seconds',
              amount: 'USDC amount as string',
              nonce: 'Unique nonce for replay protection',
            },
          },
        }, 402, { 'Payment-Required': paymentRequired });
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
};
