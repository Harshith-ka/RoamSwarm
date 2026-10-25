import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database.session import init_db
from app.api.landmarks import router as landmarks_router
from app.api.explorations import router as explorations_router
from app.api.evaluation import router as evaluation_router
from app.api.tours import router as tours_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("roamswarm.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION}...")
    await init_db()
    logger.info("Database tables verified.")
    yield
    logger.info(f"Shutting down {settings.APP_NAME}...")

app = FastAPI(
    title="RoamSwarm — Autonomous Urban Intelligence Engine API",
    description="Multi-agent AI backend powered by LangGraph, OpenStreetMap, Wikipedia, and Gemini.",
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS configuration for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static audio files
app.mount("/static/audio", StaticFiles(directory=str(settings.AUDIO_STORAGE_DIR)), name="static_audio")

# Include Routers
app.include_router(landmarks_router)
app.include_router(explorations_router)
app.include_router(evaluation_router)
app.include_router(tours_router)

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

@app.get("/", tags=["Health"])
async def root():
    return {
        "message": "Welcome to RoamSwarm Autonomous Urban Intelligence Engine",
        "docs_url": "/docs",
        "agents": ["Orchestrator", "Historian", "Live Scout", "Storyteller"],
        "orchestrator_framework": "LangGraph"
    }
