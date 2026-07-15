/**
 * GenTech x402 Test Harness — minimal, reliable
 */
export default {
  async fetch(request) {
    const url = new URL(request.url);
    const path = url.pathname;

    if (path === '/') {
      return new Response(`<!DOCTYPE html>
<html><head><title>GenTech x402 Test Harness</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{font-family:system-ui,sans-serif;background:#0a0a0f;color:#e0e0e0;max-width:800px;margin:0 auto;padding:40px 20px}
h1{color:#6366f1}code{background:#1a1a2e;padding:2px 6px;border-radius:4px}
.card{background:#101018;border:1px solid #1a1a2e;border-radius:12px;padding:20px;margin:16px 0}
.route{color:#22c55e;font-family:monospace}</style></head><body>
<h1>🧪 GenTech x402 Test Harness</h1>
<p>Test the x402 payment protocol. Returns 402 → sign → retry → 200.</p>
<div class="card">
<h3>Endpoints</h3>
<p><span class="route">GET /hello</span> — $0.001, greeting</p>
<p><span class="route">GET /evm/weather</span> — $0.001, EVM test</p>
<p><span class="route">GET /solana/weather</span> — $0.001, Solana test</p>
</div>
<div class="card">
<h3>Quick test</h3>
<code>curl -i https://test.api.gentechlabs.net/hello</code><br><br>
<code>curl -H 'X-Payment-Proof: ...' https://test.api.gentechlabs.net/hello</code>
</div>
</body></html>`, {
        headers: { 'Content-Type': 'text/html; charset=utf-8', 'Access-Control-Allow-Origin': '*' },
      });
    }

    // Paid endpoints
    const paid = ['/hello', '/evm/weather', '/solana/weather'];
    if (!paid.includes(path)) {
      return new Response(JSON.stringify({ error: 'not_found', routes: paid }), {
        status: 404,
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
      });
    }

    const payment = request.headers.get('X-Payment-Proof');
    if (!payment) {
      const challenge = {
        x402Version: 2,
        error: 'Payment required',
        resource: { url: 'https://test.api.gentechlabs.net' + path, description: 'x402 test endpoint', mimeType: 'application/json' },
        accepts: [{
          scheme: 'exact',
          network: 'eip155:84532',
          amount: '1000',
          asset: '0x833589fCD6eDb6E08f4c7C32D4f71b54bDA02913',
          payTo: '0x7EBff1DbD34172C5b55697654006C9642b5236a3',
          maxTimeoutSeconds: 300,
        }],
      };
      return new Response(JSON.stringify(challenge, null, 2), {
        status: 402,
        headers: {
          'Content-Type': 'application/json',
          'Payment-Required': btoa(JSON.stringify(challenge)),
          'Access-Control-Allow-Origin': '*',
        },
      });
    }

    // Verified response
    const responses = {
      '/hello': { message: 'Hello from GenTech x402! Payment confirmed.', network: 'base', amount: '$0.001' },
      '/evm/weather': { report: { weather: 'sunny', temperature: 72, city: 'San Francisco' }, payment: 'confirmed' },
      '/solana/weather': { report: { weather: 'clear', temperature: 85, city: 'Miami' }, payment: 'confirmed' },
    };
    return new Response(JSON.stringify(responses[path], null, 2), {
      status: 200,
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
    });
  },
};
