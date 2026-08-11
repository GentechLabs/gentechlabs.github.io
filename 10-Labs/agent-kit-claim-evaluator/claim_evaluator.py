"""
AAE Claim Evaluator — Phase A (data-side verification rail)
===========================================================

Reads the Agent Kit's four proprietary data layers and returns a
"stack vs. crowd" divergence verdict for any market claim:

    regime      -> .clarity-mode-state.json   (YIELD / RANGE_BOUND / HOLD...)
    narrative   -> DeFi/rainbow/rotation-data.json (hottest / coldest sector)
    arb basis   -> .gta-arb-state.json        (perp-vs-spot basis bps)
    price trend -> CoinGecko 30d              (asset momentum)

Fuses each layer's directional read with the claim's direction into a
single verdict: AGREE / DIVERGE / CONFIRMED / CONTRADICT / UNKNOWN,
plus an action read (HOLD / ACCUM / DEFENSIVE / TRADE / NEUTRAL).

This productizes the proprietary agent-sentiment / divergence index
(the Layer-3 signal) into a built-in kit capability.

Design rules (from develop-and-verify AUDIT checklist):
  - Individual try/except per rail: one broken feed degrades to None,
    never blocks the other rails.
  - Input length bounds: over-long claim text is rejected before any
    regex work (ReDoS / resource guard).
  - No hardcoded secrets. No error-detail leakage (generic messages).
  - Verdict JSON surfaces the layer VALUES so the user sees the stack
    (the demo value), not just the answer.
"""

from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# ── Constants ───────────────────────────────────────────────────────────

MAX_CLAIM_LEN = 4096          # input bound guard (chars)
STALE_DAYS = 7                # feed older than this gets a confidence penalty

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

DEFAULT_FILES = {
    "regime": os.environ.get(
        "REGIME_STATE_FILE",
        "/root/.hermes/profiles/gentech/scripts/.clarity-mode-state.json"),
    "arb": os.environ.get(
        "ARB_STATE_FILE",
        "/root/.hermes/profiles/gentech/scripts/.gta-arb-state.json"),
    "rotation": "/root/repos/ProtoJay4789.github.io/DeFi/rainbow/rotation-data.json",
}

# Bullish signal words -> claim direction "bull"
_BULL_WORDS = re.compile(
    r"\b(bottom|pump|rally|breakout|accumulate|long\b|bull|upside|"
    r"going up|moon|bid|support holds|confirmed low|this is the low|"
    r"floor|buy the dip|capitulation|capped out)\b",
    re.IGNORECASE,
)
# Bearish signal words -> claim direction "bear"
_BEAR_WORDS = re.compile(
    r"\b(top\b|crash|crashing|dump|dumping|sell|short\b|bear|breakdown|"
    r"downside|going down|drop|resistance holds|death|"
    r"new low|distribution|bearish)\b",
    re.IGNORECASE,
)

# regime value -> directional read
_REGIME_DIR = {
    "BULL_TRENDING": "bull",
    "PRICE_DISCOVERY": "bull",
    "ACCUMULATION": "bull",
    "BEAR_TRENDING": "bear",
    "HIGH_VOLATILITY": "bear",
    "RANGE_BOUND": "neutral",
    "YIELD": "neutral",
    "HOLD": "neutral",
    "DEFENSIVE": "bear",
}
_REGIME_STRONG = {"BULL_TRENDING", "PRICE_DISCOVERY"}

# Action map from a (verdict, claim_dir) pair
_ACTION = {
    ("AGREE", "bull"): "HOLD",
    ("AGREE", "bear"): "DEFENSIVE",
    ("DIVERGE", "bull"): "HOLD",
    ("DIVERGE", "bear"): "DEFENSIVE",
    ("CONFIRMED", "bull"): "ACCUM",
    ("CONFIRMED", "bear"): "TRADE",
    ("CONTRADICT", "bull"): "DEFENSIVE",
    ("CONTRADICT", "bear"): "HOLD",
}


