#!/usr/bin/env python3
"""
AAE Live Dashboard Generator
Fetches live data and populates the yield-farm-tracker template.
Run manually or via cron every 5-10 minutes.
"""
import json
import urllib.request
import os
from datetime import datetime, timezone, timedelta

SCRIPT_DIR = "/root/vaults/gentech/06-Content/aae-frontend-live"
TEMPLATE_PATH = "/root/vaults/gentech/03-Strategies/templates/yield-farm-tracker.html"
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "index.html")
STATE_DIR = "/root/.hermes/profiles/desmond/home/.hermes/scripts"
CONFIG_FILE = os.path.join(STATE_DIR, ".lfj-aae-config.json")
STATE_FILE = os.path.join(STATE_DIR, ".lfj-aae-state.json")

os.makedirs(SCRIPT_DIR, exist_ok=True)

with open(CONFIG_FILE) as f:
    cfg = json.load(f)
with open(STATE_FILE) as f:
    state = json.load(f)

def fetch_dexscreener():
    pool = cfg["pool_address"]
    chain = cfg["chain"]
    url = f"https://api.dexscreener.com/latest/dex/pairs/{chain}/{pool}"
    req = urllib.request.Request(url, headers={"User-Agent": "Gentech-Labs/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        pair = data.get("pair", data.get("pairs", [{}])[0] if data.get("pairs") else {})
        return {
            "price": float(pair.get("priceNative", 0)),
            "volume_24h": float(pair.get("volume", {}).get("h24", 0)),
            "liquidity_usd": float(pair.get("liquidity", {}).get("usd", 0)),
            "price_change_24h": float(pair.get("priceChange", {}).get("h24", 0)),
            "source": "dexscreener"
        }
    except Exception as e:
        print(f"DexScreener failed: {e}")
        return None

def fetch_onchain():
    pool = cfg["pool_address"]
    rpc = cfg["rpc_url"]
    t0d = cfg["token0"]["decimals"]
    t1d = cfg["token1"]["decimals"]
    def rpc_call(data):
        payload = json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":pool,"data":data},"latest"]}).encode()
        req = urllib.request.Request(rpc, data=payload, headers={"Content-Type":"application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())["result"]
    try:
        swap_data = "0xe77366f8" + "0"*63 + "1" + "0"*63 + "1"
        swap_res = rpc_call(swap_data)
        amt_out = int(swap_res[2+64:2+128], 16)
        price = amt_out / (10**t1d)
        reserves = rpc_call("0x0902f1ac")
        rx = int(reserves[2:2+64], 16)
        ry = int(reserves[2+64:2+128], 16)
        return {
            "price": price,
            "reserve0": rx / (10**t0d),
            "reserve1": ry / (10**t1d),
            "liquidity_usd": (rx / (10**t0d)) * price + (ry / (10**t1d)),
            "source": "onchain"
        }
    except Exception as e:
        print(f"On-chain failed: {e}")
        return None

pool_data = fetch_dexscreener() or fetch_onchain() or {}
price = pool_data.get("price", state.get("last_price", 9.35))
volume_24h = pool_data.get("volume_24h", 0)
liquidity_usd = pool_data.get("liquidity_usd", 4000000)
price_change = pool_data.get("price_change_24h", 0)

pos = cfg["position"]
total_pos = pos["total_usd"]
token0_amt = pos["token0_amount"]
token1_amt = pos["token1_amount"]
token0_usd = token0_amt * price
token1_usd = token1_amt
total_calc = token0_usd + token1_usd
token0_pct = (token0_usd / total_calc * 100) if total_calc > 0 else 0
token1_pct = (token1_usd / total_calc * 100) if total_calc > 0 else 0

range_low = pos["range_low"]
range_high = pos["range_high"]
in_range = range_low <= price <= range_high

fee_rate = cfg["fee_tier_bps"] / 10000
est_daily_fees = (volume_24h * fee_rate) * (total_pos / liquidity_usd) if liquidity_usd > 0 else 0
apr = ((volume_24h * fee_rate) / liquidity_usd * 100 * 365) if liquidity_usd > 0 else 0

current_idx = state.get("current_milestone_idx", -1)
current_tier = cfg["milestones"][current_idx] if 0 <= current_idx < len(cfg["milestones"]) else None

dca = cfg["dca"]
dca_weekly = f"${dca['base_amount']}"
dca_monthly = f"${dca['base_amount'] * 4}"

tz = timezone(timedelta(hours=cfg.get("quiet_hours", {}).get("timezone_offset", -4)))
now = datetime.now(tz)
timestamp = now.strftime("%A, %B %d, %Y -- %I:%M %p %Z")
date_str = now.strftime("%B %d, %Y")

if in_range:
    fees_status = "FEES ACTIVE"
    fees_status_text = "IN RANGE -- EARNING!"
    active_alert = f"FEES ACTIVE! Position is IN RANGE as of {date_str}. Earning ~${est_daily_fees:.2f} est/day. The {pos['shape'].upper()} shape is {'centered' if range_low < price < range_high else 'at the edge'} around ${price:.2f}. Keep compounding and keep DCA'ing."
else:
    fees_status = "OUT OF RANGE"
    fees_status_text = "OUT OF RANGE -- NOT EARNING"
    active_alert = f"OUT OF RANGE! Price ${price:.2f} is outside your range (${range_low:.2f}--${range_high:.2f}). Consider rebalancing."

context_tag = "LIVE"
avax_bought = 50 / price if price > 0 else 0
context_body = f"AAE Live Dashboard active. DCA locked at <strong>${dca['base_amount']}--{dca['base_amount']+dca['boost_amount']}/week</strong> -- steady accumulation."
market_read = f"AVAX at ${price:.2f} ({price_change:+.2f}% 24h). Fees {'ACTIVE' if in_range else 'PAUSED'}. {'Claim and compound.' if state.get('total_fees_earned_usd',0) > 0.5 else 'Keep building.'}"

strategy_notes = f"""
<strong>Live Position:</strong> ${total_calc:.2f} total | {token0_amt:.3f} AVAX + {token1_amt:.2f} USDC.<br><br>
<strong>Range Status:</strong> {'IN RANGE' if in_range else 'OUT OF RANGE'} -- ${price:.2f} vs [${range_low:.2f}--${range_high:.2f}].<br><br>
<strong>Fee Estimate:</strong> ~${est_daily_fees:.3f}/day (APR: {apr:,.0f}%).<br><br>
<strong>DCA Conviction:</strong> ${dca['base_amount']}--{dca['base_amount']+dca['boost_amount']}/week. Every ${dca['base_amount']} = ~{avax_bought:.2f} AVAX at ${price:.2f}.<br><br>
<strong>Milestone:</strong> {current_tier['label'] if current_tier else 'Unranked'} -- ${state.get('total_fees_earned_usd',0):.3f} earned so far.
""".strip()

if in_range and apr > 1000:
    footer_tagline = f"IN RANGE - FEES ACTIVE - DCA ${dca['base_amount']}--{dca['base_amount']+dca['boost_amount']}/WEEK - APR {apr:,.0f}%"
elif in_range:
    footer_tagline = f"IN RANGE - FEES ACTIVE - DCA ${dca['base_amount']}--{dca['base_amount']+dca['boost_amount']}/WEEK"
else:
    footer_tagline = f"OUT OF RANGE - REBALANCE NEEDED - DCA ${dca['base_amount']}--{dca['base_amount']+dca['boost_amount']}/WEEK"

with open(TEMPLATE_PATH) as f:
    html = f.read()

replacements = {
    "{{TIMESTAMP}}": timestamp,
    "{{DATE}}": date_str,
    "{{BIN_COUNT}}": "149",
    "{{FEES_STATUS}}": fees_status,
    "{{CONTEXT_TAG}}": context_tag,
    "{{CONTEXT_BODY}}": context_body,
    "{{MARKET_READ}}": market_read,
    "{{TOTAL_POSITION}}": f"${total_calc:.2f}",
    "{{POSITION_CHANGE}}": f"{price_change:+.2f}% from yesterday" if price_change else "Steady",
    "{{AVAX_PRICE}}": f"${price:.3f}",
    "{{AVAX_USDC_RATE}}": f"{price:.5f}",
    "{{REWARDS_APR}}": f"{apr:,.0f}%",
    "{{APR_TREND}}": "Live from pool volume" if apr > 1000 else f"{apr:.1f}% APR",
    "{{CLAIMABLE_USD}}": f"${state.get('total_fees_earned_usd', 0):.3f}",
    "{{CLAIMABLE_AVAX}}": f"{state.get('total_fees_earned_usd', 0)/price:.5f}" if price > 0 else "0",
    "{{FEES_24H}}": f"${est_daily_fees:.3f}",
    "{{FEES_STATUS_TEXT}}": fees_status_text,
    "{{RANGE_TVL}}": f"${liquidity_usd:,.0f}",
    "{{ACTIVE_ALERT}}": active_alert,
    "{{STRATEGY}}": pos["shape"].upper(),
    "{{AVAX_AMOUNT}}": f"{token0_amt:.3f}",
    "{{AVAX_USD}}": f"{token0_usd:.2f}",
    "{{AVAX_PCT}}": f"{token0_pct:.1f}",
    "{{USDC_AMOUNT}}": f"{token1_amt:.2f}",
    "{{USDC_USD}}": f"{token1_usd:.2f}",
    "{{USDC_PCT}}": f"{token1_pct:.1f}",
    "{{AVAX_PCT_INT}}": str(int(token0_pct)),
    "{{USDC_PCT_INT}}": str(int(token1_pct)),
    "{{FEES_24H_TOTAL}}": f"${est_daily_fees:.4f}",
    "{{FEES_TIMESTAMP}}": timestamp,
    "{{FEES_24H_AVAX}}": f"{est_daily_fees/2/price:.5f}" if price > 0 else "0",
    "{{FEES_24H_AVAX_USD}}": f"{est_daily_fees/2:.3f}",
    "{{FEES_24H_USDC}}": f"{est_daily_fees/2:.4f}",
    "{{FEES_24H_USDC_USD}}": f"{est_daily_fees/2:.3f}",
    "{{FEES_TOTAL}}": f"${state.get('total_fees_earned_usd', 0):.4f}",
    "{{FEES_TOTAL_AVAX}}": f"{state.get('total_fees_earned_usd', 0)/price:.5f}" if price > 0 else "0",
    "{{FEES_TOTAL_USDC}}": f"{state.get('total_fees_earned_usd', 0)/2:.4f}",
    "{{RANGE_MIN}}": f"{range_low:.4f}",
    "{{RANGE_MAX}}": f"{range_high:.4f}",
    "{{ACTIVE_BIN}}": f"{price:.5f}",
    "{{CURRENT_RANGE}}": f"{range_low:.3f} -- {range_high:.3f}",
    "{{RANGE_WIDTH}}": f"~{((range_high-range_low)/range_low*100):.1f}% spread",
    "{{REWARDS_PER_DAY}}": f"{est_daily_fees/price:.4f}" if price > 0 else "0",
    "{{DCA_WEEKLY}}": dca_weekly,
    "{{DCA_NOTE}}": "Steady bottom accumulation",
    "{{DCA_MONTHLY}}": dca_monthly,
    "{{DCA_MONTHLY_NOTE}}": "Fueled by Amazon Flex income",
    "{{DCA_MODE}}": dca.get("mode", "FLEXIBLE").upper(),
    "{{DCA_MODE_NOTE}}": "Invest when available",
    "{{CONVICTION}}": "HIGH",
    "{{CONVICTION_NOTE}}": f"Every ${dca['base_amount']} = ~{avax_bought:.2f} AVAX at ${price:.2f}",
    "{{POOL_ADDRESS}}": cfg["pool_address"],
    "{{PAIR}}": f"{cfg['token0']['symbol']} / {cfg['token1']['symbol']}",
    "{{PLATFORM}}": "LFJ (Trader Joe)",
    "{{NETWORK}}": "Avalanche C-Chain",
    "{{FEE_TIER}}": f"{cfg['fee_tier_bps']} bps ({cfg['fee_tier_bps']/100:.2f}%)",
    "{{FEE_TIER_SHORT}}": f"{cfg['fee_tier_bps']}bps",
    "{{STRATEGY_NOTES}}": strategy_notes,
    "{{FILENAME}}": "aae-live-dashboard.html",
    "{{FOOTER_TAGLINE}}": footer_tagline,
}

for key, val in replacements.items():
    html = html.replace(key, val)

meta_refresh = '<meta http-equiv="refresh" content="60">'
if '<meta charset="UTF-8">' in html:
    html = html.replace('<meta charset="UTF-8">', '<meta charset="UTF-8">\n    ' + meta_refresh)

with open(OUTPUT_PATH, "w") as f:
    f.write(html)

print(f"Live dashboard updated: {OUTPUT_PATH}")
print(f"   Price: ${price:.3f} | In Range: {in_range} | APR: {apr:.1f}%")
