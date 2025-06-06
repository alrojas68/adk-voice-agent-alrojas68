"""
Utility functions for Google Calendar integration.
"""

import json
import os

from datetime import datetime
from pathlib import Path


from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define scopes needed for Google Calendar
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Path for token storage
TOKEN_PATH = Path(os.path.expanduser("~/.credentials/calendar_token.json"))
CREDENTIALS_PATH = Path("credentials.json")


def get_calendar_service():
    """
    Authenticate using a Google Service Account stored in an environment variable
    (ideal for Railway or server deployments).
    """
    from google.oauth2 import service_account

    service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

    if not service_account_json:
        print("Error: Missing GOOGLE_SERVICE_ACCOUNT_JSON environment variable.")
        return None

    try:
        service_account_info = json.loads(service_account_json)

        credentials = service_account.Credentials.from_service_account_info(
            service_account_info, scopes=SCOPES
        )

        return build("calendar", "v3", credentials=credentials)

    except Exception as e:
        print(f"Error initializing Google Calendar service: {e}")
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

    # Format date as DD-MM-YYYY
    formatted_date = now.strftime("%d-%m-%Y")

    return {
        "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "formatted_date": formatted_date,
    }