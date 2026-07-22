"""Weekly deal sweep for Jordan's Steam wishlist — efficient batch approach."""
import json, sys, time
sys.path.insert(0, '.')
from deal_tracker import CheapSharkClient
from urllib.request import Request, urlopen

client = CheapSharkClient(cache_enabled=True)

with open('watchlist.json') as f:
    jordan = json.load(f)

games = jordan.get('games', [])
print(f'GAMES_COUNT:{len(games)}')

# Strategy: get ALL current deals from CheapShark (no title filter, just top deals)
# then match against our watchlist by steamAppID
# This is 1-2 API calls instead of 86

# First, get the store map
stores = client.get_stores()

# Get all current deals (paginated, top 500)
all_deals_url = "https://www.cheapshark.com/api/1.0/deals?upperPrice=9999&pageSize=500"
req = Request(all_deals_url, headers={"User-Agent": "GenTech-Shop/1.0"})
with urlopen(req, timeout=30) as resp:
    all_deals = json.loads(resp.read().decode())

print(f'FETCHED_DEALS:{len(all_deals)}')

# Build lookup by steamAppID
deal_by_appid = {}
for d in all_deals:
    appid = d.get("steamAppID")
    if appid:
        appid = int(appid)
        if appid not in deal_by_appid or float(d.get("savings", 0)) > float(deal_by_appid[appid].get("savings", 0)):
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
        
        if savings > 10:
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
