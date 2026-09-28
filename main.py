from triagebot.models import Ticket
from triagebot.storage import JsonFile

file = JsonFile("tickets.json")

data = file.read()

tickets = [Ticket.model_validate(ticket) for ticket in data]

print(type(tickets))
print(len(tickets))
print(type(tickets[0]))