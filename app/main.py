import asyncio
import base64
import json
import os
from pathlib import Path
from typing import AsyncIterable

from dotenv import load_dotenv
from fastapi import FastAPI, Query, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.adk.events.event import Event
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types
from jarvis.agent import root_agent

#
# ADK Streaming
#

# Load Gemini API Key
load_dotenv()

APP_NAME = "ADK Streaming example"
session_service = InMemorySessionService()


def start_agent_session(session_id, is_audio=False):
    """Starts an agent session"""

    # Create a Session
    session = session_service.create_session(
        app_name=APP_NAME,
        user_id=session_id,
        session_id=session_id,
    )

    # Create a Runner
    runner = Runner(
        app_name=APP_NAME,
        agent=root_agent,
        session_service=session_service,
    )

    # Set response modality
    modality = "AUDIO" if is_audio else "TEXT"

    # Create speech config with voice settings
    speech_config = types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
        )
    )

    # Create run config with basic settings
    config = {"response_modalities": [modality], "speech_config": speech_config}

    if is_audio:
        config["output_audio_transcription"] = {}

    run_config = RunConfig(**config)

    # Create a LiveRequestQueue for this session
    live_request_queue = LiveRequestQueue()

    # Start agent session
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )
    return live_events, live_request_queue


async def agent_to_client_messaging(
    websocket: WebSocket, live_events: AsyncIterable[Event | None]
):
    """Agent to client communication"""
    while True:
        async for event in live_events:
            if event is None:
                continue

            if event.turn_complete or event.interrupted:
                message = {
                    "turn_complete": event.turn_complete,
                    "interrupted": event.interrupted,
                }
                await websocket.send_text(json.dumps(message))
                print(f"[AGENT TO CLIENT]: {message}")
                continue

            part = event.content and event.content.parts and event.content.parts[0]
            if not part:
                continue

            if not isinstance(part, types.Part):
                continue

            if part.text and event.partial:
                message = {
                    "mime_type": "text/plain",
                    "data": part.text,
                    "role": "model",
                }
                await websocket.send_text(json.dumps(message))
                print(f"[AGENT TO CLIENT]: text/plain: {part.text}")

            is_audio = (
                part.inline_data
                and part.inline_data.mime_type
                and part.inline_data.mime_type.startswith("audio/pcm")
            )
            if is_audio:
                audio_data = part.inline_data and part.inline_data.data
                if audio_data:
                    message = {
                        "mime_type": "audio/pcm",
                        "data": base64.b64encode(audio_data).decode("ascii"),
                        "role": "model",
                    }
                    await websocket.send_text(json.dumps(message))
                    print(f"[AGENT TO CLIENT]: audio/pcm: {len(audio_data)} bytes.")


async def client_to_agent_messaging(
    websocket: WebSocket, live_request_queue: LiveRequestQueue
):
    """Client to agent communication"""
    while True:
        message_json = await websocket.receive_text()
        message = json.loads(message_json)
        mime_type = message["mime_type"]
        data = message["data"]
        role = message.get("role", "user")

        if mime_type == "text/plain":
            content = types.Content(role=role, parts=[types.Part.from_text(text=data)])
            live_request_queue.send_content(content=content)
            print(f"[CLIENT TO AGENT PRINT]: {data}")
        elif mime_type == "audio/pcm":
            decoded_data = base64.b64decode(data)
            live_request_queue.send_realtime(
                types.Blob(data=decoded_data, mime_type=mime_type)
            )
            print(f"[CLIENT TO AGENT]: audio/pcm: {len(decoded_data)} bytes")
        else:
            raise ValueError(f"Mime type not supported: {mime_type}")


#
# FastAPI web app
#

app = FastAPI()

# Manejo seguro del directorio estático
STATIC_DIR = Path("static")
if STATIC_DIR.exists() and STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def root():
    """Serves the index.html"""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "index.html no encontrado en /static"}


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    is_audio: str = Query(...),
):
    """Client websocket endpoint"""

    await websocket.accept()
    print(f"Client #{session_id} connected, audio mode: {is_audio}")

    live_events, live_request_queue = start_agent_session(
        session_id, is_audio == "true"
    )

    agent_to_client_task = asyncio.create_task(
        agent_to_client_messaging(websocket, live_events)
    )
    client_to_agent_task = asyncio.create_task(
        client_to_agent_messaging(websocket, live_request_queue)
    )
    await asyncio.gather(agent_to_client_task, client_to_agent_task)

    print(f"Client #{session_id} disconnected")
