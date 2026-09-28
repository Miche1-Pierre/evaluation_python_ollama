import ollama

from triagebot.models import Analysis, Ticket
from triagebot.prompts import SYSTEM_PROMPT


class OllamaClient:
    def __init__(self, model):
        self.client = ollama.Client(host="http://127.0.0.1:11434")
        self.model = model

    def analyze(self, ticket: Ticket) -> Analysis:
        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": f"<ticket>{ticket.message}</ticket>",
                },
            ],
            format=Analysis.model_json_schema(),
            options={
                "temperature": 0,
            },
        )

        return Analysis.model_validate_json(response.message.content)
