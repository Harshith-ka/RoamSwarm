import httpx
import logging
import urllib.parse
from typing import Dict, Any, List, Optional
from app.config import settings

logger = logging.getLogger("roamswarm.tools.wikipedia")

WIKI_SUMMARY_API = "https://en.wikipedia.org/api/rest_v1/page/summary/"
WIKI_OPENSEARCH_API = "https://en.wikipedia.org/w/api.php"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"

async def lookup_wikipedia_and_wikidata(
    landmark_name: str,
    wiki_tag: Optional[str] = None,
    wikidata_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieve grounded historical information, summary excerpts, and Wikidata facts
    for a given landmark. Returns verbatim quotes, source URLs, and structured facts.
    """
    title = ""
    # If OSM has a wikipedia tag e.g. "en:San Thome Basilica"
    if wiki_tag:
        if ":" in wiki_tag:
            _, title = wiki_tag.split(":", 1)
        else:
            title = wiki_tag

    headers = {"User-Agent": settings.OSM_USER_AGENT}

    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        # Disambiguate or search Wikipedia if title is not directly known
        if not title:
            title = await _search_wikipedia_title(client, landmark_name, headers)

        if not title:
            title = landmark_name

        clean_title = urllib.parse.quote(title.replace(" ", "_"))
        summary_url = f"{WIKI_SUMMARY_API}{clean_title}"

        summary_data = {}
        try:
            resp = await client.get(summary_url, headers=headers)
            if resp.status_code == 200:
                summary_data = resp.json()
            elif resp.status_code == 404:
                # Try fallback search
                fallback_title = await _search_wikipedia_title(client, f"{landmark_name} landmark", headers)
                if fallback_title and fallback_title != title:
                    clean_fb = urllib.parse.quote(fallback_title.replace(" ", "_"))
                    fb_resp = await client.get(f"{WIKI_SUMMARY_API}{clean_fb}", headers=headers)
                    if fb_resp.status_code == 200:
                        summary_data = fb_resp.json()
                        title = fallback_title
        except Exception as e:
            logger.error(f"Error fetching Wikipedia summary for '{title}': {e}")

        # Extract structured evidence
        extract = summary_data.get("extract", "")
        description = summary_data.get("description", "")
        page_url = summary_data.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{clean_title}")
        thumbnail_url = summary_data.get("thumbnail", {}).get("source")

        # Fetch Wikidata entity if available
        wikidata_facts = {}
        if not wikidata_id and summary_data.get("wikibase_item"):
            wikidata_id = summary_data.get("wikibase_item")

        if wikidata_id:
            wikidata_facts = await _fetch_wikidata_entity(client, wikidata_id, headers)

        # Break extract into verified sentences / claims
        sentences = [s.strip() for s in extract.split(". ") if len(s.strip()) > 15]
        evidence_items = []
        for idx, sentence in enumerate(sentences[:6]):
            full_sentence = sentence if sentence.endswith(".") else sentence + "."
            evidence_items.append({
                "id": f"wiki-claim-{idx+1}",
                "text": full_sentence,
                "source_url": page_url,
                "publisher": "Wikipedia",
                "confidence": 0.95,
                "verification_status": "verified"
            })

        return {
            "title": summary_data.get("title", title),
            "description": description,
            "extract": extract,
            "page_url": page_url,
            "thumbnail_url": thumbnail_url,
            "wikidata_id": wikidata_id,
            "wikidata_facts": wikidata_facts,
            "evidence_items": evidence_items,
            "found": bool(extract)
        }

async def _search_wikipedia_title(client: httpx.AsyncClient, query: str, headers: dict) -> Optional[str]:
    """Search for matching Wikipedia title via OpenSearch."""
    params = {
        "action": "opensearch",
        "search": query,
        "limit": 3,
        "namespace": 0,
        "format": "json"
    }
    try:
        resp = await client.get(WIKI_OPENSEARCH_API, params=params, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            # data is [query, [titles], [descriptions], [urls]]
            if len(data) > 1 and len(data[1]) > 0:
                return data[1][0]
    except Exception as e:
        logger.warning(f"Wikipedia opensearch error for '{query}': {e}")
    return None

async def _fetch_wikidata_entity(client: httpx.AsyncClient, entity_id: str, headers: dict) -> Dict[str, Any]:
    """Extract key claims (inception date, architect, heritage status) from Wikidata."""
    params = {
        "action": "wbgetentities",
        "ids": entity_id,
        "props": "claims|labels",
        "languages": "en",
        "format": "json"
    }
    facts = {}
    try:
        resp = await client.get(WIKIDATA_API, params=params, headers=headers)
        if resp.status_code == 200:
            entity = resp.json().get("entities", {}).get(entity_id, {})
            claims = entity.get("claims", {})
            # P571: inception / construction date
            if "P571" in claims:
                try:
                    time_val = claims["P571"][0]["mainsnak"]["datavalue"]["value"]["time"]
                    # Format: +1523-00-00T... -> 1523
                    year = time_val.lstrip("+").split("-")[0]
                    facts["inception_year"] = year
                except Exception:
                    pass
            # P84: architect
            if "P84" in claims:
                facts["architect_id"] = claims["P84"][0]["mainsnak"]["datavalue"]["value"]["id"]
            # P1435: heritage designation
            if "P1435" in claims:
                facts["heritage_status"] = True
    except Exception as e:
        logger.warning(f"Wikidata lookup error for '{entity_id}': {e}")
    return facts
