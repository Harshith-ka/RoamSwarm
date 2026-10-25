import pytest
import asyncio
from app.agents.graph import roamswarm_graph, execute_roamswarm_stream
from app.state import RoamSwarmState

@pytest.mark.asyncio
async def test_roamswarm_graph_execution():
    initial_state: RoamSwarmState = {
        "session_id": "test-sess-001",
        "landmark_id": "osm-node-kapaleeshwarar",
        "landmark_name": "Kapaleeshwarar Temple",
        "latitude": 13.0334,
        "longitude": 80.2699,
        "category": "worship_hindu",
        "language": "en",
        "story_style": "documentary",
        "duration_seconds": 60,
        "generate_audio": True,
        "status": "pending",
        "tool_calls": [],
        "execution_timeline": [],
        "retry_count": 0
    }

    # Execute graph synchronously
    result = await roamswarm_graph.ainvoke(initial_state)

    assert result["status"] in ["completed", "partial"]
    assert len(result["story_script"]) > 50
    assert len(result["citations"]) >= 1
    assert len(result["tool_calls"]) >= 2
    assert result["audio_url"] is not None
    assert "audio" in result["audio_url"]
    print("\n[SUCCESS] Generated Story Script Preview:\n", result["story_script"][:200], "...")

@pytest.mark.asyncio
async def test_roamswarm_sse_stream():
    initial_state: RoamSwarmState = {
        "session_id": "test-stream-002",
        "landmark_id": "osm-way-san-thome",
        "landmark_name": "San Thome Basilica",
        "latitude": 13.0336,
        "longitude": 80.2785,
        "category": "worship_christian",
        "language": "en",
        "story_style": "conversational",
        "duration_seconds": 60,
        "generate_audio": False,
        "status": "pending",
        "tool_calls": [],
        "execution_timeline": [],
        "retry_count": 0
    }

    events = []
    async for event in execute_roamswarm_stream(initial_state):
        events.append(event["event"])

    assert "workflow.started" in events
    assert "workflow.completed" in events
    print("\n[SUCCESS] Streamed events sequence:", events)
