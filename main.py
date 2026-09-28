import argparse
import sys

from pydantic import ValidationError

from triagebot.config import DEFAULT_MODEL
from triagebot.errors import TriageError
from triagebot.llm import OllamaClient
from triagebot.models import Ticket
from triagebot.storage import JsonFile
from triagebot.triage import TriageService


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

    client.check_ready()

    raw_tickets = input_storage.read()

    try:
        tickets = [Ticket.model_validate(item) for item in raw_tickets]
    except ValidationError as exc:
        raise TriageError(f"Ticket invalide dans {args.input} : {exc}") from exc

    results = []

    for index, ticket in enumerate(tickets, start=1):
        print(f"[{index}/{len(tickets)}] ticket {ticket.id}…")
        results.append(service.triage(ticket))

    output_storage.write([result.model_dump(mode="json") for result in results])


if __name__ == "__main__":
    try:
        main()
    except TriageError as exc:
        print(f"Erreur : {exc}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterruption.")
        sys.exit(1)
