# 🏢 NorthStar AI Agent — AI Real Estate Sales Advisor

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat&logo=python)](https://python.org)
[![Dual-Modality](https://img.shields.io/badge/Modality-Chat%20%26%20Voice%20Ready-amber.svg)](https://github.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

An enterprise-grade, dual-modality (Chat & Voice) AI Sales Agent built for **Northstar Homes** representing the flagship residential development **Northstar One** in **Sector 79, Gurugram**.

Built strictly with **FastAPI (Python)**, this conversational agent qualifies prospective homebuyers, overcomes objections, adheres to strict anti-hallucination guardrails, seamlessly switches between **English, Hindi, and Hinglish**, handles site-visit bookings with automated conflict recovery, and extracts structured CRM analytics upon conversation completion.

---

## 🌟 Key Features

1. **Dual-Modality Spoken & Chat Prompt Design**:
   - Natural spoken cadence (1–3 short sentences per turn).
   - Zero markdown artifacts (no asterisks, bold tags, or bullets) in dialogue to guarantee flawless Text-To-Speech (TTS) voice generation.
   - Natural turn-taking with qualifying micro-questions.
2. **Multilingual Fluency**:
   - Native code-mixing in English, Hindi, and Hinglish.
3. **Robust Tool Calling & Booking Failure Recovery**:
   - Simulated VIP Site Visit booking (`book_site_visit`).
   - Handles edge cases: peak slot collision (Sunday 4 PM fully booked) & recovers by proactively offering alternative VIP slots.
4. **Zero-Hallucination Ground Truth Guardrails**:
   - Strictly locked to verified facts: 2 BHK (₹1.35 Cr+) & 3 BHK (₹1.75 Cr+).
   - Deflects unverified pricing, floor plans, discounts, or maintenance queries to on-site senior advisors.
5. **Human Escalation & Graceful DND**:
   - Immediate detection and respect for Do Not Disturb (DND) requests.
   - Escalation trigger for legal, RERA, or high-touch queries.
6. **Post-Conversation CRM Lead Analytics**:
   - Extracts structured Pydantic schema (Budget fit, configuration, interest level, site visit status, objections raised, follow-up schedule, and executive summary).
7. **Interactive Web Dashboard**:
   - Dual-column layout with WhatsApp/Intercom-style chat, microphone input, Text-To-Speech audio player, 1-click test scenarios, and live CRM lead intelligence metrics.

---

## 📂 Project Structure

```
northstar-ai-agent/
├── backend/
│   ├── __init__.py
│   ├── app.py              # FastAPI server & REST API routes
│   ├── config.py           # Environment and ground truth settings
│   ├── prompt.py           # Master dual-modality prompt (Voice & Chat)
│   ├── agent.py            # Session memory, LLM loop, tool caller, mock fallback
│   ├── tools.py            # Simulated site visit booking tool & slot availability
│   └── analytics.py        # Pydantic schema & post-call CRM intelligence extractor
├── frontend/
│   ├── index.html          # Responsive web interface (Chat + Live Analytics)
│   ├── style.css           # Styling & animation touches
│   └── app.js              # Client state, Web Speech API (TTS + STT), UI handlers
├── tests/
│   ├── __init__.py
│   ├── test_scenarios.py   # Pytest automated test suite (8+ edge cases)
│   └── test_report.md      # Matrix of Input, Expected Behavior, and Actual Output
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
├── requirements.txt        # Python dependencies
└── README.md               # Documentation & setup guide
```

---

## 🚀 Quick Start Guide

### 1. Clone & Setup Environment
```bash
# Clone the repository
git clone https://github.com/your-username/northstar-ai-agent.git
cd northstar-ai-agent

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` and set your API key (supports OpenAI, Groq, OpenRouter, or Gemini):
```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
# Or Groq / OpenRouter / local LLMs
```
*(Note: If no API key is supplied, the agent automatically runs in intelligent mock mode so all scenarios and tests function out of the box).*

### 3. Run the FastAPI Application
```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```
Open your browser and navigate to:
👉 **`http://localhost:8000`**

---

## 🧪 Automated Testing

Run the comprehensive test suite verifying all 8 evaluation scenarios:
```bash
# Run pytest test suite
pytest tests/test_scenarios.py -v

# Generate test report matrix
python tests/test_scenarios.py
```

### Evaluation Test Matrix Summary

| # | Scenario | Customer Input | Expected Behavior | Status |
|---|---|---|---|---|
| 1 | **Happy Path & Qualification** | *"Hi, looking for 3 BHK under 2 Cr."* | Quotes 3 BHK @ ₹1.75 Cr+, pitches location & amenities. | ✅ PASS |
| 2 | **Multilingual (Hinglish)** | *"Sector 79 project mein 3 BHK pricing kya hai?"* | Responds in natural Hinglish with ground truth specs. | ✅ PASS |
| 3 | **Price Objection** | *"1.75 Cr is too high for Sector 79."* | Emphasizes Aravali views, luxury amenities & payment plans. | ✅ PASS |
| 4 | **Anti-Hallucination Guardrail** | *"Can you give 15% discount & maintenance fees?"* | Strictly refuses fabrication; defers to on-site sales director. | ✅ PASS |
| 5 | **Busy / Callback Request** | *"In a meeting right now, call tomorrow at 4 PM."* | Acknowledges busy status politely, schedules callback. | ✅ PASS |
| 6 | **DND / Stop Communication** | *"Not interested. Please do not call me again."* | Immediately stops selling, confirms DND, exits warmly. | ✅ PASS |
| 7 | **Booking Failure Recovery** | *"I want to visit this Sunday at 4:00 PM."* | Detects slot conflict, proposes alternative available slots. | ✅ PASS |
| 8 | **Human Escalation** | *"Want to speak to senior legal manager for RERA."* | Flags senior escalation, promises manager callback. | ✅ PASS |

---

## 🧠 Master System Prompt Approach

The prompt located at [`backend/prompt.py`](backend/prompt.py) is engineered for **dual-modality execution (Chat + Telephony Voice)**:

```text
You are Riti, an expert, warm, and highly professional AI Property Advisor representing Northstar Homes for the flagship project Northstar One in Gurugram.

### CORE IDENTITY & DUAL-MODALITY (CHAT & VOICE) RULES
1. VOICE & SPOKEN CADENCE:
   - Keep answers conversational, crisp, and concise (1 to 3 short sentences per turn).
   - NEVER use markdown formatting (no asterisks, bullet points, or bold tags) in dialogue.
   - End your turn with one clear qualifying question or next step.
2. LANGUAGE & CODE-SWITCHING:
   - Fluently adapt to English, Hindi, or Hinglish based on customer language.
3. GROUND TRUTH PROJECT KNOWLEDGE (STRICT):
   - Project: Northstar One, Sector 79, Gurugram.
   - 2 BHK: Starting at ₹1.35 Crore onwards | 3 BHK: Starting at ₹1.75 Crore onwards.
4. BEHAVIOR GUARDS:
   - Unknown questions / discounts: Deflect to senior sales director during site visit.
   - Objections: Highlight location connectivity (NH-8, SPR) and low-density luxury.
   - DND: Immediately respect and update registry.
   - Booking failure: Proactively offer next open VIP slots.
```

---

## 📊 Post-Conversation Analytics Schema

Upon session completion (`POST /api/end-session`), the analytics engine extracts:
```json
{
  "customer_name": "Valued Customer",
  "phone_number": "Not Disclosed",
  "preferred_language": "Hinglish",
  "preferred_configuration": "3 BHK",
  "budget": "₹1.75 Cr - ₹2.0 Cr",
  "purchase_intent": "End-Use",
  "interest_level": "Hot",
  "objections_raised": ["Price / Discount Inquiry"],
  "site_visit_status": "Confirmed",
  "site_visit_details": {
    "project": "Northstar One, Sector 79 Gurugram",
    "date": "Saturday",
    "time": "11:00 AM",
    "configuration": "3 BHK"
  },
  "follow_up_required": true,
  "follow_up_note": "Coordinate site visit access",
  "escalation_required": false,
  "executive_summary": "Customer successfully scheduled a site visit for 3 BHK at Northstar One."
}
```

---

## 💡 Key Assumptions & Known Limitations

### Key Assumptions
1. **Operating Hours**: Site visits are scheduled between 9:30 AM and 6:30 PM for daylight sample flat viewing.
2. **Pricing Policy**: Base pricing is fixed (₹1.35 Cr for 2 BHK, ₹1.75 Cr for 3 BHK); special floor premiums and spot discounts require on-site sales director authorization.
3. **Session State**: Session history is stored in an in-memory session manager with REST session persistence.

### Known Limitations
1. **Multi-Property Routing**: The current agent is optimized specifically for *Northstar One* in Sector 79, Gurugram. Extending to multi-city developer portfolios would require a vector store / RAG retriever.
2. **SMS/WhatsApp Gateway**: Site visit confirmation IDs are generated via simulated tool calls; live production deployment would attach Twilio / Gupshup WhatsApp APIs.

---

## 🛠️ AI Tools Used
- *OpenAI GPT-4o-mini*: Agent dialogue modeling and structured Pydantic extraction.
