#!/usr/bin/env python3
"""Yield Farm Report — one view across every rail we'd actually farm.

Jordan (Sep 15 2026): "we can compare the different pools — the SOL/USDC pool
versus the AVAX pool we've been in, or the TAO pool we thought about, or the
LINK pool. We can have these different comparisons going on. This is almost like
a yield farm — it really is like a yield farm report. We can make it its own thing."

So this is its own thing: ONE report that ranks candidate venues on the numbers
that decide where capital goes.

THE DISCIPLINE IT ENFORCES
  1. FEE CORE vs EMISSIONS SPLIT — always both, never a blended headline.
     Emissions are not durable; fees are. A venue that is 100% emissions is a
     different animal from one that is 100% fees, even at the same headline.
  2. CAPITAL-TO-GOAL — "how much do I need deployed to make $X/day?" answered
     on the FEE CORE, so the answer doesn't evaporate when a farm ends.
  3. DATA-QUALITY FLAGS — DefiLlama reports apyBase=0 for Blackhole CLMM, which
     is a reporting GAP, not a real zero. Flagged, never silently trusted.

HONEST LIMITS
  - DefiLlama APRs are venue-reported aggregates. Where we can measure on-chain
    (our own rail) the chain number wins and is labelled.
  - Reward APRs are quoted in USD at today's token price — they move with price.
    That sensitivity is real and is discussed in Jordan's price note below.
"""
import json
import os
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone

OUT_JSON = "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/agentic-treasury-report.json"
BLOOM = "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/black-health.json"
# A black-health read older than this is refused rather than reported as live
# (the clarity-mode defect: structurally valid, semantically dead).
BLACK_HEALTH_MAX_AGE_H = 12.0

# Curated candidates: (label, chain, project, symbol-substring)
CANDIDATES = [
    ("AVAX/USDC — ours (Blackhole)", "Avalanche", "blackhole-clmm", "WAVAX-USDC"),
    ("AVAX/USDC — Pharaoh v3",       "Avalanche", "pharaoh-v3",     "WAVAX-USDC"),
    ("AVAX/USDC — LFJ (old rail)",   "Avalanche", "joe-v2.2",       "WAVAX-USDC"),
    ("AVAX/USDC — UniV3",            "Avalanche", "uniswap-v3",     "WAVAX-USDC"),
    ("SOL/USDC — Orca",              "Solana",    "orca-dex",       "SOL-USDC"),
    ("SOL/USDC — Raydium",           "Solana",    "raydium-amm",    "SOL-USDC"),
    ("TAO/USDC — UniV3 (ETH)",       "Ethereum",  "uniswap-v3",     "WTAO-USDC"),
    ("TAO/USDC — Aerodrome (Base)",  "Base",      "aerodrome-slipstream", "TAO"),
    ("LINK/WETH — UniV3 (ETH)",      "Ethereum",  "uniswap-v3",     "LINK-WETH"),
    ("LINK/ETH — UniV4 (ETH)",       "Ethereum",  "uniswap-v4",     "ETH-LINK"),
]

GOALS = [5.0, 200.0]   # $/day targets to size for


def _own_pool_id(_unused=None):
    """Resolve OUR Blackhole CLMM pool id from the live pools list (never hardcode)."""
    d = get("https://yields.llama.fi/pools")
    hits = [p for p in d.get("data", [])
            if (p.get("project") or "").lower() == "blackhole-clmm"
            and p.get("chain") == "Avalanche"
            and "WAVAX-USDC" in (p.get("symbol") or "").upper()]
    if not hits:
        raise RuntimeError("own pool id not found")
    return max(hits, key=lambda x: x.get("tvlUsd") or 0)["pool"]


# ── Rank ladder — ported from LP Monitor v2 (Jordan, Sep 15 2026) ───────────
# Jordan: "the LP monitor was how I wanted the yield-farm crown job to look...
# not only the pools information, but the goals and the milestone information and
# the percentage of how long it's going to take."
# The ladder itself (rank-ladder.json) is a PORT of the LP monitor's milestones,
# so retiring that job loses no mechanism. Tiers are DAILY FEE-USD targets.
LADDER_PATH = "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/rank-ladder.json"


def load_ladder():
    try:
        with open(LADDER_PATH) as f:
            return json.load(f)
    except Exception:
        return None


def per_tenant_deployed(paths=None):
    """{tenant: deployed_usd} from the shared treasury state, or {} when it carries no split.

    WHY THIS EXISTS (Jordan, 2026-09-28): with two collaborators on one treasury, a single combined
    "deployed capital" figure describes neither of them. `treasury-state.json` already computes the
    split (`capital.lfj_per_tenant`) when it reads the chain — this just surfaces it instead of
    throwing it away and printing only the sum.

    Returns {} rather than a fabricated even split: if the state does not know, we do not guess.
    """
    for p in (paths or ("/root/.hermes/profiles/gentech-treasury/scripts/treasury-state.json",
                        "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/treasury-state.json")):
        try:
            with open(p) as f:
                d = json.load(f)
        except Exception:
            continue
        cap = d.get("capital") or {}
        for key in ("lfj_per_tenant", "per_tenant", "deployed_per_tenant"):
            v = cap.get(key)
            if isinstance(v, dict) and v:
                out = {}
                for k, x in v.items():
                    try:
                        out[str(k)] = float(x)
                    except (TypeError, ValueError):
                        continue
                if out:
                    return out
    return {}


def rank_block(deployed_usd, fee_apr_pct, ladder):
    """Current rank + next milestone + ETA. Returns None if we can't size it."""
    if not ladder or not deployed_usd or deployed_usd <= 0 or not fee_apr_pct:
        return None
    daily = deployed_usd * (fee_apr_pct / 100.0) / 365.0
    t0 = ladder.get("tier0") or {"tier": 0, "label": "Grunt", "daily_fees": 5.0}
    ms = ladder.get("milestones", [])
    cur, nxt = t0, (ms[0] if ms else None)
    for m in ms:
        if daily >= m["daily_fees"]:
            cur = m
        elif nxt is None or m["daily_fees"] < nxt["daily_fees"]:
            nxt = m
    # find the true next = lowest milestone above current daily
    above = [m for m in ms if m["daily_fees"] > daily]
    nxt = above[0] if above else None
    pct = (daily / nxt["daily_fees"] * 100.0) if nxt else 100.0
    # ETA: capital is what we scale, not time — so express it as capital required,
    # and give the days-to-target IF capital were topped up to the requirement now.
    cap_needed = (nxt["daily_fees"] * 365.0 / (fee_apr_pct / 100.0)) if nxt else None
    gap = (cap_needed - deployed_usd) if cap_needed else None
    return {
        "deployed_usd": round(deployed_usd, 2),
        "daily_fee_usd": round(daily, 4),
        "current_tier": cur["tier"], "current_label": cur["label"],
        "current_target_usd_day": cur["daily_fees"],
        "next_tier": nxt["tier"] if nxt else None,
        "next_label": nxt["label"] if nxt else "MAX",
        "next_target_usd_day": nxt["daily_fees"] if nxt else None,
        "progress_pct": round(pct, 1),
        "capital_needed_for_next": round(cap_needed, 0) if cap_needed else None,
        "capital_gap": round(gap, 0) if gap is not None else None,
        "fee_apr_used": fee_apr_pct,
        "basis": "daily fee income = deployed_usd x fee_apr / 365 (fee core only)",
    }


