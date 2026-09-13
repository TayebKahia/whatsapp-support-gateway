from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class WhatsAppMessageType(str, Enum):
    TEXT = "text"
    INTERACTIVE = "interactive"
    BUTTON = "button"
    UNKNOWN = "unknown"


class MetaTextContent(BaseModel):
    body: str


class MetaInteractiveReply(BaseModel):
    id: str
    title: str


class MetaInteractiveContent(BaseModel):
    type: Literal["button_reply", "list_reply"]
    button_reply: MetaInteractiveReply | None = None


class MetaMessage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    from_number: str = Field(alias="from")
    id: str = Field(description="WhatsApp Message ID (WAMID)")
    timestamp: str
    type: WhatsAppMessageType = WhatsAppMessageType.UNKNOWN
    text: MetaTextContent | None = None
    interactive: MetaInteractiveContent | None = None


class MetaValue(BaseModel):
    messaging_product: Literal["whatsapp"] = "whatsapp"
    metadata: dict[str, str] = Field(default_factory=dict)
    contacts: list[dict[str, object]] = Field(default_factory=list)
    messages: list[MetaMessage] = Field(default_factory=list)


class MetaChange(BaseModel):
    value: MetaValue
    field: Literal["messages"] = "messages"


class MetaEntry(BaseModel):
    id: str
    changes: list[MetaChange] = Field(default_factory=list)


class MetaWebhookPayload(BaseModel):
    object: Literal["whatsapp_business_account"] = "whatsapp_business_account"
    entry: list[MetaEntry] = Field(default_factory=list)
