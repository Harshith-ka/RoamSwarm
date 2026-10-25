import time
import logging
from typing import Dict, Any, List
from app.state import RoamSwarmState
from app.config import settings

logger = logging.getLogger("roamswarm.agents.storyteller")

TARGET_WORDS = {
    60: 130,
    90: 195,
    120: 260
}

STYLE_PROMPTS = {
    "documentary": "Adopt an authoritative, cinematic, and historically reverent tone. Highlight origins, architectural grandeur, and historical milestones.",
    "conversational": "Adopt an engaging, approachable local storyteller tone as if guiding a close friend through the landmark's secrets.",
    "educational": "Adopt an analytical, informative pedagogical tone emphasizing chronological evolution, cultural impact, and practical visitor tips."
}

async def run_storyteller(state: RoamSwarmState) -> Dict[str, Any]:
    """
    Storyteller Agent:
    Synthesizes structured outputs from Historian and Live Scout into a verified narrative.
    Enforces target duration, language, style, and claim-to-source attribution mappings.
    Separates historical narrative from venue operational guidance.
    """
    start_time = time.time()
    landmark_name = state.get("landmark_name", "Urban Landmark")
    duration = state.get("duration_seconds", 90)
    style = state.get("story_style", "documentary")
    language = state.get("language", "en")
    target_word_count = TARGET_WORDS.get(duration, 195)

    historical_facts = state.get("historical_facts") or []
    evidence = state.get("evidence") or []
    venue_facts = state.get("venue_facts") or []
    sources = state.get("sources") or []

    script = ""
    citations: List[Dict[str, Any]] = []

    # Attempt LLM generation if Gemini API key is configured
    if settings.GEMINI_API_KEY:
        try:
            from google import genai
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            prompt = f"""
You are the Storyteller Agent for RoamSwarm, an autonomous urban intelligence engine.
Your mission is to produce a source-grounded spoken audio guide for the landmark: '{landmark_name}'.

CRITICAL CONSTRAINTS:
1. Target word count: Exactly between {int(target_word_count * 0.85)} and {int(target_word_count * 1.15)} words (speaking time ~{duration} seconds).
2. Style: {style}. {STYLE_PROMPTS.get(style, "")}
3. Language: {language}.
4. FACTUAL GROUNDING: Use ONLY the verified historical facts and evidence provided below. Do NOT invent dates, architects, battles, or cultural claims.
5. VENUE SEPARATION: Conclude with practical visitor information based ONLY on the verified venue facts provided.

VERIFIED HISTORICAL EVIDENCE:
{json_dumps(evidence)}

VERIFIED HISTORICAL FACTS:
{json_dumps(historical_facts)}

VENUE OPERATIONAL FACTS:
{json_dumps(venue_facts)}

Return ONLY the narrative script.
"""
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            if response and response.text:
                script = response.text.strip()
        except Exception as e:
            logger.warning(f"Gemini LLM story generation failed, using deterministic grounding: {e}")

    # Deterministic synthesis fallback if LLM is offline or unconfigured
    if not script:
        script, citations = _synthesize_deterministic_narrative(
            landmark_name=landmark_name,
            historical_facts=historical_facts,
            evidence=evidence,
            venue_facts=venue_facts,
            sources=sources,
            style=style,
            duration=duration,
            target_word_count=target_word_count
        )
    else:
        # Build claim-to-source citations from available evidence
        for idx, ev in enumerate(evidence[:5]):
            citations.append({
                "claim_id": f"claim-{idx+1}",
                "claim_text": ev.get("text", "")[:120],
                "source_url": ev.get("source_url", ""),
                "publisher": ev.get("publisher", "Wikipedia"),
                "confidence": ev.get("confidence", 0.95),
                "verification_status": ev.get("verification_status", "verified")
            })

    total_duration = (time.time() - start_time) * 1000
    timeline_event = {
        "event": "storyteller_completed",
        "agent": "Storyteller",
        "timestamp": time.time(),
        "detail": f"Script synthesized ({len(script.split())} words, {len(citations)} source citations) in {round(total_duration, 1)}ms."
    }

    return {
        "current_agent": "Storyteller",
        "story_script": script,
        "citations": citations,
        "status": "writing",
        "execution_timeline": [timeline_event]
    }

def _synthesize_deterministic_narrative(
    landmark_name: str,
    historical_facts: List[Dict[str, Any]],
    evidence: List[Dict[str, Any]],
    venue_facts: List[Dict[str, Any]],
    sources: List[Dict[str, Any]],
    style: str,
    duration: int,
    target_word_count: int
) -> tuple[str, List[Dict[str, Any]]]:
    """
    Synthesize an authentic, grounded narrative using verified excerpts and facts,
    preserving exact claim-to-source traceability.
    """
    intro_map = {
        "documentary": f"Standing before {landmark_name}, one is immediately connected to a rich chapter of urban heritage.",
        "conversational": f"Welcome to {landmark_name}! If the walls here could speak, they'd tell an incredible story.",
        "educational": f"{landmark_name} stands as an instructive case study in regional history and architectural design."
    }

    intro = intro_map.get(style, intro_map["documentary"])
    paragraphs = [intro]
    citations = []

    history_sentences = []
    for idx, ev in enumerate(evidence):
        text = ev.get("text", "").strip()
        if text and len(text) > 20:
            history_sentences.append(text)
            citations.append({
                "claim_id": f"hist-claim-{idx+1}",
                "claim_text": text[:120],
                "source_url": ev.get("source_url", ""),
                "publisher": ev.get("publisher", "Historical Records"),
                "confidence": ev.get("confidence", 0.95),
                "verification_status": ev.get("verification_status", "verified")
            })
        if len(history_sentences) >= (4 if duration >= 90 else 2):
            break

    if history_sentences:
        paragraphs.append(" ".join(history_sentences))
    else:
        paragraphs.append(f"Historical records for {landmark_name} reflect significant community relevance, with ongoing documentation in OpenStreetMap and civic registries.")

    venue_sentences = []
    for vf in venue_facts:
        attr = vf.get("attribute")
        val = vf.get("value")
        status = vf.get("status")

        if attr == "opening_hours" and status == "verified":
            venue_sentences.append(f"Official operating hours are noted as: {val}.")
        elif attr == "opening_hours" and status == "unverified":
            venue_sentences.append(f"Opening hours are tentatively reported online as {val}, though on-site confirmation is advised.")
        elif attr == "opening_hours" and status == "missing":
            venue_sentences.append("Current opening schedules are not published officially; visitors should verify directly before visiting.")
        elif attr == "admission":
            venue_sentences.append(f"Regarding access, {val.lower()}.")
        elif attr == "accessibility":
            venue_sentences.append(f"Accessibility note: {val}.")

    if venue_sentences:
        paragraphs.append(" ".join(venue_sentences))

    outro_map = {
        "documentary": f"Today, {landmark_name} continues to anchor the cultural identity of its surroundings, bridging centuries of human experience.",
        "conversational": f"Take your time exploring around, and soak in the atmosphere of {landmark_name}.",
        "educational": f"Understanding {landmark_name} offers deeper appreciation for the preservation of living urban landmarks."
    }
    paragraphs.append(outro_map.get(style, outro_map["documentary"]))

    full_script = "\n\n".join(paragraphs)
    return full_script, citations

def json_dumps(obj: Any) -> str:
    import json
    try:
        return json.dumps(obj, indent=2)
    except Exception:
        return str(obj)
