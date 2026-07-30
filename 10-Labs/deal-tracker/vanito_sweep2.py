"""Batch sweep for Vanito - fetch more deals pages."""
import json, sys, time
sys.path.insert(0, '.')
from deal_tracker import CheapSharkClient
from urllib.request import Request, urlopen

client = CheapSharkClient(cache_enabled=True)

with open('watchlist.json') as f:
    vanito = json.load(f)

games = vanito.get('games', [])
print(f'GAMES_COUNT:{len(games)}')

# Get store map
stores = client.get_stores()

# Fetch multiple pages of deals to get broader coverage
all_deals = []
for page in range(0, 3):  # pages 0, 1, 2 = up to 1500 deals
    url = f"https://www.cheapshark.com/api/1.0/deals?upperPrice=9999&pageSize=500&pageNumber={page}"
    req = Request(url, headers={"User-Agent": "GenTech-Shop/1.0"})
    try:
        with urlopen(req, timeout=30) as resp:
            page_data = json.loads(resp.read().decode())
        if page_data and isinstance(page_data, list):
            all_deals.extend(page_data)
            print(f'PAGE_{page}:{len(page_data)}')
        else:
            break
    except Exception as e:
        print(f'PAGE_{page}_ERROR:{e}')
        break
    time.sleep(1.5)

print(f'TOTAL_DEALS:{len(all_deals)}')

# Build lookup by steamAppID
deal_by_appid = {}
for d in all_deals:
    appid = d.get("steamAppID")
    if appid:
        appid = int(appid)
        existing = deal_by_appid.get(appid)
        new_savings = float(d.get("savings", 0))
        if appid not in deal_by_appid or new_savings > float(existing.get("savings", 0)):
            deal_by_appid[appid] = d

# Match against watchlist
deals = []
upcoming = []
no_deals = []

for game in games:
    title = game['title']
    appid = game.get('steam_appid')
    
    if appid and appid in deal_by_appid:
        d = deal_by_appid[appid]
        savings = float(d.get("savings", 0))
        sale_price = float(d.get("salePrice", 0))
        normal_price = float(d.get("normalPrice", 0))
        store_id = str(d.get("storeID", "0"))
        store_name = stores.get(store_id, f"Store {store_id}")
        
        if savings > 0:
            deals.append({
                'title': title,
                'price': sale_price,
                'normal': normal_price,
                'savings': savings,
                'store': store_name
            })
        elif sale_price == 0 and normal_price == 0:
            upcoming.append(title)
        else:
            no_deals.append(title)
    else:
        no_deals.append(title)

deals.sort(key=lambda x: x['savings'], reverse=True)

print('DEALS_JSON:' + json.dumps({
    'deals': deals,
    'upcoming': upcoming,
    'no_deals': no_deals,
    'errors': [],
    'total': len(games)
}))
