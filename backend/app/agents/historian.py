import time
import logging
from typing import Dict, Any, List
from app.state import RoamSwarmState
from app.tools.wikipedia_tool import lookup_wikipedia_and_wikidata
from app.tools.web_search_tool import search_live_sources

logger = logging.getLogger("roamswarm.agents.historian")

async def run_historian(state: RoamSwarmState) -> Dict[str, Any]:
    """
    Historian Agent:
    Executes grounded historical retrieval via Wikipedia and Wikidata,
    with web search fallback for disambiguation and notable lore.
    Strictly preserves verbatim evidence excerpts and sources.
    """
    start_time = time.time()
    landmark_name = state.get("landmark_name", "Unknown Landmark")
    
    new_tool_calls: List[Dict[str, Any]] = []
    new_timeline: List[Dict[str, Any]] = [{
        "event": "historian_started",
        "agent": "Historian",
        "timestamp": start_time,
        "detail": f"Beginning historical & cultural inquiry for '{landmark_name}'."
    }]

    # Tool Execution 1: Wikipedia & Wikidata
    t1_start = time.time()
    wiki_result = await lookup_wikipedia_and_wikidata(landmark_name)
    t1_duration = (time.time() - t1_start) * 1000

    new_tool_calls.append({
        "agent_name": "Historian",
        "tool_name": "lookup_wikipedia_and_wikidata",
        "sanitized_input": {"landmark_name": landmark_name},
        "sanitized_output": {
            "title": wiki_result.get("title"),
            "extract_length": len(wiki_result.get("extract", "")),
            "evidence_count": len(wiki_result.get("evidence_items", [])),
            "wikidata_id": wiki_result.get("wikidata_id")
        },
        "duration_ms": round(t1_duration, 1),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "success": wiki_result.get("found", False)
    })

    historical_facts: List[Dict[str, Any]] = []
    evidence_claims: List[Dict[str, Any]] = []
    new_sources: List[Dict[str, Any]] = []

    if wiki_result.get("found"):
        new_sources.append({
            "id": f"src-wiki-{int(time.time()*1000)}",
            "url": wiki_result["page_url"],
            "title": wiki_result["title"],
            "publisher": "Wikipedia Encyclopedia",
            "retrieved_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        })

        extract = wiki_result.get("extract", "")
        historical_facts.append({
            "fact_type": "historical_overview",
            "text": extract[:300] + ("..." if len(extract) > 300 else ""),
            "confidence": 0.95,
            "source_url": wiki_result["page_url"]
        })

        for ev in wiki_result.get("evidence_items", []):
            evidence_claims.append(ev)

        wikidata_facts = wiki_result.get("wikidata_facts", {})
        if "inception_year" in wikidata_facts:
            historical_facts.append({
                "fact_type": "inception_date",
                "text": f"Founded or established in {wikidata_facts['inception_year']}.",
                "confidence": 0.98,
                "source_url": f"https://www.wikidata.org/wiki/{wiki_result.get('wikidata_id')}"
            })

    # Tool Execution 2: Web Search if Wikipedia yielded minimal evidence
    if len(evidence_claims) < 2:
        t2_start = time.time()
        search_query = f"{landmark_name} history architecture significance"
        search_results = await search_live_sources(search_query, max_results=3)
        t2_duration = (time.time() - t2_start) * 1000

        new_tool_calls.append({
            "agent_name": "Historian",
            "tool_name": "search_live_sources",
            "sanitized_input": {"query": search_query},
            "sanitized_output": {"results_count": len(search_results)},
            "duration_ms": round(t2_duration, 1),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "success": len(search_results) > 0
        })

        for r in search_results:
            src_id = f"src-web-{int(time.time()*1000)}"
            new_sources.append({
                "id": src_id,
                "url": r["url"],
                "title": r["title"],
                "publisher": r.get("publisher", "Web Index"),
                "retrieved_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            })
            snippet = r.get("snippet", "").strip()
            if snippet:
                evidence_claims.append({
                    "id": f"search-claim-{len(evidence_claims)+1}",
                    "text": snippet[:250],
                    "source_url": r["url"],
                    "publisher": r.get("publisher", "Web"),
                    "confidence": 0.8,
                    "verification_status": "verified"
                })

    if not evidence_claims:
        evidence_claims.append({
            "id": "unverified-0",
            "text": f"No definitive historical archives confirmed for {landmark_name}.",
            "source_url": "",
            "publisher": "Unknown",
            "confidence": 0.1,
            "verification_status": "unverified"
        })

    total_duration = (time.time() - start_time) * 1000
    new_timeline.append({
        "event": "historian_completed",
        "agent": "Historian",
        "timestamp": time.time(),
        "detail": f"Gathered {len(historical_facts)} historical facts and {len(evidence_claims)} evidence claims ({round(total_duration, 1)}ms)."
    })

    return {
        "current_agent": "Historian",
        "historical_facts": historical_facts,
        "evidence": evidence_claims,
        "sources": new_sources,
        "tool_calls": new_tool_calls,
        "execution_timeline": new_timeline
    }
