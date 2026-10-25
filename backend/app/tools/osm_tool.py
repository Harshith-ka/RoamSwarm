import time
import httpx
import logging
from typing import List, Dict, Any, Optional
from app.config import settings
from app.state import LandmarkPOI

logger = logging.getLogger("roamswarm.tools.osm")

# In-memory cache for Nominatim & Overpass
_CACHE: Dict[str, Dict[str, Any]] = {}
_LAST_NOMINATIM_CALL = 0.0

def _get_cached(key: str) -> Optional[Any]:
    record = _CACHE.get(key)
    if record and (time.time() - record["timestamp"] < settings.CACHE_TTL_SECONDS):
        return record["data"]
    return None

def _set_cached(key: str, data: Any):
    _CACHE[key] = {"data": data, "timestamp": time.time()}

async def search_locations(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Search place names using OpenStreetMap Nominatim.
    Enforces strict rate-limiting (min 1.0 second between calls) and caching.
    """
    global _LAST_NOMINATIM_CALL
    query = query.strip()
    if not query:
        return []

    cache_key = f"nominatim_{query.lower()}_{limit}"
    cached = _get_cached(cache_key)
    if cached is not None:
        logger.info(f"Nominatim cache hit for '{query}'")
        return cached

    # Enforce 1-second delay between public Nominatim requests per OSM usage policy
    elapsed = time.time() - _LAST_NOMINATIM_CALL
    if elapsed < 1.0:
        import asyncio
        await asyncio.sleep(1.0 - elapsed)

    headers = {"User-Agent": settings.OSM_USER_AGENT}
    params = {
        "q": query,
        "format": "jsonv2",
        "limit": limit,
        "addressdetails": 1
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(settings.NOMINATIM_URL, params=params, headers=headers)
            _LAST_NOMINATIM_CALL = time.time()
            if resp.status_code == 200:
                results = []
                for item in resp.json():
                    results.append({
                        "display_name": item.get("display_name"),
                        "latitude": float(item.get("lat")),
                        "longitude": float(item.get("lon")),
                        "osm_type": item.get("osm_type"),
                        "osm_id": item.get("osm_id"),
                        "type": item.get("type"),
                        "importance": item.get("importance", 0.0)
                    })
                _set_cached(cache_key, results)
                return results
            else:
                logger.warning(f"Nominatim returned status {resp.status_code}: {resp.text}")
                return []
    except Exception as e:
        logger.error(f"Nominatim search failed for '{query}': {e}")
        return []

async def fetch_nearby_landmarks(
    latitude: float,
    longitude: float,
    radius_meters: int = 2500,
    category_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Query Overpass API for cultural, historical, religious and heritage POIs around coordinates.
    Deduplicates nodes/ways/relations and normalizes POI records.
    """
    cache_key = f"overpass_{latitude:.4f}_{longitude:.4f}_{radius_meters}_{category_filter}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    # Overpass QL query targeting monuments, museums, heritage, places of worship
    overpass_query = f"""
    [out:json][timeout:25];
    (
      node["historic"](around:{radius_meters},{latitude},{longitude});
      way["historic"](around:{radius_meters},{latitude},{longitude});
      node["tourism"~"museum|attraction|monument|artwork"](around:{radius_meters},{latitude},{longitude});
      way["tourism"~"museum|attraction|monument|artwork"](around:{radius_meters},{latitude},{longitude});
      node["amenity"="place_of_worship"](around:{radius_meters},{latitude},{longitude});
      way["amenity"="place_of_worship"](around:{radius_meters},{latitude},{longitude});
      node["heritage"](around:{radius_meters},{latitude},{longitude});
      way["heritage"](around:{radius_meters},{latitude},{longitude});
    );
    out center tags;
    """

    headers = {"User-Agent": settings.OSM_USER_AGENT}

    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(
                settings.OVERPASS_URL,
                data={"data": overpass_query},
                headers=headers
            )
            if resp.status_code == 200:
                data = resp.json()
                raw_elements = data.get("elements", [])
                pois = _normalize_and_deduplicate_pois(raw_elements, latitude, longitude)
                _set_cached(cache_key, pois)
                return pois
            else:
                logger.warning(f"Overpass API error {resp.status_code}: {resp.text[:200]}")
                return _get_fallback_pois(latitude, longitude)
    except Exception as e:
        logger.error(f"Overpass query failed: {e}")
        return _get_fallback_pois(latitude, longitude)

def _normalize_and_deduplicate_pois(
    elements: List[Dict[str, Any]],
    center_lat: float,
    center_lon: float
) -> List[Dict[str, Any]]:
    """
    Extract meaningful landmarks with names, deduplicate by name & proximity,
    and categorize into heritage, museum, worship, monument.
    """
    seen_names = set()
    normalized = []

    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name") or tags.get("name:en")
        if not name:
            continue  # Skip unnamed raw POIs

        clean_name = name.strip()
        name_key = clean_name.lower()
        if name_key in seen_names:
            continue
        seen_names.add(name_key)

        # Coordinate resolution (ways have 'center')
        lat = el.get("lat") or (el.get("center", {}).get("lat") if "center" in el else None)
        lon = el.get("lon") or (el.get("center", {}).get("lon") if "center" in el else None)
        if lat is None or lon is None:
            continue

        # Categorization
        category = "heritage"
        if "place_of_worship" in tags.get("amenity", "") or "religion" in tags:
            religion = tags.get("religion", "worship")
            category = f"worship_{religion}"
        elif tags.get("tourism") == "museum":
            category = "museum"
        elif tags.get("historic") in ["monument", "memorial"]:
            category = "monument"
        elif "historic" in tags or "heritage" in tags:
            category = "historical"
        elif tags.get("tourism") == "attraction":
            category = "attraction"

        # Calculate approximate distance in meters
        import math
        dlat = (lat - center_lat) * 111000
        dlon = (lon - center_lon) * 111000 * math.cos(math.radians(center_lat))
        dist = math.sqrt(dlat * dlat + dlon * dlon)

        poi = {
            "id": f"osm-{el.get('type', 'node')}-{el.get('id')}",
            "osm_type": el.get("type", "node"),
            "osm_id": el.get("id"),
            "name": clean_name,
            "latitude": float(lat),
            "longitude": float(lon),
            "category": category,
            "distance_meters": round(dist, 1),
            "tags": {
                "historic": tags.get("historic"),
                "tourism": tags.get("tourism"),
                "amenity": tags.get("amenity"),
                "religion": tags.get("religion"),
                "opening_hours": tags.get("opening_hours"),
                "wheelchair": tags.get("wheelchair"),
                "website": tags.get("website") or tags.get("contact:website"),
                "phone": tags.get("phone") or tags.get("contact:phone"),
                "fee": tags.get("fee"),
                "wikipedia": tags.get("wikipedia"),
                "wikidata": tags.get("wikidata"),
                "description": tags.get("description"),
                "start_date": tags.get("start_date") or tags.get("historic:civilization")
            }
        }
        normalized.append(poi)

    # Sort by distance
    normalized.sort(key=lambda x: x["distance_meters"])
    return normalized[:40]

def _get_fallback_pois(lat: float, lon: float) -> List[Dict[str, Any]]:
    """Curated fallback landmarks for Chennai pilot area if Overpass times out."""
    # Check if coordinates are near Chennai (~13.08, 80.27)
    if abs(lat - 13.08) < 0.2 and abs(lon - 80.27) < 0.2:
        return [
            {
                "id": "osm-way-chennai-san-thome",
                "osm_type": "way",
                "osm_id": 987654321,
                "name": "San Thome Basilica",
                "latitude": 13.0336,
                "longitude": 80.2785,
                "category": "worship_christian",
                "distance_meters": 1200.0,
                "tags": {
                    "historic": "church",
                    "tourism": "attraction",
                    "opening_hours": "06:00-21:00",
                    "wikipedia": "en:San Thome Basilica",
                    "start_date": "1523"
                }
            },
            {
                "id": "osm-node-chennai-fort-st-george",
                "osm_type": "node",
                "osm_id": 123456789,
                "name": "Fort St. George",
                "latitude": 13.0797,
                "longitude": 80.2875,
                "category": "historical",
                "distance_meters": 1800.0,
                "tags": {
                    "historic": "fort",
                    "tourism": "museum",
                    "opening_hours": "09:00-17:00",
                    "wikipedia": "en:Fort St. George, India",
                    "start_date": "1644"
                }
            },
            {
                "id": "osm-node-chennai-kapaleeshwarar",
                "osm_type": "node",
                "osm_id": 345678901,
                "name": "Kapaleeshwarar Temple",
                "latitude": 13.0334,
                "longitude": 80.2699,
                "category": "worship_hindu",
                "distance_meters": 2100.0,
                "tags": {
                    "amenity": "place_of_worship",
                    "religion": "hindu",
                    "historic": "temple",
                    "wikipedia": "en:Kapaleeshwarar Temple",
                    "start_date": "7th century"
                }
            }
        ]
    return []
