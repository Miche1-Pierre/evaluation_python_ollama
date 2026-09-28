from pydantic import ValidationError

from triagebot.config import MAX_ATTEMPTS
from triagebot.escalation import EscalationPolicy
from triagebot.llm import OllamaClient
from triagebot.models import Analysis, Ticket, TriageResult
from triagebot.security import InjectionDetector


class TriageService:
    def __init__(self, client: OllamaClient, escalation_policy: EscalationPolicy):
        self.client = client
        self.escalation_policy = escalation_policy
        self.injection_detector = InjectionDetector()

    def triage(self, ticket: Ticket) -> TriageResult:
        analysis = self._analyze_with_retry(ticket)
        draft = self.client.draft_reply(ticket)

        result = TriageResult(
            ticket=ticket,
            analysis=analysis,
            status="ok" if analysis else "to_check",
            draft=draft,
            suspicious=self.injection_detector.is_suspicious(ticket.message),
        )
        result.escalation = self.escalation_policy.decide(result)

        return result

    def _analyze_with_retry(self, ticket: Ticket) -> Analysis | None:
        feedback = None

        for _ in range(MAX_ATTEMPTS):
            try:
                return self.client.analyze(ticket, feedback)

            except ValidationError as exc:
                feedback = str(exc)

        return None
