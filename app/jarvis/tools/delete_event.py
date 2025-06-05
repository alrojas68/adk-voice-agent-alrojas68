"""
Delete event tool for Google Calendar integration.
"""

from .calendar_utils import get_calendar_service


def delete_event(event_id: str) -> dict:
    """
    Delete a calendar event.

    Args:
        event_id (str): ID of the event to delete

    Returns:
        dict: Status of the deletion operation
    """
    try:
        # Get calendar service
        service, calendar_id = get_calendar_service()
        if not service or not calendar_id:
            return {
                "status": "error",
                "message": "Failed to authenticate with Google Calendar. Please check credentials.",
            }

        # Call the Calendar API to delete the event
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()

        return {
            "status": "success",
            "message": f"Event {event_id} has been deleted successfully",
            "event_id": event_id,
        }

    except Exception as e:
        return {"status": "error", "message": f"Error deleting event: {str(e)}"}
