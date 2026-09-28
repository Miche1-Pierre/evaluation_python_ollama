from triagebot.llm import OllamaClient
from triagebot.models import Ticket, TriageResult


class TriageService:
    def __init__(self, client: OllamaClient):
        self.client = client
         
    def triage(self, ticket: Ticket) -> TriageResult:
        analysis = self.client.analyze(ticket)
        
        return TriageResult(
            ticket = ticket,
            analysis = analysis
        )
        
    def run(self, tickets: list[Ticket]) -> list[TriageResult]:
        return [self.triage(ticket) for ticket in tickets]