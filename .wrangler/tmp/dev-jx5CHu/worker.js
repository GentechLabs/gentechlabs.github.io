var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });

// .wrangler/tmp/bundle-xBcxO7/checked-fetch.js
var urls = /* @__PURE__ */ new Set();
function checkURL(request, init) {
  const url = request instanceof URL ? request : new URL(
    (typeof request === "string" ? new Request(request, init) : request).url
  );
  if (url.port && url.port !== "443" && url.protocol === "https:") {
    if (!urls.has(url.toString())) {
      urls.add(url.toString());
      console.warn(
        `WARNING: known issue with \`fetch()\` requests to custom HTTPS ports in published Workers:
 - ${url.toString()} - the custom port will be ignored when the Worker is published using the \`wrangler deploy\` command.
`
      );
    }
  }
}
__name(checkURL, "checkURL");
globalThis.fetch = new Proxy(globalThis.fetch, {
  apply(target, thisArg, argArray) {
    const [request, init] = argArray;
    checkURL(request, init);
    return Reflect.apply(target, thisArg, argArray);
  }
});

// .wrangler/tmp/bundle-xBcxO7/strip-cf-connecting-ip-header.js
function stripCfConnectingIPHeader(input, init) {
  const request = new Request(input, init);
  request.headers.delete("CF-Connecting-IP");
  return request;
}
__name(stripCfConnectingIPHeader, "stripCfConnectingIPHeader");
globalThis.fetch = new Proxy(globalThis.fetch, {
  apply(target, thisArg, argArray) {
    return Reflect.apply(target, thisArg, [
      stripCfConnectingIPHeader.apply(null, argArray)
    ]);
  }
});

