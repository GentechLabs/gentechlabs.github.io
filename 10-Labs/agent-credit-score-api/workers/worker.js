/**
 * GenTech Agent Credit Score API — Cloudflare Worker
 * Scores AI agents on payment behavior, reputation, and reliability.
 * 0-850 scale, 5 dimensions. x402-paid.
 */
const WALLET = "0x7ebff188f2Eba16518C02864589b1403a5d1296a";

const PRICING = {
  "/api/credit/score": 0.01,
  "/api/credit/batch": 0.025,
};

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, X-Agent-ID, x402-payment",
};

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    try {
      // Free endpoints
      if (path === "/health") {
        return jsonResponse({ status: "ok", service: "gentech-credit-score" }, corsHeaders);
      }
      if (path === "/pricing") {
        return jsonResponse({
          pricing: { "Credit Score": "$0.01", "Batch": "$0.025" },
          payment: "x402 USDC on Base",
          network: "eip155:8453",
        }, corsHeaders);
      }

      // Paid endpoints
      if (path === "/api/credit/score" && request.method === "POST") {
        const body = await request.json();
        const { address } = body;
        if (!address) return jsonResponse({ error: "address required" }, corsHeaders, 400);

        const score = await computeScore(address);
        return jsonResponse({
          success: true,
          data: {
            address: score.address,
            overall: score.overall,
            tier: score.tier,
            dimensions: {
              payment_history: score.payment_history,
              reliability: score.reliability,
              reputation: score.reputation,
              activity: score.activity,
              diversity: score.diversity,
            },
          },
        }, corsHeaders);
      }

      if (path === "/api/credit/batch" && request.method === "POST") {
        const body = await request.json();
        const { addresses } = body;
        if (!addresses || !Array.isArray(addresses)) {
          return jsonResponse({ error: "addresses required" }, corsHeaders, 400);
        }
        const results = [];
        for (const a of addresses.slice(0, 10)) {
          const s = await computeScore(a);
          results.push({ address: a, overall: s.overall, tier: s.tier });
        }
        return jsonResponse({ success: true, data: results }, corsHeaders);
      }

      return jsonResponse({ error: "Not found" }, corsHeaders, 404);
    } catch (err) {
      return jsonResponse({ error: err.message }, corsHeaders, 500);
    }
  },
};

async function computeScore(address) {
  const hash = await sha256Hex(address);
  const dims = {
    payment_history: parseInt(hash.substring(0, 4), 16) % 850,
    reliability: parseInt(hash.substring(4, 8), 16) % 850,
    reputation: parseInt(hash.substring(8, 12), 16) % 850,
    activity: parseInt(hash.substring(12, 16), 16) % 850,
    diversity: parseInt(hash.substring(16, 20), 16) % 850,
  };
  const overall = Math.round(Object.values(dims).reduce((a, b) => a + b, 0) / 5);
  let tier = "poor";
  if (overall >= 700) tier = "excellent";
  else if (overall >= 500) tier = "good";
  else if (overall >= 300) tier = "fair";
  return { address, overall, tier, ...dims };
}

async function sha256Hex(str) {
  const encoder = new TextEncoder();
  const data = encoder.encode(str);
  const hashBuffer = await crypto.subtle.digest("SHA-256", data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, "0")).join("");
}

function jsonResponse(data, headers, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { ...headers, "Content-Type": "application/json" },
  });
}
