// Types
interface Game {
  gameID: string;
  external: string;
  cheapest: string;
  stores?: string;
}

interface GameDeal {
  price: string;
  storeID: string;
  savings: string;
  dealID: string;
}

interface GameDeals {
  deals?: GameDeal[];
}

interface OMDBResponse {
  Response: string;
  Error?: string;
  Search?: Movie[];
  imdbID?: string;
  Title?: string;
  Year?: string;
  Runtime?: string;
  Genre?: string;
  Director?: string;
  Actors?: string;
  imdbRating?: string;
}

interface Movie {
  imdbID: string;
  Title: string;
  Year: string;
}

// Pricing configuration
const PRICING: Record<string, number> = {
  '/v1/games/search': 0.005,
  '/v1/games/cheapest': 0.005,
  '/v1/games/{id}/news': 0.001,
  '/v1/games/{id}/release': 0.001,
  '/v1/movies/search': 0.005,
  '/v1/movies/cheapest': 0.005,
  '/v1/movies/{id}/details': 0.001,
  '/v1/movies/{id}/trailers': 0.001,
  '/v1/intel/search': 0.005,
  '/v1/intel/cheapest': 0.005,
  '/v1/airdrops/check': 0.01,
  '/v1/wallet/analyze': 0.025,
  '/v1/nft/search': 0.005,
  '/v1/score/{mint}': 0.01,
};

// Helper: extract price for endpoint
function getPrice(path: string): number {
  for (const [pattern, price] of Object.entries(PRICING)) {
    const regexPattern = pattern.replace('{id}', '[^/]+').replace('{mint}', '[^/]+');
    const regex = new RegExp(`^${regexPattern}$`);
    if (regex.test(path)) return price;
  }
  return 0;
}

// x402 Pay-Per-Call Validation
interface PaymentProof {
  signature: string;
  sender: string;
  timestamp: number;
  amount: string;
  nonce: string;
}

async function validatePayment(request: Request, requiredAmount: number): Promise<{ valid: boolean; error?: string }> {
  const x402Proof = request.headers.get('X-Payment-Proof');
  const x402Token = request.headers.get('X-Payment-Token');

  if (!x402Proof && !x402Token) {
    return { valid: false, error: 'Missing payment proof' };
  }

  // TODO: Implement full x402 signature validation
  // For now, accept valid-looking signatures (placeholder)
  if (x402Proof) {
    try {
      const proof: PaymentProof = JSON.parse(atob(x402Proof));
      
      // Basic validation
      const now = Date.now();
      if (Math.abs(now - proof.timestamp) > 300000) { // 5 minutes
        return { valid: false, error: 'Payment proof expired' };
      }

      return { valid: true };
    } catch (e) {
      return { valid: false, error: 'Invalid payment proof format' };
    }
  }

  // Token-based validation (Q402)
  if (x402Token) {
    // TODO: Verify token against Q402 registry
    return { valid: true };
  }

  return { valid: false, error: 'No valid payment method' };
}

// === GAMING ENDPOINTS ===

async function handleGamesSearch(query: string): Promise<Response> {
  const encodedQuery = encodeURIComponent(query);
  const cheapsharkUrl = `https://www.cheapshark.com/api/1.0/games?title=${encodedQuery}&limit=10`;

  const response = await fetch(cheapsharkUrl);
  const games: unknown = await response.json();

  const gamesArray = Array.isArray(games) ? games as Game[] : [];

  const formatted = gamesArray.map((game: Game) => ({
    id: game.gameID,
    title: game.external,
    cheapestPrice: parseFloat(game.cheapest) || 0,
    stores: game.stores || []
  }));

  return Response.json({ success: true, data: formatted });
}

async function handleGamesCheapest(query: string): Promise<Response> {
  const encodedQuery = encodeURIComponent(query);
  const cheapsharkUrl = `https://www.cheapshark.com/api/1.0/games?title=${encodedQuery}&limit=1&exact=0`;

  const response = await fetch(cheapsharkUrl);
  const games: unknown = await response.json();

  const gamesArray = Array.isArray(games) ? games as Game[] : [];

  if (!gamesArray || gamesArray.length === 0) {
    return Response.json({ success: false, error: 'No games found' }, { status: 404 });
  }

  const game = gamesArray[0];
  const dealUrl = `https://www.cheapshark.com/api/1.0/games?id=${game.gameID}`;
  const dealResponse = await fetch(dealUrl);
  const dealsData: unknown = await dealResponse.json();
  
  const deals = (dealsData as GameDeals).deals || [];
  const cheapest = deals.sort((a: GameDeal, b: GameDeal) => parseFloat(a.price) - parseFloat(b.price))[0];

  return Response.json({
    success: true,
    data: {
      gameId: game.gameID,
      title: game.external,
      cheapestPrice: cheapest ? parseFloat(cheapest.price) : 0,
      store: cheapest?.storeID || null,
      savings: cheapest?.savings || 0,
      dealUrl: `https://www.cheapshark.com/redirect?dealID=${cheapest?.dealID}`
    }
  });
}