// src/worker.ts
var PRICING = {
  "/v1/games/search": 5e-3,
  "/v1/games/cheapest": 5e-3,
  "/v1/games/{id}/news": 1e-3,
  "/v1/games/{id}/release": 1e-3,
  "/v1/movies/search": 5e-3,
  "/v1/movies/cheapest": 5e-3,
  "/v1/movies/{id}/details": 1e-3,
  "/v1/movies/{id}/trailers": 1e-3,
  "/v1/intel/search": 5e-3,
  "/v1/intel/cheapest": 5e-3,
  "/v1/airdrops/check": 0.01,
  "/v1/wallet/analyze": 0.025,
  "/v1/nft/search": 5e-3,
  "/v1/score/{mint}": 0.01
};
function getPrice(path) {
  for (const [pattern, price] of Object.entries(PRICING)) {
    const regexPattern = pattern.replace("{id}", "[^/]+").replace("{mint}", "[^/]+");
    const regex = new RegExp(`^${regexPattern}$`);
    if (regex.test(path))
      return price;
  }
  return 0;
}
__name(getPrice, "getPrice");
async function validatePayment(request, requiredAmount) {
  const x402Proof = request.headers.get("X-Payment-Proof");
  const x402Token = request.headers.get("X-Payment-Token");
  if (!x402Proof && !x402Token) {
    return { valid: false, error: "Missing payment proof" };
  }
  if (x402Proof) {
    try {
      const proof = JSON.parse(atob(x402Proof));
      const now = Date.now();
      if (Math.abs(now - proof.timestamp) > 3e5) {
        return { valid: false, error: "Payment proof expired" };
      }
      return { valid: true };
    } catch (e) {
      return { valid: false, error: "Invalid payment proof format" };
    }
  }
  if (x402Token) {
    return { valid: true };
  }
  return { valid: false, error: "No valid payment method" };
}
__name(validatePayment, "validatePayment");
async function handleGamesSearch(query) {
  const encodedQuery = encodeURIComponent(query);
  const cheapsharkUrl = `https://www.cheapshark.com/api/1.0/games?title=${encodedQuery}&limit=10`;
  const response = await fetch(cheapsharkUrl);
  const games = await response.json();
  const gamesArray = Array.isArray(games) ? games : [];
  const formatted = gamesArray.map((game) => ({
    id: game.gameID,
    title: game.external,
    cheapestPrice: parseFloat(game.cheapest) || 0,
    stores: game.stores || []
  }));
  return Response.json({ success: true, data: formatted });
}
__name(handleGamesSearch, "handleGamesSearch");
async function handleGamesCheapest(query) {
  const encodedQuery = encodeURIComponent(query);
  const cheapsharkUrl = `https://www.cheapshark.com/api/1.0/games?title=${encodedQuery}&limit=1&exact=0`;
  const response = await fetch(cheapsharkUrl);
  const games = await response.json();
  const gamesArray = Array.isArray(games) ? games : [];
  if (!gamesArray || gamesArray.length === 0) {
    return Response.json({ success: false, error: "No games found" }, { status: 404 });
  }
  const game = gamesArray[0];
  const dealUrl = `https://www.cheapshark.com/api/1.0/games?id=${game.gameID}`;
  const dealResponse = await fetch(dealUrl);
  const dealsData = await dealResponse.json();
  const deals = dealsData.deals || [];
  const cheapest = deals.sort((a, b) => parseFloat(a.price) - parseFloat(b.price))[0];
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
__name(handleGamesCheapest, "handleGamesCheapest");
async function handleGamesNews(gameId) {
  return Response.json({
    success: true,
    data: {
      gameId,
      news: [
        { title: "Patch v1.2.0 released", date: "2026-06-25", summary: "Bug fixes and performance improvements" },
        { title: "Server maintenance scheduled", date: "2026-06-20", summary: "Downtime 2-4 AM UTC" }
      ]
    }
  });
}
__name(handleGamesNews, "handleGamesNews");
async function handleGamesRelease(gameId) {
  return Response.json({
    success: true,
    data: {
      gameId,
      releaseDate: "2026-06-15",
      status: "Released",
      platforms: ["PC", "Xbox", "PlayStation"]
    }
  });
}
__name(handleGamesRelease, "handleGamesRelease");
async function handleMoviesSearch(query) {
  const omdbKey = "demo";
  const omdbUrl = `https://www.omdbapi.com/?apikey=${omdbKey}&s=${encodeURIComponent(query)}&type=movie`;
  const response = await fetch(omdbUrl);
  const result = await response.json();
  if (result.Response === "False") {
    return Response.json({ success: false, error: result.Error || "Not found" }, { status: 404 });
  }
  return Response.json({ success: true, data: result.Search || [] });
}
__name(handleMoviesSearch, "handleMoviesSearch");
async function handleMoviesCheapest(query) {
  return Response.json({
    success: true,
    data: {
      query,
      cheapest: {
        platform: "Netflix",
        price: "$0",
        type: "subscription"
      },
      alternatives: [
        { platform: "Amazon Prime", price: "$0", type: "subscription" },
        { platform: "Apple TV", price: "$3.99", type: "rental" }
      ]
    }
  });
}
__name(handleMoviesCheapest, "handleMoviesCheapest");
async function handleMoviesDetails(movieId) {
  const omdbKey = "demo";
  const omdbUrl = `https://www.omdbapi.com/?apikey=${omdbKey}&i=${movieId}&plot=short`;
  const response = await fetch(omdbUrl);
  const movie = await response.json();
  if (movie.Response === "False") {
    return Response.json({ success: false, error: movie.Error || "Not found" }, { status: 404 });
  }
  return Response.json({
    success: true,
    data: {
      id: movie.imdbID || "",
      title: movie.Title || "",
      year: movie.Year || "",
      runtime: movie.Runtime || "",
      genres: movie.Genre?.split(", ") || [],
      director: movie.Director || "",
      cast: movie.Actors?.split(", ") || [],
      rating: parseFloat(movie.imdbRating || "0")
    }
  });
}
__name(handleMoviesDetails, "handleMoviesDetails");
async function handleMoviesTrailers(movieId) {
  return Response.json({
    success: true,
    data: {
      movieId,
      trailers: [
        { title: "Official Trailer", url: `https://youtube.com/watch?v=demo_${movieId}`, source: "YouTube" },
        { title: "Teaser", url: `https://youtube.com/watch?v=demo_teaser_${movieId}`, source: "YouTube" }
      ]
    }
  });
}
__name(handleMoviesTrailers, "handleMoviesTrailers");
async function handleIntelSearch(query) {
  const [gamesResp, moviesResp] = await Promise.all([
    handleGamesSearch(query),
    handleMoviesSearch(query)
  ]);
  const gamesData = await gamesResp.json();
  const moviesData = await moviesResp.json();
  const games = gamesData;
  const movies = moviesData;
  return Response.json({
    success: true,
    data: {
      games: games.success ? games.data : [],
      movies: movies.success ? movies.data : []
    }
  });
}
__name(handleIntelSearch, "handleIntelSearch");
async function handleIntelCheapest(query) {
  const [gamesResp, moviesResp] = await Promise.all([
    handleGamesCheapest(query),
    handleMoviesCheapest(query)
  ]);
  const gamesData = await gamesResp.json();
  const moviesData = await moviesResp.json();
  const games = gamesData;
  const movies = moviesData;
  return Response.json({
    success: true,
    data: {
      games: games.success ? games.data : null,
      movies: movies.success ? movies.data : null
    }
  });
}
__name(handleIntelCheapest, "handleIntelCheapest");
async function handleAirdropsCheck(wallet) {
  return Response.json({
    success: true,
    data: {
      wallet,
      eligible: [],
      potential: [
        { name: "Testnet Airdrop", criteria: "Has testnet transactions", status: "Incomplete" }
      ]
    }
  });
}
__name(handleAirdropsCheck, "handleAirdropsCheck");
async function handleWalletAnalyze(address) {
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
__name(handleWalletAnalyze, "handleWalletAnalyze");
async function handleNftSearch(query) {
  return Response.json({
    success: true,
    data: {
      query,
      results: []
    }
  });
}
__name(handleNftSearch, "handleNftSearch");
async function handleTokenScore(mint) {
  return Response.json({
    success: true,
    data: {
      mint,
      score: 0,
      factors: {}
    }
  });
}
__name(handleTokenScore, "handleTokenScore");
var worker_default = {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;
    const method = request.method;
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, X-Payment-Proof, X-Payment-Token"
    };
    if (method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }
    let handler = null;
    let arg = "";
    if (path === "/v1/games/search" && method === "GET") {
      handler = handleGamesSearch;
      arg = url.searchParams.get("q") || "";
    } else if (path === "/v1/games/cheapest" && method === "GET") {
      handler = handleGamesCheapest;
      arg = url.searchParams.get("q") || "";
    } else if (path.match(/^\/v1\/games\/\d+\/news$/) && method === "GET") {
      handler = handleGamesNews;
      arg = path.split("/")[3];
    } else if (path.match(/^\/v1\/games\/\d+\/release$/) && method === "GET") {
      handler = handleGamesRelease;
      arg = path.split("/")[3];
    } else if (path === "/v1/movies/search" && method === "GET") {
      handler = handleMoviesSearch;
      arg = url.searchParams.get("q") || "";
    } else if (path === "/v1/movies/cheapest" && method === "GET") {
      handler = handleMoviesCheapest;
      arg = url.searchParams.get("q") || "";
    } else if (path.match(/^\/v1\/movies\/[a-zA-Z0-9]+\/details$/) && method === "GET") {
      handler = handleMoviesDetails;
      arg = path.split("/")[3];
    } else if (path.match(/^\/v1\/movies\/[a-zA-Z0-9]+\/trailers$/) && method === "GET") {
      handler = handleMoviesTrailers;
      arg = path.split("/")[3];
    } else if (path === "/v1/intel/search" && method === "GET") {
      handler = handleIntelSearch;
      arg = url.searchParams.get("q") || "";
    } else if (path === "/v1/intel/cheapest" && method === "GET") {
      handler = handleIntelCheapest;
      arg = url.searchParams.get("q") || "";
    } else if (path === "/v1/airdrops/check" && method === "GET") {
      handler = handleAirdropsCheck;
      arg = url.searchParams.get("wallet") || "";
    } else if (path === "/v1/wallet/analyze" && method === "GET") {
      handler = handleWalletAnalyze;
      arg = url.searchParams.get("address") || "";
    } else if (path === "/v1/nft/search" && method === "GET") {
      handler = handleNftSearch;
      arg = url.searchParams.get("q") || "";
    } else if (path.match(/^\/v1\/score\/[a-zA-Z0-9]+$/) && method === "GET") {
      handler = handleTokenScore;
      arg = path.split("/")[3];
    }
    if (!handler) {
      return Response.json({ success: false, error: "Endpoint not found" }, {
        status: 404,
        headers: corsHeaders
      });
    }
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
            currency: "USDC",
            network: "Base"
          }
        }, {
          status: 402,
          headers: corsHeaders
        });
      }
    }
    try {
      const response = await handler(arg);
      return new Response(response.body, {
        status: response.status,
        headers: {
          ...corsHeaders,
          ...Object.fromEntries(response.headers.entries())
        }
      });
    } catch (error) {
      return Response.json({
        success: false,
        error: error.message || "Internal server error"
      }, {
        status: 500,
        headers: corsHeaders
      });
    }
  }
};

