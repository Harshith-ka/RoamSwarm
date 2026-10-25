import logging
import httpx
from typing import List, Dict, Any
from app.config import settings

logger = logging.getLogger("roamswarm.tools.search")

async def search_live_sources(query: str, max_results: int = 4) -> List[Dict[str, Any]]:
    """
    Search for recent or specific venue/historical articles.
    Uses Tavily if GEMINI/TAVILY_API_KEY is configured, else falls back to DuckDuckGo.
    """
    # 1. Try Tavily if configured
    if settings.TAVILY_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": settings.TAVILY_API_KEY,
                        "query": query,
                        "search_depth": "basic",
                        "include_answer": False,
                        "max_results": max_results
                    }
                )
                if resp.status_code == 200:
                    data = resp.json()
                    results = []
                    for r in data.get("results", []):
                        results.append({
                            "title": r.get("title", ""),
                            "url": r.get("url", ""),
                            "snippet": r.get("content", ""),
                            "publisher": "Tavily Search",
                            "score": r.get("score", 0.8)
                        })
                    return results
        except Exception as e:
            logger.warning(f"Tavily search failed, falling back: {e}")

    # 2. Free fallback via DuckDuckGo
    try:
        from duckduckgo_search import DDGS
        import asyncio
        loop = asyncio.get_event_loop()
        def _ddg_sync():
            with DDGS() as ddgs:
                return list(ddgs.text(query, max_results=max_results))
        raw_results = await loop.run_in_executor(None, _ddg_sync)
        results = []
        for r in raw_results:
            results.append({
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "snippet": r.get("body", ""),
                "publisher": "DuckDuckGo Web Index",
                "score": 0.75
            })
        return results
    except Exception as e:
        logger.warning(f"DuckDuckGo search error: {e}")
        return []
