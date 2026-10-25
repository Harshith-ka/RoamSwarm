import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "RoamSwarm"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    
    # API Keys
    GEMINI_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    
    # Observability
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "RoamSwarm"
    
    # Database
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR / 'roamswarm.db'}"
    
    # OSM & HTTP Headers
    OSM_USER_AGENT: str = "RoamSwarm-Agentic-Urban-Engine/1.0 (contact: info@roamswarm.local)"
    CACHE_TTL_SECONDS: int = 86400
    
    # Audio Artifact Storage
    AUDIO_STORAGE_DIR: Path = BASE_DIR / "static" / "audio"
    
    # Rate Limiting & Overpass Config
    OVERPASS_URL: str = "https://overpass-api.de/api/interpreter"
    NOMINATIM_URL: str = "https://nominatim.openstreetmap.org/search"
    
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Ensure static audio dir exists
settings.AUDIO_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
