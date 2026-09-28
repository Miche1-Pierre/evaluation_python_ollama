from pydantic import ValidationError

from triagebot.config import MAX_ATTEMPTS
from triagebot.llm import OllamaClient
from triagebot.models import Ticket, TriageResult


class TriageService:
    def __init__(self, client: OllamaClient):
        self.client = client

    def triage(self, ticket: Ticket) -> TriageResult:
        feedback = None

        for _ in range(MAX_ATTEMPTS):
            try:
                analysis = self.client.analyze(ticket, feedback)
                draft = self.client.draft_reply(ticket)

                return TriageResult(
                    ticket=ticket,
                    analysis=analysis,
                    status="ok",
                    draft=draft if draft.strip() else None,
                )

            except ValidationError as exc:
                feedback = str(exc)

        return TriageResult(
            ticket=ticket,
            analysis=None,
            status="to_check",
            draft=None
        )

    def run(self, tickets: list[Ticket]) -> list[TriageResult]:
        results = []

        for ticket in tickets:
            results.append(self.triage(ticket))

        return results
