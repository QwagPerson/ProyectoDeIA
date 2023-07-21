import json
import logging
import os

import dotenv
import httpx

# load the environment variables
load_env = dotenv.load_dotenv(dotenv_path=f"config_files/.env.{os.environ.get('ENVIRONMENT')}")

# Defining the loggers
logger_info = logging.getLogger(os.environ.get('INFO_LOGGER'))  # Main logger for info or warning messages
logger_error = logging.getLogger(os.environ.get('ERROR_LOGGER'))  # Logger for error or debug messages

# Define constants
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
API_URL = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages?access_token={WHATSAPP_TOKEN}"


async def send_text_msg(
        to: str,
        msg: str,
) -> httpx.Response:
    """
    Sends a text message to the specified number using the Whatsapp API.
    :param to: The number to send the message to.
    :param msg: The message to send.
    :return: The response from the Whatsapp API.
    """
    logger_error.debug(f"Sending message to {to}: {msg}")
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": msg},
    }
    headers = {
        "Content-Type": "application/json",
    }
    api_url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages?access_token={WHATSAPP_TOKEN}"

    async with httpx.AsyncClient() as client:
        r = await client.post(api_url, data=data, headers=headers)
    logger_error.debug(f"Response: {r}")
    logger_error.debug(f"Response code: {r.status_code}")
    logger_error.debug(f"Response text: {r.text}")
    return r


async def send_interactive_msg(
        to: str,
        msg: str,
        quick_replies: list[tuple[str, str]]) -> httpx.Response:
    """
    Sends an interactive message to the specified number using the Whatsapp API.
    Currently only supports buttons.
    :param to: The number to send the message to.
    :param msg: The message to send attached to the msg with the buttons.
    :param quick_replies: A list of tuples with the reply_id and the title of the button.
    :return: The response from the Whatsapp API.
    """

    logger_error.debug(f"""
                       Sending interactive message to {to}: {msg}
                       With quick replies: {quick_replies}
                       """)

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": msg
            }
        },
        "action": {
            "buttons": [
                {
                    "type": "reply",
                    "reply": {
                        "id": reply_id,
                        "title": title
                    }
                } for reply_id, title in quick_replies
            ]
        }
    }

    headers = {
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(API_URL, data=data, headers=headers)

    logger_error.debug(f"Response: {r}")
    logger_error.debug(f"Response code: {r.status_code}")
    logger_error.debug(f"Response text: {r.text}")

    return r
