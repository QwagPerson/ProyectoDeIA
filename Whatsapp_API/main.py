from typing import Union, Annotated
from fastapi import FastAPI, Query, Request
from fastapi.responses import Response
import dotenv
import os
import logging

from whatsapp_message_controller.data_models import WebhookRequest
from bot.bot_poo import Bot

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
logger_info = logging.getLogger(os.environ.get('INFO_LOGGER'))  # Main logger for info or warning messages
logger_error = logging.getLogger(os.environ.get('ERROR_LOGGER'))  # Logger for error or debug messages

current_bots = {}

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
async def handle_webhook_request(request: WebhookRequest):
    logger_error.debug(f"Received request: {request}")
    logger_error.debug(f"Received entries:")
    for x in request.entry:
        logger_error.debug(f"Entry: {x}")

    # A partir de la request obtener el numero de telefono y el nombre del usuario
    # Crear un bot con el numero de telefono y el nombre del usuario o cargarlo de la lista de bots

    # parseo
    #await bot.action('asdsa')

    #bot.state != "-10"

    return Response(status_code=204)
