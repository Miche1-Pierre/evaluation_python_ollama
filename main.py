import argparse
import sys

from pydantic import ValidationError

from triagebot.config import DEFAULT_MODEL
from triagebot.errors import TriageError
from triagebot.llm import OllamaClient
from triagebot.models import Ticket
from triagebot.storage import JsonFile
from triagebot.triage import TriageService
from triagebot.cleaning import TicketCleaner

from triagebot.dashboard import Dashboard
from triagebot.stats import TriageStats


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", default="tickets.json")
    parser.add_argument("--output", default="results.json")
    parser.add_argument("--model", default=DEFAULT_MODEL)

    args = parser.parse_args()

    input_storage = JsonFile(args.input)
    output_storage = JsonFile(args.output)

    client = OllamaClient(args.model)
    service = TriageService(client)
    cleaner = TicketCleaner()

    client.check_ready()

    raw_tickets = input_storage.read()
    tickets = cleaner.clean(raw_tickets)

    results = []

    for index, ticket in enumerate(tickets, start=1):
        print(f"[{index}/{len(tickets)}] ticket {ticket.id}…")
        results.append(service.triage(ticket))

    output_storage.write([result.model_dump(mode="json") for result in results])

    stats = TriageStats(results)
    dashboard = Dashboard(stats)
    dashboard.display()


if __name__ == "__main__":
    try:
        main()
    except TriageError as exc:
        print(f"Erreur : {exc}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterruption.")
        sys.exit(1)