# ── Pure helpers ────────────────────────────────────────────────────────

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_claim_direction(claim: str) -> Optional[str]:
    """Keyword-scored claim direction: 'bull' / 'bear' / None (neutral)."""
    if not claim or not isinstance(claim, str):
        return None
    bull = len(_BULL_WORDS.findall(claim))
    bear = len(_BEAR_WORDS.findall(claim))
    if bull > bear:
        return "bull"
    if bear > bull:
        return "bear"
    return None


def _regime_direction(regime: Optional[dict]) -> Optional[str]:
    if not isinstance(regime, dict):
        return None
    raw = (regime.get("regime") or regime.get("mode") or "").upper()
    # Mode strings like "RISK-ON / GROWTH" / "DEFENSIVE / YIELD"
    if "RISK" in raw or "GROWTH" in raw:
        return "bull"
    if "DEFENSIVE" in raw:
        return "bear"
    return _REGIME_DIR.get(raw)


def _trend_direction(pct_change: Optional[float]) -> Optional[str]:
    """30d % change -> bull / bear / flat."""
    if pct_change is None:
        return None
    if pct_change >= 5.0:
        return "bull"
    if pct_change <= -5.0:
        return "bear"
    return "flat"


def _parse_narrative_coins(coins_str: str) -> List[str]:
    """'UNI ↑5%, AAVE ↑4%' -> ['UNI', 'AAVE', ...]."""
    if not coins_str:
        return []
    # tokens like UNI, AAVE (uppercase, 2-6 chars) at word boundaries
    return re.findall(r"\b([A-Z]{2,6})\b", coins_str)


def _narrative_direction(rotation: Optional[dict], asset: Optional[str]) -> Optional[str]:
    """Direction of the narrative zone containing `asset`, if any.

    Returns 'bull' (warm zone), 'bear' (cold zone), 'neutral' (asset not
    explicitly tracked), or None if the rotation feed is unavailable.
    """
    if not isinstance(rotation, dict) or not asset:
        return None
    asset = asset.upper()
    narratives = rotation.get("narratives") or []
    for n in narratives:
        coins = _parse_narrative_coins(n.get("coins", ""))
        if asset in coins:
            zone = (n.get("zone") or "").lower()
            score = n.get("sentiment_score")
            if zone == "warm" or (isinstance(score, (int, float)) and score > 0):
                return "bull"
            if zone == "cold" or (isinstance(score, (int, float)) and score < 0):
                return "bear"
            return "neutral"
    return "neutral"


def _dir_stance(claim_dir: Optional[str], layer_dir: Optional[str],
                strong: bool = False) -> Optional[str]:
    """Verdict from a claim direction vs. a layer direction."""
    if not claim_dir:
        return None
    if not layer_dir:
        return None
    if layer_dir == "flat" or layer_dir == "neutral":
        return "DIVERGE"  # conclusion ahead of data
    if claim_dir == layer_dir:
        return "CONFIRMED" if strong else "AGREE"
    return "CONTRADICT"


def _days_old(ts_iso: Optional[str]) -> Optional[float]:
    if not ts_iso:
        return None
    try:
        ts = datetime.fromisoformat(ts_iso.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - ts).total_seconds() / 86400.0
    except (ValueError, TypeError):
        return None