def _deployed_usd(paths=None):
    """Read DEPLOYED capital from treasury state; refuse to guess.

    2026-09-27 FIX — a failed read was wearing the costume of a FLAT TREASURY. This
    looked for a TOP-LEVEL "deployed_usd"/"deployed" key. The state schema moved the
    number under `capital` and turned the top-level `deployed` into a LIST of
    positions, so the reader matched NOTHING and returned None on every run. main()
    renders None as "$0.00 — TREASURY IS FLAT", so a book with real capital in the
    pool would ALSO have printed FLAT — and worse, every per-rail rank line would have
    read 0%, because rank_block() is fed this same value. A flat treasury and an
    unreadable treasury must never be the same output.
    Read the CURRENT schema first (`capital.deployed_usd`, carrying its measured_at
    stamp so a stale file is visibly stale), then the legacy top-level keys.
    """
    for p in (paths or ("/root/.hermes/profiles/gentech-treasury/scripts/treasury-state.json",
                        "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/treasury-state.json")):
        try:
            with open(p) as f:
                d = json.load(f)
            cap = d.get("capital")
            if isinstance(cap, dict):
                v = cap.get("deployed_usd")
                if isinstance(v, (int, float)):
                    stamp = cap.get("measured_at") or "unstamped"
                    return float(v), f"{p} (capital.deployed_usd, measured {stamp})"
            for k in ("deployed_usd", "deployed"):
                if isinstance(d.get(k), (int, float)):
                    return float(d[k]), f"{p} (legacy top-level {k})"
        except Exception:
            continue
    return None, None


# ── TRADING layer (Jordan, Sep 16 2026) ─────────────────────────────────────
# "we should also add trading to that. We can call it the agentic treasury report."
#
# The trading legs are capital-gated: while the treasury is flat the arb scanner
# and executor are paused, so their state files go STALE. A stale basis is not a
# live basis — the same rule as a reverted eth_call read as zero. Every trading
# input is therefore reported WITH ITS AGE and refused past the gate.
#
# The buy list is NOT gated, so its prices/bands are live and are the anchor here.

ARB_STATE_CANDIDATES = [
    "/root/.hermes/profiles/gentech-treasury/scripts/.gta-arb-state.json",
    "/root/.hermes/scripts/.gta-arb-state.json",
]
BUYLIST_STATE = "/root/.hermes/scripts/.steward-buylist-state.json"
ARB_MAX_AGE_H = 6.0     # matches the executor's truth gate
BUYLIST_MAX_AGE_H = 12.0


def _age_hours(ts):
    """Age in hours from EITHER an ISO-8601 string OR a POSIX epoch stamp (s or ms).

    2026-09-27 FIX — TWO STACKED DEFECTS, one symptom. black-health.json stamps its
    "ts" as an EPOCH FLOAT (1789918206.46). This function called
    datetime.fromisoformat(str(ts)) unconditionally, which RAISES on an epoch, so the
    age came back None. It then fell to the refusal branch — which formatted the
    MISSING age with `{age_h:.1f}` and crashed with "unsupported format string passed
    to NoneType.__format__". The report showed that Python error to Jordan as if it
    were the state of the world:
        BLACK health source   black-health.json unreadable: unsupported format string...
    An age-parse failure had been silently masking a WORKING chain read. Any
    unparseable stamp now returns None (UNKNOWN, i.e. refuse) and the refusal path
    prints "unknown" rather than raising.
    """
    if ts is None:
        return None
    try:
        if isinstance(ts, (int, float)):
            secs = float(ts)
            if abs(secs) > 1e11:          # epoch MILLISECONDS
                secs /= 1000.0
            t = datetime.fromtimestamp(secs, tz=timezone.utc)
        else:
            s = str(ts).strip()
            try:
                t = datetime.fromisoformat(s.replace("Z", "+00:00"))
            except ValueError:
                secs = float(s)
                if abs(secs) > 1e11:
                    secs /= 1000.0
                t = datetime.fromtimestamp(secs, tz=timezone.utc)
            if t.tzinfo is None:
                t = t.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - t).total_seconds() / 3600.0
    except Exception:
        return None


def refresh_black_health(timeout_s: int = 240):
    """RUN the black-health producer instead of hoping someone else did.

    Jordan retired the daily Re-Entry Watch cron (Sep 16 2026: "fold it into the Sunday
    meeting / the yield report"). black_health.py was that job's producer, so this
    reader would have gone on reading a file nobody regenerated — structurally valid,
    semantically dead. Rather than re-schedule a job to feed one reader, the reader now
    produces its own input. Returns (ok, error_message).
    """
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "black_health.py")
    if not os.path.exists(script):
        return False, f"producer not found: {script}"
    try:
        r = subprocess.run([sys.executable, script], capture_output=True, text=True,
                           timeout=timeout_s)
        if r.returncode != 0:
            return False, f"exit {r.returncode}: {(r.stderr or '')[:120]}"
        return True, None
    except Exception as e:                                          # noqa: BLE001
        return False, f"{type(e).__name__}: {e}"


def trading_block():
    """Arb basis (age-gated) + buy-list value bands + accumulation state."""
    out = {"arb": None, "buylist": None, "notes": []}

    # --- rail basis / arb ---
    for p in ARB_STATE_CANDIDATES:
        try:
            with open(p) as f:
                d = json.load(f)
            age = _age_hours(d.get("last_scan"))
            opps = d.get("opportunities") or []
            out["arb"] = {
                "source": p, "last_scan": d.get("last_scan"),
                "age_hours": round(age, 1) if age is not None else None,
                "stale": (age is None or age > ARB_MAX_AGE_H),
                "max_age_h": ARB_MAX_AGE_H,
                "opportunities": opps,
            }
            break
        except Exception:
            continue
    if out["arb"] is None:
        out["notes"].append("no arb state file found")

    # --- buy list bands + prices (not capital-gated, so usually live) ---
    try:
        with open(BUYLIST_STATE) as f:
            b = json.load(f)
        # state has last_prices; ts lives on the farm_vs_trade sub-record
        ts = (b.get("farm_vs_trade") or {}).get("ts")
        prices = b.get("last_prices") or {}
        out["buylist"] = {
            "prices": {k: (v or {}).get("price") for k, v in prices.items()},
            "coins_tracked": len(prices),
            "last_state_ts": ts,
            "n_prices": len(prices),
        }
    except Exception as e:
        out["notes"].append(f"buy-list state unreadable: {e}")

    return out


