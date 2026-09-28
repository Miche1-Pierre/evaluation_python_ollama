import argparse
import sys

from triagebot.cleaning import TicketCleaner
from triagebot.config import DEFAULT_INPUT, DEFAULT_MODEL, DEFAULT_OUTPUT, DEFAULT_REPORT
from triagebot.dashboard import Dashboard
from triagebot.errors import TriageError
from triagebot.escalation import EscalationPolicy
from triagebot.llm import OllamaClient
from triagebot.models import Ticket, TriageResult
from triagebot.report import MarkdownReport
from triagebot.stats import TriageStats
from triagebot.storage import JsonFile, write_text
from triagebot.triage import TriageService


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TriageBot : tri des tickets support")
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    return parser.parse_args()


def triage_all(service: TriageService, tickets: list[Ticket]) -> list[TriageResult]:
    results = []

    for index, ticket in enumerate(tickets, start=1):
        print(f"[{index}/{len(tickets)}] ticket {ticket.id}…")
        results.append(service.triage(ticket))

    return results


def main() -> None:
    args = parse_args()

    client = OllamaClient(args.model)
    client.check_ready()

    raw_tickets = JsonFile(args.input).read()
    cleaner = TicketCleaner()
    tickets = cleaner.clean(raw_tickets)

    service = TriageService(client, EscalationPolicy())
    results = triage_all(service, tickets)

    JsonFile(args.output).write([result.model_dump(mode="json") for result in results])

    Dashboard(TriageStats(results)).display()

    report = MarkdownReport(
        results=results,
        received_count=len(raw_tickets),
        ignored_count=len(cleaner.rejected),
        model=args.model,
    )
    write_text(args.report, report.render())

    print(f"\nRésultats : {args.output} | Rapport : {args.report}")


if __name__ == "__main__":
    try:
        main()
    except TriageError as exc:
        print(f"Erreur : {exc}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterruption.")
        sys.exit(1)
