from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import re

def analyze_venue_details(
    osm_tags: Dict[str, Any],
    landmark_name: str,
    web_venue_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Synthesize venue access details from OSM tags and web findings.
    Assigns strict freshness statuses: 'verified', 'stale', 'missing', or 'unverified'.
    Never presents an unverified opening status as confirmed live information.
    """
    now = datetime.now(timezone.utc).isoformat()
    facts: List[Dict[str, Any]] = []

    opening_hours_raw = osm_tags.get("opening_hours")
    website = osm_tags.get("website") or (web_venue_info.get("website") if web_venue_info else None)
    phone = osm_tags.get("phone") or (web_venue_info.get("phone") if web_venue_info else None)
    wheelchair = osm_tags.get("wheelchair")
    fee = osm_tags.get("fee")

    # 1. Opening hours analysis
    if opening_hours_raw:
        facts.append({
            "attribute": "opening_hours",
            "value": opening_hours_raw,
            "status": "verified",
            "confidence": 0.85,
            "source": "OpenStreetMap Tags",
            "note": "Standard operating schedule recorded in OSM."
        })
    elif web_venue_info and web_venue_info.get("opening_hours"):
        facts.append({
            "attribute": "opening_hours",
            "value": web_venue_info["opening_hours"],
            "status": "unverified",
            "confidence": 0.65,
            "source": web_venue_info.get("source_url", "Web Search"),
            "note": "Reported online; requires on-site verification."
        })
    else:
        facts.append({
            "attribute": "opening_hours",
            "value": "Schedule not officially verified",
            "status": "missing",
            "confidence": 0.0,
            "source": "OSM/Live Scout",
            "note": "Visitors are advised to check directly before visiting."
        })

    # 2. Admission / Fee analysis
    if fee is not None:
        fee_str = "Free admission" if str(fee).lower() in ["no", "0", "free"] else f"Entry fee applies: {fee}"
        facts.append({
            "attribute": "admission",
            "value": fee_str,
            "status": "verified",
            "confidence": 0.9,
            "source": "OpenStreetMap",
            "note": "Tagged in community registry."
        })
    else:
        facts.append({
            "attribute": "admission",
            "value": "Admission policy unconfirmed",
            "status": "unverified",
            "confidence": 0.4,
            "source": "Live Scout",
            "note": "May be free or require ticket depending on special exhibits."
        })

    # 3. Accessibility
    if wheelchair:
        accessibility_label = "Wheelchair accessible" if wheelchair in ["yes", "designated"] else f"Wheelchair status: {wheelchair}"
        facts.append({
            "attribute": "accessibility",
            "value": accessibility_label,
            "status": "verified",
            "confidence": 0.85,
            "source": "OpenStreetMap Accessibility Metadata",
            "note": "Verified facility access tag."
        })

    # 4. Official Contact / Web
    if website:
        facts.append({
            "attribute": "website",
            "value": website,
            "status": "verified",
            "confidence": 0.95,
            "source": "Official / Registered Link",
            "note": "Official landmark portal."
        })

    if phone:
        facts.append({
            "attribute": "phone",
            "value": phone,
            "status": "verified",
            "confidence": 0.8,
            "source": "OSM Contact Data",
            "note": "Venue telephone contact."
        })

    # Determine overall venue status
    verified_count = sum(1 for f in facts if f["status"] == "verified")
    overall_status = "verified" if verified_count >= 2 else ("partial" if verified_count == 1 else "unverified")

    return {
        "landmark_name": landmark_name,
        "analyzed_at": now,
        "overall_status": overall_status,
        "facts": facts,
        "has_confirmed_hours": any(f["attribute"] == "opening_hours" and f["status"] == "verified" for f in facts),
        "source_attribution": "Live Scout OSM & Open Web Analysis"
    }
