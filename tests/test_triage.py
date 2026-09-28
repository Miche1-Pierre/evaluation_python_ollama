from pydantic import ValidationError

from triagebot.models import Analysis, Ticket
from triagebot.triage import TriageService


class FakeClient:
    def __init__(self):
        self.calls = 0

    def analyze(self, ticket, feedback=None):
        self.calls += 1
        Analysis.model_validate_json("{}")


class FakePolicy:
    def decide(self, result):
        return "human_review"


def test_failed_client_reaches_to_check_after_two_attempts():
    client = FakeClient()
    service = TriageService(client, FakePolicy())

    ticket = Ticket(
        id=1,
        player="Player",
        message="Le jeu plante.",
    )

    result = service.triage(ticket)

    assert client.calls == 2
    assert result.status == "to_check"
    assert result.analysis is None
    assert result.draft is None
    assert result.escalation == "human_review"
