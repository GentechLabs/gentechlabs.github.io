"""Check specific titles for deals."""
import json, sys
sys.path.insert(0, '.')
from deal_tracker import CheapSharkClient

client = CheapSharkClient(cache_enabled=True)

titles_to_check = [
    "Satisfactory",
    "Resident Evil 3", 
    "Marvel Rivals",
    "Deep Rock Galactic: Rogue Core",
    "Aliens: Fireteam Elite 2",
    "Murky Divers",
    "The Texas Chain Saw Massacre",
    "Orcs Must Die! Deathtrap",
    "Blight: Survival",
    "The Forever Winter"
]

for title in titles_to_check:
    deals = client.search_deals(title, upper_price=9999)
    if deals:
        best = deals[0]
        print(f"DEAL|{title}|${best.sale_price}|{best.savings:.0f}% off|{best.store_name}")
    else:
        print(f"NODEAL|{title}")
