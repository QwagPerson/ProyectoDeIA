from pydantic import BaseModel, HttpUrl
from typing import List, Union


class Profile(BaseModel):
    name: str


class Metadata(BaseModel):
    display_phone_number: str
    phone_number_id: str


class TextMessage(BaseModel):
    body: str


class ReactionMessage(BaseModel):
    message_id: str
    emoji: str


class ImageMessage(BaseModel):
    caption: str
    mime_type: str
    sha256: str
    id: str


class StickerMessage(BaseModel):
    mime_type: str
    sha256: str
    id: str


class UnknownMessage(BaseModel):
    code: int
    details: str
    title: str


class Message(BaseModel):
    from_: str
    id: str
    timestamp: int
    type: str = None
    # Depending on the message type one of the following fields will be present
    text: TextMessage = None
    reaction: ReactionMessage = None
    image: ImageMessage = None

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

    def __str__(self):
        return f"WebhookRequest(Amount of entries={len(self.entry)}, type of entries=" \
               f"{[e.changes[0].value.messages[0].type for e in self.entry]}"

    def __repr__(self):
        return self.__str__()
