import ollama

from triagebot.config import HOST
from triagebot.models import Analysis, Ticket
from triagebot.prompts import SYSTEM_PROMPT


class OllamaClient:
    def __init__(self, model):
        self.client = ollama.Client(host=HOST)
        self.model = model

    def analyze(self, ticket: Ticket, feedback: str | None = None) -> Analysis:
        user_message = f"<ticket>{ticket.message}</ticket>"

        if feedback:
            user_message += f"\n\nTa réponse précédente était invalide : {feedback}"

        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
            format=Analysis.model_json_schema(),
            options={
                "temperature": 0,
            },
        )

        return Analysis.model_validate_json(response.message.content)
