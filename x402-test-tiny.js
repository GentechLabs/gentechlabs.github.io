export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (url.pathname === '/hello') {
      return new Response(JSON.stringify({ x402Version: 2, status: 'payment_required', accepts: [{ scheme: "exact", network: "eip155:84532", amount: "1000", asset: "0x833589fCD6eDb6E08f4c7C32D4f71b54bDA02913", payTo: "0x7EBff1DbD34172C5b55697654006C9642b5236a3", maxTimeoutSeconds: 300 }] }), {
        status: 402,
        headers: { 'Content-Type': 'application/json' },
      });
    }
    return new Response('test harness', { headers: { 'Content-Type': 'text/plain' } });
  },
};
