from typing import Union, Annotated
from fastapi import FastAPI, Query, Request
from fastapi.responses import Response
import dotenv
import os
import logging

from data_models import WebhookRequest

# Loading the environment variables
load_env = dotenv.load_dotenv(dotenv_path=f"config_files/.env.{os.environ.get('ENVIRONMENT')}")

# Creating the app
app = FastAPI(
    title="Whatsapp API",
    description="An API for sending and receiving messages from Whatsapp",
    version="0.1.0",
    openapi_url=os.path.join(os.environ.get("ROOT_PATH"), "openapi.json"),
    root_path=os.environ.get("ROOT_PATH"),
)

# Defining the loggers
logger_info = logging.getLogger("uvicorn.info")  # Main logger for info or warning messages
logger_error = logging.getLogger("uvicorn.error")  # Logger for error or debug messages


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/webhook")
def read_webhooks(
        hub_mode: Annotated[str | None, Query(alias="hub.mode")] = None,
        hub_challenge: Annotated[str | None, Query(alias="hub.challenge")] = None,
        hub_verify_token: Annotated[str | None, Query(alias="hub.verify_token")] = None
):
    # Checking the 'verify token'
    if hub_verify_token != os.environ.get("VERIFY_TOKEN"):
        return {"error": "Invalid verify token"}

    # Responding to the challenge
    if hub_mode == "subscribe" and hub_challenge:
        return int(hub_challenge)

    return {"Status": "Failure"}


@app.post("/webhook")
async def notice_change(request: WebhookRequest):
    # Print the request body
    logger_info.warn(request)
    logger_error.debug(request)
    return Response(status_code=204)
