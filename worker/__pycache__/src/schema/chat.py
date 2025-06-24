from __future__ import annotations

from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel, Field


class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    source: str
    msg: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())



