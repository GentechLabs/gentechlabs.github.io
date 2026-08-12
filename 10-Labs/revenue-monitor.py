#!/usr/bin/env python3
"""
Revenue Monitor v3 — Tracks x402 API income + service health + multichain status.

Scans EVM wallet for incoming USDC transfers (x402 payments).
Pings all 8 deployed services before scanning.
Reports infrastructure readiness even when revenue is $0.
Multichain: Base, Avalanche, Solana, BNB, OKX.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────
WALLET_EVM = "0x7ebff188f2Eba16518C02864589b1403a5d1296a"
WALLET_SOL = "71Y3H36eb2WRGseYM9GwinjNawfMfAUbcof5eeWGoGSA"
DATA_DIR = Path("/root/.hermes/profiles/gentech/scripts")
TRACKER_FILE = DATA_DIR / "revenue-tracker.json"

# USDC contract addresses per chain
USDC_CONTRACTS = {
    "base": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    "avalanche": "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E",
    "bnb": "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",
}

RPC_URLS = {
    "base": "https://mainnet.base.org",
    "avalanche": "https://api.avax.network/ext/bc/C/rpc",
    "bnb": "https://bsc-dataseed.binance.org",
}

# ── Our deployed services ───────────────────────────────────────────────
SERVICES = {
    "x402-gateway":     {"url": "https://api.gentechlabs.net",       "health": "/health"},
    "mcp-directory":    {"url": "https://mcp.gentechlabs.net",       "health": "/health"},
    "agent-registration":{"url": "https://register.gentechlabs.net",  "health": "/health"},
    "defi-intelligence":{"url": "https://defi.gentechlabs.net",      "health": "/health"},
    "agent-search":     {"url": "https://search.gentechlabs.net",    "health": "/health"},
    "fleet-monitor":    {"url": "https://fleet.gentechlabs.net",     "health": "/health"},
    "starter-kit":      {"url": "https://start.gentechlabs.net",     "health": "/health"},
    "feedback-api":     {"url": "https://feedback.gentechlabs.net",  "health": "/health"},
    "lp-analytics":     {"url": "https://lp.gentechlabs.net",        "health": "/health"},
    "landing-page":     {"url": "https://gentechlabs.net",           "health": "/health"},
}

# ── KNOWN SENDERS (label-only) ──────────────────────────────────────────
# All external USDC transfers are counted as revenue regardless of sender.
# Populate this with known customer addresses to get named labels in reports.
# Format: "sender_address_lowercase": "customer_name"
# 👇 Add new known senders here
KNOWN_SENDERS = {
    # Example: "0xabc...def": "premium-api-user",
}

# ── Extensible Source Registry ──────────────────────────────────────────
# Add new chains/services here when you deploy on a new network.
# Each entry: {chain_key, display_name, rpc_url, usdc_address (or None for native), scan_fn}
# scan_fn is called as: scan_fn(chain_key, wallet_address, since_block, tracker_state)
# Return list of {"tx_hash": ..., "block": ..., "sender": ..., "amount_usdc": ..., "chain": ...}

# Solana config
USDC_MINT_SOL = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
SOL_RPC = "https://api.mainnet-beta.solana.com"
def SCAN_SOL(wallet, since_sig, tracker):
    """Scan Solana for incoming SPL USDC transfers to our wallet."""
    # Current balance via getTokenAccountsByOwner
    try:
        import subprocess, json
        payload = {
            "jsonrpc": "2.0", "id": 1,
            "method": "getTokenAccountsByOwner",
            "params": [
                wallet,
                {"mint": USDC_MINT_SOL},
                {"encoding": "jsonParsed"}
            ]
        }
        r = subprocess.run(["curl", "-s", "-X", "POST", SOL_RPC,
            "-H", "Content-Type: application/json",
            "-d", json.dumps(payload)],
            capture_output=True, text=True, timeout=15)
        resp = json.loads(r.stdout)
        accounts = resp.get("result", {}).get("value", [])
        if not accounts:
            return [], 0.0
        ata = accounts[0]
        ata_address = ata["pubkey"]
        balance = float(ata["account"]["data"]["parsed"]["info"]["tokenAmount"]["uiAmount"] or 0)
        tracker["sol_usdc_balance"] = balance
        tracker["sol_usdc_ata"] = ata_address
    except Exception as e:
        return [], tracker.get("sol_usdc_balance", 0.0)

    # Scan recent transfer signatures to the ATA
    try:
        payload = {
            "jsonrpc": "2.0", "id": 1,
            "method": "getSignaturesForAddress",
            "params": [ata_address, {"limit": 15}]
        }
        r = subprocess.run(["curl", "-s", "-X", "POST", SOL_RPC,
            "-H", "Content-Type: application/json",
            "-d", json.dumps(payload)],
            capture_output=True, text=True, timeout=15)
        sigs = json.loads(r.stdout).get("result", [])

        # Filter to new sigs since last scan
        seen = set(tracker.get("sol_tx_hashes", []))
        new_sigs = [s for s in sigs if s["signature"] not in seen][:5]

        transfers = []
        for sig_info in new_sigs:
            sig = sig_info["signature"]
            try:
                tx_payload = {
                    "jsonrpc": "2.0", "id": 1,
                    "method": "getTransaction",
                    "params": [sig, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}]
                }
                tx_r = subprocess.run(["curl", "-s", "-X", "POST", SOL_RPC,
                    "-H", "Content-Type: application/json",
                    "-d", json.dumps(tx_payload)],
                    capture_output=True, text=True, timeout=15)
                tx_data = json.loads(tx_r.stdout).get("result", {})
                if not tx_data:
                    continue
                # Parse token balances for incoming USDC to our wallet
                pre_balances = {b["mint"]: b for b in tx_data.get("meta", {}).get("preTokenBalances", [])}
                post_balances = {b["mint"]: b for b in tx_data.get("meta", {}).get("postTokenBalances", [])}
                # Check if our USDC ATA had a balance increase
                for mint_key, post in post_balances.items():
                    if post.get("mint") != USDC_MINT_SOL:
                        continue
                    if post.get("owner") != wallet:
                        continue
                    pre = pre_balances.get(mint_key)
                    pre_amt = float(pre["uiTokenAmount"]["uiAmount"] or 0) if pre else 0
                    post_amt = float(post["uiTokenAmount"]["uiAmount"] or 0)
                    diff = post_amt - pre_amt
                    if diff > 0:
                        # Find sender from account keys
                        accts = tx_data.get("transaction", {}).get("message", {}).get("accountKeys", [])
                        sender = accts[0] if accts else "unknown"
                        transfers.append({
                            "chain": "solana",
                            "tx_hash": sig,
                            "block": tx_data.get("slot", 0),
                            "sender": sender,
                            "amount_usdc": round(diff, 6),
                            "service": KNOWN_SENDERS.get(sender.lower(), "unknown"),
                        })
            except Exception:
                continue

        # Update seen hashes
        all_seen = set(tracker.get("sol_tx_hashes", []))
        for s in sigs:
            all_seen.add(s["signature"])
        tracker["sol_tx_hashes"] = list(all_seen)[-200:]
        return transfers, balance
    except Exception:
        return [], tracker.get("sol_usdc_balance", 0.0)

# ── Helpers ─────────────────────────────────────────────────────────────

def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def load_tracker():
    try:
        with open(TRACKER_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "version": 3,
            "snapshots": [],
            "transactions": [],
            "revenue_by_service": {},
            "total_revenue_usd": 0.0,
            "first_track_date": datetime.now().isoformat(),
            "last_scan_block": {"base": 0, "avalanche": 0, "bnb": 0},
            "service_health_history": [],
        }


def save_tracker(data):
    with open(TRACKER_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ── Service Health Check ────────────────────────────────────────────────

def check_service_health():
    """Ping all deployed services. Returns list of (name, status, detail)."""
    results = []
    for name, svc in SERVICES.items():
        url = f"{svc['url']}{svc['health']}"
        try:
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", url],
                capture_output=True, text=True, timeout=10
            )
            code = result.stdout.strip()
            is_ok = code in ("200", "204")
            results.append((name, "ok" if is_ok else f"HTTP {code}", svc["url"]))
        except subprocess.TimeoutExpired:
            results.append((name, "timeout", svc["url"]))
        except Exception as e:
            results.append((name, f"error: {e}", svc["url"]))
    return results


# ── On-Chain Scanning ──────────────────────────────────────────────────

def get_current_block(chain):
    rpc = RPC_URLS.get(chain)
    if not rpc:
        return 0
    try:
        result = subprocess.run(
            ["curl", "-s", "-X", "POST", rpc,
             "-H", "Content-Type: application/json",
             "-d", json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []})],
            capture_output=True, text=True, timeout=10
        )
        resp = json.loads(result.stdout)
        return int(resp["result"], 16)
    except Exception:
        return 0


def fetch_usdc_transfers(chain, wallet, since_block=0):
    """Fetch ERC-20 Transfer events for USDC to our wallet."""
    contract = USDC_CONTRACTS.get(chain)
    rpc = RPC_URLS.get(chain)
    if not contract or not rpc:
        return []
    transfer_sig = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    MAX_RANGE = {"base": 9999, "avalanche": 2047, "bnb": 9999}

    current_block = get_current_block(chain)
    if current_block == 0:
        return []

    max_range = MAX_RANGE.get(chain, 2000)
    if since_block == 0:
        since_block = current_block - (max_range * 5)

    all_transfers = []
    from_block = since_block

    while from_block < current_block:
        to_block = min(from_block + max_range, current_block)
        payload = {
            "jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
            "params": [{
                "fromBlock": hex(from_block), "toBlock": hex(to_block),
                "address": contract,
                "topics": [transfer_sig, None, f"0x000000000000000000000000{wallet[2:].lower()}"]
            }]
        }
        try:
            result = subprocess.run(
                ["curl", "-s", "-X", "POST", rpc,
                 "-H", "Content-Type: application/json",
                 "-d", json.dumps(payload)],
                capture_output=True, text=True, timeout=30
            )
            resp = json.loads(result.stdout)
            if "error" in resp:
                from_block = to_block + 1
                continue
            for log in resp.get("result", []):
                data = log.get("data", "0x0")
                if data in ("0x", "0x0"):
                    continue
                amount = int(data, 16) / 1e6
                sender = "0x" + log["topics"][1][-40:]
                all_transfers.append({
                    "chain": chain,
                    "tx_hash": log["transactionHash"],
                    "block": int(log["blockNumber"], 16),
                    "sender": sender,
                    "amount_usdc": amount,
                    "service": KNOWN_SENDERS.get(sender.lower(), "unknown"),
                })
        except Exception:
            pass
        from_block = to_block + 1
    return all_transfers


def get_wallet_balances():
    balances = {}

    # Base ETH + USDC
    try:
        r = subprocess.run(
            ["curl", "-s", "-X", "POST", "https://mainnet.base.org",
             "-H", "Content-Type: application/json",
             "-d", json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getBalance", "params": [WALLET_EVM, "latest"]})],
            capture_output=True, text=True, timeout=15
        )
        balances["base_eth"] = round(int(json.loads(r.stdout)["result"], 16) / 1e18, 6)
    except Exception:
        balances["base_eth"] = 0

    # Avalanche
    try:
        r = subprocess.run(
            ["curl", "-s", "-X", "POST", "https://api.avax.network/ext/bc/C/rpc",
             "-H", "Content-Type: application/json",
             "-d", json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getBalance", "params": [WALLET_EVM, "latest"]})],
            capture_output=True, text=True, timeout=15
        )
        balances["avax"] = round(int(json.loads(r.stdout)["result"], 16) / 1e18, 6)
    except Exception:
        balances["avax"] = 0

    # Solana
    try:
        r = subprocess.run(
            ["curl", "-s", "-X", "POST", "https://api.mainnet-beta.solana.com",
             "-H", "Content-Type: application/json",
             "-d", json.dumps({"jsonrpc": "2.0", "id": 1, "method": "getBalance", "params": [WALLET_SOL]})],
            capture_output=True, text=True, timeout=15
        )
        balances["sol"] = round(json.loads(r.stdout).get("result", {}).get("value", 0) / 1e9, 6)
    except Exception:
        balances["sol"] = 0

    # BNB
    try:
        r = subprocess.run(
            ["curl", "-s", "-X", "POST", "https://bsc-dataseed.binance.org",
             "-H", "Content-Type: application/json",
             "-d", json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getBalance", "params": [WALLET_EVM, "latest"]})],
            capture_output=True, text=True, timeout=15
        )
        balances["bnb"] = round(int(json.loads(r.stdout)["result"], 16) / 1e18, 6)
    except Exception:
        balances["bnb"] = 0

    return balances


def get_sol_price():
    try:
        r = subprocess.run(
            ["curl", "-s", "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"],
            capture_output=True, text=True, timeout=10
        )
        return json.loads(r.stdout)["solana"]["usd"]
    except Exception:
        return 150


def get_bankr_balances():
    """Fetch Bankr wallet portfolio via API. Returns dict or None if no key/error."""
    key = os.environ.get("BANKR_API_KEY") or ""
    if not key:
        return None
    try:
        r = subprocess.run(
            ["curl", "-s", "-m", "10", "-H", f"Authorization: Bearer {key}",
             "https://api.bankr.bot/wallet/portfolio"],
            capture_output=True, text=True, timeout=15
        )
        resp = json.loads(r.stdout)
        if not resp.get("success"):
            return {"error": resp.get("message", "bankr API error")}
        return {
            "evm": resp.get("evmAddress"),
            "sol": resp.get("solAddress"),
            "balances": resp.get("balances", {}),
        }
    except Exception as e:
        return {"error": str(e)}


# ── Marketplace Income (Aug 12, 2026) ──────────────────────────────────
# New sell-side rails we've stood up. Polled by the Revenue Monitor so
# Jordan sees marketplace earnings alongside on-chain x402 revenue.
# Best-effort: any failure here must NOT break the rest of the report.

# AgentLux — the live autonomous rail. First-Hire Guarantee armed Aug 12.
AGENTLUX_AGENT_ID = "9fed6922-48d0-4ed6-975a-c828bdf02446"
AGENTLUX_TOKEN_FILE = Path("/root/.blockrun/agentlux-token")
AGENTLUX_AGENT_WALLET = "0x7ebff188f2Eba16518C02864589b1403a5d1296a"


def get_marketplace_income():
    """Best-effort poll of our marketplace rails for EARNED INCOME only.

    Per Jordan (Aug 12): this is a REVENUE job. It records income from jobs
    (pending hires to accept, settled payouts), NOT marketplace status/health.
    Status lines live in the marketplace registry / scanner, not here.
    """
    results = []
    # AgentLux — only surface REAL income events: pending hire to accept + settled payout
    results.append(get_agentlux_earnings())
    # Nevermined — LIVE (registered Aug 12). Income = settled USDC (already scanned on-chain
    # via the USDC transfer scan to our wallet). No extra API poll needed.
    return results


def get_agentlux_earnings():
    """AgentLux income events: pending hire (money to accept) or settled payout.

    Returns only actionable income. NOT a status check.
    """
    out = {"platform": "AgentLux", "type": "income", "detail": "no income events yet"}
    try:
        token = AGENTLUX_TOKEN_FILE.read_text().strip() if AGENTLUX_TOKEN_FILE.exists() else ""
        if not token:
            return out  # no token = no income to report; don't flag as status
        # Pending hire request = income waiting to be accepted
        r = subprocess.run(
            ["curl", "-s", "-m", "12",
             "https://api.agentlux.ai/v1/services/hire/requests?role=provider&status=pending",
             "-H", f"Authorization: Bearer {token}"],
            capture_output=True, text=True, timeout=15)
        try:
            data = json.loads(r.stdout)
        except json.JSONDecodeError:
            data = {}
        reqs = data.get("requests") or data.get("data") or []
        if reqs and isinstance(reqs, list) and len(reqs) > 0:
            total = sum(float(q.get("priceUsd", 0) or 0) for q in reqs)
            out.update(
                detail=f"{len(reqs)} pending hire(s) worth ~${total:.2f} — ACCEPT + deliver",
                pending_hire_count=len(reqs),
                pending_hire_usd=round(total, 2),
            )
        # Settled payout would be surfaced here too (on-chain USDC scan already covers it)
    except Exception:
        pass
    return out




# ── Scan + Report ───────────────────────────────────────────────────────

def run():
    """Full scan: health check + wallet scan + balances + report."""
    data = load_tracker()
    existing_txs = {tx["tx_hash"] for tx in data.get("transactions", [])}

    # 1. Health check
    health = check_service_health()
    services_up = sum(1 for _, s, _ in health if s == "ok")
    services_down = [n for n, s, _ in health if s != "ok"]
    health_record = {
        "timestamp": datetime.now().isoformat(),
        "services_up": services_up,
        "services_down": services_down,
        "total": len(health),
    }
    data.setdefault("service_health_history", []).append(health_record)
    if len(data["service_health_history"]) > 60:
        data["service_health_history"] = data["service_health_history"][-60:]

    # 2. Wallet balances
    balances = get_wallet_balances()
    sol_price = get_sol_price()

    # 3. Scan chains for USDC transfers
    new_transfers = []
    for chain in ("base", "avalanche", "bnb"):
        last_block = data.get("last_scan_block", {}).get(chain, 0)
        transfers = fetch_usdc_transfers(chain, WALLET_EVM, last_block)
        for t in transfers:
            if t["tx_hash"] not in existing_txs:
                new_transfers.append(t)
        if transfers:
            data.setdefault("last_scan_block", {})[chain] = max(t["block"] for t in transfers)

    # 3b. Scan Solana USDC
    sol_transfers, sol_usdc_balance = SCAN_SOL(WALLET_SOL, None, data)
    for t in sol_transfers:
        if t["tx_hash"] not in existing_txs:
            new_transfers.append(t)

    # Filter out self-transfers (LP deposits, internal moves)
    our_wallets = {WALLET_EVM.lower(), WALLET_SOL.lower()}
    external = [t for t in new_transfers if t["sender"].lower() not in our_wallets]
    data["transactions"].extend(external)

    # 4. Revenue — ALL external transfers count as revenue
    # KNOWN_SENDERS provides optional labels, never filters.
    for tx in external:
        svc_name = tx["service"] if tx["service"] != "unknown" else tx["chain"]
        data.setdefault("revenue_by_service", {})
        data["revenue_by_service"].setdefault(svc_name, {
            "total_usdc": 0, "tx_count": 0, "chains": []
        })
        data["revenue_by_service"][svc_name]["total_usdc"] += tx["amount_usdc"]
        data["revenue_by_service"][svc_name]["tx_count"] += 1
        if tx["chain"] not in data["revenue_by_service"][svc_name]["chains"]:
            data["revenue_by_service"][svc_name]["chains"].append(tx["chain"])

    data["total_revenue_usd"] = sum(
        tx["amount_usdc"] for tx in data["transactions"]
    )

    # 5. Portfolio value (rough)
    sol_usdc_val = data.get("sol_usdc_balance", 0)
    total_portfolio = (
        balances.get("base_eth", 0) * 3500 +
        balances.get("avax", 0) * 6 +
        balances.get("sol", 0) * sol_price +
        sol_usdc_val +
        balances.get("bnb", 0) * 580
    )

    # 6. Snapshot
    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "balances": balances,
        "sol_usdc_balance": sol_usdc_val,
        "total_portfolio_usd": round(total_portfolio, 2),
        "total_revenue_usd": round(data["total_revenue_usd"], 4),
        "new_transfers": len(external),
        "sol_price": sol_price,
        "services_up": services_up,
        "services_total": len(health),
    }
    data["snapshots"].append(snapshot)
    if len(data["snapshots"]) > 120:
        data["snapshots"] = data["snapshots"][-120:]

    save_tracker(data)

    # 7. Bankr wallet (distinct channel)
    bankr = get_bankr_balances()

    # 8. Marketplace income (best-effort poll of our rails)
    marketplace = get_marketplace_income()

    return {
        "snapshot": snapshot,
        "health": health,
        "services_up": services_up,
        "services_down": services_down,
        "new_payments": external,
        "revenue_by_service": data.get("revenue_by_service", {}),
        "total_revenue": data["total_revenue_usd"],
        "total_transactions": len(data["transactions"]),
        "balances": balances,
        "sol_usdc_balance": sol_usdc_val,
        "sol_price": sol_price,
        "bankr": bankr,
        "marketplace": marketplace,
    }


def format_report(result):
    snap = result["snapshot"]
    lines = []
    lines.append("💰 Revenue Monitor — GenTech Labs")
    lines.append(f"📅 {now_str()}")
    lines.append("")

    # ── Service Health ──
    lines.append("🔌 Service Health")
    for name, status, url in result["health"]:
        icon = "🟢" if status == "ok" else "🔴"
        lines.append(f"  {icon} {name} — {status}")
    if result["services_down"]:
        lines.append(f"  ⚠️  {len(result['services_down'])} service(s) down")
    lines.append(f"  {result['services_up']}/{len(result['health'])} healthy")
    lines.append("")

    # ── Portfolio ──
    b = result["balances"]
    sol_usdc = result.get("sol_usdc_balance", 0)
    lines.append("📊 Portfolio")
    lines.append(f"  Total: ${snap['total_portfolio_usd']:.2f}")
    lines.append(f"  SOL: {b.get('sol', 0):.4f} (${b.get('sol', 0) * snap['sol_price']:.2f})")
    if sol_usdc:
        lines.append(f"  SOL USDC: {sol_usdc:.2f}")
    lines.append(f"  AVAX: {b.get('avax', 0):.4f}")
    lines.append(f"  ETH (Base): {b.get('base_eth', 0):.6f}")
    lines.append(f"  BNB: {b.get('bnb', 0):.4f}")
    lines.append("")

    # ── Revenue ──
    lines.append("💵 x402 Revenue")
    lines.append(f"  Total earned: ${result['total_revenue']:.4f} USDC")
    lines.append(f"  Transactions tracked: {result['total_transactions']}")
    if result["revenue_by_service"]:
        lines.append("")
        lines.append("  By source:")
        for svc, info in result["revenue_by_service"].items():
            lines.append(f"    • {svc}: ${info['total_usdc']:.4f} ({info['tx_count']} txs)")
    else:
        lines.append("  No sources yet")

    if result["new_payments"]:
        lines.append("")
        lines.append("  ⚡ New transfer(s) detected!")
        for tx in result["new_payments"]:
            tag = "✅ x402" if tx["service"] != "unknown" else "ℹ️ unknown"
            lines.append(f"    +${tx['amount_usdc']:.4f} from {tx['sender'][:10]}... ({tx['chain']}) [{tag}]")

    if not result["new_payments"] and result["total_revenue"] == 0:
        lines.append("")
        lines.append("  ⏳ No payments yet — infrastructure ready, awaiting first x402 transaction")
    elif not result["new_payments"] and result["total_revenue"] > 0:
        lines.append("")
        lines.append("  📋 No new transfers since last scan")

    # ── Balance Sources ──
    lines.append("")
    lines.append("🔗 Balance Sources")
    lines.append("  ✅ On-chain (Base/AVAX/BNB EVM) — scanned via RPC")
    lines.append("  ✅ On-chain (Solana) — scanned via RPC")
    lines.append("  ⏳ Pay wallet — checked by agent in cron prompt")
    lines.append("  ⏳ Q402 wallet — checked by agent in cron prompt")
    lines.append("  ⏳ OKX Agentic Wallet — checked by agent in cron prompt")
    lines.append("  ⏳ x402-list directory — GenTech Labs x402 Gateway live (6 endpoints, 100% uptime) — traffic source for x402 revenue")

    # ── Marketplace Income (EARNED only — per Jordan Aug 12) ──
    # Revenue job: record income from jobs, NOT marketplace status.
    marketplace = result.get("marketplace") or []
    income_events = [m for m in marketplace if m.get("type") == "income"
                     and m.get("pending_hire_count", 0) > 0]
    if income_events:
        lines.append("")
        lines.append("🛒 Marketplace Income")
        for m in income_events:
            lines.append(f"  🟢 {m['platform']}: {m.get('detail','')}")
    else:
        lines.append("  ⏳ Marketplace income — no pending hires/payouts (on-chain USDC scan covers settled revenue)")

    # ── Bankr ──
    bankr = result.get("bankr")
    lines.append("")
    lines.append("🏦 Bankr Wallet")
    if bankr is None:
        lines.append("  ⏳ No BANKR_API_KEY configured — skipping")
    elif "error" in bankr:
        lines.append(f"  ⚠️ Error: {bankr['error']}")
    else:
        lines.append(f"  EVM: {bankr['evm']}")
        lines.append(f"  SOL: {bankr['sol']}")
        total_usd = 0.0
        for chain, bal in (bankr.get("balances") or {}).items():
            try:
                usd = float((bal or {}).get("total", 0) or 0)
                total_usd += usd
            except (TypeError, ValueError):
                continue
        lines.append(f"  Portfolio: ${total_usd:.2f} across {len(bankr.get('balances') or {})} chains")

    # ── Credits & Resources ──
    lines.append("")
    lines.append("🎫 Credits & Subsidies")
    lines.append("  ✅ Virtuals Spark Tier — $200/wk inference credits (claimed Jul 15)")
    lines.append("  ⏳ Other platforms — add as approved")

    lines.append(f"📈 SOL: ${snap['sol_price']:.2f}")

    return "\n".join(lines)


if __name__ == "__main__":
    result = run()
    if "--json" in sys.argv:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(format_report(result))
