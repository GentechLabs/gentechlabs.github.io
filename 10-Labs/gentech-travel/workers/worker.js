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
  cost_of_living: 0.003,   // per city query
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
        case "/cost-of-living":
          result = await handleCostOfLiving(request, agentId, paymentToken);
          break;
        case "/route":
          result = await handleRoute(request, agentId, paymentToken);
          break;
        default:
          return jsonResponse({ error: "Not found", paths: ["/health","/pricing","/plan","/hotels","/flights","/pois","/cost-of-living","/route"] }, corsHeaders, 404);
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

  // Add cost of living data
  const cityMatch = COST_OF_LIVING_CITIES.find(c => 
    destination.toLowerCase().includes(c.n.split(",")[0].toLowerCase())
  );
  const costOfLiving = cityMatch ? {
    currency: cityMatch.cu,
    cost_of_living_index: cityMatch.idx[0],
    meal_price: cityMatch.p.meal,
    apt_1br_center: cityMatch.p.apt1_center,
    monthly_budget_estimate: {
      hotel: `~${(cityMatch.p.apt1_center / 30 * guests * (checkOut ? (new Date(checkOut) - new Date(checkIn)) / (1000*60*60*24) || 3 : 3)).toFixed(0)} ${cityMatch.cu}`,
      food_daily: `~${(cityMatch.p.meal * 2 + cityMatch.p.coffee * 2).toFixed(0)} ${cityMatch.cu}`,
      transport_daily: `~${(cityMatch.p.transit * 2).toFixed(0)} ${cityMatch.cu}`,
    },
  } : null;

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
    cost_of_living: costOfLiving,
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

// ── Cost of Living Data ──

