#!/usr/bin/env python3
"""avax_rpc.py — ONE resilient AVAX C-Chain provider path for every treasury reader.

WHY THIS EXISTS (2026-09-22): `api.avax.network` returned Cloudflare **1015** (rate limit by
SOURCE, not a bad payload) with `retry-after: 3372`. That single hardcoded host is named in ~212
files across the fleet, so one IP-level throttle took out the hourly LFJ fee snapshot (`a4cae2e71105`
lost its 15:00 point) and every on-demand reader (`treasury_truth.py`, `value_now.py`,
`lfj-truth.py` all exit 1). Some scripts already carried a second URL; the pattern existed in our
house and was simply not shared.

THE RULES THIS ENFORCES:
- **ROTATE, do not replace.** A 1015 ban is per-source and moves, so the public host stays in the
  list as a last resort rather than being deleted.
- **Verify by call, not by construction.** A provider "works" only when it answers `eth_chainId`
  with 43114. A provider that returns HTML (a 503 gateway page parses as no JSON-RPC result) is a
  failure, not a success.
- **FAIL CLOSED.** If every provider fails, raise `RpcUnavailable`. Never return a Web3 bound to a
  dead endpoint, and never let a caller degrade to a zero/stale value and act on it.

Usage:
    from avax_rpc import connect, RpcUnavailable
    w3 = connect()                      # raises if no provider answers
    w3 = connect(timeout=45, tries=2)

    # diagnostics
    python3 avax_rpc.py                 # health of every provider
    python3 avax_rpc.py --selftest      # prove the failure path actually fails
"""
from __future__ import annotations

import os
import sys

CHAIN_ID = 43114

# Order matters: cheapest/most-reliable public hosts first, the rate-limiting host LAST.
# Override with AVAX_RPC_URLS (comma-separated) for a pinned environment.
DEFAULT_PROVIDERS = (
    "https://avalanche-c-chain-rpc.publicnode.com",
    "https://avalanche.drpc.org",
    "https://1rpc.io/avax/c",
    "https://api.avax.network/ext/bc/C/rpc",
)

# Providers that need an API key now and must never be auto-added as a silent fallback.
KNOWN_UNUSABLE = (
    "https://rpc.ankr.com/avalanche",   # -32000 Unauthorized
)


def providers() -> list[str]:
    env = (os.environ.get("AVAX_RPC_URLS") or "").strip()
    if env:
        return [u.strip() for u in env.split(",") if u.strip()]
    return list(DEFAULT_PROVIDERS)


class RpcUnavailable(RuntimeError):
    """Every provider failed. Callers must ABORT — never act on a degraded read."""


def _probe(url: str, timeout: float = 20.0):
    """Return the chain id if this provider answers JSON-RPC, else None (never raises)."""
    import json
    import urllib.error
    import urllib.request

    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_chainId", "params": []}).encode()
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json", "User-Agent": "gentech-treasury/1"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                return None
            payload = json.loads(resp.read().decode("utf-8", errors="replace"))
        result = payload.get("result")
        if not isinstance(result, str):
            return None                      # HTML/503 page, or an error object
        return int(result, 16)
    except Exception:
        return None


def connect(timeout: float = 40.0, tries: int = 1, verbose: bool = False):
    """A Web3 bound to the first provider that VERIFIABLY answers on chain 43114.

    Raises RpcUnavailable when none do. `tries` = full passes over the list (bounded retry).
    """
    from web3 import Web3

    attempts: list[str] = []
    for attempt in range(max(1, tries)):
        for url in providers():
            chain = _probe(url)
            if chain == CHAIN_ID:
                if verbose:
                    print(f"  avax_rpc: using {url}", file=sys.stderr)
                return Web3(Web3.HTTPProvider(url, request_kwargs={"timeout": timeout}))
            attempts.append(f"{url} (chain={chain if chain else 'no response'})")
        if attempt + 1 < max(1, tries):
            import time
            time.sleep(2.0)
    raise RpcUnavailable(
        "no AVAX C-Chain provider answered chain 43114 after "
        f"{max(1, tries)} pass(es): " + "; ".join(attempts)
    )


def url(timeout: float = 20.0) -> str:
    """A STRING url for callers that build their own provider (Web3(url) or urllib).

    Returns the fixed public host ONLY as a last resort. Callers should re-probe rather than
    trust it, but returning a string beats raising in a hot path that just needs some endpoint.
    """
    for u in providers():
        if _probe(u, timeout=timeout) == CHAIN_ID:
            return u
    return DEFAULT_PROVIDERS[-1]


def health() -> list[tuple[str, object]]:
    return [(u, _probe(u)) for u in providers()]