async function handleGamesNews(gameId: string): Promise<Response> {
  // Mock data - integrate with Steam/IGDB in production
  return Response.json({
    success: true,
    data: {
      gameId,
      news: [
        { title: 'Patch v1.2.0 released', date: '2026-06-25', summary: 'Bug fixes and performance improvements' },
        { title: 'Server maintenance scheduled', date: '2026-06-20', summary: 'Downtime 2-4 AM UTC' }
      ]
    }
  });
}

async function handleGamesRelease(gameId: string): Promise<Response> {
  // Mock data - integrate with Steam in production
  return Response.json({
    success: true,
    data: {
      gameId,
      releaseDate: '2026-06-15',
      status: 'Released',
      platforms: ['PC', 'Xbox', 'PlayStation']
    }
  });
}

// === MOVIE ENDPOINTS ===

async function handleMoviesSearch(query: string): Promise<Response> {
  const omdbKey = 'demo'; // Replace with real OMDB key
  const omdbUrl = `https://www.omdbapi.com/?apikey=${omdbKey}&s=${encodeURIComponent(query)}&type=movie`;

  const response = await fetch(omdbUrl);
  const result: OMDBResponse = await response.json();

  if (result.Response === 'False') {
    return Response.json({ success: false, error: result.Error || 'Not found' }, { status: 404 });
  }

  return Response.json({ success: true, data: result.Search || [] });
}

async function handleMoviesCheapest(query: string): Promise<Response> {
  // Mock data - integrate with JustWatch/Reelgood in production
  return Response.json({
    success: true,
    data: {
      query,
      cheapest: {
        platform: 'Netflix',
        price: '$0',
        type: 'subscription'
      },
      alternatives: [
        { platform: 'Amazon Prime', price: '$0', type: 'subscription' },
        { platform: 'Apple TV', price: '$3.99', type: 'rental' }
      ]
    }
  });
}

async function handleMoviesDetails(movieId: string): Promise<Response> {
  const omdbKey = 'demo';
  const omdbUrl = `https://www.omdbapi.com/?apikey=${omdbKey}&i=${movieId}&plot=short`;

  const response = await fetch(omdbUrl);
  const movie: OMDBResponse = await response.json();

  if (movie.Response === 'False') {
    return Response.json({ success: false, error: movie.Error || 'Not found' }, { status: 404 });
  }

  return Response.json({
    success: true,
    data: {
      id: movie.imdbID || '',
      title: movie.Title || '',
      year: movie.Year || '',
      runtime: movie.Runtime || '',
      genres: movie.Genre?.split(', ') || [],
      director: movie.Director || '',
      cast: movie.Actors?.split(', ') || [],
      rating: parseFloat(movie.imdbRating || '0')
    }
  });
}

async function handleMoviesTrailers(movieId: string): Promise<Response> {
  // Mock data - integrate with YouTube API in production
  return Response.json({
    success: true,
    data: {
      movieId,
      trailers: [
        { title: 'Official Trailer', url: `https://youtube.com/watch?v=demo_${movieId}`, source: 'YouTube' },
        { title: 'Teaser', url: `https://youtube.com/watch?v=demo_teaser_${movieId}`, source: 'YouTube' }
      ]
    }
  });
}

// === UNIFIED INTEL ENDPOINTS ===

async function handleIntelSearch(query: string): Promise<Response> {
  // Parallel search of games + movies
  const [gamesResp, moviesResp] = await Promise.all([
    handleGamesSearch(query),
    handleMoviesSearch(query)
  ]);

  const gamesData: unknown = await gamesResp.json();
  const moviesData: unknown = await moviesResp.json();

  const games = gamesData as { success: boolean; data: any[] };
  const movies = moviesData as { success: boolean; data: any[] };

  return Response.json({
    success: true,
    data: {
      games: games.success ? games.data : [],
      movies: movies.success ? movies.data : []
    }
  });
}

async function handleIntelCheapest(query: string): Promise<Response> {
  const [gamesResp, moviesResp] = await Promise.all([
    handleGamesCheapest(query),
    handleMoviesCheapest(query)
  ]);

  const gamesData: unknown = await gamesResp.json();
  const moviesData: unknown = await moviesResp.json();

  const games = gamesData as { success: boolean; data: any };
  const movies = moviesData as { success: boolean; data: any };

  return Response.json({
    success: true,
    data: {
      games: games.success ? games.data : null,
      movies: movies.success ? movies.data : null
    }
  });
}

// === DEFI & WALLET ENDPOINTS ===