const COST_OF_LIVING_CITIES = [
  { n: "New York, United States", co: "US", cu: "USD", idx: [100.0, 100.0, 100.0, 100.0, 100.0], p: { meal: 25, beer: 8, coffee: 5.49, milk: 1.42, bread: 4.02, eggs: 4.35, chicken: 13.67, transit: 2.90, monthly_pass: 132, taxi_km: 1.86, utilities: 182.66, internet: 66.20, fitness: 112.14, apt1_center: 3400, apt1_out: 2100, salary: 6700 } },
  { n: "London, United Kingdom", co: "UK", cu: "GBP", idx: [82.3, 60.5, 68.4, 86.7, 71.2], p: { meal: 15, beer: 6, coffee: 3.85, milk: 1.25, bread: 1.25, eggs: 3.40, chicken: 7.10, transit: 3.00, monthly_pass: 200, taxi_km: 1.50, utilities: 220, internet: 35, fitness: 50, apt1_center: 1900, apt1_out: 1400, salary: 3500 } },
  { n: "Tokyo, Japan", co: "JP", cu: "JPY", idx: [73.4, 46.8, 70.2, 51.3, 84.5], p: { meal: 1000, beer: 600, coffee: 500, milk: 210, bread: 250, eggs: 350, chicken: 1200, transit: 210, monthly_pass: 10000, taxi_km: 420, utilities: 20000, internet: 4500, fitness: 9000, apt1_center: 130000, apt1_out: 80000, salary: 450000 } },
  { n: "Singapore, Singapore", co: "SG", cu: "SGD", idx: [79.5, 66.7, 72.1, 52.4, 93.2], p: { meal: 7, beer: 8, coffee: 5.80, milk: 3.50, bread: 2.80, eggs: 4.20, chicken: 8.50, transit: 2.20, monthly_pass: 120, taxi_km: 0.80, utilities: 150, internet: 40, fitness: 120, apt1_center: 3500, apt1_out: 2300, salary: 5800 } },
  { n: "Dubai, United Arab Emirates", co: "AE", cu: "AED", idx: [64.5, 51.2, 58.3, 57.8, 127.5], p: { meal: 35, beer: 12, coffee: 18, milk: 6, bread: 5, eggs: 10, chicken: 25, transit: 8, monthly_pass: 300, taxi_km: 2, utilities: 800, internet: 350, fitness: 300, apt1_center: 5500, apt1_out: 3500, salary: 15000 } },
  { n: "Bangkok, Thailand", co: "TH", cu: "THB", idx: [36.2, 18.5, 30.1, 22.4, 42.8], p: { meal: 2.50, beer: 3, coffee: 2.50, milk: 1.80, bread: 1.50, eggs: 2.20, chicken: 3.50, transit: 1, monthly_pass: 35, taxi_km: 0.50, utilities: 80, internet: 22, fitness: 40, apt1_center: 550, apt1_out: 350, salary: 1500 } },
  { n: "Bali, Indonesia", co: "ID", cu: "IDR", idx: [30.5, 10.2, 25.8, 14.6, 25.0], p: { meal: 3, beer: 4.50, coffee: 3, milk: 1.50, bread: 1.20, eggs: 1.80, chicken: 4, transit: 0.50, monthly_pass: 20, taxi_km: 0.30, utilities: 60, internet: 35, fitness: 30, apt1_center: 400, apt1_out: 250, salary: 500 } },
  { n: "Mexico City, Mexico", co: "MX", cu: "MXN", idx: [33.0, 15.8, 28.5, 18.2, 48.5], p: { meal: 8, beer: 3.50, coffee: 3, milk: 1.30, bread: 2, eggs: 2.50, chicken: 5, transit: 0.40, monthly_pass: 15, taxi_km: 0.30, utilities: 50, internet: 28, fitness: 45, apt1_center: 700, apt1_out: 400, salary: 800 } },
  { n: "Buenos Aires, Argentina", co: "AR", cu: "ARS", idx: [25.0, 10.5, 22.0, 14.0, 35.0], p: { meal: 6, beer: 3, coffee: 2.50, milk: 1, bread: 0.80, eggs: 1.50, chicken: 3.50, transit: 0.30, monthly_pass: 12, taxi_km: 0.20, utilities: 45, internet: 25, fitness: 35, apt1_center: 500, apt1_out: 300, salary: 600 } },
  { n: "Lisbon, Portugal", co: "PT", cu: "EUR", idx: [48.0, 32.5, 40.2, 38.5, 55.0], p: { meal: 12, beer: 3, coffee: 2, milk: 0.85, bread: 1.20, eggs: 2.80, chicken: 6, transit: 1.80, monthly_pass: 45, taxi_km: 0.80, utilities: 110, internet: 38, fitness: 35, apt1_center: 1200, apt1_out: 800, salary: 1500 } },
  { n: "Hanoi, Vietnam", co: "VN", cu: "VND", idx: [22.0, 8.5, 19.0, 10.5, 20.0], p: { meal: 2, beer: 1, coffee: 1.50, milk: 1.20, bread: 0.60, eggs: 1.20, chicken: 2.50, transit: 0.30, monthly_pass: 8, taxi_km: 0.20, utilities: 45, internet: 15, fitness: 25, apt1_center: 350, apt1_out: 200, salary: 350 } },
  { n: "Barcelona, Spain", co: "ES", cu: "EUR", idx: [55.0, 38.5, 45.0, 50.0, 62.0], p: { meal: 14, beer: 4.50, coffee: 2.20, milk: 1.05, bread: 1.30, eggs: 2.90, chicken: 7.50, transit: 2.40, monthly_pass: 55, taxi_km: 1.10, utilities: 130, internet: 42, fitness: 45, apt1_center: 1400, apt1_out: 900, salary: 2000 } },
  { n: "Cape Town, South Africa", co: "ZA", cu: "ZAR", idx: [28.0, 18.5, 24.0, 22.0, 52.0], p: { meal: 10, beer: 3, coffee: 2.50, milk: 1.20, bread: 1, eggs: 2, chicken: 4.50, transit: 1, monthly_pass: 35, taxi_km: 0.60, utilities: 85, internet: 35, fitness: 35, apt1_center: 600, apt1_out: 400, salary: 1800 } },
  { n: "Seoul, South Korea", co: "KR", cu: "KRW", idx: [68.5, 42.0, 62.0, 45.0, 72.0], p: { meal: 12, beer: 5, coffee: 4.50, milk: 2.80, bread: 3.50, eggs: 3.80, chicken: 10, transit: 1.50, monthly_pass: 65, taxi_km: 1, utilities: 180, internet: 28, fitness: 55, apt1_center: 1100, apt1_out: 700, salary: 3200 } },
  { n: "Sydney, Australia", co: "AU", cu: "AUD", idx: [82.0, 62.0, 72.0, 78.0, 78.0], p: { meal: 22, beer: 10, coffee: 5, milk: 2.50, bread: 3.50, eggs: 5.50, chicken: 14, transit: 4, monthly_pass: 180, taxi_km: 2.50, utilities: 220, internet: 75, fitness: 70, apt1_center: 2500, apt1_out: 1800, salary: 5200 } },
];

