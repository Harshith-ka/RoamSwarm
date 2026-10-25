"""
AI Evaluation Rubric and Scoring Engine for RoamSwarm.
Computes quantitative benchmarks across accuracy, grounding, latency, and resilience.
"""

from typing import Dict, Any, List

def evaluate_run(
    run_result: Dict[str, Any],
    benchmark_meta: Dict[str, Any],
    target_duration: int = 90
) -> Dict[str, Any]:
    """
    Evaluate a single workflow run against ground truth metadata and engineering criteria.
    """
    script = run_result.get("story_script", "")
    citations = run_result.get("citations", [])
    tool_calls = run_result.get("tool_calls", [])
    status = run_result.get("status", "failed")
    latency_ms = run_result.get("latency_ms", 0.0)

    # 1. Completion Score (1.0 for completed/partial, 0.0 for failed)
    completion_score = 1.0 if status in ["completed", "partial"] else 0.0

    # 2. Citation Accuracy Score: % of citations with non-empty, valid URLs
    valid_citations = [c for c in citations if c.get("source_url") and len(c.get("source_url")) > 10]
    citation_accuracy = len(valid_citations) / max(1, len(citations)) if citations else 0.0

    # 3. Factuality Check: If ground truth inception exists, verify presence in script or claims
    gt_inception = benchmark_meta.get("ground_truth_inception")
    factuality_score = 1.0
    if gt_inception:
        if gt_inception.lower() in script.lower():
            factuality_score = 1.0
        else:
            # Check claims
            found_in_claims = any(gt_inception.lower() in c.get("claim_text", "").lower() for c in citations)
            factuality_score = 0.9 if found_in_claims else 0.5

    # 4. Word Adherence Score
    words = len(script.split())
    target_words = 130 if target_duration == 60 else (260 if target_duration == 120 else 195)
    word_diff = abs(words - target_words)
    word_adherence = max(0.0, 1.0 - (word_diff / float(target_words)))

    # 5. Tool Diversity & Execution
    tool_count = len(tool_calls)
    tool_score = min(1.0, tool_count / 2.0)

    # Composite Quality Score (0 - 100)
    composite_score = round(
        (completion_score * 0.25 +
         citation_accuracy * 0.35 +
         factuality_score * 0.25 +
         word_adherence * 0.15) * 100.0,
        1
    )

    return {
        "landmark_name": benchmark_meta.get("name"),
        "status": status,
        "composite_score": composite_score,
        "completion": completion_score,
        "citation_accuracy": round(citation_accuracy * 100, 1),
        "factuality_score": round(factuality_score * 100, 1),
        "word_adherence": round(word_adherence * 100, 1),
        "word_count": words,
        "tool_executions": tool_count,
        "citations_count": len(valid_citations),
        "latency_ms": latency_ms
    }

def aggregate_benchmark_report(
    multi_agent_results: List[Dict[str, Any]],
    baseline_results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Compute comparative summary metrics across 4-Agent LangGraph vs Single-Agent Baseline.
    """
    def _avg(results, key):
        vals = [r[key] for r in results if key in r]
        return round(sum(vals) / max(1, len(vals)), 2)

    def _p95(results, key):
        vals = sorted([r[key] for r in results if key in r])
        if not vals:
            return 0.0
        idx = int(0.95 * len(vals))
        return round(vals[min(idx, len(vals)-1)], 2)

    report = {
        "sample_size": len(multi_agent_results),
        "multi_agent": {
            "avg_composite_score": _avg(multi_agent_results, "composite_score"),
            "completion_rate_pct": _avg(multi_agent_results, "completion") * 100,
            "avg_citation_accuracy_pct": _avg(multi_agent_results, "citation_accuracy"),
            "avg_factuality_score_pct": _avg(multi_agent_results, "factuality_score"),
            "avg_word_adherence_pct": _avg(multi_agent_results, "word_adherence"),
            "avg_citations_count": _avg(multi_agent_results, "citations_count"),
            "avg_tool_executions": _avg(multi_agent_results, "tool_executions"),
            "p50_latency_ms": _avg(multi_agent_results, "latency_ms"),
            "p95_latency_ms": _p95(multi_agent_results, "latency_ms")
        },
        "single_agent_baseline": {
            "avg_composite_score": _avg(baseline_results, "composite_score"),
            "completion_rate_pct": _avg(baseline_results, "completion") * 100,
            "avg_citation_accuracy_pct": _avg(baseline_results, "citation_accuracy"),
            "avg_factuality_score_pct": _avg(baseline_results, "factuality_score"),
            "avg_word_adherence_pct": _avg(baseline_results, "word_adherence"),
            "avg_citations_count": _avg(baseline_results, "citations_count"),
            "avg_tool_executions": _avg(baseline_results, "tool_executions"),
            "p50_latency_ms": _avg(baseline_results, "latency_ms"),
            "p95_latency_ms": _p95(baseline_results, "latency_ms")
        }
    }

    # Relative improvement
    ma_score = report["multi_agent"]["avg_composite_score"]
    base_score = report["single_agent_baseline"]["avg_composite_score"]
    report["citation_grounding_improvement_pct"] = round(
        report["multi_agent"]["avg_citation_accuracy_pct"] - report["single_agent_baseline"]["avg_citation_accuracy_pct"],
        1
    )
    report["factuality_improvement_pct"] = round(
        report["multi_agent"]["avg_factuality_score_pct"] - report["single_agent_baseline"]["avg_factuality_score_pct"],
        1
    )

    return report
