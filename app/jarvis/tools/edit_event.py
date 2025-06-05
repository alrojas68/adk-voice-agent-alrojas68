"""
Edit event tool for Google Calendar integration.
"""

import datetime
from typing import Optional

from .calendar_utils import get_calendar_service, parse_datetime


def edit_event(
    event_id: str,
    summary: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    attendees: Optional[list[str]] = None,
) -> dict:
    """
    Edit an existing calendar event.

    Args:
        event_id (str): ID of the event to edit
        summary (str, optional): New event title
        start_time (str, optional): New start time
        end_time (str, optional): New end time
        description (str, optional): New event description
        location (str, optional): New event location
        attendees (list[str], optional): New list of attendee email addresses

    Returns:
        dict: Information about the edited event or error details
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

        # First get the existing event
        try:
            event = (
                service.events().get(calendarId=calendar_id, eventId=event_id).execute()
            )
        except Exception:
            return {
                "status": "error",
                "message": f"Event with ID {event_id} not found in primary calendar.",
            }

        # Update the event with new values
        if summary:
            event["summary"] = summary

        # Get timezone from the original event
        timezone_id = "America/New_York"  # Default
        if "start" in event and "timeZone" in event["start"]:
            timezone_id = event["start"]["timeZone"]

        # Update start time if provided
        if start_time:
            start_dt = parse_datetime(start_time)
            if not start_dt:
                return {
                    "status": "error",
                    "message": "Invalid start time format. Please use YYYY-MM-DD HH:MM format.",
                }
            event["start"] = {"dateTime": start_dt.isoformat(), "timeZone": timezone_id}

        # Update end time if provided
        if end_time:
            end_dt = parse_datetime(end_time)
            if not end_dt:
                return {
                    "status": "error",
                    "message": "Invalid end time format. Please use YYYY-MM-DD HH:MM format.",
                }
            event["end"] = {"dateTime": end_dt.isoformat(), "timeZone": timezone_id}

        # Update the event
        updated_event = (
            service.events()
            .update(calendarId=calendar_id, eventId=event_id, body=event)
            .execute()
        )

        return {
            "status": "success",
            "message": "Event updated successfully",
            "event_id": updated_event["id"],
            "event_link": updated_event.get("htmlLink", ""),
        }

    except Exception as e:
        return {"status": "error", "message": f"Error updating event: {str(e)}"}
