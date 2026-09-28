from pydantic import ValidationError

from triagebot.models import Ticket


class TicketCleaner:
    def __init__(self):
        self.rejected = []

    def clean(self, raw_items) -> list[Ticket]:
        tickets = []
        self.rejected = []

        seen = {}

        for item in raw_items:
            try:
                ticket = Ticket.model_validate(item)

            except ValidationError as exc:
                item_id = item.get("id") if isinstance(item, dict) else None

                self.rejected.append(
                    {
                        "id": item_id,
                        "reason": str(exc),
                    }
                )
                continue

            key = (
                ticket.player,
                ticket.message.strip().casefold(),
            )

            if key in seen:
                print(f"ticket {ticket.id} ignoré : " f"doublon du ticket {seen[key]}")

                self.rejected.append(
                    {
                        "id": ticket.id,
                        "reason": f"doublon du ticket {seen[key]}",
                    }
                )
                continue

            seen[key] = ticket.id
            tickets.append(ticket)

        return tickets
