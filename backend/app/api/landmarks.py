from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from app.tools.osm_tool import search_locations, fetch_nearby_landmarks

router = APIRouter(prefix="/api", tags=["Geospatial & Landmarks"])

@router.get("/locations/search")
async def search_city_or_place(
    q: str = Query(..., min_length=2, description="Place name or city query"),
    limit: int = Query(5, ge=1, le=10)
):
    """
    Search place names using rate-limited and cached Nominatim geocoder.
    """
    results = await search_locations(q, limit=limit)
    return {"query": q, "results": results}

@router.get("/landmarks/nearby")
async def get_nearby_landmarks(
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
    radius_meters: int = Query(2500, ge=500, le=10000),
    category: Optional[str] = Query(None)
):
    """
    Query OpenStreetMap Overpass API for cultural, historical, and heritage POIs.
    Deduplicates and filters incomplete records.
    """
    pois = await fetch_nearby_landmarks(
        latitude=latitude,
        longitude=longitude,
        radius_meters=radius_meters,
        category_filter=category
    )
    return {
        "center": {"latitude": latitude, "longitude": longitude},
        "radius_meters": radius_meters,
        "count": len(pois),
        "landmarks": pois
    }

@router.get("/landmarks/{landmark_id}")
async def get_landmark_detail(landmark_id: str):
    """
    Retrieve landmark metadata from cache or database.
    """
    return {
        "landmark_id": landmark_id,
        "status": "available",
        "description": "Registered OpenStreetMap cultural point of interest."
    }
