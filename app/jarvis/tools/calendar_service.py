import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Define el alcance de permisos (puedes ajustarlo si necesitas más)
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """
    Crea un cliente autenticado para acceder a Google Calendar
    usando una Service Account cargada desde variable de entorno.
    """
    # Asegúrate de tener esta variable en Railway con el contenido del JSON
    service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

    if not service_account_json:
        raise EnvironmentError("Falta la variable GOOGLE_SERVICE_ACCOUNT_JSON en Railway.")

    service_account_info = json.loads(service_account_json)

    credentials = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=SCOPES
    )

    service = build("calendar", "v3", credentials=credentials)
    return service
