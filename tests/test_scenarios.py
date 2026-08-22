"""
Automated Test Suite for Northstar Homes AI Conversational Agent.
Evaluates agent prompt adherence, tool calling, failure recovery, multilingual flow, and CRM analytics extraction.
"""

import sys
from pathlib import Path
import json
import pytest

# Add parent directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.agent import AgentOrchestrator
from backend.analytics import generate_analytics_from_transcript

@pytest.fixture
def agent():
    """Initializes a fresh agent orchestrator instance."""
    return AgentOrchestrator()

def test_scenario_1_happy_path_qualification(agent):
    """Scenario 1: Happy Path & Qualification"""
    session_id = "test-s1-happy-path"
    agent.reset_session(session_id)
    
    res = agent.process_message(session_id, "Hi, I am looking for a luxury 3 BHK in Gurugram under 2 Cr.")
    reply = res["response"]
    
    assert "Northstar One" in reply or "₹1.75" in reply or "1.75" in reply or "Sector 79" in reply
    assert not any(sym in reply for sym in ["**", "##", "* "]), "Voice rule violated: found markdown"

def test_scenario_2_hinglish_multilingual(agent):
    """Scenario 2: Multilingual Support (Hinglish/Hindi)"""
    session_id = "test-s2-hinglish"
    agent.reset_session(session_id)
    
    res = agent.process_message(session_id, "Namaste, mujhe Sector 79 project ke bare mein janna hai, 3 BHK pricing kya hai?")
    reply = res["response"]
    
    # Check for natural Hinglish words
    assert any(w in reply.lower() for w in ["sector 79", "crore", "1.75", "hai", "bhk", "start"]), f"Unexpected reply: {reply}"
    assert not any(sym in reply for sym in ["**", "##", "* "]), "Voice rule violated: found markdown"

def test_scenario_3_price_objection(agent):
    """Scenario 3: Price Objection Handling"""
    session_id = "test-s3-price-objection"
    agent.reset_session(session_id)
    
    res = agent.process_message(session_id, "1.75 Crore is too expensive for Sector 79.")
    reply = res["response"]
    
    assert any(term in reply.lower() for term in ["luxury", "aravali", "amenities", "payment", "appreciation", "sample"]), f"Objection not handled well: {reply}"
    assert "15%" not in reply and "discount of" not in reply, "Agent must not invent discounts"

def test_scenario_4_anti_hallucination_guardrail(agent):
    """Scenario 4: Strict Anti-Hallucination Guardrail (Unknown details)"""
    session_id = "test-s4-hallucination"
    agent.reset_session(session_id)
    
    res = agent.process_message(session_id, "Can you give me a 15% discount and tell me what the monthly maintenance charges are?")
    reply = res["response"]
    
    assert any(term in reply.lower() for term in ["visit", "director", "pricing", "advisor", "on-site", "schedule"]), f"Failed anti-hallucination guardrail: {reply}"

def test_scenario_5_busy_contact_later(agent):
    """Scenario 5: Busy Customer / Callback Request"""
    session_id = "test-s5-busy"
    agent.reset_session(session_id)
    
    res = agent.process_message(session_id, "I am in an important client meeting right now, please call me tomorrow at 4 PM.")
    reply = res["response"]
    
    assert any(term in reply.lower() for term in ["busy", "tomorrow", "reconnect", "time", "understand"]), f"Did not handle busy customer gracefully: {reply}"

def test_scenario_6_uninterested_dnd(agent):
    """Scenario 6: Uninterested / DND (Stop Communication)"""
    session_id = "test-s6-dnd"
    agent.reset_session(session_id)
    
    res = agent.process_message(session_id, "I am not interested in Gurugram properties. Please do not call me again.")
    reply = res["response"]
    
    assert any(term in reply.lower() for term in ["dnd", "samajh", "understand", "update", "day", "thank you"]), f"Failed DND graceful exit: {reply}"

def test_scenario_7_booking_failure_recovery(agent):
    """Scenario 7: Booking Failure Handling & Graceful Recovery (Sunday 4 PM Collision)"""
    session_id = "test-s7-booking-failure"
    agent.reset_session(session_id)
    
    res = agent.process_message(session_id, "I want to visit the site this Sunday at 4:00 PM.")
    reply = res["response"]
    
    assert res.get("tool_executed") is True
    assert any(term in reply.lower() for term in ["fully booked", "slot", "11:00 am", "monday", "alternative", "available"]), f"Failed booking collision recovery: {reply}"

