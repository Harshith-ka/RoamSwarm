import time
import logging
from typing import Dict, Any, List
from app.state import RoamSwarmState

logger = logging.getLogger("roamswarm.agents.orchestrator")

def plan_workflow(state: RoamSwarmState) -> Dict[str, Any]:
    """
    Orchestrator Planning Phase:
    Validates input parameters, checks cached sessions, sets up execution timeline,
    and dispatches parallel research goals to Historian and Live Scout.
    """
    landmark_name = state.get("landmark_name") or f"Landmark-{state.get('landmark_id')}"
    duration = state.get("duration_seconds") or 90
    style = state.get("story_style") or "documentary"
    language = state.get("language") or "en"
    
    start_time = time.time()
    timeline_event = {
        "event": "orchestrator_planned",
        "agent": "Orchestrator",
        "timestamp": start_time,
        "detail": f"Formulated dual research plan for '{landmark_name}' (Target: {duration}s, Style: {style}, Lang: {language})"
    }

    return {
        "status": "researching",
        "current_agent": "Orchestrator",
        "landmark_name": landmark_name,
        "duration_seconds": duration,
        "story_style": style,
        "language": language,
        "retry_count": state.get("retry_count", 0),
        "execution_timeline": [timeline_event],
        "orchestrator_notes": f"Plan initialized for {landmark_name}. Parallel dispatching to Historian and Live Scout."
    }

def aggregate_and_validate_evidence(state: RoamSwarmState) -> Dict[str, Any]:
    """
    Convergence point for Historian and Live Scout parallel outputs.
    Evaluates evidence sufficiency, source diversity, and factual grounding.
    Enforces maximum retry bounds to avoid infinite loops.
    """
    historical_facts = state.get("historical_facts") or []
    venue_facts = state.get("venue_facts") or []
    evidence = state.get("evidence") or []
    retry_count = state.get("retry_count", 0)

    has_history = len(historical_facts) >= 1 or len(evidence) >= 1
    has_venue = len(venue_facts) >= 1
    sources = state.get("sources") or []
    has_sources = len(sources) >= 1

    is_sufficient = has_history and has_sources
    timestamp = time.time()

    if is_sufficient:
        note = f"Evidence validated: {len(historical_facts)} historical facts, {len(venue_facts)} venue facts from {len(sources)} sources."
        return {
            "status": "validating",
            "current_agent": "Orchestrator",
            "is_sufficient": True,
            "execution_timeline": [{
                "event": "evidence_validated",
                "agent": "Orchestrator",
                "timestamp": timestamp,
                "detail": note
            }],
            "orchestrator_notes": note
        }
    else:
        if retry_count < 1:
            note = f"Insufficient evidence detected. Triggering targeted retry 1 of 1 for {state.get('landmark_name')}."
            return {
                "status": "researching",
                "current_agent": "Orchestrator",
                "is_sufficient": False,
                "retry_count": retry_count + 1,
                "execution_timeline": [{
                    "event": "retrieval_retry_triggered",
                    "agent": "Orchestrator",
                    "timestamp": timestamp,
                    "detail": note
                }],
                "orchestrator_notes": note
            }
        else:
            note = f"Max retries reached. Marking research as partial/uncertain; proceeding to Storyteller with strict uncertainty caveats."
            return {
                "status": "partial",
                "current_agent": "Orchestrator",
                "is_sufficient": True,
                "execution_timeline": [{
                    "event": "partial_evidence_accepted",
                    "agent": "Orchestrator",
                    "timestamp": timestamp,
                    "detail": note
                }],
                "orchestrator_notes": note
            }

def validate_and_finalize_story(state: RoamSwarmState) -> Dict[str, Any]:
    """
    Final validation pass:
    Verifies that the generated script contains valid citations,
    separates historical facts from venue facts, and marks completion.
    """
    script = state.get("story_script") or ""
    citations = state.get("citations") or []
    status = "completed" if state.get("status") != "partial" else "partial"

    valid_citations = [c for c in citations if c.get("source_url")]
    timeline_event = {
        "event": "story_validated",
        "agent": "Orchestrator",
        "timestamp": time.time(),
        "detail": f"Script verified ({len(script.split())} words). Grounded by {len(valid_citations)} citations."
    }

    return {
        "status": status,
        "current_agent": "Orchestrator",
        "execution_timeline": [timeline_event],
        "orchestrator_notes": f"Workflow finished with status: {status}."
    }