def fee_income_at_size(deploy_usd=500.0):
    """Rank venues by FEE DOLLARS AT OUR SIZE — Jordan's actual objective.

    Jordan (Sep 16 2026): "I care more about earning more in fees than I do
    liquidity, because that's kind of where I want to be — where we're earning
    the most."

    He is right that fee RATE is the return and depth is only a constraint. But
    "fee APR" is a rate, not income, and a high printed APR can be three different
    things — only one of which is money we can actually collect:

      1. REAL AND SUSTAINED  -> the fee flow is organic and repeatable.
      2. A DECAYING SPIKE    -> a one-off volume event annualised. Raydium LINK-USDC
                                printed 76,677% then 3,546% then 1,681% then 1,150%
                                on consecutive days. Annualising a spike manufactures
                                a number nobody can earn.
      3. A WASH/ARTIFACT     -> turnover far above organic. Some LINK pools on Solana
                                showed $0 TVL with multi-BILLION percent APRs.

    So we gate on turnover (a wash signature) and on 7d-vs-24h decay (a spike
    signature), then report FEE DOLLARS AT OUR SIZE, not the headline rate.

    Income model is honest about our own impact: our share of the fee flow is
    D/(TVL+D), because we cannot earn the advertised rate on the liquidity we
    ourselves add.
    """
    TURNOVER_WASH = 10.0    # >10x TVL/day is not organic trading
    DECAY_RATIO = 0.25      # 24h APR below 25% of 7d APR => the flow is collapsing
    MIN_TVL = 50_000.0
    STABLES = {"USDC", "USDT", "DAI", "MIM", "FRAX"}
    WANT = ["AVAX", "SOL", "LINK", "TAO", "ETH", "BTC"]

    try:
        rows = get("https://yields.llama.fi/pools").get("data", [])
    except Exception as e:
        return {"error": f"venue fetch failed: {e}"}

    def norm(s):
        s = (s or "").upper()
        for a, b in (("WAVAX", "AVAX"), ("WSOL", "SOL"), ("LINK.E", "LINK"),
                     ("USDC.E", "USDC"), ("WETH", "ETH"), ("WTAO", "TAO")):
            s = s.replace(a, b)
        return s

    out = []
    for p in rows:
        sym = norm(p.get("symbol"))
        parts = [x.strip() for x in sym.replace("/", "-").split("-") if x.strip()]
        if len(parts) != 2 or not any(x in STABLES for x in parts):
            continue
        coin = [x for x in parts if x not in STABLES]
        if not coin or coin[0] not in WANT:
            continue
        tvl = p.get("tvlUsd") or 0
        apy = p.get("apyBase") or 0
        vol = p.get("volumeUsd1d") or 0
        if tvl < MIN_TVL or apy <= 0:
            continue
        turnover = (vol / tvl) if tvl else 0.0

        # ── THE SPIKE GATE (learned the hard way, Sep 16 2026) ──────────────
        # A 7d-average decay test FAILS to catch a single-day spike, because the
        # spike contaminates the 7d average too. Measured case: uniswap-v2
        # WETH-USDC on Base printed 468.60% while its 30-day mean was 13.38% and
        # its prior eight days read 14.6 / 10.2 / 16.1 / 3.3 / 2.7 / 6.5 / 14.4.
        # 468/74.5 (the 7d) = 6.3, so it PASSED the old gate at full size.
        # Fix: compare the live print against apyMean30d and honour the pool's own
        # outlier flag and sigma. Then rank on the DURABLE rate, not the spike.
        mean30 = p.get("apyMean30d")
        sigma = p.get("sigma")
        is_outlier = bool(p.get("outlier"))
        spike = bool(mean30 and apy > max(3.0 * mean30, mean30 + 50.0))
        durable_rate = min(apy, mean30) if mean30 else apy

        flags = []
        if turnover > TURNOVER_WASH:
            flags.append(f"turnover {turnover:.1f}x = wash signature")
        if spike:
            flags.append(f"SPIKE: {apy:.0f}% today vs {mean30:.1f}% 30d mean "
                         f"({apy/max(mean30,0.01):.1f}x) — annualised one-day event")
        if is_outlier:
            flags.append(f"DefiLlama flags this pool as an outlier (sigma {sigma})")
        if sigma and sigma > 3.0:
            flags.append(f"APY volatility sigma {sigma} — unstable")
        if apy > 1000:
            flags.append(f"{apy:.0f}% APR is implausibly high for a durable pool")

        share = deploy_usd / (tvl + deploy_usd)
        fees_day = tvl * (durable_rate / 100.0 / 365.0) * share
        out.append({
            "coin": coin[0], "chain": p.get("chain"), "project": p.get("project"),
            "symbol": p.get("symbol"), "tvl_usd": round(tvl),
            "fee_apr_pct": round(apy, 2),
            "apy_mean_30d_pct": round(mean30, 2) if mean30 else None,
            "durable_rate_pct": round(durable_rate, 2),
            "spike_x": round(apy / mean30, 1) if mean30 else None,
            "sigma": sigma,
            "volume_usd_1d": round(vol),
            "turnover_x": round(turnover, 2),
            "our_share_pct": round(share * 100, 4),
            "fees_per_day_usd": round(fees_day, 4),
            "flags": flags,
            "durable": not flags,
        })
    out.sort(key=lambda x: -x["fees_per_day_usd"])
    return {"deploy_usd": deploy_usd,
            "gates": {"turnover_wash": TURNOVER_WASH, "decay_ratio": DECAY_RATIO,
                      "min_tvl": MIN_TVL},
            "ranked": out}


