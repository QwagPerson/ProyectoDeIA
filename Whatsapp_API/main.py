from typing import Union, Annotated
from fastapi import FastAPI, Query, Request
from fastapi.responses import Response
import dotenv
import os
import logging
from bot.whatsapp_connector.data_models import WebhookRequest
from bot.whatsapp_connector.message_controller import send_text_msg, send_interactive_msg
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

    user_name = request.entry[0].changes[0].value.contacts[0].profile.name
    user_id = request.entry[0].changes[0].value.messages[0].from_

    if user_id not in current_bots.keys():
        logger_error.debug(f"Creating new bot for user {user_id}")
        current_bots[user_id] = Bot(user_id, user_name)

    bot = current_bots[user_id]

    # A partir de cada cambio extraigo el tipo de mensaje y lo aplico al bot
    msg_type = request.entry[0].changes[0].value.messages[0].type

    if msg_type == "text":
        # Sacamos el texto de la response
        text = request.entry[0].changes[0].value.messages[0].text.body
        logger_error.debug(f"Received text: {text} from user {user_id}")
        await bot.action(text)
    elif msg_type == "interactive":
        # Sacamos el valor de la respuesta
        payload = request.entry[0].changes[0].value.messages[0].interactive.button_reply.id_
        logger_error.debug(f"Received payload: {payload} from user {user_id}")
        await bot.action(payload)
    else:
        logger_error.debug(f"Received message of type {msg_type} from user {user_id}")
        await send_text_msg(user_id, "No entiendo tu mensaje TROLLAZO")

    return Response(status_code=204)
