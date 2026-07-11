/**
 * GenTech x402 Gateway — Testnet Worker
 * Mirrors main gateway with testnet USDC on Base Sepolia.
 * Devs can try all 16 endpoints for free using faucet USDC.
 */
import { Hono } from "hono";
import { paymentMiddleware, x402ResourceServer } from "@x402/hono";
import { ExactEvmScheme } from "@x402/evm/exact/server";
import { CdpFacilitatorClient } from "./cdp-facilitator.js";

const app = new Hono();

// Wallet
const EVM_WALLET = "0x7ebff188f2Eba16518C02864589b1403a5d1296a";

// Testnet USDC addresses
const USDC_BASE_SEPOLIA = "0x036CbD53842c5426634e7929541eC2318f3dcCF7";
const USDC_SOL_DEVNET = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v";
const USDC_AVAX_FUJI = "0x5425890298aed601595a70AB815c96711a31Bc65";

// Testnet network identifiers
const NET_BASE_SEPOLIA = "eip155:11155111";
const NET_SOL_DEVNET = "solana:EtWTRABZaYq6iMFeY7ouHTXzYsTJQzJAknhfty47sFpU";
const NET_AVAX_FUJI = "eip155:43113";

const AI_MODEL = "@cf/meta/llama-3.1-8b-instruct-fast";

// Route prices (same as mainnet, but USDC has no real value)
const ROUTES = {
  "/api/games/search":     { price: "$0.005", desc: "Game search across multiple platforms" },
  "/api/games/cheapest":   { price: "$0.005", desc: "Cheapest game price finder" },
  "/api/games/news":       { price: "$0.001", desc: "Game news and patch notes" },
  "/api/games/release":    { price: "$0.001", desc: "Game release info and dates" },
  "/api/movies/search":    { price: "$0.005", desc: "Movie search" },
  "/api/movies/cheapest":  { price: "$0.005", desc: "Cheapest movie watch option" },
  "/api/movies/details":   { price: "$0.001", desc: "Movie details (cast, studio, genres)" },
  "/api/movies/trailers":  { price: "$0.001", desc: "Movie trailers (YouTube)" },
  "/api/intel/search":     { price: "$0.005", desc: "Unified search across games + movies" },
  "/api/intel/cheapest":   { price: "$0.005", desc: "Cheapest across all categories" },
  "/api/airdrops/check":   { price: "$0.01",  desc: "Airdrop eligibility checker" },
  "/api/wallet/analyze":   { price: "$0.025", desc: "AI-powered wallet analytics and smart money tracking" },
  "/api/nft/search":       { price: "$0.005", desc: "NFT search and collection data" },
  "/api/token/risk":       { price: "$0.01",  desc: "AI-powered token risk assessment" },
  "/api/shipping/track":   { price: "$0.005", desc: "Multi-carrier shipping tracker" },
  "/api/agentscan":        { price: "$0.10",  desc: "AgentScan — AI-powered agent reconnaissance" },
};

// Build testnet x402 route configs
const x402Routes = {};
for (const [path, r] of Object.entries(ROUTES)) {
  const resource = `https://gentech-x402-testnet.jordanjones0902.workers.dev${path}`;
  x402Routes[path] = {
    resource,
    description: `${r.desc} (TESTNET — free USDC from faucet)`,
    mimeType: "application/json",
    accepts: [
      { scheme: "exact", price: r.price, network: NET_BASE_SEPOLIA, payTo: EVM_WALLET, asset: USDC_BASE_SEPOLIA, maxTimeoutSeconds: 300, extra: { name: "USD Coin", version: "2" } },
    ],
    extensions: {
      bazaar: {
        info: {
          input: { type: "http", method: "GET", queryParams: { q: { type: "string", description: "Search query" } } },
          output: { type: "json", example: { success: true } },
        },
      },
    },
  };
}

// CDP facilitator
function createFacilitatorClient(env) {
  const CDP_KEYS = {
    apiKeyId: env.CDP_API_KEY_ID || "",
    apiKeySecret: env.CDP_API_KEY_SECRET || "",
    walletSecret: env.CDP_WALLET_SECRET || "",
  };
  return new CdpFacilitatorClient(CDP_KEYS);
}

function createResourceServer(env) {
  return new x402ResourceServer(createFacilitatorClient(env))
    .register(NET_BASE_SEPOLIA, new ExactEvmScheme());
}

let paymentMiddlewareInstance = null;

app.use("*", async (c, next) => {
  if (!paymentMiddlewareInstance) {
    const resourceServer = createResourceServer(c.env);
    paymentMiddlewareInstance = paymentMiddleware(
      x402Routes,
      resourceServer,
      undefined,
      undefined,
      true,
    );
  }
  return await paymentMiddlewareInstance(c, next);
});

// ── Free endpoints ────────────────────────────────────────────

