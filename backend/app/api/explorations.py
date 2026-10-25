import json
import uuid
import time
import asyncio
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.database.session import get_db, AsyncSessionLocal
from app.database.models import ExplorationSession, Story, AudioArtifact, ToolExecution, AgentRun
from app.state import ExplorationRequest, ExplorationSessionResponse, RoamSwarmState
from app.agents.graph import roamswarm_graph, execute_roamswarm_stream

router = APIRouter(prefix="/api/explorations", tags=["Exploration Sessions"])

# In-memory session state store for real-time SSE streaming & quick access
_ACTIVE_SESSIONS: Dict[str, Dict[str, Any]] = {}

async def _run_workflow_background(session_id: str, initial_state: RoamSwarmState):
    """
    Executes LangGraph workflow in background, updates in-memory state,
    and persists final results and traces to database.
    """
    try:
        _ACTIVE_SESSIONS[session_id]["status"] = "researching"
        final_state = await roamswarm_graph.ainvoke(initial_state)
        _ACTIVE_SESSIONS[session_id].update(final_state)
        _ACTIVE_SESSIONS[session_id]["status"] = final_state.get("status", "completed")
        _ACTIVE_SESSIONS[session_id]["completed_at"] = datetime.now(timezone.utc).isoformat()

        # Persist to database
        async with AsyncSessionLocal() as db:
            sess_record = await db.get(ExplorationSession, session_id)
            if sess_record:
                sess_record.status = _ACTIVE_SESSIONS[session_id]["status"]
                sess_record.completed_at = datetime.now(timezone.utc)
                
                # Persist Story
                script = final_state.get("story_script")
                if script:
                    story = Story(
                        id=f"story-{session_id}",
                        session_id=session_id,
                        script=script,
                        language=final_state.get("language", "en"),
                        style=final_state.get("story_style", "documentary"),
                        citations_data=final_state.get("citations", [])
                    )
                    db.add(story)

                    # Persist Audio Artifact
                    audio_url = final_state.get("audio_url")
                    if audio_url:
                        audio = AudioArtifact(
                            id=f"audio-{session_id}",
                            story_id=story.id,
                            storage_path=audio_url,
                            playback_url=audio_url,
                            duration_seconds=final_state.get("audio_duration_seconds", 0.0)
                        )
                        db.add(audio)

                await db.commit()
    except Exception as e:
        _ACTIVE_SESSIONS[session_id]["status"] = "failed"
        _ACTIVE_SESSIONS[session_id]["errors"] = [str(e)]