// node_modules/wrangler/templates/middleware/middleware-ensure-req-body-drained.ts
var drainBody = /* @__PURE__ */ __name(async (request, env, _ctx, middlewareCtx) => {
  try {
    return await middlewareCtx.next(request, env);
  } finally {
    try {
      if (request.body !== null && !request.bodyUsed) {
        const reader = request.body.getReader();
        while (!(await reader.read()).done) {
        }
      }
    } catch (e) {
      console.error("Failed to drain the unused request body.", e);
    }
  }
}, "drainBody");
var middleware_ensure_req_body_drained_default = drainBody;

// node_modules/wrangler/templates/middleware/middleware-miniflare3-json-error.ts
function reduceError(e) {
  return {
    name: e?.name,
    message: e?.message ?? String(e),
    stack: e?.stack,
    cause: e?.cause === void 0 ? void 0 : reduceError(e.cause)
  };
}
__name(reduceError, "reduceError");
var jsonError = /* @__PURE__ */ __name(async (request, env, _ctx, middlewareCtx) => {
  try {
    return await middlewareCtx.next(request, env);
  } catch (e) {
    const error = reduceError(e);
    return Response.json(error, {
      status: 500,
      headers: { "MF-Experimental-Error-Stack": "true" }
    });
  }
}, "jsonError");
var middleware_miniflare3_json_error_default = jsonError;

