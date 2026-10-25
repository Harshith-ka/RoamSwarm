from __future__ import annotations
import operator
from typing import TypedDict, Literal, Optional, List, Dict, Any, Annotated
from pydantic import BaseModel, Field

# Reducer functions for concurrent parallel updates in LangGraph
def merge_lists(left: Optional[List[Any]], right: Optional[List[Any]]) -> List[Any]:
    l = list(left) if left else []
    r = list(right) if right else []
    return l + r

def last_value(left: Any, right: Any) -> Any:
    return right if right is not None else left

# ---------------------------------------------------------------------------
# LangGraph Shared State (TypedDict) with Annotated Reducers for Parallel Execution
# ---------------------------------------------------------------------------

class RoamSwarmState(TypedDict, total=False):
    session_id: str
    landmark_id: str
    landmark_name: str
    latitude: float
    longitude: float
    category: Any
    language: str              # "en", "ta", "te", "hi"
    story_style: str           # "documentary", "conversational", "educational"
    duration_seconds: int      # 60, 90, 120
    generate_audio: bool

    # Grounded Research Outputs (Merged across parallel Historian & Live Scout)
    historical_facts: Annotated[List[Dict[str, Any]], merge_lists]
    venue_facts: Annotated[List[Dict[str, Any]], merge_lists]
    evidence: Annotated[List[Dict[str, Any]], merge_lists]
    sources: Annotated[List[Dict[str, Any]], merge_lists]

    # Story & Audio Outputs
    story_script: str
    citations: Annotated[List[Dict[str, Any]], merge_lists]
    audio_url: Optional[str]
    audio_duration_seconds: Optional[float]

    # Orchestration, Observability & Error Handling
    status: Annotated[str, last_value]
    current_agent: Annotated[str, last_value]
    tool_calls: Annotated[List[Dict[str, Any]], merge_lists]
    errors: Annotated[List[str], merge_lists]
    retry_count: int
    token_usage: Dict[str, int]
    execution_timeline: Annotated[List[Dict[str, Any]], merge_lists]

    # Internal evaluation & validation
    is_sufficient: bool
    orchestrator_notes: str


# ---------------------------------------------------------------------------
# Pydantic Schemas for API, Validation, and Client Contracts
# ---------------------------------------------------------------------------

class ExplorationRequest(BaseModel):
    landmark_id: str = Field(..., description="Unique landmark ID e.g. osm-way-123456 or place name")
    landmark_name: Optional[str] = Field(None, description="Landmark name if known")
    latitude: Optional[float] = Field(None, description="Landmark latitude")
    longitude: Optional[float] = Field(None, description="Landmark longitude")
    category: Optional[str] = Field("historical", description="POI category")
    language: str = Field("en", description="Story language: en, ta, te, hi")
    story_style: str = Field("documentary", description="documentary, conversational, educational")
    duration_seconds: int = Field(90, description="Target duration: 60, 90, or 120")
    generate_audio: bool = Field(True, description="Whether to synthesize audio")


class SourceRecord(BaseModel):
    id: str
    url: str
    title: str
    publisher: str
    retrieved_at: str
    published_at: Optional[str] = None


class EvidenceClaim(BaseModel):
    id: str
    claim_text: str
    confidence: float
    verification_status: Literal["verified", "unverified", "disputed", "stale"]
    source_id: str
    supporting_excerpt: str


class ToolExecutionTrace(BaseModel):
    agent_name: str
    tool_name: str
    sanitized_input: Dict[str, Any]
    sanitized_output: Dict[str, Any]
    duration_ms: float
    timestamp: str
    success: bool
    error: Optional[str] = None


class AgentRunTrace(BaseModel):
    agent_name: str
    status: str
    started_at: str
    completed_at: Optional[str] = None
    latency_ms: float
    tool_executions: List[ToolExecutionTrace] = []
    error: Optional[str] = None


class LandmarkPOI(BaseModel):
    id: str
    osm_type: str
    osm_id: int
    name: str
    latitude: float
    longitude: float
    category: str
    tags: Dict[str, Any] = {}
    distance_meters: Optional[float] = None
    address: Optional[str] = None


class ExplorationSessionResponse(BaseModel):
    session_id: str
    landmark_id: str
    landmark_name: str
    status: str
    language: str
    story_style: str
    duration_seconds: int
    story_script: Optional[str] = None
    audio_url: Optional[str] = None
    audio_duration_seconds: Optional[float] = None
    citations: List[Dict[str, Any]] = []
    sources: List[Dict[str, Any]] = []
    historical_facts: List[Dict[str, Any]] = []
    venue_facts: List[Dict[str, Any]] = []
    tool_calls: List[Dict[str, Any]] = []
    errors: List[str] = []
    execution_timeline: List[Dict[str, Any]] = []
    token_usage: Dict[str, int] = {}
    created_at: str
    completed_at: Optional[str] = None
