from typing import Union, Annotated
from fastapi import FastAPI, Query, Request
from fastapi.responses import Response
import dotenv
import os

# Loading the secret variables
load_env = dotenv.load_dotenv(dotenv_path=f"config_files/.env.{os.environ.get('ENVIRONMENT')}")

app = FastAPI(
    title="Whatsapp API",
    description="An API for sending and receiving messages from Whatsapp",
    version="0.1.0",
    root_path=os.environ.get("ROOT_PATH"),
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: Union[int, str]):
    return {"item_id": item_id}


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
        return {"hub.challenge": hub_challenge}

    return {"Status": "Failure"}


@app.post("/webhooks")
def notice_change(request: Request):
    # Print the request body
    print(request.body)
    return Response(status_code=204)