// .wrangler/tmp/bundle-xBcxO7/middleware-insertion-facade.js
var __INTERNAL_WRANGLER_MIDDLEWARE__ = [
  middleware_ensure_req_body_drained_default,
  middleware_miniflare3_json_error_default
];
var middleware_insertion_facade_default = worker_default;

// node_modules/wrangler/templates/middleware/common.ts
var __facade_middleware__ = [];
function __facade_register__(...args) {
  __facade_middleware__.push(...args.flat());
}
__name(__facade_register__, "__facade_register__");
function __facade_invokeChain__(request, env, ctx, dispatch, middlewareChain) {
  const [head, ...tail] = middlewareChain;
  const middlewareCtx = {
    dispatch,
    next(newRequest, newEnv) {
      return __facade_invokeChain__(newRequest, newEnv, ctx, dispatch, tail);
    }
  };
  return head(request, env, ctx, middlewareCtx);
}
__name(__facade_invokeChain__, "__facade_invokeChain__");
function __facade_invoke__(request, env, ctx, dispatch, finalMiddleware) {
  return __facade_invokeChain__(request, env, ctx, dispatch, [
    ...__facade_middleware__,
    finalMiddleware
  ]);
}
__name(__facade_invoke__, "__facade_invoke__");

// .wrangler/tmp/bundle-xBcxO7/middleware-loader.entry.ts
var __Facade_ScheduledController__ = class {
  constructor(scheduledTime, cron, noRetry) {
    this.scheduledTime = scheduledTime;
    this.cron = cron;
    this.#noRetry = noRetry;
  }
  #noRetry;
  noRetry() {
    if (!(this instanceof __Facade_ScheduledController__)) {
      throw new TypeError("Illegal invocation");
    }
    this.#noRetry();
  }
};
__name(__Facade_ScheduledController__, "__Facade_ScheduledController__");
function wrapExportedHandler(worker) {
  if (__INTERNAL_WRANGLER_MIDDLEWARE__ === void 0 || __INTERNAL_WRANGLER_MIDDLEWARE__.length === 0) {
    return worker;
  }
  for (const middleware of __INTERNAL_WRANGLER_MIDDLEWARE__) {
    __facade_register__(middleware);
  }
  const fetchDispatcher = /* @__PURE__ */ __name(function(request, env, ctx) {
    if (worker.fetch === void 0) {
      throw new Error("Handler does not export a fetch() function.");
    }
    return worker.fetch(request, env, ctx);
  }, "fetchDispatcher");
  return {
    ...worker,
    fetch(request, env, ctx) {
      const dispatcher = /* @__PURE__ */ __name(function(type, init) {
        if (type === "scheduled" && worker.scheduled !== void 0) {
          const controller = new __Facade_ScheduledController__(
            Date.now(),
            init.cron ?? "",
            () => {
            }
          );
          return worker.scheduled(controller, env, ctx);
        }
      }, "dispatcher");
      return __facade_invoke__(request, env, ctx, dispatcher, fetchDispatcher);
    }
  };
}
__name(wrapExportedHandler, "wrapExportedHandler");
function wrapWorkerEntrypoint(klass) {
  if (__INTERNAL_WRANGLER_MIDDLEWARE__ === void 0 || __INTERNAL_WRANGLER_MIDDLEWARE__.length === 0) {
    return klass;
  }
  for (const middleware of __INTERNAL_WRANGLER_MIDDLEWARE__) {
    __facade_register__(middleware);
  }
  return class extends klass {
    #fetchDispatcher = (request, env, ctx) => {
      this.env = env;
      this.ctx = ctx;
      if (super.fetch === void 0) {
        throw new Error("Entrypoint class does not define a fetch() function.");
      }
      return super.fetch(request);
    };
    #dispatcher = (type, init) => {
      if (type === "scheduled" && super.scheduled !== void 0) {
        const controller = new __Facade_ScheduledController__(
          Date.now(),
          init.cron ?? "",
          () => {
          }
        );
        return super.scheduled(controller);
      }
    };
    fetch(request) {
      return __facade_invoke__(
        request,
        this.env,
        this.ctx,
        this.#dispatcher,
        this.#fetchDispatcher
      );
    }
  };
}
__name(wrapWorkerEntrypoint, "wrapWorkerEntrypoint");
var WRAPPED_ENTRY;
if (typeof middleware_insertion_facade_default === "object") {
  WRAPPED_ENTRY = wrapExportedHandler(middleware_insertion_facade_default);
} else if (typeof middleware_insertion_facade_default === "function") {
  WRAPPED_ENTRY = wrapWorkerEntrypoint(middleware_insertion_facade_default);
}
var middleware_loader_entry_default = WRAPPED_ENTRY;
export {
  __INTERNAL_WRANGLER_MIDDLEWARE__,
  middleware_loader_entry_default as default
};
//# sourceMappingURL=worker.js.map
