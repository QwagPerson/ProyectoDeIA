from pydantic import BaseModel, HttpUrl
from typing import List, Union


class Profile(BaseModel):
    name: str


class Metadata(BaseModel):
    display_phone_number: str
    phone_number_id: str


class TextMessage(BaseModel):
    body: str


class Message(BaseModel):
    from_: str
    id: str
    timestamp: int
    text: TextMessage
    type: str

    class Config:
        fields = {
            'from_': 'from'
        }


class Contact(BaseModel):
    profile: Profile
    wa_id: str


class ChangeValue(BaseModel):
    messaging_product: str
    metadata: Metadata
    contacts: list[Contact]
    messages: list[Message]


class Change(BaseModel):
    value: ChangeValue
    field: str


class Entry(BaseModel):
    id: str
    changes: list[Change]


class WebhookRequest(BaseModel):
    object: str
    entry: list[Entry]


