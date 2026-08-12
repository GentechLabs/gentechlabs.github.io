"""Jordan weekly sweep via Steam Store API (appdetails) - exact AppID match."""
import json, time, sys
from urllib.request import Request, urlopen
from concurrent.futures import ThreadPoolExecutor, as_completed

with open('watchlist.json') as f:
    jordan = json.load(f)

games = jordan['games']
print(f'GAMES_COUNT:{len(games)}')

def check(appid, title):
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=us&filters=price_overview,release_date"
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode())
        app = data.get(str(appid), {})
        if not app.get('success'):
            return (appid, title, None)
        d = app.get('data', {})
        price = d.get('price_overview', {})
        rd = d.get('release_date', {})
        return (appid, title, {
            'discount': price.get('discount_percent', 0),
            'final': price.get('final', 0) / 100 if price else 0,
            'initial': price.get('initial', 0) / 100 if price else 0,
            'coming_soon': rd.get('coming_soon', False),
            'released': bool(rd.get('date', '')),
        })
    except Exception as e:
        return (appid, title, {'error': str(e)})

results = {}
with ThreadPoolExecutor(max_workers=8) as ex:
    futs = {ex.submit(check, g['steam_appid'], g['title']): g['title'] for g in games if g.get('steam_appid')}
    for f in as_completed(futs):
        appid, title, info = f.result()
        results[title] = info
        time.sleep(0.2)

# bucket
deals = []
upcoming = []
no_info = []
errors = []
for g in games:
    t = g['title']
    info = results.get(t)
    if not info:
        no_info.append(t)
        continue
    if 'error' in info:
        errors.append((t, info['error']))
        continue
    if info['coming_soon'] or not info['released']:
        upcoming.append(t)
    elif info['discount'] > 10:
        deals.append({'title': t, 'price': info['final'], 'normal': info['initial'],
                      'savings': info['discount'], 'store': 'Steam'})
    else:
        no_info.append(t)  # on sale <10% or not on sale

deals.sort(key=lambda x: x['savings'], reverse=True)
print('DEALS_JSON:' + json.dumps({
    'deals': deals, 'upcoming': upcoming, 'no_deals': no_info,
    'errors': errors, 'total': len(games)
}))
