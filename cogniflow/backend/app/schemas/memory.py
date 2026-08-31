from typing import Any

from pydantic import BaseModel, Field


class FactCreate(BaseModel):
    user_id: str = Field(min_length=1)
    fact: str = Field(min_length=1)
    metadata: dict[str, Any] | None = None


class ContextResponse(BaseModel):
    long_term_facts: list[str]
    short_term_messages: list[dict[str, Any]]
