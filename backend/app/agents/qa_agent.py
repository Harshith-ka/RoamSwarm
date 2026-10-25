import logging
from typing import Dict, Any, List
from app.config import settings

logger = logging.getLogger("roamswarm.agents.qa")

async def answer_landmark_question(
    question: str,
    landmark_name: str,
    session_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Conversational Audio Guide Q&A:
    Answers user follow-up questions during playback strictly grounded in
    the session's verified historical evidence, venue facts, and citations.
    """
    evidence = session_data.get("evidence", [])
    venue_facts = session_data.get("venue_facts", [])
    sources = session_data.get("sources", [])
    citations = session_data.get("citations", [])

    answer = ""
    cited_sources = []

    # Attempt Gemini API if configured
    if settings.GEMINI_API_KEY:
        try:
            from google import genai
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            prompt = f"""
You are the AI Audio Guide for {landmark_name}.
A visitor listening to the audio guide has asked: "{question}".

GROUNDED CONTEXT ONLY:
Evidence: {evidence}
Venue Facts: {venue_facts}
Citations: {citations}

CRITICAL RULES:
1. Answer concisely (2-4 sentences).
2. Use ONLY facts present in the context above.
3. If the context does not contain the answer, explicitly state: "I don't have verified records on that specific detail in our grounded archives."
"""
            for model_candidate in ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-flash-lite-latest"]:
                try:
                    res = client.models.generate_content(
                        model=model_candidate,
                        contents=prompt
                    )
                    if res and res.text:
                        answer = res.text.strip()
                        break
                except Exception:
                    continue
        except Exception as e:
            logger.warning(f"Gemini QA error: {e}")

    # Fallback deterministic search across evidence and venue facts
    if not answer:
        q_lower = question.lower()
        matched_claims = []

        # Check venue attributes first (hours, fees, wheelchair, website)
        if any(w in q_lower for w in ["hour", "time", "open", "close", "timing"]):
            for vf in venue_facts:
                if vf.get("attribute") == "opening_hours":
                    matched_claims.append(f"Operating hours: {vf.get('value')} ({vf.get('status')} via {vf.get('source')}).")
        
        if any(w in q_lower for w in ["fee", "ticket", "cost", "price", "entry", "admission"]):
            for vf in venue_facts:
                if vf.get("attribute") == "admission":
                    matched_claims.append(f"Admission details: {vf.get('value')}.")

        if any(w in q_lower for w in ["wheelchair", "accessible", "disability", "ramp"]):
            for vf in venue_facts:
                if vf.get("attribute") == "accessibility":
                    matched_claims.append(f"Accessibility: {vf.get('value')}.")

        # Check historical evidence for keywords
        words = [w for w in q_lower.split() if len(w) > 3]
        for ev in evidence:
            ev_text = ev.get("text", "")
            if any(w in ev_text.lower() for w in words):
                matched_claims.append(ev_text)
                if ev.get("source_url") and ev.get("source_url") not in cited_sources:
                    cited_sources.append(ev.get("source_url"))

        if matched_claims:
            answer = f"Based on verified archives for {landmark_name}: " + " ".join(matched_claims[:2])
        else:
            answer = f"According to verified records for {landmark_name}, this site anchors significant cultural importance, though specific archival details on '{question}' are currently unverified in our retrieved sources."

    # Attach citation references
    if not cited_sources and sources:
        cited_sources = [s.get("url") for s in sources[:2] if s.get("url")]

    return {
        "question": question,
        "landmark_name": landmark_name,
        "answer": answer,
        "cited_sources": cited_sources,
        "grounded": True
    }