async function handleAirdropsCheck(wallet: string): Promise<Response> {
  // Mock data - integrate with airdrop trackers in production
  return Response.json({
    success: true,
    data: {
      wallet,
      eligible: [],
      potential: [
        { name: 'Testnet Airdrop', criteria: 'Has testnet transactions', status: 'Incomplete' }
      ]
    }
  });
}

async function handleWalletAnalyze(address: string): Promise<Response> {
  // Mock data - integrate with DeFi SDKs in production
  return Response.json({
    success: true,
    data: {
      address,
      totalValue: 0,
      holdings: [],
      positions: [],
      activityScore: 0
    }
  });
}

async function handleNftSearch(query: string): Promise<Response> {
  // Mock data - integrate with Solana NFT APIs in production
  return Response.json({
    success: true,
    data: {
      query,
      results: []
    }
  });
}

async function handleTokenScore(mint: string): Promise<Response> {
  // Mock data - integrate with token scoring in production
  return Response.json({
    success: true,
    data: {
      mint,
      score: 0,
      factors: {}
    }
  });
}

// === ROUTING ===

type HandlerFunction = (arg: string) => Promise<Response>;

export default {
  async fetch(request: Request, env: any, ctx: any): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname;
    const method = request.method;

    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, X-Payment-Proof, X-Payment-Token',
    };

    if (method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    // Route handler
    let handler: HandlerFunction | null = null;
    let arg = '';

    if (path === '/v1/games/search' && method === 'GET') {
      handler = handleGamesSearch;
      arg = url.searchParams.get('q') || '';
    } else if (path === '/v1/games/cheapest' && method === 'GET') {
      handler = handleGamesCheapest;
      arg = url.searchParams.get('q') || '';
    } else if (path.match(/^\/v1\/games\/\d+\/news$/) && method === 'GET') {
      handler = handleGamesNews;
      arg = path.split('/')[3];
    } else if (path.match(/^\/v1\/games\/\d+\/release$/) && method === 'GET') {
      handler = handleGamesRelease;
      arg = path.split('/')[3];
    } else if (path === '/v1/movies/search' && method === 'GET') {
      handler = handleMoviesSearch;
      arg = url.searchParams.get('q') || '';
    } else if (path === '/v1/movies/cheapest' && method === 'GET') {
      handler = handleMoviesCheapest;
      arg = url.searchParams.get('q') || '';
    } else if (path.match(/^\/v1\/movies\/[a-zA-Z0-9]+\/details$/) && method === 'GET') {
      handler = handleMoviesDetails;
      arg = path.split('/')[3];
    } else if (path.match(/^\/v1\/movies\/[a-zA-Z0-9]+\/trailers$/) && method === 'GET') {
      handler = handleMoviesTrailers;
      arg = path.split('/')[3];
    } else if (path === '/v1/intel/search' && method === 'GET') {
      handler = handleIntelSearch;
      arg = url.searchParams.get('q') || '';
    } else if (path === '/v1/intel/cheapest' && method === 'GET') {
      handler = handleIntelCheapest;
      arg = url.searchParams.get('q') || '';
    } else if (path === '/v1/airdrops/check' && method === 'GET') {
      handler = handleAirdropsCheck;
      arg = url.searchParams.get('wallet') || '';
    } else if (path === '/v1/wallet/analyze' && method === 'GET') {
      handler = handleWalletAnalyze;
      arg = url.searchParams.get('address') || '';
    } else if (path === '/v1/nft/search' && method === 'GET') {
      handler = handleNftSearch;
      arg = url.searchParams.get('q') || '';
    } else if (path.match(/^\/v1\/score\/[a-zA-Z0-9]+$/) && method === 'GET') {
      handler = handleTokenScore;
      arg = path.split('/')[3];
    }

    if (!handler) {
      return Response.json({ success: false, error: 'Endpoint not found' }, { 
        status: 404,
        headers: corsHeaders 
      });
    }

    // Validate payment
    const price = getPrice(path);
    if (price > 0) {
      const payment = await validatePayment(request, price);
      if (!payment.valid) {
        return Response.json({ 
          success: false, 
          error: payment.error,
          x402: {
            required: true,
            amount: price,
            currency: 'USDC',
            network: 'Base'
          }
        }, { 
          status: 402, 
          headers: corsHeaders 
        });
      }
    }

    // Execute handler
    try {
      const response = await handler(arg);
      // Return response directly with CORS headers added
      return new Response(response.body, {
        status: response.status,
        headers: {
          ...corsHeaders,
          ...Object.fromEntries(response.headers.entries())
        }
      });
    } catch (error: any) {
      return Response.json({ 
        success: false, 
        error: error.message || 'Internal server error' 
      }, { 
        status: 500,
        headers: corsHeaders 
      });
    }
  }
};