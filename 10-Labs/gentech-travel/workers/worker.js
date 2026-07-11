/**
 * GenTech Travel Agent — Cloudflare Worker
 * 
 * Proxies travel queries through x402 payment layer.
 * Routes: Travala MCP (hotels), LetsFG MCP (flights), OpenStreetMap (POIs)
 */

// External MCP endpoints
const TRAVALA_MCP = "https://travel-mcp.travala.com/mcp";
const LETSFG_MCP = "https://letsfg-mcp.vercel.app/mcp";
const X402_GATEWAY = "https://gentech-x402-gateway.jordanjones0902.workers.dev";

// Pricing (USDC)
const PRICING = {
  plan_trip: 0.02,
  search_hotel: 0.005,
  search_flights: 0.005,
  search_pois: 0.003,
  route_plan: 0.01,
  pricing: 0,       // free
  health: 0,         // free
};

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

    // CORS headers
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, X-Agent-ID, X-Payment-Token",
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    try {
      // ── Free endpoints ──
      if (path === "/health") {
        return jsonResponse({ status: "ok", service: "gentech-travel-agent" }, corsHeaders);
      }

      if (path === "/pricing") {
        return jsonResponse({ pricing: PRICING, currency: "USDC", network: "eip155:8453" }, corsHeaders);
      }

      // ── Paid endpoints ──
      const agentId = request.headers.get("X-Agent-ID") || "anonymous";
      const paymentToken = request.headers.get("X-Payment-Token");

      // Route to handler
      let result;
      switch (path) {
        case "/plan":
          result = await handlePlan(request, agentId, paymentToken);
          break;
        case "/hotels":
          result = await handleHotels(request, agentId, paymentToken);
          break;
        case "/flights":
          result = await handleFlights(request, agentId, paymentToken);
          break;
        case "/pois":
          result = await handlePOIs(request, agentId, paymentToken);
          break;
        case "/route":
          result = await handleRoute(request, agentId, paymentToken);
          break;
        default:
          return jsonResponse({ error: "Not found", paths: ["/health","/pricing","/plan","/hotels","/flights","/pois","/route"] }, corsHeaders, 404);
      }

      return jsonResponse(result, corsHeaders);
    } catch (err) {
      return jsonResponse({ error: err.message }, corsHeaders, 500);
    }
  },
};

// ── Handlers ──

async function handlePlan(request, agentId, paymentToken) {
  const body = await request.json();
  const { destination, checkIn, checkOut, origin, guests = 1 } = body;
  if (!destination || !checkIn || !checkOut) {
    return { error: "Missing required fields: destination, checkIn, checkOut" };
  }

  // Parallel calls
  const [hotels, pois] = await Promise.all([
    callTravala("search_hotel", { destination, checkIn, checkOut, guests }),
    searchOSMPOIs(destination, 2000),
  ]);

  let flights = [];
  if (origin) {
    flights = await callLetsFG("search_flights", {
      origin: origin.toUpperCase(),
      destination: destination.toUpperCase(),
      date: checkIn,
      passengers: guests,
    });
  }

  return {
    destination,
    date: `${checkIn} → ${checkOut}`,
    hotels: (hotels.results || []).slice(0, 5).map(h => ({
      name: h.name || h.hotelName || "Unknown",
      price: h.price || h.totalPrice || "?",
    })),
    flights: flights.slice(0, 5).map(f => ({
      airline: f.airline || "?",
      price: f.price?.total || "?",
      stops: f.stops || 0,
    })),
    pois: pois.slice(0, 8).map(p => ({ name: p.name, category: p.category })),
    pricing: PRICING,
  };
}

async function handleHotels(request, agentId, paymentToken) {
  const body = await request.json();
  const { destination, checkIn, checkOut, guests = 1, maxPrice } = body;
  if (!destination || !checkIn || !checkOut) {
    return { error: "Missing required fields: destination, checkIn, checkOut" };
  }
  const result = await callTravala("search_hotel", { destination, checkIn, checkOut, guests, maxPrice });
  return { results: (result.results || []).slice(0, 10) };
}

async function handleFlights(request, agentId, paymentToken) {
  const body = await request.json();
  const { origin, destination, date, passengers = 1 } = body;
  if (!origin || !destination || !date) {
    return { error: "Missing required fields: origin, destination, date" };
  }
  const result = await callLetsFG("search_flights", {
    origin: origin.toUpperCase(),
    destination: destination.toUpperCase(),
    date,
    passengers,
  });
  return { results: result.slice(0, 10) };
}

async function handlePOIs(request, agentId, paymentToken) {
  const body = await request.json();
  const { location, lat, lon, radius = 1000 } = body;
  let coords;
  if (location) {
    coords = await geocode(location);
  } else if (lat !== undefined && lon !== undefined) {
    coords = { lat, lon };
  } else {
    return { error: "Provide 'location' or 'lat' + 'lon'" };
  }
  const pois = await searchOSMPOIs(coords.lat, coords.lon, radius);
  return { results: pois.slice(0, 20) };
}

async function handleRoute(request, agentId, paymentToken) {
  const body = await request.json();
  const { fromLat, fromLon, toLat, toLon } = body;
  if (fromLat === undefined || fromLon === undefined || toLat === undefined || toLon === undefined) {
    return { error: "Missing fields: fromLat, fromLon, toLat, toLon" };
  }
  return await getOSRMRoute(fromLat, fromLon, toLat, toLon);
}

// ── External API calls ──

async function callTravala(tool, params) {
  const resp = await fetch(TRAVALA_MCP, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tool, params }),
  });
  return await resp.json();
}

async function callLetsFG(tool, params) {
  const resp = await fetch(LETSFG_MCP, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tool, params }),
  });
  return await resp.json();
}

async function geocode(location) {
  const resp = await fetch(
    `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(location)}&format=json&limit=1`,
    { headers: { "User-Agent": "GenTechTravel/1.0" } }
  );
  const data = await resp.json();
  if (!data || data.length === 0) throw new Error(`Location not found: ${location}`);
  return { lat: parseFloat(data[0].lat), lon: parseFloat(data[0].lon) };
}

async function searchOSMPOIs(lat, lon, radius) {
  const query = `[out:json];(node(around:${radius},${lat},${lon})["tourism"];way(around:${radius},${lat},${lon})["tourism"];node(around:${radius},${lat},${lon})["amenity"~"restaurant|cafe"];node(around:${radius},${lat},${lon})["leisure"="park"];);out center 20;`;
  const resp = await fetch("https://overpass-api.de/api/interpreter", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: query,
  });
  const data = await resp.json();
  return (data.elements || [])
    .filter(el => el.tags?.name)
    .map(el => ({
      name: el.tags.name,
      lat: el.lat || el.center?.lat || lat,
      lon: el.lon || el.center?.lon || lon,
      category: el.tags.tourism || el.tags.amenity || el.tags.leisure || "attraction",
    }));
}

async function getOSRMRoute(fromLat, fromLon, toLat, toLon) {
  const resp = await fetch(
    `https://router.project-osrm.org/route/v1/driving/${fromLon},${fromLat};${toLon},${toLat}?overview=full&geometries=geojson`
  );
  const data = await resp.json();
  if (data.code !== "Ok" || !data.routes?.length) throw new Error("No route found");
  const route = data.routes[0];
  return {
    distance_km: Math.round(route.distance / 1000 * 10) / 10,
    duration_min: Math.round(route.duration / 60),
  };
}

// ── Helpers ──

function jsonResponse(data, headers, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { ...headers, "Content-Type": "application/json" },
  });
}
