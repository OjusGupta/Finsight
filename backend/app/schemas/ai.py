from pydantic import BaseModel
from typing import Any


class AIChatRequest(BaseModel):
    message: str


class AIChatResponse(BaseModel):
    answer: str
    intent: str | None = None
    tool_calls: list[Any] | None = None
    metadata: dict[str, Any] | None = None
