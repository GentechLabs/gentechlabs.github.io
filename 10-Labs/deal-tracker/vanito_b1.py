"""Check more titles for deals - small batch."""
import json, sys
sys.path.insert(0, '.')
from deal_tracker import CheapSharkClient

client = CheapSharkClient(cache_enabled=True)

titles_to_check = [
    "HUNGER", "ILL", "Holstin", "The Killing Antidote", "DarkSwarm",
    "Enginefall", "DEFECT", "Entities", "NAKWON: LAST PARADISE", "Better Than Dead",
    "Light No Fire", "The Midnight Walkers", "Displacement", "Valor Mortis", "SAW: Genesis",
    "Active Matter", "Fear The Timeloop", "Tempus Triad", "Underground: World War", "Acts of Blood",
    "Windrose", "The Headliners", "God Save Birmingham", "LIVING HELL", "GRAFT"
]

for title in titles_to_check:
    deals = client.search_deals(title, upper_price=9999)
    if deals:
        best = deals[0]
        if best.savings > 0:
            print(f"DEAL|{title}|${best.sale_price}|{best.savings:.0f}% off|{best.store_name}")
