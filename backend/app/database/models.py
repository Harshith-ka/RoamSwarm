import json
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Text, ForeignKey, JSON, Boolean
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def utcnow():
    return datetime.now(timezone.utc)

class Landmark(Base):
    __tablename__ = "landmarks"

    id = Column(String(128), primary_key=True) # e.g. osm-node-12345
    osm_type = Column(String(32), nullable=False)
    osm_id = Column(Integer, nullable=False)
    name = Column(String(256), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    category = Column(String(64), nullable=False)
    landmark_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    sessions = relationship("ExplorationSession", back_populates="landmark")


class ExplorationSession(Base):
    __tablename__ = "exploration_sessions"

    id = Column(String(64), primary_key=True)
    landmark_id = Column(String(128), ForeignKey("landmarks.id"), nullable=True)
    landmark_name = Column(String(256), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    status = Column(String(32), default="pending")
    language = Column(String(16), default="en")
    story_style = Column(String(32), default="documentary")
    duration_seconds = Column(Integer, default=90)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)

    landmark = relationship("Landmark", back_populates="sessions")
    agent_runs = relationship("AgentRun", back_populates="session", cascade="all, delete-orphan")
    stories = relationship("Story", back_populates="session", cascade="all, delete-orphan")
    evidence_claims = relationship("EvidenceClaim", back_populates="session", cascade="all, delete-orphan")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(String(64), primary_key=True)
    session_id = Column(String(64), ForeignKey("exploration_sessions.id"), nullable=False)
    agent_name = Column(String(64), nullable=False)
    status = Column(String(32), default="pending")
    started_at = Column(DateTime(timezone=True), default=utcnow)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    latency_ms = Column(Float, default=0.0)
    error = Column(Text, nullable=True)

    session = relationship("ExplorationSession", back_populates="agent_runs")
    tool_executions = relationship("ToolExecution", back_populates="agent_run", cascade="all, delete-orphan")


class ToolExecution(Base):
    __tablename__ = "tool_executions"

    id = Column(String(64), primary_key=True)
    agent_run_id = Column(String(64), ForeignKey("agent_runs.id"), nullable=False)
    tool_name = Column(String(64), nullable=False)
    sanitized_input = Column(JSON, default=dict)
    sanitized_output = Column(JSON, default=dict)
    duration_ms = Column(Float, default=0.0)
    success = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    agent_run = relationship("AgentRun", back_populates="tool_executions")


class Source(Base):
    __tablename__ = "sources"

    id = Column(String(128), primary_key=True)
    url = Column(String(512), nullable=False, unique=True)
    title = Column(String(256), nullable=False)
    publisher = Column(String(128), default="Unknown")
    retrieved_at = Column(DateTime(timezone=True), default=utcnow)
    published_at = Column(String(64), nullable=True)


class EvidenceClaim(Base):
    __tablename__ = "evidence_claims"

    id = Column(String(64), primary_key=True)
    session_id = Column(String(64), ForeignKey("exploration_sessions.id"), nullable=False)
    claim_text = Column(Text, nullable=False)
    confidence = Column(Float, default=1.0)
    verification_status = Column(String(32), default="verified")
    source_id = Column(String(128), ForeignKey("sources.id"), nullable=True)
    supporting_excerpt = Column(Text, nullable=True)

    session = relationship("ExplorationSession", back_populates="evidence_claims")


class Story(Base):
    __tablename__ = "stories"

    id = Column(String(64), primary_key=True)
    session_id = Column(String(64), ForeignKey("exploration_sessions.id"), nullable=False)
    script = Column(Text, nullable=False)
    language = Column(String(16), default="en")
    style = Column(String(32), default="documentary")
    version = Column(Integer, default=1)
    citations_data = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    session = relationship("ExplorationSession", back_populates="stories")
    audio = relationship("AudioArtifact", uselist=False, back_populates="story", cascade="all, delete-orphan")


class AudioArtifact(Base):
    __tablename__ = "audio_artifacts"

    id = Column(String(64), primary_key=True)
    story_id = Column(String(64), ForeignKey("stories.id"), nullable=False)
    storage_path = Column(String(512), nullable=False)
    playback_url = Column(String(512), nullable=False)
    duration_seconds = Column(Float, default=0.0)
    model = Column(String(64), default="gemini-tts-v1")
    created_at = Column(DateTime(timezone=True), default=utcnow)

    story = relationship("Story", back_populates="audio")


class ApiUsage(Base):
    __tablename__ = "api_usage"

    id = Column(String(64), primary_key=True)
    session_id = Column(String(64), nullable=False)
    provider = Column(String(64), nullable=False) # e.g. "gemini", "tavily"
    model = Column(String(64), nullable=False)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    estimated_cost_usd = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=utcnow)
