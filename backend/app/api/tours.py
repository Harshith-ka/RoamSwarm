from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.agents.tour_planner import plan_curated_tour

router = APIRouter(prefix="/api/tours", tags=["Walking Tour Planner"])

class TourPlanRequest(BaseModel):
    landmarks: List[Dict[str, Any]] = Field(..., description="List of 2-5 landmark POIs to include in the tour")
    title: Optional[str] = Field("Chennai Heritage & Architecture Trail", description="Custom tour title")
    theme: Optional[str] = Field("historical", description="historical, spiritual, architecture")

@router.post("/plan")
async def create_walking_tour(req: TourPlanRequest):
    """
    Generate an intelligent, walkable multi-landmark tour route.
    Calculates distance, walking duration between consecutive stops,
    and synthesizes a unified audio guide connecting the sites.
    """
    if len(req.landmarks) < 2:
        raise HTTPException(status_code=400, detail="At least 2 landmarks required to plan a tour route.")

    tour = await plan_curated_tour(
        landmarks=req.landmarks,
        tour_title=req.title or "Curated Urban Heritage Trail",
        theme=req.theme or "historical"
    )
    return tour
