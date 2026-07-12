
from playwright.sync_api import sync_playwright
import json, sys
p = sync_playwright().start()
browser = p.chromium.launch(headless=True)
page = browser.new_page(user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')
page.goto('https://cantina.xyz/competitions', wait_until='networkidle', timeout=30000)
page.wait_for_timeout(3000)
cards = page.query_selector_all('a[href*="/competitions/"]')
out = []
for c in cards:
    href = c.get_attribute('href')
    text = c.inner_text()[:500]
    out.append({'href': href, 'text': text})
print(json.dumps(out))
browser.close()
p.stop()
