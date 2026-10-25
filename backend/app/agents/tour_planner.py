import math
import time
from typing import List, Dict, Any
from app.state import LandmarkPOI
from app.agents.storyteller import _synthesize_deterministic_narrative
from app.tools.tts_tool import synthesize_speech

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in meters between two lat/lon points."""
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)

def optimize_walking_itinerary(landmarks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Greedy nearest-neighbor ordering for walkable itinerary between selected landmarks.
    Computes leg-by-leg distances, walking pace (~4.5 km/h), and route waypoints.
    """
    if not landmarks:
        return {"waypoints": [], "total_distance_meters": 0, "total_walking_minutes": 0}

    unvisited = list(landmarks)
    current = unvisited.pop(0)
    ordered_waypoints = [current]
    total_dist = 0.0

    while unvisited:
        # Find nearest unvisited landmark
        nearest_idx = 0
        min_dist = float("inf")
        c_lat = current.get("latitude", 0.0)
        c_lon = current.get("longitude", 0.0)

        for i, cand in enumerate(unvisited):
            dist = haversine_distance(c_lat, c_lon, cand.get("latitude", 0.0), cand.get("longitude", 0.0))
            if dist < min_dist:
                min_dist = dist
                nearest_idx = i

        next_stop = unvisited.pop(nearest_idx)
        total_dist += min_dist
        next_stop["leg_distance_meters"] = min_dist
        next_stop["walking_minutes"] = round(min_dist / 75.0, 1) # ~75 meters/min (4.5 km/h)
        ordered_waypoints.append(next_stop)
        current = next_stop

    # First stop has 0 leg distance
    ordered_waypoints[0]["leg_distance_meters"] = 0
    ordered_waypoints[0]["walking_minutes"] = 0

    total_walk_mins = round(total_dist / 75.0, 1)

    return {
        "waypoints": ordered_waypoints,
        "total_distance_meters": round(total_dist, 1),
        "total_walking_minutes": total_walk_mins
    }

async def plan_curated_tour(
    landmarks: List[Dict[str, Any]],
    tour_title: str = "Curated Urban Heritage Trail",
    theme: str = "historical"
) -> Dict[str, Any]:
    """
    Synthesize an overarching multi-stop walking tour.
    Combines route optimization with unified narrative storytelling.
    """
    itinerary = optimize_walking_itinerary(landmarks)
    waypoints = itinerary["waypoints"]

    # Synthesize thematic narrative connecting stops
    names = [w.get("name", "Landmark") for w in waypoints]
    intro = f"Welcome to the {tour_title}. Today's curated route connects {len(waypoints)} significant urban landmarks: {', '.join(names)}."
    
    stop_narratives = []
    for idx, stop in enumerate(waypoints, 1):
        walk_note = f"After a {stop.get('walking_minutes', 0)} minute stroll from the previous stop" if idx > 1 else "Beginning our journey here"
        stop_narratives.append(
            f"Stop {idx}: {stop.get('name')}. {walk_note}, we arrive at this {stop.get('category', 'heritage')} milestone, notable for its architectural presence and local lore."
        )

    outro = f"This walking loop spans approximately {round(itinerary['total_distance_meters']/1000, 2)} kilometers with an estimated {itinerary['total_walking_minutes']} minutes of walking."
    tour_script = f"{intro}\n\n" + "\n\n".join(stop_narratives) + f"\n\n{outro}"

    # Generate Tour Audio
    tts_res = await synthesize_speech(tour_script, story_id=f"tour_{int(time.time())}")

    return {
        "tour_id": f"tour_{int(time.time())}",
        "title": tour_title,
        "theme": theme,
        "waypoints": waypoints,
        "total_distance_meters": itinerary["total_distance_meters"],
        "total_walking_minutes": itinerary["total_walking_minutes"],
        "tour_script": tour_script,
        "audio_url": tts_res.get("playback_url"),
        "audio_duration_seconds": tts_res.get("duration_seconds", 0.0)
    }
