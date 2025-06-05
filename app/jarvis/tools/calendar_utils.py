"""
Utility functions for Google Calendar integration.
"""

import json
import os
from datetime import datetime

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Define scopes needed for Google Calendar
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_calendar_service():
    """
    Authenticate and create a Google Calendar service object using
    service account credentials from an environment variable.

    Returns:
        A Google Calendar service object or None if authentication fails
    """
    try:
        credentials_json = os.environ["GOOGLE_CREDENTIALS_JSON"]
        creds_dict = json.loads(credentials_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        service = build("calendar", "v3", credentials=creds)
        return service
    except Exception as e:
        print(f"Error loading calendar credentials: {e}")
        return None


def format_event_time(event_time):
    """
    Format an event time into a human-readable string.

    Args:
        event_time (dict): The event time dictionary from Google Calendar API

    Returns:
        str: A human-readable time string
    """
    if "dateTime" in event_time:
        # This is a datetime event
        dt = datetime.fromisoformat(event_time["dateTime"].replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %I:%M %p")
    elif "date" in event_time:
        # This is an all-day event
        return f"{event_time['date']} (All day)"
    return "Unknown time format"


def parse_datetime(datetime_str):
    """
    Parse a datetime string into a datetime object.

    Args:
        datetime_str (str): A string representing a date and time

    Returns:
        datetime: A datetime object or None if parsing fails
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
    Get the current time and date
    """
    now = datetime.now()

    # Format date as MM-DD-YYYY
    formatted_date = now.strftime("%m-%d-%Y")

    return {
        "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "formatted_date": formatted_date,
    }