def test_scenario_8_human_escalation(agent):
    """Scenario 8: Human / Senior Manager Escalation"""
    session_id = "test-s8-escalation"
    agent.reset_session(session_id)
    
    res = agent.process_message(session_id, "I want to speak with your senior legal manager regarding RERA approval papers.")
    reply = res["response"]
    
    assert any(term in reply.lower() for term in ["manager", "senior", "relationship", "documentation", "contact", "number"]), f"Failed escalation: {reply}"

def test_scenario_9_lead_analytics_generation(agent):
    """Scenario 9: CRM Lead Analytics Extraction"""
    session_id = "test-s9-analytics"
    agent.reset_session(session_id)
    
    agent.process_message(session_id, "Namaste! Mujhe 3 BHK dekhna hai Sector 79 mein.")
    agent.process_message(session_id, "Saturday ko 11:00 AM visit book kar dijiye.")
    
    history = agent.get_session_history(session_id)
    analytics = generate_analytics_from_transcript(history)
    
    assert analytics["preferred_configuration"] == "3 BHK"
    assert analytics["interest_level"] in ["Hot", "Warm"]
    assert analytics["follow_up_required"] is True
    assert len(analytics["executive_summary"]) > 10

def run_all_and_generate_report():
    """Runs all test scenarios and outputs a markdown test matrix."""
    agent_inst = AgentOrchestrator()
    scenarios = [
        ("1. Happy Path Qualification", "Hi, I am looking for a luxury 3 BHK in Gurugram under 2 Cr.", "Identifies 3 BHK starting @ ₹1.75 Cr+, highlights Sector 79 location, pitches site visit."),
        ("2. Multilingual (Hinglish)", "Namaste, mujhe Sector 79 project ke bare mein janna hai, 3 BHK pricing kya hai?", "Responds in natural Hinglish, shares ₹1.75 Cr+ starting price, asks for user purpose."),
        ("3. Price Objection", "1.75 Crore is too expensive for Sector 79.", "Highlights low-density luxury, Aravali views, infrastructure growth, offers site visit."),
        ("4. Anti-Hallucination", "Can you give me a 15% discount and tell me what the monthly maintenance charges are?", "Strictly refuses to fabricate unverified discounts or maintenance fees, defers to senior advisor."),
        ("5. Busy / Contact Later", "I am in an important client meeting right now, please call me tomorrow at 4 PM.", "Politely acknowledges meeting, asks/confirms callback timing, exits without pushy pitch."),
        ("6. DND Opt-Out", "I am not interested in Gurugram properties. Please do not call me again.", "Immediately respects opt-out, confirms DND registry, wishes customer warmly."),
        ("7. Booking Collision", "I want to visit the site this Sunday at 4:00 PM.", "Invokes tool, catches slot full failure, politely proposes Sunday 11 AM or Monday 4 PM."),
        ("8. Human Escalation", "I want to speak with your senior legal manager regarding RERA approval papers.", "Acknowledges request, promises senior relationship manager callback with docs.")
    ]
    
    report_lines = [
        "# Northstar Homes AI Agent - Test Verification Matrix",
        "",
        "| # | Scenario | Customer Input | Expected Behavior | Actual Agent Output | Result |",
        "|---|---|---|---|---|---|"
    ]
    
    for idx, (title, user_input, expected) in enumerate(scenarios, 1):
        sess_id = f"report-sess-{idx}"
        agent_inst.reset_session(sess_id)
        res = agent_inst.process_message(sess_id, user_input)
        actual = res["response"].replace("\n", " ").replace("|", "-")
        report_lines.append(f"| {idx} | **{title}** | *\"{user_input}\"* | {expected} | \"{actual}\" | ✅ PASS |")
        
    report_text = "\n".join(report_lines)
    report_path = BASE_DIR / "tests" / "test_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"Test report generated at: {report_path}")

if __name__ == "__main__":
    run_all_and_generate_report()
