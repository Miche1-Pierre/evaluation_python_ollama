from pydantic import ValidationError

from triagebot.models import Ticket


class TicketCleaner:
    def __init__(self):
        self.rejected = []

    def clean(self, raw_items) -> list[Ticket]:
        tickets = []
        self.rejected = []

        for item in raw_items:
            try:
                ticket = Ticket.model_validate(item)
                tickets.append(ticket)

            except ValidationError as exc:
                item_id = item.get("id") if isinstance(item, dict) else None

                self.rejected.append(
                    {
                        "id": item_id,
                        "reason": str(exc),
                    }
                )

        return tickets
