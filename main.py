from triagebot.models import Ticket
from triagebot.storage import JsonFile
from triagebot.llm import OllamaClient

file = JsonFile("tickets.json")
data = file.read()
client = OllamaClient("qwen2.5:7b-instruct")

tickets = [Ticket.model_validate(ticket) for ticket in data]
analysis = client.analyze(tickets[0])

print("Category:", analysis.category)
print("Sentiment:", analysis.sentiment)
print("Severity:", analysis.severity)
print("Summary:", analysis.summary)