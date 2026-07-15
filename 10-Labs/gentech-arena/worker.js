/**
 * GenTech Agent Arena — Agent Match Prediction Layer
 * 
 * Watch AI agents play. Predict the winner. Stake USDC.
 * 
 * Endpoints:
 *   GET  /          — Match lobby (HTML)
 *   GET  /match/:id — Match detail + bet UI (HTML)
 *   POST /api/bet   — Place a bet (x402-paid)
 *   GET  /api/matches — List active/upcoming matches
 *   GET  /health    — Health check
 *   GET  /pricing   — Pricing info
 */

// ── Match Data ──
const MATCHES = [
  {
    id: "gs-doubles-001",
    game: "GenTech Smash",
    format: "Doubles",
    teamA: { name: "KAGE & Forge", players: ["Jordan (Human)", "Forge (AI)"], odds: 1.8 },
    teamB: { name: "HIKARI & Reparathy", players: ["CPU", "CPU"], odds: 2.2 },
    status: "upcoming",
    scheduled: "2026-07-15T20:00:00Z",
    result: null,
    description: "Human + AI team up against CPU in GenTech Smash doubles. KAGE and Forge vs HIKARI and Reparathy.",
  },
  {
    id: "gs-singles-001",
    game: "GenTech Smash",
    format: "Singles",
    teamA: { name: "Forge (AI)", players: ["Forge AI Agent"], odds: 2.5 },
    teamB: { name: "CPU (Hard)", players: ["Vanito (CPU)"], odds: 1.5 },
    status: "upcoming",
    scheduled: "2026-07-15T21:00:00Z",
    result: null,
    description: "Pure AI vs CPU — can Forge beat Vanito in a singles match?",
  },
  {
    id: "gs-doubles-002",
    game: "GenTech Smash",
    format: "Doubles",
    teamA: { name: "Forge + Forge", players: ["Forge AI (P1)", "Forge AI (P2)"], odds: 3.0 },
    teamB: { name: "CPU + CPU", players: ["CPU (P1)", "CPU (P2)"], odds: 1.33 },
    status: "upcoming",
    scheduled: "2026-07-15T22:00:00Z",
    result: null,
    description: "Two AI agents vs two CPUs — pure agent vs agent doubles action.",
  },
];

// ── Pricing ──
const PRICING = {
  "/api/bet": 0.01,  // $0.01 USDC per bet
};

// ── CORS ──
const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, x402-payment",
};

// ── HTML Templates ──

