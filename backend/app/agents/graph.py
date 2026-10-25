import time
import logging
from typing import AsyncGenerator, Dict, Any
from langgraph.graph import StateGraph, START, END
from app.state import RoamSwarmState
from app.agents.orchestrator import (
    plan_workflow,
    aggregate_and_validate_evidence,
    validate_and_finalize_story
)
from app.agents.historian import run_historian
from app.agents.live_scout import run_live_scout
from app.agents.storyteller import run_storyteller
from app.tools.tts_tool import synthesize_speech

logger = logging.getLogger("roamswarm.graph")

async def run_audio_synthesis_node(state: RoamSwarmState) -> Dict[str, Any]:
    """
    Audio generation node:
    Synthesizes audio narration asynchronously once script is finalized.
    """
    if not state.get("generate_audio", True):
        return {"audio_url": None, "audio_duration_seconds": 0.0}

    script = state.get("story_script", "")
    language = state.get("language", "en")
    session_id = state.get("session_id", "sess")

    tts_result = await synthesize_speech(
        script=script,
        language=language,
        story_id=session_id
    )

    timeline_event = {
        "event": "audio_synthesis_completed",
        "agent": "Speech Synthesizer",
        "timestamp": time.time(),
        "detail": f"Audio artifact created: {tts_result.get('playback_url')} ({tts_result.get('duration_seconds')}s)."
    }

    return {
        "status": "completed" if state.get("status") != "partial" else "partial",
        "audio_url": tts_result.get("playback_url"),
        "audio_duration_seconds": tts_result.get("duration_seconds", 0.0),
        "execution_timeline": [timeline_event]
    }

def route_after_aggregation(state: RoamSwarmState) -> str:
    """
    Conditional routing function:
    Retries research if evidence is insufficient and retry limit has not been exceeded.
    Otherwise proceeds to Storyteller.
    """
    if not state.get("is_sufficient", True) and state.get("retry_count", 0) <= 1:
        return "retry"
    return "proceed"

def create_roamswarm_graph() -> StateGraph:
    """
    Assemble the LangGraph 4-Agent Workflow for RoamSwarm.
    """
    workflow = StateGraph(RoamSwarmState)

    # Register agent and tool nodes
    workflow.add_node("orchestrator_plan", plan_workflow)
    workflow.add_node("historian_research", run_historian)
    workflow.add_node("live_scout_research", run_live_scout)
    workflow.add_node("aggregate_and_validate", aggregate_and_validate_evidence)
    workflow.add_node("storyteller_generate", run_storyteller)
    workflow.add_node("validate_and_finalize", validate_and_finalize_story)
    workflow.add_node("synthesize_audio", run_audio_synthesis_node)

    # Define edges: START -> Orchestrator Plan
    workflow.add_edge(START, "orchestrator_plan")

    # Parallel Research Branches from Orchestrator
    workflow.add_edge("orchestrator_plan", "historian_research")
    workflow.add_edge("orchestrator_plan", "live_scout_research")

    # Both parallel branches join into Convergence Validator
    workflow.add_edge("historian_research", "aggregate_and_validate")
    workflow.add_edge("live_scout_research", "aggregate_and_validate")

    # Conditional Routing: Retry or Proceed
    workflow.add_conditional_edges(
        "aggregate_and_validate",
        route_after_aggregation,
        {
            "retry": "historian_research",
            "proceed": "storyteller_generate"
        }
    )

    # Narrative generation -> Orchestrator Final Validation -> Audio Synthesis -> END
    workflow.add_edge("storyteller_generate", "validate_and_finalize")
    workflow.add_edge("validate_and_finalize", "synthesize_audio")
    workflow.add_edge("synthesize_audio", END)

    return workflow.compile()

# Singleton compiled graph instance
roamswarm_graph = create_roamswarm_graph()

async def execute_roamswarm_stream(initial_state: RoamSwarmState) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Executes the compiled LangGraph workflow step-by-step and yields real-time
    execution updates suitable for Server-Sent Events (SSE).
    """
    yield {
        "event": "workflow.started",
        "session_id": initial_state.get("session_id"),
        "landmark_name": initial_state.get("landmark_name"),
        "timestamp": time.time()
    }

    current_state = dict(initial_state)

    async for chunk in roamswarm_graph.astream(initial_state, stream_mode="updates"):
        for node_name, updates in chunk.items():
            current_state.update(updates)
            
            event_type = f"agent.{node_name}"
            if "historian" in node_name:
                event_type = "agent.historian.completed"
            elif "scout" in node_name:
                event_type = "agent.live_scout.completed"
            elif "storyteller" in node_name:
                event_type = "story.ready"
            elif "synthesize_audio" in node_name:
                event_type = "audio.ready"

            yield {
                "event": event_type,
                "node": node_name,
                "current_agent": updates.get("current_agent", node_name),
                "status": updates.get("status", current_state.get("status")),
                "tool_calls": current_state.get("tool_calls", []),
                "timeline_latest": current_state.get("execution_timeline", [])[-1] if current_state.get("execution_timeline") else None,
                "story_script": current_state.get("story_script"),
                "audio_url": current_state.get("audio_url"),
                "citations": current_state.get("citations", []),
                "timestamp": time.time()
            }

    yield {
        "event": "workflow.completed",
        "session_id": current_state.get("session_id"),
        "final_status": current_state.get("status"),
        "state": current_state,
        "timestamp": time.time()
    }
