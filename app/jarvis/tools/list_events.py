"""
List events tool for Google Calendar integration.
"""

import datetime

from .calendar_utils import format_event_time, get_calendar_service


def list_events(
    calendar_id: str,
    start_date: str,
    days: int,
) -> dict:
    """
    List upcoming calendar events within a specified date range.

    Args:
        calendar_id (str): Calendar ID to list events from
        start_date (str): Start date in YYYY-MM-DD format. If empty string, defaults to today.
        days (int): Number of days to look ahead. Use 1 for today only, 7 for a week, 30 for a month, etc.

    Returns:
        dict: Information about upcoming events or error details
    """
    try:
        print("Listing events")
        print("Calendar ID: ", calendar_id)
        print("Start date: ", start_date)
        print("Days: ", days)
        # Get calendar service
        service = get_calendar_service()
        if not service:
            return {
                "status": "error",
                "message": "Failed to authenticate with Google Calendar. Please check credentials.",
                "events": [],
            }

        # Always use a large max_results value to return all events
        max_results = 100

        # Set time range
        if not start_date or start_date.strip() == "":
            start_time = datetime.datetime.utcnow()
        else:
            try:
                start_time = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                return {
                    "status": "error",
                    "message": f"Invalid date format: {start_date}. Use YYYY-MM-DD format.",
                    "events": [],
                }

        # If days is not provided or is invalid, default to 1 day
        if not days or days < 1:
            days = 1

        end_time = start_time + datetime.timedelta(days=days)

        # Format times for API call
        time_min = start_time.isoformat() + "Z"
        time_max = end_time.isoformat() + "Z"

        # Call the Calendar API
        events_result = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = events_result.get("items", [])

        if not events:
            return {
                "status": "success",
                "message": "No upcoming events found.",
                "events": [],
            }

        # Format events for display
        formatted_events = []
        for event in events:
            formatted_event = {
                "id": event.get("id"),
                "summary": event.get("summary", "Untitled Event"),
                "start": format_event_time(event.get("start", {})),
                "end": format_event_time(event.get("end", {})),
                "location": event.get("location", ""),
                "description": event.get("description", ""),
                "attendees": [
                    attendee.get("email")
                    for attendee in event.get("attendees", [])
                    if "email" in attendee
                ],
                "link": event.get("htmlLink", ""),
            }
            formatted_events.append(formatted_event)

        return {
            "status": "success",
            "message": f"Found {len(formatted_events)} event(s).",
            "events": formatted_events,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error fetching events: {str(e)}",
            "events": [],
            }

def list_all_events(start_date: str, days: int) -> dict:
    # IDs de tus calendarios
    main_calendar_id = "alrojas68@gmail.com"
    family_calendar_id = "family16804437535786257436@group.calendar.google.com"

    # Llama a list_events para cada calendario
    main_events = list_events(main_calendar_id, start_date, days)
    family_events = list_events(family_calendar_id, start_date, days)

    # Combina los eventos (puedes agregar una etiqueta para saber de cuál calendario viene)
    all_events = []
    for event in main_events.get("events", []):
        event["calendar"] = "Principal"
        all_events.append(event)
    for event in family_events.get("events", []):
        event["calendar"] = "Family"
        all_events.append(event)

    # Opcional: ordena todos los eventos por fecha/hora de inicio
    all_events.sort(key=lambda e: e["start"])

    return {
        "status": "success",
        "message": f"Found {len(all_events)} event(s) in both calendars.",
        "events": all_events,
    }