def accumulation_rails():
    """For each coin we want to ACCUMULATE, find the best LIVE LP venue.

    Jordan's principle (Sep 16 2026): "the only reason I thought about using the
    LINK pool on Blackhole is because not only could we earn some type of fees, but
    we're still using it to accumulate more as dips happen. Kind of the best of both
    worlds — we didn't have to just trade and let it sit."

    That mental model is CORRECT: in an LP, as the volatile asset falls the pool
    sells the other leg to buy it back, so you end up holding MORE of it. Fees are
    the bonus; the accumulation is the point.

    Two hard limits the report must show, because they decide whether the trade works:
      1. It only happens INSIDE your range. Below the floor you are 100% the volatile
         asset and earning NOTHING.
      2. The fee rate has to be big enough to pay for the range management and the
         impermanent loss. At ~120% it clearly is. At ~8% the LP barely beats simply
         dollar-cost-averaging the coin.
    So we show the BEST LIVE venue per coin WITH its fee APR and TVL — and flag when
    the best available venue is too small to be real.
    """
    MIN_REAL_TVL = 50_000.0   # below this a pool is dust, not a market
    STABLES = {"USDC", "USDT", "DAI", "USDC.E", "USDt", "MIM", "FRAX"}
    # A "fee APR" in the thousands on a thin memecoin pair is a TURNOVER ARTIFACT,
    # not a farmable yield — WSOL-DOGE printed 3966% on $73K. Cap what we will quote
    # as a headline and flag anything above it for on-chain verification.
    SUSPECT_APR = 1000.0
    TARGETS = ["AVAX", "LINK", "SOL", "TAO", "COQ"]
    try:
        d = get("https://yields.llama.fi/pools")
        rows = d.get("data", [])
    except Exception as e:
        return {"error": f"venue fetch failed: {e}"}

    def stable_symbol(sym):
        """Strip protocol quirks so WAVAX/WSOL/LINK.e match AVAX/SOL/LINK."""
        s = (sym or "").upper()
        s = s.replace("WAVAX", "AVAX").replace("WSOL", "SOL")
        s = s.replace("LINK.E", "LINK").replace("USDC.E", "USDC")
        s = s.replace("WETH", "ETH").replace("WTAO", "TAO")
        return s

    out = {}
    for tgt in TARGETS:
        cands = []
        for p in rows:
            sym = stable_symbol(p.get("symbol"))
            parts = [x.strip() for x in sym.replace("/", "-").split("-") if x.strip()]
            if tgt not in parts:
                continue
            other = [x for x in parts if x != tgt]
            # Only count pairs where the OTHER leg is a stable. That is the
            # configuration that actually accumulates the coin from cash — a
            # coin/memecoin pair accumulates a memecoin, not the coin.
            if not other or not any(o in STABLES for o in other):
                continue
            tvl = p.get("tvlUsd") or 0
            base = p.get("apyBase")
            if not base or tvl <= 0:
                continue
            cands.append({
                "chain": p.get("chain"), "project": p.get("project"),
                "symbol": p.get("symbol"), "tvl_usd": round(tvl),
                "fee_apr_pct": round(base, 2),
                "total_apr_pct": round(p.get("apy") or 0, 2),
                "suspect_apr": base > SUSPECT_APR,
                "pool": p.get("pool"),
            })
        real = [c for c in cands if c["tvl_usd"] >= MIN_REAL_TVL]
        # prefer the highest fee APR that is not a turnover artifact
        sane = [c for c in real if not c["suspect_apr"]]
        best = (sane or real or None)
        best = max(best, key=lambda x: x["fee_apr_pct"]) if best else None

        # ── CROSS-RAIL BREAKDOWN (Jordan, Sep 16 2026) ──────────────────────
        # "I didn't even know you could get LINK on Solana. Just like TAO is on
        # Solana. So certain coins — we've got to see what rail they have the most
        # liquidity on."
        #
        # The rail is a FIRST-CLASS choice, not a detail. The same coin can pay
        # 207% on one chain and 8% on another, and the deepest pool is often not
        # where we already are. So show, per coin, the liquidity leader AND the
        # APR leader — and say out loud when they are different chains.
        by_chain = {}
        for c in real:
            ch = c["chain"] or "?"
            e = by_chain.setdefault(ch, {"chain": ch, "tvl_usd": 0, "best_apr": None,
                                         "best_symbol": None, "project": None,
                                         "venues": 0})
            e["tvl_usd"] += c["tvl_usd"]
            e["venues"] += 1
            if e["best_apr"] is None or c["fee_apr_pct"] > e["best_apr"]:
                e["best_apr"] = c["fee_apr_pct"]
                e["best_symbol"] = c["symbol"]
                e["project"] = c["project"]
        chains = sorted(by_chain.values(), key=lambda x: -x["tvl_usd"])
        liq_leader = chains[0] if chains else None
        apr_leader = max(chains, key=lambda x: x["best_apr"] or 0) if chains else None
        split = bool(liq_leader and apr_leader and liq_leader["chain"] != apr_leader["chain"])

        out[tgt] = {
            "best_real": best,
            "real_count": len(real),
            "all_count": len(cands),
            "chains": chains[:4],
            "liquidity_leader": liq_leader,
            "apr_leader": apr_leader,
            "split_decision": split,
            "verdict": ("no live stable-paired venue above the dust floor — accumulate "
                        "by direct DCA, not by LP"
                        if not real else
                        "LP is viable: fees on a live pool plus automatic dip accumulation"),
        }
    return {"min_real_tvl": MIN_REAL_TVL, "suspect_apr": SUSPECT_APR, "targets": out}


def price_sensitivity():
    """Jordan's insight, measured: (Sep 15 2026)

    'if I wanted to make five dollars a day, I would need more money if the price
     is higher — but as the price gets lower that goal becomes even easier.'

    WHY HE IS RIGHT (mechanism, verified on 196 days of history):
      - corr(AVAX price, pool TVL) is strongly POSITIVE (~+0.83): when AVAX falls,
        the WAVAX half of the pool is worth less, so TVL shrinks.
      - corr(AVAX price, emissions APR) is NEGATIVE (~-0.43): the BLACK emission
        rate is FIXED per second, so when TVL shrinks the same BLACK lands on less
        capital -> the reward APR RISES.
      => a lower AVAX price mechanically raises the emissions APR, so a fixed
         $/day goal needs LESS capital. His intuition is correct.

    WHAT IT DOES *NOT* DO:
      - The FEE core does NOT rise with a lower price. Fees track VOLUME, not
        price level. So fee-core sizing is roughly price-independent.
      - This is a MEASURED RELATIONSHIP over one history, not a law. It is a
        reason to prefer the emissions layer when price is low — never a promise.
    """
    try:
        import statistics as st
        px = get("https://coins.llama.fi/chart/avax:0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
                 "?span=196&period=1d")
        series = px["coins"]["avax:0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"]["prices"]
        prices = {datetime.utcfromtimestamp(int(p["timestamp"])).strftime("%Y-%m-%d"): p["price"]
                  for p in series}
        hist = get("https://yields.llama.fi/chart/%s" % _own_pool_id(px))
        pts = hist.get("data", [])
    except Exception:
        return None
    if not pts:
        return None
    rows = []
    for p in pts:
        d = p["timestamp"][:10]
        if d in prices and p.get("apyReward"):
            rows.append((prices[d], p.get("tvlUsd") or 0, p["apyReward"]))
    if len(rows) < 20:
        return None

    def corr(a, b):
        ma, mb = st.mean(a), st.mean(b)
        num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
        den = (sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b)) ** 0.5
        return num / den if den else None

    pr = [r[0] for r in rows]
    tv = [r[1] for r in rows]
    ar = [r[2] for r in rows]

    # simple linear fit: emissions APR vs price
    n = len(rows)
    mp, ma_ = st.mean(pr), st.mean(ar)
    denom = sum((x - mp) ** 2 for x in pr)
    slope = sum((x - mp) * (y - ma_) for x, y in zip(pr, ar)) / denom if denom else 0
    intercept = ma_ - slope * mp

    def apr_at(price):
        return max(0.0, slope * price + intercept)

    return {
        "days": n,
        "corr_price_tvl": round(corr(pr, tv), 3) if corr(pr, tv) else None,
        "corr_price_emissions_apr": round(corr(pr, ar), 3) if corr(pr, ar) else None,
        "price_range": [round(min(pr), 2), round(max(pr), 2)],
        "emissions_apr_at_price": {str(p): round(apr_at(p), 1)
                                   for p in (5.50, 6.00, 7.30, 8.50, 10.00)},
        "note": ("Measured over %d days. Lower price -> smaller TVL -> same fixed "
                 "BLACK emission over less capital -> higher reward APR. The FEE "
                 "core does not behave this way; it tracks volume." % n),
    }