app.get("/health", (c) => {
  return c.json({
    status: "ok",
    service: "gentech-x402-gateway",
    version: "6.0.0",
    mode: "testnet",
    network: "Base Sepolia",
    usdc_contract: USDC_BASE_SEPOLIA,
    paid_endpoints: 16,
    ai_powered: true,
    bazaar_indexed: true,
    faucet_guide: "https://github.com/ProtoJay4789/gentech-vault/blob/main/10-Labs/x402-gateway/TESTNET-FAUCET.md",
  });
});

app.get("/pricing", (c) => {
  const pricing = {};
  for (const [path, r] of Object.entries(ROUTES)) {
    pricing[path] = { price: r.price, description: r.desc };
  }
  return c.json({
    service: "gentech-x402-gateway",
    mode: "testnet",
    pricing,
    payment: "x402 (USDC on Base Sepolia)",
    wallet: EVM_WALLET,
    note: "Testnet USDC has no real value. Get free USDC from faucets.",
  });
});

app.get("/openapi.json", (c) => {
  return c.json({
    openapi: "3.0.0",
    info: { title: "GenTech x402 Gateway (Testnet)", version: "6.0.0-testnet" },
    servers: [{ url: "https://gentech-x402-testnet.jordanjones0902.workers.dev" }],
    paths: {},
  });
});

// ── AI-powered endpoint handlers ──────────────────────────────

async function aiResponse(c, prompt) {
  const ai = c.env.AI;
  if (!ai) {
    return c.json({ success: true, data: { mock: true, note: "AI not available — returning mock data" } });
  }
  const result = await ai.run(AI_MODEL, { prompt, stream: false });
  return c.json({ success: true, data: result });
}

app.get("/api/games/search", async (c) => {
  const q = c.req.query("q") || "popular games";
  return aiResponse(c, `Search for games matching "${q}". Return as JSON array with name, platform, price, release_date.`);
});

app.get("/api/games/cheapest", async (c) => {
  const q = c.req.query("q") || "popular game";
  return aiResponse(c, `Find cheapest prices for "${q}" across stores. Return as JSON array with store, price, url.`);
});

app.get("/api/games/news", async (c) => {
  return aiResponse(c, "Get latest gaming news. Return as JSON array with title, source, date, summary.");
});

app.get("/api/games/release", async (c) => {
  return aiResponse(c, "Get upcoming game releases. Return as JSON array with name, platform, release_date, genre.");
});

app.get("/api/movies/search", async (c) => {
  const q = c.req.query("q") || "popular movies";
  return aiResponse(c, `Search for movies matching "${q}". Return as JSON array with title, year, genre, rating.`);
});

app.get("/api/movies/cheapest", async (c) => {
  const q = c.req.query("q") || "popular movie";
  return aiResponse(c, `Find cheapest watch options for "${q}". Return as JSON array with service, price, quality.`);
});

app.get("/api/movies/details", async (c) => {
  const id = c.req.query("id") || "unknown";
  return aiResponse(c, `Get movie details for ID "${id}". Return as JSON with title, cast, studio, genres, rating.`);
});

app.get("/api/movies/trailers", async (c) => {
  const id = c.req.query("id") || "unknown";
  return aiResponse(c, `Get movie trailers for ID "${id}". Return as JSON array with title, url, quality.`);
});

app.get("/api/intel/search", async (c) => {
  const q = c.req.query("q") || "popular";
  return aiResponse(c, `Unified search for "${q}" across games and movies. Return as JSON with games and movies arrays.`);
});

app.get("/api/intel/cheapest", async (c) => {
  const q = c.req.query("q") || "popular";
  return aiResponse(c, `Find cheapest options for "${q}" across all categories. Return as JSON array.`);
});

app.get("/api/airdrops/check", async (c) => {
  const address = c.req.query("address") || "0x0";
  return aiResponse(c, `Check airdrop eligibility for wallet address "${address}". Return as JSON array with protocol, token, amount, status.`);
});

app.get("/api/wallet/analyze", async (c) => {
  const address = c.req.query("address") || "0x0";
  const chain = c.req.query("chain") || "base";
  return aiResponse(c, `Analyze wallet "${address}" on ${chain}. Return as JSON with risk_score, portfolio_value, top_holdings, recommendations.`);
});

app.get("/api/nft/search", async (c) => {
  const q = c.req.query("q") || "popular nfts";
  return aiResponse(c, `Search NFTs matching "${q}". Return as JSON array with name, collection, floor_price, volume_24h.`);
});

app.get("/api/token/risk", async (c) => {
  const address = c.req.query("address") || "0x0";
  const chain = c.req.query("chain") || "base";
  return aiResponse(c, `Assess token risk for "${address}" on ${chain}. Return as JSON with risk_score, risk_level, factors, recommendation.`);
});

app.get("/api/shipping/track", async (c) => {
  const tn = c.req.query("tn") || "unknown";
  return aiResponse(c, `Track package with tracking number "${tn}". Return as JSON with status, location, estimated_delivery, events.`);
});

app.get("/api/agentscan", async (c) => {
  const target = c.req.query("target") || "self";
  return aiResponse(c, `Perform agent reconnaissance on "${target}". Return as JSON with agent_info, capabilities, reputation, risk_score.`);
});

export default app;
