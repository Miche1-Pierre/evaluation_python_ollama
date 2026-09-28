from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Category = Literal["bug", "payment", "account", "suggestion", "toxicity", "autre"]
Escalation = Literal["moderation", "support_manager", "human_review", "standard"]


class Ticket(BaseModel):
    id: int
    player: str
    message: str = Field(min_length=1)

    model_config = ConfigDict(str_strip_whitespace=True)


class Analysis(BaseModel):
    category: Category
    sentiment: Literal["positive", "neutral", "negative"]
    severity: int = Field(ge=1, le=5)
    summary: str = Field(min_length=1)

    model_config = ConfigDict(extra="forbid")


class TriageResult(BaseModel):
    ticket: Ticket
    analysis: Analysis | None = None
    status: Literal["ok", "to_check"]
    draft: str | None = None
    escalation: Escalation | None = None
    suspicious: bool = False

    @property
    def needs_review(self) -> bool:
        return self.status == "to_check" or self.suspicious
