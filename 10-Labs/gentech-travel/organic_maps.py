"""
GenTech Travel Agent — Organic Maps Integration
Local POIs, attractions, and route planning via OpenStreetMap.
No API key needed — uses OSM's free public API.
"""

import json, os
from dataclasses import dataclass
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import URLError

OSM_API = "https://overpass-api.de/api/interpreter"
NOMINATIM_API = "https://nominatim.openstreetmap.org"

class OrganicMapsError(Exception):
    pass


@dataclass
class POI:
    name: str
    lat: float
    lon: float
    category: str  # restaurant, museum, park, hotel, etc.
    address: Optional[str] = None
    rating: Optional[float] = None
    website: Optional[str] = None
    phone: Optional[str] = None


def geocode(location: str) -> tuple[float, float]:
    """Convert a place name to lat/lon coordinates."""
    url = f"{NOMINATIM_API}/search?q={location.replace(' ', '+')}&format=json&limit=1"
    try:
        with urlopen(Request(url, headers={"User-Agent": "GenTechTravel/1.0"}), timeout=10) as resp:
            data = json.loads(resp.read())
            if data:
                return (float(data[0]["lat"]), float(data[0]["lon"]))
            raise OrganicMapsError(f"Location not found: {location}")
    except URLError as e:
        raise OrganicMapsError(f"Geocode failed: {e}")


def search_pois(lat: float, lon: float, radius_m: int = 1000, categories: list[str] = None) -> list[POI]:
    """Search for POIs near coordinates using Overpass API."""
    if categories is None:
        categories = ["restaurant", "museum", "park", "cafe", "hotel", "attraction"]

    # Build Overpass QL query
    tags = " ".join(f'["tourism"="{c}"]' for c in categories if c in ("museum", "attraction", "hotel"))
    tags += " ".join(f'["amenity"="{c}"]' for c in categories if c in ("restaurant", "cafe"))
    tags += '["leisure"="park"]' if "park" in categories else ""

    query = f"""
    [out:json];
    (
      node(around:{radius_m},{lat},{lon}){tags};
      way(around:{radius_m},{lat},{lon}){tags};
    );
    out center 20;
    """

    try:
        req = Request(
            OSM_API,
            data=query.encode(),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except URLError as e:
        raise OrganicMapsError(f"Overpass query failed: {e}")

    pois = []
    for el in data.get("elements", []):
        name = el.get("tags", {}).get("name", "")
        if not name:
            continue
        lat_p = el.get("lat") or el.get("center", {}).get("lat", lat)
        lon_p = el.get("lon") or el.get("center", {}).get("lon", lon)
        tags = el.get("tags", {})

        # Determine category
        cat = "attraction"
        for c in categories:
            if tags.get("tourism") == c or tags.get("amenity") == c or tags.get("leisure") == c:
                cat = c
                break

        pois.append(POI(
            name=name,
            lat=lat_p,
            lon=lon_p,
            category=cat,
            address=tags.get("addr:full") or tags.get("addr:street", ""),
            website=tags.get("website"),
            phone=tags.get("phone"),
        ))

    return pois


def get_route(origin: tuple[float, float], dest: tuple[float, float]) -> dict:
    """Get driving route between two points using OSRM."""
    url = (
        f"https://router.project-osrm.org/route/v1/driving/"
        f"{origin[1]},{origin[0]};{dest[1]},{dest[0]}"
        f"?overview=full&geometries=geojson"
    )
    try:
        with urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read())
            if data.get("code") != "Ok" or not data.get("routes"):
                raise OrganicMapsError("No route found")
            route = data["routes"][0]
            return {
                "distance_km": round(route["distance"] / 1000, 1),
                "duration_min": round(route["duration"] / 60, 0),
                "geometry": route["geometry"],
            }
    except URLError as e:
        raise OrganicMapsError(f"Route failed: {e}")


# ── CLI ──

if __name__ == "__main__":
    import sys, argparse

    parser = argparse.ArgumentParser(description="GenTech Travel — Organic Maps")
    parser.add_argument("action", choices=["pois", "route", "geocode"])
    parser.add_argument("--location", help="City or place name")
    parser.add_argument("--lat", type=float)
    parser.add_argument("--lon", type=float)
    parser.add_argument("--radius", type=int, default=1000)
    parser.add_argument("--from-lat", type=float)
    parser.add_argument("--from-lon", type=float)
    parser.add_argument("--to-lat", type=float)
    parser.add_argument("--to-lon", type=float)
    args = parser.parse_args()

    try:
        if args.action == "geocode":
            if not args.location:
                print("Usage: organic_maps.py geocode --location Tokyo")
                sys.exit(1)
            lat, lon = geocode(args.location)
            print(f"📍 {args.location}: {lat}, {lon}")

        elif args.action == "pois":
            if args.location:
                lat, lon = geocode(args.location)
            elif args.lat and args.lon:
                lat, lon = args.lat, args.lon
            else:
                print("Usage: organic_maps.py pois --location Tokyo [--radius 1000]")
                sys.exit(1)
            pois = search_pois(lat, lon, args.radius)
            print(f"📍 Found {len(pois)} POIs near ({lat:.4f}, {lon:.4f})")
            for p in pois[:10]:
                print(f"  • {p.name} ({p.category})")

        elif args.action == "route":
            if not all([args.from_lat, args.from_lon, args.to_lat, args.to_lon]):
                print("Usage: organic_maps.py route --from-lat 35.6 --from-lon 139.7 --to-lat 35.7 --to-lon 139.8")
                sys.exit(1)
            route = get_route((args.from_lat, args.from_lon), (args.to_lat, args.to_lon))
            print(f"🚗 {route['distance_km']} km — {route['duration_min']} min")

    except OrganicMapsError as e:
        print(f"❌ {e}")
        sys.exit(1)
