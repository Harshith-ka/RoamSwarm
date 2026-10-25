from fastapi import APIRouter, BackgroundTasks
from pathlib import Path
import json
from app.eval.dataset import EVALUATION_DATASET

router = APIRouter(prefix="/api/evaluations", tags=["AI Evaluation"])

@router.get("/dataset")
async def get_evaluation_dataset():
    """
    Return the 50-landmark evaluation benchmark dataset.
    """
    return {
        "count": len(EVALUATION_DATASET),
        "landmarks": EVALUATION_DATASET
    }

@router.get("/benchmark/latest")
async def get_latest_benchmark_report():
    """
    Return the latest cached evaluation benchmark report comparing
    the 4-Agent LangGraph engine against the Single-Agent baseline.
    """
    report_path = Path(__file__).resolve().parent.parent / "eval" / "benchmark_latest.json"
    if report_path.exists():
        with open(report_path, "r", encoding="utf-8") as f:
            return json.load(f)

    return {
        "status": "pending",
        "message": "Benchmark report not yet generated. Run python backend/app/eval/run_eval.py to compute."
    }

@router.post("/benchmark/run")
async def trigger_benchmark_run(limit: int = 5):
    """
    Trigger an automated AI evaluation benchmark run comparing
    4-Agent LangGraph vs Single-Agent Baseline.
    """
    from app.eval.run_eval import run_benchmark
    report = await run_benchmark(sample_limit=limit)
    return {
        "status": "completed",
        "report": report
    }
