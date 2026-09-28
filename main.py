import argparse

from triagebot.config import DEFAULT_MODEL
from triagebot.llm import OllamaClient
from triagebot.models import Ticket
from triagebot.storage import JsonFile
from triagebot.triage import TriageService


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        default="tickets.json",
    )

    parser.add_argument(
        "--output",
        default="results.json",
    )

    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
    )

    args = parser.parse_args()

    input_file = JsonFile(args.input)
    output_file = JsonFile(args.output)

    data = input_file.read()
    tickets = [Ticket.model_validate(ticket) for ticket in data]

    client = OllamaClient(args.model)
    service = TriageService(client)

    results = []

    for index, ticket in enumerate(tickets, start = 1):
        print(f"[{index}/{len(tickets)}] ticket {ticket.id}…")

        result = service.triage(ticket)
        results.append(result)

    output_data = [result.model_dump(mode = "json") for result in results]

    output_file.write(output_data)


if __name__ == "__main__":
    main()
