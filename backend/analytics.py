"""
Structured Analytics & Lead Intelligence Extraction Engine.
Generates comprehensive CRM fields from complete conversation transcripts.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import json
import logging
from backend.prompt import ANALYTICS_SYSTEM_PROMPT
from backend.config import settings

logger = logging.getLogger(__name__)

class LeadAnalytics(BaseModel):
    customer_name: Optional[str] = Field(default="Valued Customer", description="Customer name if identified")
    phone_number: Optional[str] = Field(default="Not Disclosed", description="Phone number if shared")
    preferred_language: str = Field(default="Hinglish", description="Dominant language used (English, Hindi, Hinglish)")
    preferred_configuration: str = Field(default="Undecided", description="2 BHK, 3 BHK, Both, or Undecided")
    budget: str = Field(default="Not Disclosed", description="Estimated or stated budget range")
    purchase_intent: str = Field(default="End-Use", description="End-Use, Investment, or Browsing")
    interest_level: str = Field(default="Warm", description="Hot, Warm, Cold, or Dead (DND)")
    objections_raised: List[str] = Field(default_factory=list, description="Specific objections raised (e.g., Price, Location, Distance)")
    site_visit_status: str = Field(default="Not Discussed", description="Confirmed, Proposed, Rescheduled, Failed / Conflict, Declined, or Not Discussed")
    site_visit_details: Optional[Dict[str, Any]] = Field(default=None, description="Booking reference, date, and time slot if booked")
    follow_up_required: bool = Field(default=True, description="Whether a follow-up is needed by sales reps")
    follow_up_note: Optional[str] = Field(default=None, description="Specific follow-up instructions or preferred callback timing")
    escalation_required: bool = Field(default=False, description="Whether a senior manager / escalation is triggered")
    escalation_reason: Optional[str] = Field(default=None, description="Reason for escalation (e.g. Legal check, Escalated objection)")
    key_highlights_discussed: List[str] = Field(default_factory=list, description="Key features discussed (e.g. Sector 79 location, Clubhouse, 2 BHK pricing)")
    executive_summary: str = Field(default="Customer inquired about Northstar One.", description="2-3 sentence CRM executive summary")

def generate_analytics_from_transcript(messages: List[Dict[str, Any]], client=None) -> Dict[str, Any]:
    """
    Analyzes conversation messages and returns structured LeadAnalytics.
    Supports LLM extraction with reliable rule-based fallback.
    """
    transcript_text = ""
    for msg in messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        tool_calls = msg.get("tool_calls", [])
        if role in ["user", "assistant"]:
            transcript_text += f"{role.upper()}: {content}\n"
        if tool_calls:
            transcript_text += f"TOOL_CALL: {tool_calls}\n"
            
    if not transcript_text.strip():
        return LeadAnalytics(executive_summary="No conversation recorded.").model_dump()
        
    # If LLM client is available and configured
    if client and settings.OPENAI_API_KEY:
        try:
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": ANALYTICS_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"Please extract structured lead intelligence for the following transcript in JSON matching the LeadAnalytics schema:\n\n{transcript_text}"
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            parsed_json = json.loads(response.choices[0].message.content)
            validated_analytics = LeadAnalytics(**parsed_json)
            return validated_analytics.model_dump()
        except Exception as e:
            logger.warning(f"LLM analytics extraction encountered error: {e}. Using deterministic extraction fallback.")

    # Rule-Based / Deterministic High-Quality Fallback Engine
    return extract_fallback_analytics(messages)

def extract_fallback_analytics(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Robust fallback heuristic extractor for offline/mock evaluation."""
    full_text = " ".join([m.get("content", "").lower() for m in messages if m.get("role") == "user"])
    assistant_text = " ".join([m.get("content", "").lower() for m in messages if m.get("role") == "assistant"])
    
    # Language detection
    hindi_keywords = ["kya", "hai", "mujhe", "bataiye", "kitna", "chahiye", "accha", "bilkul", "kaise", "nahi"]
    hindi_hits = sum(1 for kw in hindi_keywords if kw in full_text)
    if hindi_hits >= 2:
        lang = "Hinglish"
    else:
        lang = "English"
        
    # Configuration
    if "3 bhk" in full_text or "3bhk" in full_text:
        config = "3 BHK"
    elif "2 bhk" in full_text or "2bhk" in full_text:
        config = "2 BHK"
    else:
        config = "2 BHK & 3 BHK"
        
    # Budget
    budget = "Not Disclosed"
    if "1.35" in full_text or "1.5" in full_text or "1.75" in full_text or "2 cr" in full_text or "crore" in full_text:
        budget = "₹1.35 Cr - ₹2.0 Cr"
        
    # DND / Uninterested check
    is_dnd = any(dnd in full_text for dnd in ["don't call", "dont call", "not interested", "stop calling", "dnd", "mat karna", "interest nahi"])
    
    # Busy check
    is_busy = any(b in full_text for b in ["busy", "meeting", "call later", "tomorrow", "baad mein", "kal"])
    
    # Escalation check
    is_escalation = any(esc in full_text for esc in ["manager", "senior", "legal", "rera", "complaint", "documents", "approvals"])
    
    # Objections
    objections = []
    if "expensive" in full_text or "too high" in full_text or "price" in full_text or "mehnga" in full_text or "discount" in full_text:
        objections.append("Price / Discount Inquiry")
    if "far" in full_text or "location" in full_text or "sector 79" in full_text and "connectivity" in full_text:
        objections.append("Location Connectivity")
        
    # Check for site visit booking tools in transcript
    site_visit_status = "Not Discussed"
    site_visit_details = None
    
    for m in messages:
        if m.get("tool_calls"):
            for tc in m.get("tool_calls", []):
                fn_name = tc.get("function", {}).get("name", "")
                if fn_name == "book_site_visit":
                    args = json.loads(tc.get("function", {}).get("arguments", "{}"))
                    site_visit_status = "Confirmed"
                    site_visit_details = {
                        "project": "Northstar One, Sector 79 Gurugram",
                        "date": args.get("preferred_date", "Upcoming Weekend"),
                        "time": args.get("preferred_time", "11:00 AM"),
                        "configuration": args.get("configuration", config)
                    }
        content_lower = m.get("content", "").lower()
        if "site visit for northstar one is confirmed" in content_lower or "visit is confirmed" in content_lower:
            site_visit_status = "Confirmed"
        if "slot is currently fully booked" in content_lower or "slot is completely full" in content_lower or "slot_unavailable" in str(m).lower():
            site_visit_status = "Failed / Slot Conflict (Alternative Proposed)"
            
    if is_dnd:
        interest = "Dead"
        follow_up = False
        intent = "DND"
        summary = "Customer requested to stop all communication. Marked as DND."
    elif is_busy:
        interest = "Warm"
        follow_up = True
        intent = "Browsing"
        summary = "Customer was in a meeting or busy. Requested a callback at a later time."
    elif site_visit_status == "Confirmed":
        interest = "Hot"
        follow_up = True
        intent = "End-Use"
        summary = f"Customer successfully scheduled a site visit for {config} at Northstar One."
    elif is_escalation:
        interest = "Hot"
        follow_up = True
        intent = "End-Use"
        summary = "Customer requested senior advisor escalation regarding project verifications/legal approvals."
    else:
        interest = "Warm"
        follow_up = True
        intent = "End-Use"
        summary = f"Customer inquired about {config} configurations at Northstar One, Sector 79 Gurugram."

    analytics = LeadAnalytics(
        preferred_language=lang,
        preferred_configuration=config,
        budget=budget,
        purchase_intent=intent,
        interest_level=interest,
        objections_raised=objections,
        site_visit_status=site_visit_status,
        site_visit_details=site_visit_details,
        follow_up_required=follow_up,
        follow_up_note="Call back as requested" if is_busy else ("Coordinate site visit access" if site_visit_status == "Confirmed" else "Follow up with project brochure"),
        escalation_required=is_escalation,
        escalation_reason="Customer requested senior manager callback" if is_escalation else None,
        key_highlights_discussed=["Sector 79 Location", f"{config} Pricing", "Site Visit Amenities"],
        executive_summary=summary
    )
    return analytics.model_dump()
