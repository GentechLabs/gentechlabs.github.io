#!/usr/bin/env python3
"""
GenTech Shop — per-user weekly sales sweep (identity-aware).

Usage:
    python3 user_sweep.py <watchlist_path> "<User Label>"

Example:
    python3 user_sweep.py watchlist-vanito.json "Vanito"
    python3 user_sweep.py watchlist-jordan.json "Jordan"

Each user's sweep reads ONLY its own watchlist file and labels the report with
the given user. This replaces the old single-watchlist scripts (jordan_sweep*,
vanito_sweep*, weekly_sweep) that ALL read the same watchlist.json.

Strategy:
  1. CheapShark batch all-deals (paginated) matched by steamAppID — cross-store.
  2. If CheapShark 429s, fall back to Steam Store API appdetails (Steam only).
"""
import json, sys, time
from urllib.request import Request, urlopen
from urllib.error import HTTPError

BASE = "https://www.cheapshark.com/api/1.0"


def get(url, timeout=30):
    req = Request(url, headers={"User-Agent": "GenTech-Shop/1.0"})
    with urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def main():
    if len(sys.argv) < 3:
        print("USAGE: python3 user_sweep.py <watchlist_path> \"<User Label>\"")
        sys.exit(1)
    watchlist_path = sys.argv[1]
    user_label = sys.argv[2]

    with open(watchlist_path) as f:
        data = json.load(f)
    games = data.get('games', data.get('items', []))
    if not games:
        print(f"[{user_label}] watchlist {watchlist_path} empty or unreadable")
        sys.exit(0)

    wanted = {int(g['steam_appid']): g['title'] for g in games if g.get('steam_appid')}
    print(f"[{user_label}] GAMES_COUNT:{len(games)}  APPIDS:{len(wanted)}  FILE:{watchlist_path}")

    # --- store map ---
    store_map = {}
    try:
        store_map = {str(s["storeID"]): s["storeName"] for s in get(f"{BASE}/stores")}
    except Exception as e:
        print(f"[{user_label}] STORE_ERR:{e}")

    # --- CheapShark batch all-deals, paginated ---
    deal_by_appid = {}
    pages = 0
    rate_limited = False
    for page in range(0, 10):
        try:
            batch = get(f"{BASE}/deals?upperPrice=9999&pageSize=60&pageNumber={page}")
            if not batch:
                break
            pages += 1
            for d in batch:
                appid = d.get("steamAppID")
                if appid:
                    appid = int(appid)
                    if appid not in deal_by_appid or float(d.get("savings", 0)) > float(deal_by_appid[appid].get("savings", 0)):
                        deal_by_appid[appid] = d
        except HTTPError as e:
            if e.code == 429:
                print(f"[{user_label}] RATE_LIMIT_AT_PAGE:{page} — falling back to Steam API")
                rate_limited = True
                break
            print(f"[{user_label}] HTTP_ERR_PAGE:{page}:{e}")
        except Exception as e:
            print(f"[{user_label}] PAGE_ERR:{page}:{e}")
        time.sleep(0.4)
    print(f"[{user_label}] PAGES:{pages}  UNIQUE_DEALS:{len(deal_by_appid)}")

    deals, upcoming, matched, no_deals = [], [], [], []

    if not rate_limited:
        for appid, title in wanted.items():
            d = deal_by_appid.get(appid)
            if d:
                matched.append(title)
                savings = float(d.get("savings", 0))
                sale_price = float(d.get("salePrice", 0))
                normal_price = float(d.get("normalPrice", 0))
                store_name = store_map.get(str(d.get("storeID", "0")), "Store")
                if savings > 10:
                    deals.append({'title': title, 'price': sale_price, 'normal': normal_price,
                                  'savings': savings, 'store': store_name, 'appid': appid})
                elif sale_price == 0 and normal_price == 0:
                    upcoming.append(title)
                else:
                    no_deals.append(title)
            else:
                no_deals.append(title)
    else:
        # CheapShark blocked → Steam Store API fallback (exact AppID, Steam-only)
        from urllib.request import Request as R2
        from concurrent.futures import ThreadPoolExecutor, as_completed

        def check(appid, title):
            url = f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=us&filters=price_overview,release_date"
            req = R2(url, headers={"User-Agent": "Mozilla/5.0"})
            try:
                with urlopen(req, timeout=15) as r:
                    d = json.loads(r.read().decode())
                app = d.get(str(appid), {})
                if not app.get('success'):
                    return (title, None)
                dd = app.get('data', {})
                po = dd.get('price_overview', {})
                rd = dd.get('release_date', {})
                return (title, {
                    'discount': po.get('discount_percent', 0),
                    'final': po.get('final', 0) / 100 if po else 0,
                    'initial': po.get('initial', 0) / 100 if po else 0,
                    'coming_soon': rd.get('coming_soon', False),
                    'released': bool(rd.get('date', '')),
                })
            except Exception as e:
                return (title, {'error': str(e)})

        results = {}
        with ThreadPoolExecutor(max_workers=8) as ex:
            futs = {ex.submit(check, a, t): t for a, t in wanted.items()}
            for f in as_completed(futs):
                title, info = f.result()
                results[title] = info
                time.sleep(0.15)

        for title, info in results.items():
            if not info or 'error' in info:
                no_deals.append(title); continue
            if info['coming_soon'] or not info['released']:
                upcoming.append(title)
            elif info['discount'] > 10:
                deals.append({'title': title, 'price': info['final'], 'normal': info['initial'],
                              'savings': info['discount'], 'store': 'Steam', 'appid': None})
            else:
                no_deals.append(title)

    deals.sort(key=lambda x: x['savings'], reverse=True)
    print('DEALS_JSON:' + json.dumps({
        'user': user_label, 'deals': deals, 'upcoming': upcoming,
        'matched': matched, 'no_deals': no_deals, 'total': len(games),
        'source': 'Steam' if rate_limited else 'CheapShark'
    }))


if __name__ == '__main__':
    main()
