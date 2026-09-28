from pydantic import ValidationError

from triagebot.config import MAX_ATTEMPTS
from triagebot.llm import OllamaClient
from triagebot.models import Ticket, TriageResult


class TriageService:
    def __init__(self, client: OllamaClient, escalation_policy):
        self.client = client
        self.escalation_policy = escalation_policy

    def triage(self, ticket: Ticket) -> TriageResult:
        feedback = None

        for _ in range(MAX_ATTEMPTS):
            try:
                analysis = self.client.analyze(ticket, feedback)
                draft = self.client.draft_reply(ticket)

                result = TriageResult(
                    ticket=ticket,
                    analysis=analysis,
                    status="ok",
                    draft=draft if draft.strip() else None,
                )

                result.escalation = self.escalation_policy.decide(result)
                return result

            except ValidationError as exc:
                feedback = str(exc)

        result = TriageResult(
            ticket=ticket, analysis=None, status="to_check", draft=None
        )

        result.escalation = self.escalation_policy.decide(result)
        return result

    def run(self, tickets: list[Ticket]) -> list[TriageResult]:
        results = []

        for ticket in tickets:
            results.append(self.triage(ticket))

        return results
