from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Ticket(BaseModel):
    id: int
    player: str
    message: str = Field(min_length=1)

    model_config = ConfigDict(str_strip_whitespace=True)


class Analysis(BaseModel):
    category: Literal["bug", "feature_request", "billing", "account", "how_to", "other"]
    sentiment: Literal["positive", "neutral", "negative"]
    severity: int = Field(ge=1, le=5)
    summary: str = Field(min_length=1)

    model_config = ConfigDict(extra="forbid")


class TriageResult(BaseModel):
    ticket: Ticket
    analysis: Analysis | None = None
    status: Literal["ok", "to_check"]
