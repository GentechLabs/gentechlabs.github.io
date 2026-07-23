/**
 * GenTech Labs — VPS Reverse Proxy Worker
 * 
 * Proxies all gentechlabs.net traffic to the VPS.
 * VPS serves the actual content (hub, portfolio, investor deck, APIs).
 * This Worker just handles SSL termination and caching at the edge.
 */

// VPS backend
const VPS_IP = '2.24.195.196';
const VPS_PORT = '80';

// API subdomain routes that go to specific backend ports on the VPS
const API_ROUTES = {
  'deals': { host: 'deals.gentechlabs.net', port: 8080 },
  'prices': { host: 'prices.gentechlabs.net', port: 8082 },
  'gas': { host: 'gas.gentechlabs.net', port: 8084 },
  'rugcheck': { host: 'rugcheck.gentechlabs.net', port: 8088 },
};

// CORS headers for API responses
const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Payment-Proof, X-Payment-Token',
  'Access-Control-Max-Age': '86400',
};

function htmlResponse(body, status = 200) {
  return new Response(body, {
    status,
    headers: {
      'Content-Type': 'text/html; charset=utf-8',
      'Access-Control-Allow-Origin': '*',
    },
  });
}

function jsonResponse(body, status = 200) {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
    },
  });
}

async function proxyToVPS(request, targetHost, targetPort) {
  const url = new URL(request.url);
  const targetUrl = `http://${VPS_IP}:${targetPort}${url.pathname}${url.search}`;
  
  const proxyReq = new Request(targetUrl, {
    method: request.method,
    headers: request.headers,
    body: request.body,
  });
  proxyReq.headers.set('Host', targetHost);
  proxyReq.headers.set('X-Forwarded-Proto', 'https');
  proxyReq.headers.set('X-Forwarded-For', request.headers.get('CF-Connecting-IP') || '');

  try {
    const response = await fetch(proxyReq);
    const newResp = new Response(response.body, response);
    newResp.headers.set('Access-Control-Allow-Origin', '*');
    return newResp;
  } catch (err) {
    return jsonResponse({ error: 'backend_unreachable', message: 'Backend temporarily unavailable' }, 502);
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const host = request.headers.get('Host') || '';
    const path = url.pathname;

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: CORS_HEADERS });
    }

    // ── API subdomain routing ──
    for (const [subdomain, config] of Object.entries(API_ROUTES)) {
      if (host.startsWith(subdomain + '.') || path.startsWith('/api/' + subdomain)) {
        return proxyToVPS(request, config.host, config.port);
      }
    }

    // ── Health check ──
    if (path === '/health') {
      return jsonResponse({
        status: 'ok',
        service: 'gentechlabs-vps-proxy',
        vps: VPS_IP,
        timestamp: new Date().toISOString(),
      });
    }

    // ── Everything else: proxy to VPS ──
    // This includes: /, /portfolio/, /investor-deck.html, /hub.html, etc.
    return proxyToVPS(request, 'gentechlabs.net', 80);
  },
};