const HTML_HEAD = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Agent Arena — Agent Match Predictions</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0a0a0f; color: #e0e0e0; min-height: 100vh; }
  .container { max-width: 900px; margin: 0 auto; padding: 20px; }
  header { text-align: center; padding: 40px 0 20px; }
  h1 { font-size: 2.5em; background: linear-gradient(135deg, #ff6b35, #f7c948); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  .subtitle { color: #888; font-size: 1.1em; margin-top: 8px; }
  .tagline { color: #f7c948; font-size: 0.9em; margin-top: 4px; font-style: italic; }
  
  .match-card { background: #14141f; border: 1px solid #2a2a3a; border-radius: 12px; padding: 24px; margin-bottom: 20px; transition: border-color 0.2s; }
  .match-card:hover { border-color: #ff6b35; }
  .match-card.live { border-color: #00ff88; }
  .match-card.completed { border-color: #555; opacity: 0.7; }
  
  .match-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
  .match-game { color: #888; font-size: 0.85em; text-transform: uppercase; letter-spacing: 1px; }
  .match-status { padding: 4px 12px; border-radius: 20px; font-size: 0.8em; font-weight: 600; }
  .status-upcoming { background: #2a2a3a; color: #888; }
  .status-live { background: #003322; color: #00ff88; }
  .status-completed { background: #222; color: #666; }
  
  .teams { display: grid; grid-template-columns: 1fr auto 1fr; gap: 16px; align-items: center; margin-bottom: 16px; }
  .team { padding: 16px; border-radius: 8px; text-align: center; }
  .team-a { background: rgba(255, 107, 53, 0.1); border: 1px solid rgba(255, 107, 53, 0.3); }
  .team-b { background: rgba(0, 136, 255, 0.1); border: 1px solid rgba(0, 136, 255, 0.3); }
  .team-name { font-size: 1.2em; font-weight: 700; margin-bottom: 4px; }
  .team-a .team-name { color: #ff6b35; }
  .team-b .team-name { color: #4a9eff; }
  .team-players { font-size: 0.85em; color: #aaa; }
  .team-odds { font-size: 1.4em; font-weight: 700; margin-top: 8px; }
  .vs { font-size: 1.5em; font-weight: 900; color: #f7c948; }
  
  .bet-area { text-align: center; padding-top: 12px; border-top: 1px solid #2a2a3a; }
  .bet-btn { display: inline-block; padding: 10px 24px; border-radius: 8px; border: none; font-size: 1em; font-weight: 600; cursor: pointer; margin: 0 8px; transition: transform 0.1s; }
  .bet-btn:hover { transform: scale(1.05); }
  .bet-btn-a { background: #ff6b35; color: #fff; }
  .bet-btn-b { background: #4a9eff; color: #fff; }
  .bet-btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }
  .bet-info { color: #888; font-size: 0.85em; margin-top: 8px; }
  
  .result-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.85em; font-weight: 600; margin-top: 8px; }
  .result-win { background: #003322; color: #00ff88; }
  .result-loss { background: #330000; color: #ff4444; }
  
  .how-it-works { background: #14141f; border: 1px solid #2a2a3a; border-radius: 12px; padding: 24px; margin-top: 30px; }
  .how-it-works h2 { color: #f7c948; margin-bottom: 12px; }
  .how-it-works ol { padding-left: 20px; line-height: 2; color: #aaa; }
  .how-it-works li span { color: #e0e0e0; }
  
  .footer { text-align: center; padding: 30px; color: #555; font-size: 0.85em; }
  .footer a { color: #f7c948; text-decoration: none; }
  
  .wallet-badge { display: inline-block; background: #1a1a2e; border: 1px solid #333; border-radius: 8px; padding: 6px 12px; font-size: 0.8em; color: #888; margin-top: 10px; }
  
  @media (max-width: 600px) {
    .teams { grid-template-columns: 1fr; }
    .vs { display: none; }
  }
</style>
</head>
<body>
<div class="container">`;

const HTML_FOOT = `
  <div class="how-it-works">
    <h2>⚡ How It Works</h2>
    <ol>
      <li><span>Watch live AI agent matches on stream</span></li>
      <li><span>Pick your winner and stake USDC via x402</span></li>
      <li><span>If your team wins, collect your payout automatically</span></li>
      <li><span>Every match trains the agent — it gets smarter over time</span></li>
    </ol>
    <div class="wallet-badge">⚡ Powered by x402 · USDC on Base</div>
  </div>
  <div class="footer">
    <p>Agent Arena — Agent Match Predictions</p>
    <p><a href="/health">Health</a> · <a href="/pricing">Pricing</a></p>
  </div>
</div>
</body>
</html>`;

function renderMatchCard(m) {
  const statusClass = `status-${m.status}`;
  const oddsA = m.teamA.odds.toFixed(1);
  const oddsB = m.teamB.odds.toFixed(1);
  const betDisabled = m.status !== "upcoming" ? "disabled" : "";
  
  let resultHtml = "";
  if (m.result) {
    const cls = m.result === "A" ? "result-win" : "result-loss";
    const label = m.result === "A" ? `${m.teamA.name} Won` : `${m.teamB.name} Won`;
    resultHtml = `<div class="result-badge ${cls}">${label}</div>`;
  }

  return `
  <div class="match-card ${m.status}" id="match-${m.id}">
    <div class="match-header">
      <span class="match-game">${m.game} · ${m.format}</span>
      <span class="match-status ${statusClass}">${m.status.toUpperCase()}</span>
    </div>
    <div class="match-description" style="color:#888;font-size:0.9em;margin-bottom:12px;">${m.description}</div>
    <div class="teams">
      <div class="team team-a">
        <div class="team-name">${m.teamA.name}</div>
        <div class="team-players">${m.teamA.players.join(" + ")}</div>
        <div class="team-odds" style="color:#ff6b35">${oddsA}x</div>
      </div>
      <div class="vs">VS</div>
      <div class="team team-b">
        <div class="team-name">${m.teamB.name}</div>
        <div class="team-players">${m.teamB.players.join(" + ")}</div>
        <div class="team-odds" style="color:#4a9eff">${oddsB}x</div>
      </div>
    </div>
    ${resultHtml}
    <div class="bet-area">
      <button class="bet-btn bet-btn-a" ${betDisabled} onclick="placeBet('${m.id}', 'A', ${m.teamA.odds})">Bet ${m.teamA.name}</button>
      <button class="bet-btn bet-btn-b" ${betDisabled} onclick="placeBet('${m.id}', 'B', ${m.teamB.odds})">Bet ${m.teamB.name}</button>
      <div class="bet-info">Stake: $0.01 USDC · Payout: ${oddsA}x / ${oddsB}x</div>
    </div>
  </div>`;
}

// ── Worker ──

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    try {
      // ── API Routes ──
      if (path === "/health") {
        return jsonResponse({ status: "ok", service: "agent-arena" }, corsHeaders);
      }

      if (path === "/pricing") {
        return jsonResponse({ pricing: PRICING, currency: "USDC", network: "eip155:8453" }, corsHeaders);
      }

      if (path === "/api/matches") {
        return jsonResponse({ matches: MATCHES }, corsHeaders);
      }

      if (path === "/api/bet" && request.method === "POST") {
        const body = await request.json();
        const { matchId, team } = body;
        
        if (!matchId || !team) {
          return jsonResponse({ error: "matchId and team required" }, corsHeaders, 400);
        }
        if (team !== "A" && team !== "B") {
          return jsonResponse({ error: "team must be 'A' or 'B'" }, corsHeaders, 400);
        }

        const match = MATCHES.find(m => m.id === matchId);
        if (!match) {
          return jsonResponse({ error: "Match not found" }, corsHeaders, 404);
        }
        if (match.status !== "upcoming") {
          return jsonResponse({ error: "Match is not accepting bets" }, corsHeaders, 400);
        }

        const odds = team === "A" ? match.teamA.odds : match.teamB.odds;
        const teamName = team === "A" ? match.teamA.name : match.teamB.name;

        return jsonResponse({
          success: true,
          bet: {
            matchId,
            team,
            teamName,
            stake: PRICING["/api/bet"],
            odds,
            potentialPayout: (PRICING["/api/bet"] * odds).toFixed(4),
            currency: "USDC",
          },
          payment: {
            scheme: "exact",
            network: "eip155:8453",
            asset: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
            payTo: "0x7ebff188f2Eba16518C02864589b1403a5d1296a",
            amount: PRICING["/api/bet"] * 1000000, // USDC has 6 decimals
          },
        }, corsHeaders);
      }

      // ── Match Detail Page ──
      const matchMatch = path.match(/^\/match\/(.+)$/);
      if (matchMatch) {
        const match = MATCHES.find(m => m.id === matchMatch[1]);
        if (!match) {
          return new Response("Match not found", { status: 404 });
        }
        return new Response(
          HTML_HEAD + renderMatchCard(match) + HTML_FOOT,
          { headers: { "Content-Type": "text/html" } }
        );
      }

      // ── Lobby Page ──
      if (path === "/" || path === "") {
        const cards = MATCHES.map(renderMatchCard).join("\n");
        const lobbyScript = [
          '<script>',
          'async function placeBet(matchId, team, odds) {',
          '  var stake = 0.01;',
          '  var payout = (stake * odds).toFixed(4);',
          '  var teamName = team === "A" ? "KAGE & Forge" : "HIKARI & Reparathy";',
          '  if (!confirm("Place " + stake + " USDC on " + teamName + "?\\nPotential payout: " + payout + " USDC")) return;',
          '  try {',
          '    var resp = await fetch("/api/bet", {',
          '      method: "POST",',
          '      headers: { "Content-Type": "application/json" },',
          '      body: JSON.stringify({ matchId: matchId, team: team }),',
          '    });',
          '    var data = await resp.json();',
          '    if (data.success) {',
          '      alert("✅ Bet placed!\\n\\n" + data.bet.teamName + "\\nStake: " + data.bet.stake + " USDC\\nOdds: " + data.bet.odds + "x\\nPotential payout: " + data.bet.potentialPayout + " USDC\\n\\nSend " + data.bet.stake + " USDC to:\\n" + data.payment.payTo + "\\n\\n(Manual payment for now - auto-pay coming soon)");',
          '    } else {',
          '      alert("❌ " + (data.error || "Bet failed"));',
          '    }',
          '  } catch (e) {',
          '    alert("❌ Network error: " + e.message);',
          '  }',
          '}',
          '</script>',
        ].join("\n");
        return new Response(
          HTML_HEAD + `
  <header>
    <h1>⚡ Agent Arena</h1>
    <div class="subtitle">Agent Match Predictions</div>
    <div class="tagline">\"Friend, Foe, Builder, Destroyer, Helpful.\"</div>
  </header>
  <div style="text-align:center;padding:12px;background:#1a1a2e;border-radius:8px;margin-bottom:24px;border:1px solid #2a2a3a;">
    <p style="color:#f7c948;font-weight:600;">🎾 GenTech Smash — Doubles Tournament</p>
    <p style="color:#888;font-size:0.85em;">Human + AI team up against CPU. Predict the winner. Stake USDC.</p>
  </div>
  ${cards}
` + lobbyScript + HTML_FOOT,
          { headers: { "Content-Type": "text/html" } }
        );
      }

      return new Response("Not found", { status: 404 });
    } catch (err) {
      return jsonResponse({ error: err.message }, corsHeaders, 500);
    }
  },
};

function jsonResponse(data, headers, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { ...headers, "Content-Type": "application/json" },
  });
}
