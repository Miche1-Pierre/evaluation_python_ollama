from pydantic import ValidationError

from triagebot.models import Ticket
from triagebot.triage import TriageService


class FakeClient:
    def analyze(self, ticket, feedback=None):
        raise ValidationError.from_exception_data(
            "Analysis",
            [
                {
                    "type": "missing",
                    "loc": ("category",),
                    "input": {},
                }
            ],
        )


ticket = Ticket(
    id=999,
    player="Test",
    message="Test",
)

service = TriageService(FakeClient())

result = service.triage(ticket)

print(result)
print(result.status)
print(result.analysis)