# ── CHAIN-FEE CACHE READER (Agentic Treasury Makeover, 2026-09-19) ──────────
# chain-fee-rank.py measures pools straight from Swap events but takes minutes (24 log windows per
# pool), far too slow to run inline here. So it caches its result and this reads it: measure once,
# read many.
#
# WITH A STALENESS GUARD and a VOLATILITY WARNING, because both are real and measured:
#   - a cached number with no timestamp is indistinguishable from a fresh one (the regime lesson);
#   - and the numbers genuinely MOVE between runs. Measured 2026-09-19, one hour apart, same pools,
#     same method: WETH.e-WAVAX 126.46% -> 179.72%, WAVAX-USDC 77.77% -> 135.22%, LFJ 7.85% -> 16.95%.
#     A 40-70% swing on an hourly re-measure means the absolute APR is NOT deployable. The report says
#     so rather than printing a confident number that a second run would contradict.
# The cache is GENERATED data, so it is NOT in the scripts sync manifest — the profile copy of this
# report would therefore never find it sitting next to itself. Look in the vault too, so the report
# reads the same measurement whether it runs from the vault or from the executed copy.
_HERE = os.path.dirname(os.path.abspath(__file__))
CHAIN_CACHE_CANDIDATES = [
    os.path.join(_HERE, "chain-fee-measurements.json"),
    "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/chain-fee-measurements.json",
]
CHAIN_CACHE = next((p for p in CHAIN_CACHE_CANDIDATES if os.path.exists(p)), CHAIN_CACHE_CANDIDATES[0])
CHAIN_MAX_AGE_H = 12.0

# report venue label -> (chain pair, chain venue, chain tier) as chain-fee-rank.py names them
CHAIN_MAP = {
    "AVAX/USDC — LFJ (old rail)": ("WAVAX-USDC", "lfj", "bs10"),
    "AVAX/USDC — UniV3":          ("WAVAX-USDC", "univ3", "0.05%"),
    "AVAX/USDC — Pharaoh v3":     None,      # not measured on-chain yet
    "WAVAX/USDC — LFJ binStep 10": ("WAVAX-USDC", "lfj", "bs10"),
}


def load_chain_measurements():
    """Return (by_key, note). by_key maps (pair, venue, tier) -> measurement dict."""
    if not os.path.exists(CHAIN_CACHE):
        return {}, "no chain-measurement cache — run chain-fee-rank.py"
    try:
        with open(CHAIN_CACHE) as f:
            d = json.load(f)
    except Exception as e:
        return {}, f"cache unreadable ({type(e).__name__})"
    ts = d.get("measured_at")
    if not ts:
        return {}, "cache carries NO TIMESTAMP — refusing it (an undated reading is not a fresh one)"
    try:
        age_h = (datetime.now(timezone.utc)
                 - datetime.fromisoformat(ts.replace("Z", "+00:00"))).total_seconds() / 3600.0
    except Exception:
        return {}, "cache timestamp unparseable — refusing it"
    if age_h > CHAIN_MAX_AGE_H:
        return {}, f"cache is STALE ({age_h:.1f}h old, limit {CHAIN_MAX_AGE_H:.0f}h) — refusing it"
    by = {}
    for p in d.get("pools", []):
        by[(p.get("pair"), p.get("venue"), p.get("tier"))] = p
    return by, f"chain-measured {age_h:.1f}h ago ({len(by)} pools)"