@router.post("", response_model=Dict[str, Any])
async def start_exploration(
    req: ExplorationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Initiates an exploration session and launches the LangGraph workflow asynchronously.
    Returns session ID immediately to client.
    """
    session_id = f"sess_{uuid.uuid4().hex[:12]}"
    landmark_name = req.landmark_name or req.landmark_id

    # Create DB record
    db_session = ExplorationSession(
        id=session_id,
        landmark_id=req.landmark_id,
        landmark_name=landmark_name,
        latitude=req.latitude,
        longitude=req.longitude,
        status="pending",
        language=req.language,
        story_style=req.story_style,
        duration_seconds=req.duration_seconds
    )
    db.add(db_session)
    await db.commit()

    initial_state: RoamSwarmState = {
        "session_id": session_id,
        "landmark_id": req.landmark_id,
        "landmark_name": landmark_name,
        "latitude": req.latitude or 0.0,
        "longitude": req.longitude or 0.0,
        "category": req.category or "heritage",
        "language": req.language,
        "story_style": req.story_style,
        "duration_seconds": req.duration_seconds,
        "generate_audio": req.generate_audio,
        "status": "pending",
        "tool_calls": [],
        "execution_timeline": [],
        "retry_count": 0,
        "sources": [],
        "evidence": [],
        "historical_facts": [],
        "venue_facts": []
    }

    _ACTIVE_SESSIONS[session_id] = {
        **initial_state,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    # Launch LangGraph in background
    background_tasks.add_task(_run_workflow_background, session_id, initial_state)

    return {
        "session_id": session_id,
        "landmark_id": req.landmark_id,
        "landmark_name": landmark_name,
        "status": "pending",
        "events_stream_url": f"/api/explorations/{session_id}/events"
    }

@router.get("/{session_id}", response_model=Dict[str, Any])
async def get_exploration_state(session_id: str, db: AsyncSession = Depends(get_db)):
    """
    Retrieve full state of an exploration session.
    """
    if session_id in _ACTIVE_SESSIONS:
        return _ACTIVE_SESSIONS[session_id]

    sess = await db.get(ExplorationSession, session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": sess.id,
        "landmark_id": sess.landmark_id,
        "landmark_name": sess.landmark_name,
        "status": sess.status,
        "language": sess.language,
        "story_style": sess.story_style,
        "duration_seconds": sess.duration_seconds,
        "created_at": sess.created_at.isoformat() if sess.created_at else None,
        "completed_at": sess.completed_at.isoformat() if sess.completed_at else None
    }

@router.get("/{session_id}/events")
async def stream_exploration_events(session_id: str):
    """
    Server-Sent Events (SSE) endpoint:
    Streams live agent activation, tool execution, and story progress events.
    """
    session_data = _ACTIVE_SESSIONS.get(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found in active streams")

    async def sse_event_generator():
        # Re-stream from current state
        last_event_idx = 0
        while True:
            current = _ACTIVE_SESSIONS.get(session_id)
            if not current:
                break

            timeline = current.get("execution_timeline") or []
            while last_event_idx < len(timeline):
                ev = timeline[last_event_idx]
                payload = json.dumps({
                    "event": ev.get("event"),
                    "agent": ev.get("agent"),
                    "detail": ev.get("detail"),
                    "timestamp": ev.get("timestamp"),
                    "status": current.get("status"),
                    "story_script": current.get("story_script"),
                    "audio_url": current.get("audio_url"),
                    "citations": current.get("citations", []),
                    "tool_calls": current.get("tool_calls", [])
                })
                yield f"data: {payload}\n\n"
                last_event_idx += 1

            if current.get("status") in ["completed", "partial", "failed"]:
                # Send terminal message
                yield f"data: {json.dumps({'event': 'stream.ended', 'status': current.get('status')})}\n\n"
                break

            await asyncio.sleep(0.4)

    return StreamingResponse(
        sse_event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.get("/{session_id}/trace")
async def get_session_trace(session_id: str):
    """
    Retrieve sanitized tool execution trace, timeline, and agent latencies.
    """
    current = _ACTIVE_SESSIONS.get(session_id)
    if not current:
        raise HTTPException(status_code=404, detail="Execution trace not available")

    return {
        "session_id": session_id,
        "landmark_name": current.get("landmark_name"),
        "status": current.get("status"),
        "tool_calls": current.get("tool_calls", []),
        "timeline": current.get("execution_timeline", []),
        "sources": current.get("sources", []),
        "orchestrator_notes": current.get("orchestrator_notes")
    }

@router.get("/{session_id}/story")
async def get_session_story(session_id: str):
    """
    Retrieve finalized story script, citations, and audio playback link.
    """
    current = _ACTIVE_SESSIONS.get(session_id)
    if not current or not current.get("story_script"):
        raise HTTPException(status_code=404, detail="Story not yet generated for this session")

    return {
        "session_id": session_id,
        "landmark_name": current.get("landmark_name"),
        "story_script": current.get("story_script"),
        "citations": current.get("citations", []),
        "audio_url": current.get("audio_url"),
        "audio_duration_seconds": current.get("audio_duration_seconds"),
        "style": current.get("story_style"),
        "language": current.get("language")
    }

@router.get("/history/all")
async def get_exploration_history(db: AsyncSession = Depends(get_db)):
    """
    Retrieve exploration history across sessions.
    """
    result = await db.execute(select(ExplorationSession).order_by(ExplorationSession.created_at.desc()).limit(20))
    sessions = result.scalars().all()
    return [
        {
            "session_id": s.id,
            "landmark_name": s.landmark_name,
            "status": s.status,
            "language": s.language,
            "story_style": s.story_style,
            "duration_seconds": s.duration_seconds,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "completed_at": s.completed_at.isoformat() if s.completed_at else None
        }
        for s in sessions
    ]

class QuestionRequest(BaseModel):
    question: str

@router.post("/{session_id}/ask")
async def ask_landmark_question(session_id: str, req: QuestionRequest):
    """
    Conversational Audio Guide Q&A:
    Answers visitor questions during audio playback strictly grounded in
    the session's verified evidence claims and venue facts.
    """
    from app.agents.qa_agent import answer_landmark_question

    session_data = _ACTIVE_SESSIONS.get(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Exploration session not found")

    landmark_name = session_data.get("landmark_name", "Landmark")
    answer_res = await answer_landmark_question(
        question=req.question,
        landmark_name=landmark_name,
        session_data=session_data
    )
    return answer_res