def _read_json(path: str) -> Optional[Any]:
    """Read+parse a JSON file; return None on any failure (no crash)."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


# ── Evaluator ───────────────────────────────────────────────────────────

class ClaimEvaluator:
    """Evaluates a market claim against the kit's four data layers."""

    def __init__(self, regime_file: Optional[str] = None,
                 arb_file: Optional[str] = None,
                 rotation_file: Optional[str] = None) -> None:
        self.regime_file = regime_file or DEFAULT_FILES["regime"]
        self.arb_file = arb_file or DEFAULT_FILES["arb"]
        self.rotation_file = rotation_file or DEFAULT_FILES["rotation"]

    # ── per-rail loaders (each isolated, returns None on failure) ──────

    def _load_regime(self) -> Optional[dict]:
        return _read_json(self.regime_file)

    def _load_rotation(self) -> Optional[dict]:
        return _read_json(self.rotation_file)

    def _load_arb(self) -> Optional[dict]:
        return _read_json(self.arb_file)

    # Claim symbols -> CoinGecko API ids (CG uses ids, not symbols)
    _COINGECKO_ID = {
        "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana",
        "AVAX": "avalanche-2", "LINK": "chainlink", "UNI": "uniswap",
        "AAVE": "aave", "MKR": "maker", "FET": "fetch-ai",
        "RENDER": "render-token", "TAO": "bittensor", "AKT": "akash-network",
        "ONDO": "ondo-finance", "DOGE": "dogecoin", "PEPE": "pepe",
        "NEAR": "near", "ARB": "arbitrum", "IMX": "immutable-x",
        "GALA": "gala", "WIF": "dogwifcoin", "BONK": "bonk",
    }
    _COINGECKO_ID_FALLBACK = "bitcoin"  # safe default for unmapped symbols

    def _load_price_trend(self, asset: Optional[str]) -> Optional[dict]:
        """30d price trend via CoinGecko. Returns {change_pct, price_30d_ago,
        price_now} or None on any failure."""
        if not asset:
            return None
        cg_id = self._COINGECKO_ID.get(asset.upper()) or self._COINGECKO_ID_FALLBACK
        try:
            import urllib.request
            url = (
                f"https://api.coingecko.com/api/v3/coins/{cg_id}/market_chart"
                f"?vs_currency=usd&days=30&interval=daily"
            )
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode())
            prices = data.get("prices") or []
            if len(prices) < 2:
                return None
            first = prices[0][1]
            last = prices[-1][1]
            change_pct = ((last - first) / first * 100.0) if first else 0.0
            return {
                "change_pct": round(change_pct, 2),
                "price_now": round(last, 4),
                "price_30d_ago": round(first, 4),
            }
        except Exception:
            return None

    # ── per-rail directional reads (isolated) ──────────────────────────

    def _read_regime_rail(self) -> Optional[dict]:
        data = self._load_regime()
        if not isinstance(data, dict):
            return None
        return {
            "raw": {
                "mode": data.get("mode"),
                "regime": data.get("regime"),
                "confidence": data.get("confidence"),
                "action": data.get("action"),
                "updated_at": data.get("updated_at"),
            },
            "direction": _regime_direction(data),
            "strong": (data.get("regime") or "").upper() in _REGIME_STRONG,
        }

    def _read_narrative_rail(self, asset: str) -> Optional[dict]:
        data = self._load_rotation()
        if not isinstance(data, dict):
            return None
        direction = _narrative_direction(data, asset)
        stale = False
        age = _days_old(data.get("lastUpdated"))
        if age is not None and age > STALE_DAYS:
            stale = True
        return {
            "raw": {
                "lastUpdated": data.get("lastUpdated"),
                "btc_7d": data.get("btc"),
            },
            "direction": direction,
            "stale": stale,
        }

    def _read_arb_rail(self, asset: str) -> Optional[dict]:
        data = self._load_arb()
        if not isinstance(data, dict):
            return None
        asset = (asset or "").upper()
        hottest = None
        hottest_bps = -1.0
        target = None
        for opp in data.get("opportunities") or []:
            sym = (opp.get("symbol") or "").upper()
            bps = float(opp.get("basis_bps") or 0.0)
            if bps > hottest_bps:
                hottest_bps, hottest = bps, sym
            if asset and sym == asset:
                target = bps
        return {
            "raw": {
                "last_scan": data.get("last_scan"),
                "hottest": {"symbol": hottest, "basis_bps": round(hottest_bps, 2)},
                "target_basis_bps": target,
            },
            # High positive basis on the target asset = mild bullish carry
            "direction": "bull" if (target is not None and target > 5.0) else "neutral",
        }

    def _read_price_rail(self, asset: str) -> Optional[dict]:
        data = self._load_price_trend(asset)
        if not data:
            return None
        return {
            "raw": data,
            "direction": _trend_direction(data.get("change_pct")),
        }

    # ── public API ─────────────────────────────────────────────────────

    def evaluate(self, claim: str, asset: Optional[str] = None,
                 feeds: Optional[dict] = None) -> dict:
        """Evaluate a claim against the kit's data layers.

        Args:
            claim: the market claim text (e.g. "crypto bottom is in").
            asset: optional asset symbol (e.g. "BTC") for price/narrative rails.
            feeds: optional override dict {regime, rotation, arb, price}. When
                   provided, these are used instead of loading from disk
                   (used by tests; leave None for live use).

        Returns:
            Verdict JSON: {verdict, action, confidence, claim_direction,
                           layers: {regime, narrative, arb, price_trend}, ...}
        """
        if not claim or not isinstance(claim, str):
            return self._empty("EMPTY", "NEUTRAL", 0.0,
                               "claim text required")
        if len(claim) > MAX_CLAIM_LEN:
            raise ValueError(
                f"claim too long ({len(claim)} chars, max {MAX_CLAIM_LEN})")

        claim_dir = _parse_claim_direction(claim)

        # Load each rail individually — one failure never blocks the others.
        if feeds is not None:
            regime_rail = self._read_regime_from_feed(feeds.get("regime"))
            narrative_rail = self._read_narrative_from_feed(feeds.get("rotation"), asset)
            arb_rail = self._read_arb_from_feed(feeds.get("arb"), asset)
            price_rail = self._read_price_from_feed(feeds.get("price"))
        else:
            regime_rail = self._read_regime_rail()
            narrative_rail = self._read_narrative_rail(asset)
            arb_rail = self._read_arb_rail(asset)
            price_rail = self._read_price_rail(asset)

        layer_dirs = {
            "regime": regime_rail["direction"] if regime_rail else None,
            "narrative": narrative_rail["direction"] if narrative_rail else None,
            "arb": arb_rail["direction"] if arb_rail else None,
            "price_trend": price_rail["direction"] if price_rail else None,
        }

        # Fuse: strongest signal wins, regime carries the most weight.
        strong_confirm = bool(regime_rail and regime_rail.get("strong"))
        # No data at all -> cannot render any verdict
        if all(d is None for d in layer_dirs.values()):
            verdict = "UNKNOWN"
        elif claim_dir is None:
            verdict = "UNKNOWN"
        elif layer_dirs["regime"] == "bull" or layer_dirs["regime"] == "bear":
            # Regime is decisive when it has a clear direction
            verdict = _dir_stance(claim_dir, layer_dirs["regime"], strong=strong_confirm)
        else:
            # No decisive regime: gather the other rails
            non_neutral = [d for k, d in layer_dirs.items()
                           if d in ("bull", "bear")]
            if not non_neutral:
                verdict = _dir_stance(claim_dir, "neutral")  # DIVERGE
            elif all(d == claim_dir for d in non_neutral):
                verdict = "CONFIRMED" if len(non_neutral) >= 2 else "AGREE"
            else:
                verdict = "DIVERGE"

        # Guard: when claim_dir is None the verdict is UNKNOWN and action is
        # NEUTRAL by construction (lookup misses the map).
        final_verdict = verdict or "UNKNOWN"
        final_claim_dir = claim_dir or "neutral"
        action = _ACTION.get((final_verdict, final_claim_dir), "NEUTRAL")

        # Confidence: base on regime confidence, penalize stale feeds.
        confidence = 0.5
        if regime_rail and isinstance(regime_rail["raw"].get("confidence"), (int, float)):
            confidence = float(regime_rail["raw"]["confidence"])
        if narrative_rail and narrative_rail.get("stale"):
            confidence *= 0.8

        return {
            "claim": claim,
            "asset": asset,
            "claim_direction": claim_dir,
            "verdict": verdict,
            "action": action,
            "confidence": round(confidence, 2),
            "layers": {
                "regime": regime_rail["raw"] if regime_rail else None,
                "narrative": {
                    "direction": narrative_rail["direction"],
                    "stale": narrative_rail.get("stale", False),
                    "lastUpdated": narrative_rail["raw"].get("lastUpdated")
                    if narrative_rail else None,
                } if narrative_rail else None,
                "arb": arb_rail["raw"] if arb_rail else None,
                "price_trend": price_rail["raw"] if price_rail else None,
            },
            "evaluated_at": _now_iso(),
        }

    # ── feed-override readers (tests / batch) ──────────────────────────

    def _read_regime_from_feed(self, data: Any) -> Optional[dict]:
        if not isinstance(data, dict):
            return None
        return {
            "raw": {
                "mode": data.get("mode"),
                "regime": data.get("regime"),
                "confidence": data.get("confidence"),
                "action": data.get("action"),
                "updated_at": data.get("updated_at"),
            },
            "direction": _regime_direction(data),
            "strong": (data.get("regime") or "").upper() in _REGIME_STRONG,
        }

    def _read_narrative_from_feed(self, data: Any, asset: Optional[str]) -> Optional[dict]:
        if not isinstance(data, dict):
            return None
        direction = _narrative_direction(data, asset)
        age = _days_old(data.get("lastUpdated"))
        stale = age is not None and age > STALE_DAYS
        return {
            "raw": {"lastUpdated": data.get("lastUpdated"), "btc_7d": data.get("btc")},
            "direction": direction,
            "stale": stale,
        }

    def _read_arb_from_feed(self, data: Any, asset: Optional[str]) -> Optional[dict]:
        if not isinstance(data, dict):
            return None
        asset = (asset or "").upper()
        hottest = None
        hottest_bps = -1.0
        target = None
        for opp in data.get("opportunities") or []:
            sym = (opp.get("symbol") or "").upper()
            bps = float(opp.get("basis_bps") or 0.0)
            if bps > hottest_bps:
                hottest_bps, hottest = bps, sym
            if asset and sym == asset:
                target = bps
        return {
            "raw": {
                "last_scan": data.get("last_scan"),
                "hottest": {"symbol": hottest, "basis_bps": round(hottest_bps, 2)},
                "target_basis_bps": target,
            },
            "direction": "bull" if (target is not None and target > 5.0) else "neutral",
        }

    def _read_price_from_feed(self, data: Any) -> Optional[dict]:
        if not isinstance(data, list) or len(data) < 2:
            return None
        try:
            first = data[0][1]
            last = data[-1][1]
            change_pct = ((last - first) / first * 100.0) if first else 0.0
        except (TypeError, IndexError):
            return None
        return {
            "raw": {
                "change_pct": round(change_pct, 2),
                "price_now": round(last, 4),
                "price_30d_ago": round(first, 4),
            },
            "direction": _trend_direction(change_pct),
        }

    @staticmethod
    def _empty(verdict: str, action: str, confidence: float,
               reason: str) -> dict:
        return {
            "verdict": verdict,
            "action": action,
            "confidence": confidence,
            "claim_direction": None,
            "layers": {"regime": None, "narrative": None, "arb": None,
                       "price_trend": None},
            "reason": reason,
            "evaluated_at": _now_iso(),
        }


# ── CLI ────────────────────────────────────────────────────────────────

def main() -> None:
    import sys as _sys
    args = _sys.argv[1:]
    claim = args[0] if args else "crypto bottom is in"
    asset = args[1] if len(args) > 1 else "BTC"
    ev = ClaimEvaluator()
    result = ev.evaluate(claim, asset)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
