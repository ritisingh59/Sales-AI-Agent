"""
Tool definitions and execution handlers for Northstar Homes Agent.
Includes simulated site visit booking and booking failure handling.
"""

from typing import Dict, Any
import uuid

# OpenAI / Function Calling JSON Schema
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "book_site_visit",
            "description": "Book a guided VIP site visit for the customer to experience Northstar One in Sector 79, Gurugram.",
            "parameters": {
                "type": "object",
                "properties": {
                    "preferred_date": {
                        "type": "string",
                        "description": "Date requested for the visit (e.g. 'Tomorrow', 'This Saturday', 'Sunday', '2026-08-25')"
                    },
                    "preferred_time": {
                        "type": "string",
                        "description": "Time slot requested for the visit (e.g. '11:00 AM', '4:00 PM', 'Morning', 'Evening')"
                    },
                    "configuration": {
                        "type": "string",
                        "enum": ["2 BHK", "3 BHK", "Undecided"],
                        "description": "The configuration the customer is interested in viewing."
                    },
                    "customer_name": {
                        "type": "string",
                        "description": "Customer's name if mentioned in conversation."
                    },
                    "phone_number": {
                        "type": "string",
                        "description": "Customer's phone number if provided."
                    }
                },
                "required": ["preferred_date", "preferred_time"]
            }
        }
    }
]

def execute_book_site_visit(
    preferred_date: str,
    preferred_time: str,
    configuration: str = "Undecided",
    customer_name: str = "Valued Customer",
    phone_number: str = "Not Provided"
) -> Dict[str, Any]:
    """
    Executes a simulated site-visit booking.
    Demonstrates realistic scheduling behavior and failure edge case recovery:
    - Fails if requested slot is 'Sunday 4 PM' or '4:00 PM on Sunday' (simulates fully booked weekend peak slot).
    - Fails if requested time is late night (outside 9:00 AM to 6:30 PM).
    - Succeeds for other daytime slots.
    """
    date_clean = preferred_date.lower().strip()
    time_clean = preferred_time.lower().strip()
    
    # Edge case 1: Slot fully booked (Sunday 4:00 PM collision simulation)
    if "sunday" in date_clean and ("4" in time_clean or "evening" in time_clean or "16:00" in time_clean):
        return {
            "status": "failed",
            "error_code": "SLOT_UNAVAILABLE",
            "message": "The Sunday 4:00 PM VIP slot is completely full. Alternative open slots: Sunday 11:00 AM or Monday 4:00 PM.",
            "available_slots": ["Sunday 11:00 AM", "Monday 4:00 PM", "Saturday 3:00 PM"]
        }
        
    # Edge case 2: Visiting hours check (Site office operates 9:30 AM to 6:30 PM)
    if any(night_term in time_clean for night_term in ["8:00 pm", "9:00 pm", "10:00 pm", "night", "8pm", "9pm"]):
        return {
            "status": "failed",
            "error_code": "OUTSIDE_OPERATING_HOURS",
            "message": "Site office and sample flats are open between 9:30 AM and 6:30 PM for daylight viewings.",
            "available_slots": ["Tomorrow 11:30 AM", "Tomorrow 4:30 PM"]
        }
    
    # Happy Path Success
    booking_ref = f"NS-VISIT-{uuid.uuid4().hex[:6].upper()}"
    return {
        "status": "success",
        "booking_id": booking_ref,
        "message": "VIP Site Visit slot successfully reserved.",
        "details": {
            "project": "Northstar One",
            "location": "Experience Centre, Sector 79, Gurugram",
            "date": preferred_date,
            "time": preferred_time,
            "configuration": configuration or "2 & 3 BHK Sample Show flat",
            "host": "Senior Property Consultant",
            "gate_pass": "VIP-EXPRESS-PASS"
        }
    }

def dispatch_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Routes tool execution requests to the corresponding implementation."""
    if tool_name == "book_site_visit":
        return execute_book_site_visit(
            preferred_date=arguments.get("preferred_date", "Upcoming Weekend"),
            preferred_time=arguments.get("preferred_time", "11:00 AM"),
            configuration=arguments.get("configuration", "Undecided"),
            customer_name=arguments.get("customer_name", "Valued Customer"),
            phone_number=arguments.get("phone_number", "Not Provided")
        )
    return {"status": "error", "message": f"Unknown tool: {tool_name}"}
