import time
import logging
from typing import Dict, Any, List
from app.state import RoamSwarmState
from app.tools.venue_tool import analyze_venue_details
from app.tools.web_search_tool import search_live_sources

logger = logging.getLogger("roamswarm.agents.live_scout")

async def run_live_scout(state: RoamSwarmState) -> Dict[str, Any]:
    """
    Live Scout Agent:
    Retrieves venue facts, operating hours, visitor guidelines, and freshness labels.
    Never presents unverified schedules as confirmed live information.
    """
    start_time = time.time()
    landmark_name = state.get("landmark_name", "Unknown Landmark")
    
    new_tool_calls: List[Dict[str, Any]] = []
    new_timeline: List[Dict[str, Any]] = [{
        "event": "live_scout_started",
        "agent": "Live Scout",
        "timestamp": start_time,
        "detail": f"Auditing venue operational tags and current access status for '{landmark_name}'."
    }]

    # Prepare OSM tags
    osm_tags = {}
    if isinstance(state.get("category"), dict):
        osm_tags = state.get("category")

    # Tool Execution 1: Analyze OSM venue attributes
    t1_start = time.time()
    venue_analysis = analyze_venue_details(osm_tags, landmark_name)
    t1_duration = (time.time() - t1_start) * 1000

    new_tool_calls.append({
        "agent_name": "Live Scout",
        "tool_name": "analyze_venue_details",
        "sanitized_input": {"landmark_name": landmark_name, "tags_present": list(osm_tags.keys())},
        "sanitized_output": {
            "overall_status": venue_analysis.get("overall_status"),
            "facts_count": len(venue_analysis.get("facts", []))
        },
        "duration_ms": round(t1_duration, 1),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "success": True
    })

    # Tool Execution 2: If opening hours missing, search live web for venue hours
    if not venue_analysis.get("has_confirmed_hours"):
        t2_start = time.time()
        search_query = f"{landmark_name} opening hours timings visitor admission"
        live_search_results = await search_live_sources(search_query, max_results=2)
        t2_duration = (time.time() - t2_start) * 1000

        new_tool_calls.append({
            "agent_name": "Live Scout",
            "tool_name": "search_live_sources",
            "sanitized_input": {"query": search_query},
            "sanitized_output": {"results_found": len(live_search_results)},
            "duration_ms": round(t2_duration, 1),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "success": len(live_search_results) > 0
        })

        if live_search_results:
            top_res = live_search_results[0]
            venue_analysis["facts"].append({
                "attribute": "web_reported_hours",
                "value": top_res.get("snippet", "")[:160],
                "status": "unverified",
                "confidence": 0.6,
                "source": top_res.get("url", "Web"),
                "note": "Reported on external travel page. Unverified by official OSM entity."
            })

    total_duration = (time.time() - start_time) * 1000
    new_timeline.append({
        "event": "live_scout_completed",
        "agent": "Live Scout",
        "timestamp": time.time(),
        "detail": f"Resolved venue status '{venue_analysis['overall_status']}' with {len(venue_analysis['facts'])} attributes ({round(total_duration, 1)}ms)."
    })

    return {
        "current_agent": "Live Scout",
        "venue_facts": venue_analysis.get("facts", []),
        "tool_calls": new_tool_calls,
        "execution_timeline": new_timeline
    }
