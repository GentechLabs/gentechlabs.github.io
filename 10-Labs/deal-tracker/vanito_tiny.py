"""Check titles for deals - tiny batch."""
import json, sys
sys.path.insert(0, '.')
from deal_tracker import CheapSharkClient

client = CheapSharkClient(cache_enabled=True)

titles_to_check = [
    "HUNGER", "ILL", "Holstin", "The Killing Antidote", "DarkSwarm"
]

for title in titles_to_check:
    deals = client.search_deals(title, upper_price=9999)
    if deals:
        best = deals[0]
        if best.savings > 0:
            print(f"DEAL|{title}|${best.sale_price}|{best.savings:.0f}% off|{best.store_name}")
        else:
            print(f"NODEAL|{title}")
    else:
        print(f"NODEAL|{title}")
