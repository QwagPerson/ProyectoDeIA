import json
import dotenv
import os
import httpx

# load the environment variables
load_env = dotenv.load_dotenv(dotenv_path=f"config_files/.env.{os.environ.get('ENVIRONMENT')}")

# Define constants
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")


async def echo_message(to, reply_message):
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": reply_message},
    }
    headers = {
        "Content-Type": "application/json",
    }
    api_url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages?access_token={WHATSAPP_TOKEN}"

    async with httpx.AsyncClient() as client:
        r = await client.post(api_url, data=data)
        print(r)
    return r


def dispatch_messages(request, func):
    for entry in request.entry:
        for change in entry.changes:
            value = change.value
            to = value.metadata.phone_number_id
            for message in value.messages:
                if message.type == "text":
                    reply_message = f"You said {message.text}"
                    echo_message(to, reply_message)
                else:
                    reply_message = f"Sorry, I don't know how to handle {message.type} messages"
                    echo_message(to, reply_message)
