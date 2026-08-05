"""Jordan weekly deal sweep — per-title search, filtered by steam_appid."""
import json, sys, time
sys.path.insert(0, '.')
from deal_tracker import CheapSharkClient

client = CheapSharkClient(cache_enabled=True)

with open('watchlist.json') as f:
    jordan = json.load(f)

games = jordan.get('games', [])
print(f'GAMES_COUNT:{len(games)}')

deals = []
upcoming = []
for game in games:
    title = game['title']
    appid = game.get('steam_appid')
    try:
        results = client.search_deals(title)
    except Exception as e:
        print(f'ERR:{title}:{e}')
        continue
    if not results:
        continue
    best = results[0]
    # Filter by steam AppID when we have one; otherwise strict title match already applied
    if appid and best.steam_appid and best.steam_appid != appid:
        continue
    if best.savings > 10:
        deals.append({
            'title': title,
            'price': best.sale_price,
            'normal': best.normal_price,
            'savings': best.savings,
            'store': best.store_name
        })
    elif best.sale_price == 0 and best.normal_price == 0:
        upcoming.append(title)

deals.sort(key=lambda x: x['savings'], reverse=True)

print('DEALS_JSON:' + json.dumps({
    'deals': deals,
    'upcoming': upcoming,
    'total': len(games)
}))