async function handleCostOfLiving(request, agentId, paymentToken) {
  const url = new URL(request.url);
  const query = url.searchParams.get("city")?.toLowerCase() || "";
  const compare = url.searchParams.get("compare")?.toLowerCase() || "";

  const findCity = (q) => COST_OF_LIVING_CITIES.find(c => c.n.toLowerCase().includes(q) || c.co.toLowerCase().includes(q));

  if (!query) {
    return {
      summary: true,
      total_cities: COST_OF_LIVING_CITIES.length,
      cities: COST_OF_LIVING_CITIES.map(c => ({
        name: c.n,
        country: c.co,
        currency: c.cu,
        cost_of_living_index: c.idx[0],
        avg_salary: c.p.salary,
        apt_1br_center: c.p.apt1_center,
        meal_price: c.p.meal,
      })),
    };
  }

  const city = findCity(query);
  if (!city) {
    return { error: `City not found: ${query}` };
  }

  const indices = ["Cost of Living", "Rent", "Groceries", "Restaurants", "Local Purchasing Power"];
  const indexLabels = {};
  city.idx.forEach((v, i) => { indexLabels[indices[i]] = v; });

  // Affordability
  const salaryRatio = ((city.idx[0] / city.idx[4]) * 100).toFixed(0);
  const rentBurden = ((city.p.apt1_center / city.p.salary) * 100).toFixed(0);

  let result = {
    city: { name: city.n, country: city.co, currency: city.cu },
    indices: indexLabels,
    prices: {
      meal_inexpensive: city.p.meal,
      domestic_beer: city.p.beer,
      cappuccino: city.p.coffee,
      milk_1l: city.p.milk,
      bread_loaf: city.p.bread,
      eggs_12: city.p.eggs,
      chicken_1kg: city.p.chicken,
      one_way_ticket: city.p.transit,
      monthly_transit: city.p.monthly_pass,
      taxi_per_km: city.p.taxi_km,
      utilities_monthly: city.p.utilities,
      internet_monthly: city.p.internet,
      fitness_club: city.p.fitness,
      apt_1br_center: city.p.apt1_center,
      apt_1br_outside: city.p.apt1_out,
      avg_salary_monthly: city.p.salary,
    },
    affordability: {
      cost_of_living_vs_salary: `${salaryRatio}% of salary goes to living costs`,
      rent_burden: `${rentBurden}% of salary for city-center 1BR`,
      recommendation: city.idx[4] > 90 ? "High purchasing power — great for savings." :
        city.idx[4] > 60 ? "Moderate purchasing power — comfortable lifestyle." :
        "Lower purchasing power — budget-friendly destination.",
    },
  };

  // If comparing two cities
  if (compare) {
    const compareCity = findCity(compare);
    if (compareCity) {
      const diffs = {};
      indices.forEach((label, i) => {
        const diff = ((city.idx[i] - compareCity.idx[i]) / compareCity.idx[i] * 100).toFixed(1);
        diffs[label] = `${diff}%`;
      });
      result.comparison = {
        city_2: { name: compareCity.n, country: compareCity.co, currency: compareCity.cu },
        differentials: diffs,
        verdict: `${city.n} cost of living is ${city.idx[0] > compareCity.idx[0] ? "higher" : "lower"} than ${compareCity.n}. ` +
          `Rent is ${city.idx[1] > compareCity.idx[1] ? "+" : ""}${((city.idx[1] - compareCity.idx[1]) / compareCity.idx[1] * 100).toFixed(0)}% different.`,
      };
    }
  }

  return result;
}

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
