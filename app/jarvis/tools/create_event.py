"""
Create event tool for Google Calendar integration.
"""

import datetime
from .calendar_utils import get_calendar_service, parse_datetime

def create_event(
    summary: str,
    start_time: str,
    end_time: str,
) -> dict:
    """
    Create a new event in Google Calendar.

    Args:
        summary (str): Event title/summary
        start_time (str): Start time (e.g., "2023-12-31 14:00")
        end_time (str): End time (e.g., "2023-12-31 15:00")

    Returns:
        dict: Information about the created event or error details
    """
    try:
        # Get calendar service
        service = get_calendar_service()
        if not service:
            return {
                "status": "error",
                "message": "Failed to authenticate with Google Calendar. Please check credentials.",
            }

        # Use your personal calendar instead of the service account's "primary"
        calendar_id = "alrojas68@gmail.com"

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
