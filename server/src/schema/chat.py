from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field

class Message(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    timestamp: str = Field(default_factory=lambda: str(datetime.now()))
    sender: str
    content: str



class Chat(BaseModel):
    token: str
    name: str
    messages: list[Message]

