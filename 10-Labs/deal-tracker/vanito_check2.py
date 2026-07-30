"""Check remaining titles for deals."""
import json, sys
sys.path.insert(0, '.')
from deal_tracker import CheapSharkClient

client = CheapSharkClient(cache_enabled=True)

titles_to_check = [
    "Satisfactory",
    "The Texas Chain Saw Massacre",
    "HUNGER",
    "ILL",
    "ILL",
    "Holstin",
    "The Killing Antidote",
    "DarkSwarm",
    "Enginefall",
    "DEFECT",
    "Entities",
    "NAKWON: LAST PARADISE",
    "Better Than Dead",
    "Light No Fire",
    "The Midnight Walkers",
    "Displacement",
    "Valor Mortis",
    "SAW: Genesis",
    "Active Matter",
    "Fear The Timeloop",
    "Tempus Triad",
    "Underground: World War",
    "Acts of Blood",
    "Windrose",
    "The Headliners",
    "God Save Birmingham",
    "LIVING HELL",
    "GRAFT",
    "ArcheAge Chronicles",
    "The CUBE",
    "Mistfall Hunter",
    "Covenant",
    "HAEX",
    "Liquid Lungs",
    "DREADMOOR",
    "Samson",
    "The Revanchist",
    "Funnel Runners",
    "Project Retrograde: The Becoming",
    "Guns of Eschaton",
    "Bruisers 2D Boxing",
    "Kaidan",
    "Embers of the Uncrowned",
    "Terminal War",
    "P.O.N.",
    "Inferno Protocol",
    "Rules of Engagement: The Grey State",
    "Undead Chronicles",
    "Give Us A Sign",
    "PANLINE",
    "SHRAPNEL",
    "EMPULSE",
    "Elderfeast",
    "TERRORSTORM: Ground Zero",
    "DIOXIDE",
    "Bloody Lens",
    "HANDS OVER",
    "Turok: Origins",
    "Long Gone",
    "Hero's Journey",
    "NO LAW",
    "WARDOGS",
    "ENENRA: DAEMON CORE",
    "Endorphin Vice",
    "Blight: Survival",
    "FEROCIOUS",
    "Ad Mortem",
    "Clive Barker's Hellraiser: Revival",
    "Carnal Instinct",
    "SAND: Raiders of Sophie",
    "Deadlock",
    "beta decay",
    "State of Decay 3",
    "Project Warlock: Lost Chapters",
    "ROUTINE",
    "Lost Lands: Dark Overlord Collector's Edition",
    "Brawlhalla",
    "Out of Action",
    "The Mound: Omen of Cthulhu",
    "The Legend of California",
    "The Forever Winter",
    "Aliens: Fireteam Elite 2"
]

for title in titles_to_check:
    deals = client.search_deals(title, upper_price=9999)
    if deals:
        best = deals[0]
        savings = best.savings
        if savings > 0:
            print(f"DEAL|{title}|${best.sale_price}|{savings:.0f}% off|{best.store_name}")
        else:
            print(f"NODEAL|{title}")
    else:
        print(f"NODEAL|{title}")
