import json
import dotenv
import os
import httpx

# load the environment variables
load_env = dotenv.load_dotenv(dotenv_path=f"config_files/.env.{os.environ.get('ENVIRONMENT')}")

# Define constants
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
CLASSIFIER_APP_URL = os.environ.get("CLASSIFIER_APP_URL")
CLASSIFIER_APP_KEY = os.environ.get("CLASSIFIER_APP_KEY")
ANSWER_MAP = {
    "Pedir hora": "Buscando una hora... \n"
                  "Encontré una hora para el 10 de agosto a las 10:00. \n",
    "Reagendar hora": "Reagendando hora, por favor espere... \n"
                      "La hora puede ser reagendada para el 14 de agosto a las 09:25. \n"
                      "¿Desea reagendar la hora?",
    "No asistiré": "La hora ha sido cancelada.",
    "Asistiré": "La hora ha sido confirmada.",
}


async def query_classifier_app(text):
    data = {
        "text": text
    }
    headers = {
        "Content-Type": "application/json",
        "Secret-Key": CLASSIFIER_APP_KEY
    }

    api_url = f"http://classifier_app:8000/predict"

    async with httpx.AsyncClient() as client:
        r = await client.post(api_url, data=data, headers=headers)
    return r.json()["class"]


async def echo_message(to, reply_message):
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": reply_message},
    }
    headers = {
        "Content-Type": "application/json",
    }
    api_url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages?access_token={WHATSAPP_TOKEN}"

    async with httpx.AsyncClient() as client:
        r = await client.post(api_url, data=data, headers=headers)
    return r


async def respond_according_to_message_class(message):
    to = message.from_
    if message.type != "text":
        reply_message = "Sorry, I don't know how to handle this type of message"
    else:
        text_class = await query_classifier_app(message.text)
        reply_message = ANSWER_MAP[text_class]
    await echo_message(to, reply_message)


async def repeat_message(message):
    to = message.from_
    if message.type == "text":
        reply_message = f"You said {message.text}"
    else:
        reply_message = f"Sorry, I don't know how to handle {message.type} messages"
    await echo_message(to, reply_message)


async def dispatch_messages(request, func):
    for entry in request.entry:
        for change in entry.changes:
            value = change.value
            for message in value.messages:
                await func(message)
