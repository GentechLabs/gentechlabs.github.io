"""Jordan weekly sweep - batch all-deals approach, paginated for coverage."""
import json, sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import time

BASE = "https://www.cheapshark.com/api/1.0"

with open('watchlist.json') as f:
    jordan = json.load(f)

games = jordan['games']
wanted = {}
for g in games:
    appid = g.get('steam_appid')
    if appid:
        wanted[int(appid)] = g['title']
print(f'GAMES_COUNT:{len(games)}  WANTED_APPIDS:{len(wanted)}')

# store map
def get(url):
    req = Request(url, headers={"User-Agent": "GenTech-Shop/1.0"})
    with urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

try:
    stores = get(f"{BASE}/stores")
    store_map = {str(s["storeID"]): s["storeName"] for s in stores}
except Exception as e:
    print(f'STORE_ERR:{e}')
    store_map = {}

# paginate deals - fetch up to 8 pages (480 deals)
deal_by_appid = {}
pages_fetched = 0
for page in range(0, 8):
    try:
        url = f"{BASE}/deals?upperPrice=9999&pageSize=60&pageNumber={page}"
        batch = get(url)
        if not batch:
            break
        pages_fetched += 1
        for d in batch:
            appid = d.get("steamAppID")
            if appid:
                appid = int(appid)
                if appid not in deal_by_appid or float(d.get("savings", 0)) > float(deal_by_appid[appid].get("savings", 0)):
                    deal_by_appid[appid] = d
    except HTTPError as e:
        if e.code == 429:
            print(f'RATE_LIMIT_AT_PAGE:{page}')
            time.sleep(3)
            continue
        print(f'HTTP_ERR_PAGE:{page}:{e}')
    except Exception as e:
        print(f'PAGE_ERR:{page}:{e}')
    time.sleep(0.5)

print(f'PAGES_FETCHED:{pages_fetched}  UNIQUE_DEALS:{len(deal_by_appid)}')

deals = []
upcoming = []
matched_any = []

for appid, title in wanted.items():
    d = deal_by_appid.get(appid)
    if d:
        savings = float(d.get("savings", 0))
        sale_price = float(d.get("salePrice", 0))
        normal_price = float(d.get("normalPrice", 0))
        store_name = store_map.get(str(d.get("storeID", "0")), "Store")
        matched_any.append(title)
        if savings > 10:
            deals.append({'title': title, 'price': sale_price, 'normal': normal_price,
                          'savings': savings, 'store': store_name, 'appid': appid})
        elif sale_price == 0 and normal_price == 0:
            upcoming.append(title)

deals.sort(key=lambda x: x['savings'], reverse=True)
print('DEALS_JSON:' + json.dumps({
    'deals': deals, 'upcoming': upcoming, 'matched': matched_any,
    'total': len(games)
}))
