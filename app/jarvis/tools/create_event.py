"""
Create event tool for Google Calendar integration.
"""

import datetime
from typing import Optional
from .calendar_utils import get_calendar_service, parse_datetime

def create_event(
    summary: str,
    start_time: str,
    end_time: str,
    description: Optional[str] = None,
    location: Optional[str] = None,
    attendees: Optional[list[str]] = None,
) -> dict:
    """
    Create a new calendar event.

    Args:
        summary (str): Event title
        start_time (str): Start time in a format that can be parsed
        end_time (str): End time in a format that can be parsed
        description (str, optional): Event description
        location (str, optional): Event location
        attendees (list[str], optional): List of attendee email addresses

    Returns:
        dict: Information about the created event or error details
    """
    try:
        # Get calendar service
        service, calendar_id = get_calendar_service()
        if not service or not calendar_id:
            return {
                "status": "error",
                "message": "Failed to authenticate with Google Calendar. Please check credentials.",
                "event": None,
            }

        # Parse times
        start_dt = parse_datetime(start_time)
        end_dt = parse_datetime(end_time)

        if not start_dt or not end_dt:
            return {
                "status": "error",
                "message": "Invalid date/time format. Please use YYYY-MM-DD HH:MM format.",
            }

        # Determine timezone
        timezone_id = "America/New_York"
        try:
            settings = service.settings().list().execute()
            for setting in settings.get("items", []):
                if setting.get("id") == "timezone":
                    timezone_id = setting.get("value")
                    break
        except Exception:
            pass

        # Create event body
        event_body = {
            "summary": summary,
            "start": {
                "dateTime": start_dt.isoformat(),
                "timeZone": timezone_id,
            },
            "end": {
                "dateTime": end_dt.isoformat(),
                "timeZone": timezone_id,
            },
        }

        # Insert event into your calendar
        event = service.events().insert(calendarId=calendar_id, body=event_body).execute()

        return {
            "status": "success",
            "message": "Event created successfully",
            "event_id": event["id"],
            "event_link": event.get("htmlLink", ""),
        }

    except Exception as e:
        return {"status": "error", "message": f"Error creating event: {str(e)}"}