def get(url, timeout=180):
    req = urllib.request.Request(url, headers={"User-Agent": "GenTech-Steward/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def capital_for(goal_usd_day, apr_pct):
    """Capital needed to earn goal_usd_day at apr_pct (on a 365-day year)."""
    if not apr_pct or apr_pct <= 0:
        return None
    return goal_usd_day * 365.0 / (apr_pct / 100.0)


def main():
    d = get("https://yields.llama.fi/pools")
    pools = d.get("data", [])
    by_chain = {}
    for p in pools:
        by_chain.setdefault((p.get("chain"), (p.get("project") or "").lower()), []).append(p)

    # chain-measured truth for our own rail (wins over venue-reported)
    #
    # STALE-PRODUCER GUARD (Jordan, Sep 16 2026). This reader used to depend on
    # black-health.json being refreshed by a DAILY cron job. When Jordan retired that
    # job ("fold it into the Sunday meeting / the yield report"), this reader would
    # have gone on silently reading a file whose producer no longer ran — the exact
    # clarity-mode defect: structurally valid, semantically dead. A reader must not
    # depend on a producer that is not scheduled, so the report now PRODUCES the
    # input itself and refuses it if that fails.
    own, own_note = None, None
    produced, perr = refresh_black_health()
    if produced:
        own_note = "black_health produced fresh by this run"
    else:
        own_note = (f"black_health could NOT be produced this run ({perr}) — "
                    f"falling back to the on-disk value WITH an age check")
    try:
        bh = json.load(open(BLOOM))
        age_h = _age_hours(bh.get("ts"))
        if produced or (age_h is not None and age_h <= BLACK_HEALTH_MAX_AGE_H):
            own = {"fee_apr_pct": bh["yield_split"]["fee_apr_pct"],
                   "emissions_apr_pct": bh["yield_split"]["emissions_apr_pct"],
                   "tvl_usd": bh["pool"]["tvl_usd"],
                   "when": bh.get("when")}
            own["age_hours"] = round(age_h, 2) if age_h is not None else None
        else:
            age_txt = f"{age_h:.1f}h old" if age_h is not None else "of UNKNOWN age"
            own_note = (f"REFUSED: on-disk black-health is {age_txt} "
                        f"(gate {BLACK_HEALTH_MAX_AGE_H:.0f}h) and could not be "
                        f"regenerated — reporting NO chain-measured figure rather "
                        f"than a stale one")
    except Exception as e:
        own_note = f"black-health.json unreadable: {e}"

    rows = []
    for label, chain, project, symfrag in CANDIDATES:
        cands = by_chain.get((chain, project.lower()), [])
        hits = [p for p in cands if symfrag.upper() in (p.get("symbol") or "").upper()]
        if not hits:
            rows.append({"label": label, "chain": chain, "project": project,
                         "status": "not_found"})
            continue
        p = max(hits, key=lambda x: x.get("tvlUsd") or 0)
        base = p.get("apyBase")
        rew = p.get("apyReward") or 0
        tvl = p.get("tvlUsd") or 0
        flags = []
        if (base in (0, None)) and rew > 0:
            flags.append("apyBase=0 — reporting GAP, not a real zero (measure on-chain)")
        split = None
        if base is not None and (base + rew) > 0:
            split = round(rew / (base + rew) * 100, 1)
        rows.append({
            "label": label, "chain": chain, "project": p.get("project"),
            "symbol": p.get("symbol"), "tvl_usd": round(tvl, 0),
            "fee_apr_pct": base, "emissions_apr_pct": rew,
            "headline_apr_pct": p.get("apy"),
            "emissions_share_pct": split,
            "capital_for_goal": {f"${int(g)}/day": (round(capital_for(g, base), 0)
                                                   if base else None) for g in GOALS},
            "flags": flags, "status": "ok",
        })

    # override our rail with the chain-measured read
    for r in rows:
        if "Blackhole" in r["label"] and own:
            r["fee_apr_pct"] = own["fee_apr_pct"]
            r["emissions_apr_pct"] = own["emissions_apr_pct"]
            r["tvl_usd"] = round(own["tvl_usd"], 0)
            tot = own["fee_apr_pct"] + own["emissions_apr_pct"]
            r["emissions_share_pct"] = round(own["emissions_apr_pct"] / tot * 100, 1)
            r["capital_for_goal"] = {f"${int(g)}/day": round(capital_for(g, own["fee_apr_pct"]), 0)
                                     for g in GOALS}
            # DefiLlama books the whole Blackhole pool as REWARD (apyBase=0), so its
            # headline `apy` is 1124.5% — an artifact, NOT our headline. Recompute it
            # from the honest split after the override so no reader can quote it as ours.
            r["headline_apr_pct"] = round(own["fee_apr_pct"] + own["emissions_apr_pct"], 2)
            r["headline_basis"] = "fee + emissions (recomputed from split, not DefiLlama apy)"
            r["flags"] = ["fee APR is CHAIN-MEASURED (DefiLlama reports apyBase=0)",
                          "DefiLlama headline apy ignored — it books fees as reward; ours = fee + emissions"]
            r["source"] = "chain + defillama"

    ps = price_sensitivity()
    tb = trading_block()
    acc = accumulation_rails()
    feei = fee_income_at_size(500.0)
    ladder = load_ladder()
    deployed, dsrc = _deployed_usd()
    own_fee = own["fee_apr_pct"] if own else None
    ranks = {}
    for r in rows:
        if r["status"] != "ok":
            continue
        rb = rank_block(deployed, r["fee_apr_pct"], ladder)
        if rb:
            ranks[r["label"]] = rb
    out = {"when": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
           "ts": time.time(), "goals": GOALS, "venues": rows,
           "own_rail_measured": own, "price_sensitivity": ps,
           "rank_ladder": {
               "deployed_usd": deployed, "deployed_source": dsrc,
               "per_venue": ranks,
               "ladder_source": ladder.get("source") if ladder else None,
               "note": ("Rank tiers are DAILY FEE-USD targets. Progress moves by "
                        "CAPITAL and by fee APR, not by waiting. When flat, daily "
                        "fee income is $0 and every tier reads 0% — that is the "
                        "honest reading, not a failure."),
           },
           "trading": tb, "accumulation_rails": acc, "fee_income_at_size": feei}
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=2)

    # ── MOBILE / TELEGRAM LAYOUT (Jordan, 2026-09-19: "let's give this treatment to our overall
    # agentic treasury so everything looks good on mobile or on telegram")
    # Before: a 100+ line wall, a label on every row, inconsistent section rules, and a STALE TITLE
    # ("YIELD FARM REPORT" long after this became the three-layer agentic report). Now: ruled section
    # headers, one fact per line, values aligned so the eye can scan a column, and the long
    # explanation trimmed to the decision.
    _RULE = "━" * 29

    def hdr(emoji: str, text: str) -> None:
        print(_RULE)
        print(f"{emoji}  {text}")
        print(_RULE)
        print()

    hdr("🌾", "AGENTIC TREASURY REPORT")
    print(f"   {out['when']}")
    print()

    hdr("💵", "CAPITAL TO TARGET")
    for g in GOALS:
        print(f"   **${int(g)}/day**")
        for r in rows:
            if r["status"] != "ok":
                continue
            c = r["capital_for_goal"].get(f"${int(g)}/day")
            if c is None:
                continue
            print(f"   {r['label']:<32} ${c:>10,.0f}")
        print()

    hdr("🔍", "VENUE DETAIL")
    # ── SOURCE TIER ON EVERY ROW (doctrine: "name the source of any number driving a decision").
    # Where a venue has a chain measurement, BOTH numbers are printed and the gap flagged — not the
    # aggregator quietly replaced by the chain. The two disagree by wide margins in both directions
    # (measured 2026-09-19: LFJ aggregator $476,586 @ 33.711% vs chain $723,806 @ 16.95%; UniV3
    # $3,814,921 @ 27.940% vs chain $1,177,045 @ 135.22%), and showing one alone would hide which
    # one a decision is resting on.
    _chain, _chain_note = load_chain_measurements()
    print(f"   chain measurements: {_chain_note}")
    print()
    for r in rows:
        if r["status"] != "ok":
            print(f"   ✗ {r['label']} — NOT FOUND")
            print()
            continue
        fl = r["flags"][0] if r["flags"] else ""
        chain_measured = "CHAIN-MEASURED" in fl
        print(f"   **{r['label']}**")
        print(f"   AGGREGATOR  TVL ${r['tvl_usd']:>10,.0f}   fee {str(r['fee_apr_pct'])[:6]}%   "
              f"emis {str(r['emissions_apr_pct'])[:7]}%")
        key = CHAIN_MAP.get(r["label"])
        cm = _chain.get(key) if key else None
        if cm:
            gap = abs(cm["fee_apr_pct"] - (r["fee_apr_pct"] or 0))
            print(f"   CHAIN       TVL ${cm['tvl_usd']:>10,.0f}   fee {cm['fee_apr_pct']:>6.2f}%   "
                  f"{cm['swaps_24h']:,} swaps/24h")
            if gap > 5:
                print(f"   ⚠️  they disagree by {gap:.1f} pts on the fee rate — "
                      f"{'chain' if cm['fee_apr_pct'] > (r['fee_apr_pct'] or 0) else 'aggregator'} is higher")
        elif chain_measured:
            print("   CHAIN       ✓ this row IS the chain-measured figure")
        elif key:
            print("   CHAIN       not measured this cycle")
        print(f"   source: {'CHAIN' if chain_measured else 'AGGREGATOR'}")
        if fl:
            print(f"   ⚠️  {fl}")
        print()
    # Name the instability rather than hiding it. Two runs an hour apart, same pools, same method,
    # differed by 40-70% on the fee rate. That is a finding about the MEASUREMENT, and it belongs in
    # the report because it is the reason the chain APR is not yet deployable.
    if _chain:
        print("   ⚠️  CHAIN MEASUREMENTS ARE VOLATILE. Two runs one hour apart, same pools and same")
        print("      method, differed by 40–70% on the fee rate (WETH.e-WAVAX 126.46% → 179.72%,")
        print("      WAVAX-USDC 77.77% → 135.22%, LFJ 7.85% → 16.95%). Treat these as DIRECTION, not")
        print("      as a rate you can size on. Source of the instability is unresolved — the public")
        print("      Avalanche RPC truncating eth_getLogs is the prime suspect.")
        print()

    if ps:
        hdr("📉", "PRICE SENSITIVITY")
        print(f"   over {ps['days']} days")
        ct = ps['corr_price_tvl']
        ce = ps['corr_price_emissions_apr']
        print(f"   corr(price, TVL)             {ct:+.3f}" if ct is not None else
              "   corr(price, TVL)             n/a")
        print(f"   corr(price, emissions APR)   {ce:+.3f}" if ce is not None else
              "   corr(price, emissions APR)   n/a")
        print()
        # 2026-09-27 FIX — THIS LINE USED TO BE HARDCODED. It printed
        #   "Lower price = higher reward APR (fixed emission over smaller TVL)."
        # unconditionally, directly ABOVE a fitted table that -- with today's data --
        # showed the OPPOSITE direction, and beside a corr of +0.039 (i.e. no
        # detectable relationship at all). A stated mechanism asserted regardless of
        # what the measurement says is the same defect as a failed read printed as a
        # zero: the prose was the only confidently-wrong number on the page. The claim
        # is now GATED ON THE MEASURED SIGN and the fit is labelled AS a fit.
        print("   modeled from a linear fit to this window (not a law):")
        for p, v in ps["emissions_apr_at_price"].items():
            print(f"   AVAX ${p:<6} → emissions {v}%")
        print()
        if ce is None:
            print("   corr not measurable this run — no claim about direction made.")
        elif ce <= -0.15:
            print("   MECHANISM VISIBLE: corr(price, emissions APR) is negative, as the")
            print("   fixed-emission-over-smaller-TVL mechanism predicts — a lower price")
            print("   raises the REWARD APR, so a fixed $/day goal needs less capital.")
        elif ce >= 0.15:
            print(f"   ⚠️  MECHANISM NOT VISIBLE — corr is {ce:+.3f} (POSITIVE), the opposite")
            print("   of what fixed emission over shrinking TVL predicts for this window.")
            print("   Do NOT size on 'a lower price raises the APR' from this reading.")
        else:
            print(f"   ⚠️  NO DETECTABLE RELATIONSHIP this window (corr {ce:+.3f} ≈ 0).")
            print("   The modeled row above is an artifact of fitting a line to noise —")
            print("   treat the direction as UNKNOWN rather than as a rule.")
        print("   The FEE core is different in kind: it tracks VOLUME, not price level,")
        print("   so fee-core sizing is roughly price-independent either way.")
        print()
    hdr("🪜", "RANK & MILESTONES")
    if deployed is None:
        # 2026-09-27: an UNREADABLE treasury is NOT a flat one. Both used to print
        # "$0.00 — TREASURY IS FLAT", so a broken reader looked like a fact about the
        # book. Say which one it is.
        print("   Deployed capital  ⚠️ UNREADABLE — no treasury-state figure this run")
        print("   Daily fee income  unknown (cannot compute from a missing balance)")
        print()
        print("   Reporting NO deployment figure rather than an implied $0.00.")
        print(f"   Below: what each rail ranks at on a ${25:.0f} reference deploy.")
        print()
    elif deployed <= 0:
        print("   Deployed capital  $0.00 — **TREASURY IS FLAT**")
        print(f"   Source            {dsrc}")
        print("   Daily fee income  $0.00")
        print()
        print("   Progress moves by deploying capital and by fee APR — not by waiting.")
        print(f"   Below: what each rail ranks at on a ${25:.0f} reference deploy.")
        print()
    else:
        # ── EACH BOOK, NOT JUST THE TOTAL (Jordan, 2026-09-28) ───────────────────────────────────
        # `treasury-state.json` carries a COMBINED deployed figure with a per-tenant split inside it
        # (`capital.lfj_per_tenant`). Reporting only the total made one person's capital look like
        # the scale the whole ladder was measured against — and with two collaborators now, "the
        # treasury has $193.91" is not a fact about either of them. Show the split whenever the
        # state provides one; say so plainly when it does not.
        _split = per_tenant_deployed()
        if _split:
            _who = "   ".join(f"{k} ${v:,.2f}" for k, v in sorted(_split.items()))
            print(f"   Deployed capital  ${deployed:,.2f}  (ACROSS {len(_split)} BOOKS)")
            print(f"   Per book          {_who}")
        else:
            print(f"   Deployed capital  ${deployed:,.2f}")
        print(f"   Source            {dsrc}")
        # PERCENT, NOT FRACTION: `own_fee` is an APR in percent (e.g. 176.2), so the /100 is not
        # optional. The first version of this line omitted it and reported $93.62/day on $193.91 —
        # an implied 17,623% APR. `rank_block()` below does `fee_apr_pct / 100.0`; this must match it
        # or the same book gets two different daily figures in one report.
        if own_fee:
            print(f"   Daily fee income  ${deployed * (own_fee / 100.0) / 365.0:,.4f}/day"
                  f"  (at the measured {own_fee:.1f}% fee core, COMBINED)")
        else:
            print("   Daily fee income  unknown (no measured fee core this run)")
        print()

        # ── EACH BOOK GETS ITS OWN LADDER (Jordan, 2026-09-28) ────────────────────────────────────
        # Jordan: "yes we need to separate. we have the same goals but are at different paces."
        # The ladder and milestones are SHARED — same goals, correctly, so both books are measured
        # against the same definition of progress. What differs is the PACE, and a combined tier
        # hides it: $193.91 reaches a tier that neither $146.68 nor $47.23 reaches alone, so a
        # combined line flatters the smaller book and says nothing about either one's actual rung.
        # Same ladder, evaluated per book, from each book's OWN deployed capital.
        if _split and own_fee:
            print("   ── PER BOOK (same milestones, each at its own pace) ──")
            for _name, _cap in sorted(_split.items(), key=lambda kv: -kv[1]):
                _rb = rank_block(_cap, own_fee, ladder)
                if not _rb:
                    continue
                print(f"   {_name:<9} ${_cap:>8,.2f}  →  ${_rb['daily_fee_usd']:,.4f}/day"
                      f"   Tier {_rb['current_tier']} {_rb['current_label']}"
                      f" → {_rb['next_label']} [{_rb['progress_pct']:.1f}%]")
                if _rb.get("capital_gap") is not None:
                    print(f"   {'':<9} {'':>8}     next rung needs "
                          f"${_rb['capital_needed_for_next']:,.0f} deployed "
                          f"(+${_rb['capital_gap']:,.0f} from here)")
            print()
        print("   Progress moves by deploying capital and by fee APR — not by waiting.")
        print(f"   Below: what each rail ranks at on a ${25:.0f} reference deploy.")
        print()
    probe_cap = deployed if (deployed and deployed > 0) else 25.0
    shown = 0
    for r in rows:
        if r["status"] != "ok" or not r["fee_apr_pct"]:
            continue
        rb = rank_block(probe_cap, r["fee_apr_pct"], ladder)
        if not rb:
            continue
        tag = "★ " if "Blackhole" in r["label"] else "  "
        print(f"   {tag}{r['label']:<30} ${rb['daily_fee_usd']:>7.3f}/day")
        print(f"     Tier {rb['current_tier']} {rb['current_label']} → {rb['next_label']} "
              f"[{rb['progress_pct']:.1f}%]   needs ${rb['capital_gap']:,.0f}")
        print()
        shown += 1
        if shown >= 6:
            break

    # ── TRADING LAYER ───────────────────────────────────────────────────────
    hdr("📈", "TRADING")
    arb = tb.get("arb")
    if arb is None:
        print("   Rail basis   NO SOURCE — arb state file not found.")
    elif arb["stale"]:
        print(f"   Rail basis   ⚠️ STALE — last scan {arb['age_hours']}h ago "
              f"(gate {arb['max_age_h']:.0f}h). NOT live.")
        print()
        print("   The arb legs are capital-gated, so they are paused while the treasury is flat.")
        print("   A stale basis is not a live basis — refusing it rather than printing")
        print("   yesterday's spread as today's opportunity.")
    else:
        print(f"   Rail basis ({arb['age_hours']}h old, LIVE)")
        for o in (arb["opportunities"] or [])[:5]:
            print(f"   {o.get('symbol'):<6} {o.get('basis_bps'):+.2f} bps "
                  f"(perp {o.get('perp')} / spot {o.get('spot')})")
    print()
    bl = tb.get("buylist")
    if bl:
        print(f"   Buy list — {bl['coins_tracked']} coins priced (live, not capital-gated)")
        print()
        for s in ("BTC", "AVAX", "SOL", "LINK", "TAO", "COQ"):
            v = (bl["prices"] or {}).get(s)
            if v:
                shown_px = f"${v:,.2f}" if v >= 1 else f"${v:.4e}"
                print(f"   {s:<6} {shown_px}")
    for n in (tb.get("notes") or []):
        print(f"   ⚠️  {n}")
    print()

    hdr("🔄", "RE-ENTRY READ")
    print(f"   BLACK health source   {own_note}")
    if own:
        print(f"   Our rail   fee {own.get('fee_apr_pct')}% + emissions {own.get('emissions_apr_pct')}%")
        print(f"   TVL        ${own.get('tvl_usd', 0):,.0f}"
              + (f"   ·  read {own['age_hours']}h old" if own.get("age_hours") is not None else ""))
        em = own.get("emissions_apr_pct") or 0
        fe = own.get("fee_apr_pct") or 0
        if (fe + em) > 0:
            print()
            print(f"   Emissions are {em / (fe + em) * 100:.0f}% of the headline and they are")
            print(f"   staking-dependent. The durable half is the fee core: {fe}%.")
    else:
        print("   ⚠️  No chain-measured figure this run — refusing to print a stale one.")
    print()
    print("   The question this answers: should we re-enter at all?")
    print("   If not, waiting buys tokens — never yield. A cheaper entry does not raise the fee rate.")
    print()

    # ── FEE INCOME AT OUR SIZE ─────────────────────────────────────────────
    hdr("💲", "FEE INCOME AT OUR SIZE")
    fd = feei.get("deploy_usd", 500.0)
    g = feei.get("gates", {})
    print(f"   Ranked by fee DOLLARS/DAY on a ${fd:,.0f} deploy — not by headline APR.")
    print(f"   Gates: turnover > {g.get('turnover_wash')}x = wash · print >3x its own 30d mean =")
    print("   annualised spike · plus DefiLlama's outlier flag and sigma. Income uses the DURABLE rate.")
    print()
    ranked = feei.get("ranked") or []
    clean = [r for r in ranked if r["durable"]]
    dirty = [r for r in ranked if not r["durable"]]
    if clean:
        print(f"   ✅ DURABLE — {len(clean)} of {len(ranked)}, no artifact flags")
        print()
        for r in clean[:6]:
            print(f"   {r['coin']} · {r['chain']} · {(r['project'] + ' ' + r['symbol'])[:26]}")
            print(f"     ${r['fees_per_day_usd']:,.4f}/day   DURABLE {r['durable_rate_pct']:,.2f}%")
            print(f"     TVL ${r['tvl_usd']:,}   turnover {r['turnover_x']:,.2f}x")
            print()
    else:
        print("   ✅ DURABLE — none. Every venue in range carries an artifact flag.")
        print("   That is the finding, not a failure: the fee leaderboard is mostly noise.")
        print()
    if dirty:
        print(f"   ⚠️  FLAGGED — {len(dirty)}. What the raw leaderboard would have sold us:")
        print()
    for r in dirty[:6]:
        print(f"   {r['coin']} · {r['chain']} · {(r['project'] + ' ' + r['symbol'])[:26]}")
        print(f"     ${r['fees_per_day_usd']:,.4f}/day   print {r['fee_apr_pct']:,.2f}% → "
              f"DURABLE {r['durable_rate_pct']:,.2f}%")
        print(f"     TVL ${r['tvl_usd']:,}   turnover {r['turnover_x']:,.2f}x")
        for f in r["flags"]:
            print(f"     └─ {f}")
        print()
    if feei.get("error"):
        print(f"   ⚠️  {feei['error']}")
        print()

    hdr("🔁", "ACCUMULATION RAILS")
    print("   LP the coin you want MORE of. In an LP the pool buys the volatile leg as it")
    print("   dips, so you end up holding more of it. Fees are the bonus. It works only")
    print("   inside your range, and the fee rate must pay for range management + IL.")
    print()
    tg = (acc or {}).get("targets") or {}
    for coin in ("AVAX", "LINK", "SOL", "TAO", "COQ"):
        t = tg.get(coin)
        if not t:
            continue
        b = t.get("best_real")
        ch = t.get("chains") or []
        if not ch:
            print(f"     {coin:<5} ⚠ NO LIVE VENUE above the dust floor "
                  f"({t['all_count']} pools exist, all tiny) — DCA directly instead")
            continue
        if b:
            cap = (acc or {}).get("min_real_tvl", 0)
            flag = " ⚠ APR likely a turnover artifact — verify on-chain" if b.get("suspect_apr") else ""
            print(f"     {coin}  — best single venue: {b['project']} {b['symbol']} "
                  f"({b['chain']}) fee {b['fee_apr_pct']}%{flag}")
        else:
            print(f"     {coin}")
        for c in ch[:3]:
            star = "  <- deepest" if c is ch[0] else ""
            print(f"        {c['chain']:<12} TVL ${c['tvl_usd']:>11,}  "
                  f"best fee {c['best_apr']:>8.2f}%  ({c['project']} {c['best_symbol']}){star}")
        ll, al = t.get("liquidity_leader"), t.get("apr_leader")
        if ll and al:
            cap_apr = float((acc or {}).get("suspect_apr") or 1000.0)
            asus = (al.get("best_apr") or 0) > cap_apr
            warn = ("  ⚠ that APR exceeds the turnover-artifact threshold — verify "
                    "on-chain before trusting it") if asus else ""
            if t.get("split_decision"):
                print(f"        ⚠ SPLIT: liquidity lives on {ll['chain']}, but the best fee "
                      f"APR is on {al['chain']} ({al['best_apr']:.2f}%). Different rails — choose deliberately.")
                if warn:
                    print(f"        {warn.strip()}")
            else:
                print(f"        ✅ deepest AND best-paying both on {ll['chain']}")
    if (acc or {}).get("error"):
        print(f"   ⚠ {acc['error']}")
    print()
    print(f"   wrote {OUT_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
