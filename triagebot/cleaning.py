from typing import Any

from pydantic import ValidationError

from triagebot.models import Ticket


class TicketCleaner:
    def __init__(self) -> None:
        self.rejected: list[dict[str, Any]] = []

    def clean(self, raw_items: list[Any]) -> list[Ticket]:
        tickets = []
        self.rejected = []
        seen: dict[tuple[str, str], int] = {}

        for item in raw_items:
            try:
                ticket = Ticket.model_validate(item)

            except ValidationError as exc:
                item_id = item.get("id") if isinstance(item, dict) else None
                fields = ", ".join(str(error["loc"][0]) for error in exc.errors() if error["loc"])
                self._reject(item_id, f"ticket invalide (champ : {fields or 'format'})")
                continue

            key = (ticket.player, ticket.message.casefold())

            if key in seen:
                self._reject(ticket.id, f"doublon du ticket {seen[key]}")
                continue

            seen[key] = ticket.id
            tickets.append(ticket)

        return tickets

    def _reject(self, ticket_id: Any, reason: str) -> None:
        print(f"ticket {ticket_id} ignoré : {reason}")
        self.rejected.append({"id": ticket_id, "reason": reason})
