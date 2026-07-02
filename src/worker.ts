export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    
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
};
