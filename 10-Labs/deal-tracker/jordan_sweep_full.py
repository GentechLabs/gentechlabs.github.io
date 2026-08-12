"""Jordan weekly sweep - per-title search with 429 tolerance."""
import json, sys, time
sys.path.insert(0, '.')
from deal_tracker import CheapSharkClient

client = CheapSharkClient(cache_enabled=True)

with open('watchlist.json') as f:
    jordan = json.load(f)

games = jordan['games']
print(f'GAMES_COUNT:{len(games)}')

deals = []
upcoming = []
no_deals = []

for i, game in enumerate(games):
    title = game['title']
    appid = game.get('steam_appid')
    try:
        results = client.search_deals(title)
    except Exception as e:
        print(f'ERROR_ON:{title}:{e}')
        # rate limited - bail, keep what we have
        if '429' in str(e) or 'HTTP Error 429' in str(e):
            print('RATE_LIMITED_BAIL')
            break
        no_deals.append(title)
        continue
    if results:
        # filter by steam appid if we have it
        if appid:
            matched = [r for r in results if r.steam_appid == appid]
            if matched:
                results = matched
        best = results[0]
        if best.savings > 10:
            deals.append({'title': title, 'price': best.sale_price,
                          'normal': best.normal_price, 'savings': best.savings,
                          'store': best.store_name, 'appid': appid})
        elif best.sale_price == 0 and best.normal_price == 0:
            upcoming.append(title)
        else:
            no_deals.append(title)
    else:
        no_deals.append(title)

deals.sort(key=lambda x: x['savings'], reverse=True)
print('DEALS_JSON:' + json.dumps({
    'deals': deals, 'upcoming': upcoming, 'no_deals': no_deals,
    'total': len(games), 'checked': i+1
}))