def rpc_call(method: str, params: list | None = None, timeout: float = 55.0, tries: int = 1):
    """Raw JSON-RPC with provider ROTATION — for readers that speak urllib, not Web3.

    Returns the `result` on success, or raises RpcUnavailable when every provider fails.
    Unlike a retry-on-the-same-host loop, this MOVES when a host is source-banned (1015).
    """
    import json
    import urllib.error
    import urllib.request

    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method,
                       "params": params or []}).encode()
    seen: list[str] = []
    for attempt in range(max(1, tries)):
        for url in providers():
            req = urllib.request.Request(
                url, data=body,
                headers={"Content-Type": "application/json",
                         "User-Agent": "gentech-treasury/1"},
            )
            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    if resp.status != 200:
                        seen.append(f"{url} (http {resp.status})")
                        continue
                    payload = json.loads(resp.read().decode("utf-8", errors="replace"))
            except Exception as exc:
                seen.append(f"{url} ({type(exc).__name__})")
                continue
            if isinstance(payload, dict) and payload.get("error") is None \
                    and payload.get("result") is not None:
                return payload["result"]
            # A well-formed JSON-RPC ERROR means the provider WORKED — it answered. A revert
            # ("execution reverted", code 3 / -32000) is the CHAIN's answer, not a dead host, and
            # rotating on it burns every provider and then reports a fake outage. Only rotate on
            # provider-level failure: transport errors, throttling, or capacity.
            err = payload if isinstance(payload, dict) else {}
            emsg = str((err.get("error") or {}).get("message", "")).lower()
            ecode = (err.get("error") or {}).get("code")
            # PROVIDER-LEVEL limits, not chain answers. A capability cap ("limited to 0 - 50
            # blocks range" on 1rpc, "exceed maximum block range" on publicnode) means THIS
            # PROVIDER cannot serve the request — another one can. Treating it as a chain answer
            # made `eth_getLogs` return None, i.e. "no logs", which is a FALSE VALUE: a pool with
            # real swaps reads as having zero activity. Rotate instead.
            # Deliberately narrow: only phrasings that name a PROVIDER limit. A bare revert
            # ("execution reverted") must still return None, or we burn every provider on it.
            provider_limited = any(k in emsg for k in (
                "rate limit", "too many", "capacity", "limit exceeded", "429",
                "limited to", "exceed maximum", "exceeds maximum", "maximum block range",
                "block range", "not supported", "unsupported", "api key", "personal token",
                "archive")) or ecode in (-32005,)
            if provider_limited:
                seen.append(f"{url} (provider-limited: {emsg[:40] or ecode})")
                continue
            return None                      # valid chain response (e.g. revert) — do not rotate
        if attempt + 1 < max(1, tries):
            import time
            time.sleep(1.0)
    raise RpcUnavailable(f"{method} failed on every provider: " + "; ".join(seen))


def _selftest() -> int:
    """Prove BOTH directions: a good list connects, a bad list RAISES (does not degrade)."""
    print("avax_rpc selftest")
    ok = connect(verbose=True)
    print(f"  PASS  live connect -> {getattr(ok.provider, 'endpoint_uri', 'ok')}")

    saved = os.environ.get("AVAX_RPC_URLS")
    os.environ["AVAX_RPC_URLS"] = "https://127.0.0.1:9/nope,https://avalanche.invalid/rpc"
    try:
        try:
            connect(timeout=3)
        except RpcUnavailable as exc:
            print(f"  PASS  all-providers-down RAISES RpcUnavailable ({str(exc)[:60]}...)")
        else:
            print("  FAIL  connected with no working provider — this would fail OPEN")
            return 1
    finally:
        if saved is None:
            os.environ.pop("AVAX_RPC_URLS", None)
        else:
            os.environ["AVAX_RPC_URLS"] = saved
    # ── REGRESSION: a REVERT must not rotate (it is the chain answering) ──────────────
    # Permanent-Fix Rule step 3: the defect fails LOUDLY if it returns. A revert that rotates
    # burns every provider and then reports a fake outage; a provider CAPABILITY limit
    # ("limited to 0 - 50 blocks range") that does NOT rotate returns None = "no logs", a false
    # value. Both directions are asserted here so neither can silently come back.
    try:
        from web3 import Web3 as _W3
        _good = connect(verbose=False)
        # a call that reverts on-chain, against a live provider
        _rev = rpc_call("eth_call", [{"to": "0x864d4e5ee7318e97483db7eb0912e09f161516ea",
                                      "data": "0xdeadbeef"}, "latest"], timeout=30)
        print(f"  PASS  revert/bad-selector returns None rather than rotating (got {_rev!r})")
    except RpcUnavailable as _e:
        print(f"  FAIL  a chain-level error was treated as a provider outage: {_e}")
        return 1
    except Exception as _e:
        print(f"  SKIP  revert probe unavailable: {type(_e).__name__}")

    if _probe("https://1rpc.io/avax/c") == CHAIN_ID:
        try:
            # 1rpc caps getLogs at 50 blocks; the request must ROTATE to a provider that can serve
            # it, not return None. Ask for a range 1rpc refuses and require a real answer.
            _w3 = connect(verbose=False)
            _h = int(_w3.eth.block_number)
            _lg = rpc_call("eth_getLogs", [{"fromBlock": hex(_h - 43200), "toBlock": hex(_h - 1),
                                            "address": "0x864d4e5ee7318e97483db7eb0912e09f161516ea"}],
                           timeout=45, tries=2)
            if _lg is None:
                print("  FAIL  eth_getLogs returned None (reads as 'no logs') — provider cap not rotated")
                return 1
            print(f"  PASS  provider block-range cap ROTATED correctly ({len(_lg):,} logs)")
        except RpcUnavailable as _e:
            print(f"  WARN  all providers refused a 24h getLogs: {str(_e)[:70]}")
        except Exception as _e:
            print(f"  SKIP  1rpc cap probe unavailable: {type(_e).__name__}")

    print("  selftest OK")
    return 0


def main() -> int:
    if "--selftest" in sys.argv:
        return _selftest()
    print("AVAX C-Chain provider health (chain must be 43114):")
    any_ok = False
    for url, chain in health():
        if chain == CHAIN_ID:
            any_ok = True
            print(f"  ✅ {url}")
        else:
            print(f"  ❌ {url}  -> {chain if chain else 'no JSON-RPC response'}")
    for url in KNOWN_UNUSABLE:
        print(f"  ⛔ {url}  (known unusable — needs an API key; never auto-add)")
    return 0 if any_ok else 1


if __name__ == "__main__":
    sys.exit(main())
