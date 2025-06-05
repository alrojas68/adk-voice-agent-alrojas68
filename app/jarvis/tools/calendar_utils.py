"""
Utility functions for Google Calendar integration.
"""

import json
import os
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Google API scopes for calendar access
SCOPES = ["https://www.googleapis.com/auth/calendar"]
CALENDAR_EMAIL = "alrojas68@gmail.com"


def get_calendar_service():
    """
    Authenticate and create a Google Calendar service object using
    service account credentials loaded from the environment variable.

    Returns:
        Google Calendar API service instance or None if authentication fails
    """
    try:
        # Load the service account credentials from an env var (Railway Secret)
        credentials_json = os.environ["GOOGLE_CREDENTIALS_JSON"]
        creds_dict = json.loads(credentials_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        service = build("calendar", "v3", credentials=creds)
        
        # Set the calendar ID to the specific email
        calendar_id = CALENDAR_EMAIL
        
        return service, calendar_id
    except Exception as e:
        print(f"Error loading calendar credentials: {e}")
        return None, None


def format_event_time(event_time: dict) -> str:
    """
    Format a Google Calendar event time into a human-readable string.

    Args:
        event_time: dict from Google Calendar API (either date or dateTime)

    Returns:
        Formatted time string
    """
    if "dateTime" in event_time:
        dt = datetime.fromisoformat(event_time["dateTime"].replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %I:%M %p")
    elif "date" in event_time:
        return f"{event_time['date']} (All day)"
    return "Unknown time format"


def parse_datetime(datetime_str: str) -> datetime | None:
    """
    Try to parse a datetime string into a datetime object.

    Args:
        datetime_str: Input string with date and time

    Returns:
        datetime object or None if parsing fails
    """
    formats = [
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %I:%M %p",
        "%Y-%m-%d",
        "%m/%d/%Y %H:%M",
        "%m/%d/%Y %I:%M %p",
        "%m/%d/%Y",
        "%B %d, %Y %H:%M",
        "%B %d, %Y %I:%M %p",
        "%B %d, %Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(datetime_str, fmt)
        except ValueError:
            continue

    return None


def get_current_time() -> dict:
    """
    Get the current time and formatted date.

    Returns:
        Dictionary with current_time and formatted_date keys
    """
    now = datetime.now()
    return {
        "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "formatted_date": now.strftime("%m-%d-%Y"),
    }
