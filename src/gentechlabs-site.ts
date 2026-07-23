/**
 * GenTech Labs — Site Proxy Worker v2
 * 
 * Proxies all gentechlabs.net/* traffic to the VPS via internal routing.
 */

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});

async function handleRequest(request) {
  const url = new URL(request.url);
  
  // Proxy to VPS via its IP
  const backendUrl = `http://2.24.195.196:80${url.pathname}${url.search}`;
  
  const proxyReq = new Request(backendUrl, {
    method: request.method,
    headers: {
      ...Object.fromEntries(request.headers),
      'Host': 'gentechlabs.net',
      'X-Forwarded-Proto': 'https',
      'X-Real-IP': request.headers.get('CF-Connecting-IP') || '',
    },
    body: request.body,
  });

  try {
    const response = await fetch(proxyReq);
    const headers = new Headers(response.headers);
    headers.set('Access-Control-Allow-Origin', '*');
    headers.set('Cache-Control', 'public, max-age=300');
    return new Response(response.body, {
      status: response.status,
      headers,
    });
  } catch (err) {
    return new Response(`Backend temporarily unavailable`, { 
      status: 502,
      headers: { 'Content-Type': 'text/plain' },
    });
  }
}
