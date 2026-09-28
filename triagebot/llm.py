import ollama

from triagebot.config import HOST
from triagebot.models import Analysis, Ticket
from triagebot.prompts import SYSTEM_PROMPT
from triagebot.errors import TriageError


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

    def check_ready(self):
        try:
            self.client.show(self.model)

        except ConnectionError as exc:
            raise TriageError(
                "Ollama n'est pas lancé ou n'est pas accessible."
            ) from exc

        except ollama.ResponseError as exc:
            if exc.status_code == 404:
                raise TriageError(f"Modèle Ollama introuvable : {self.model}") from exc

            raise TriageError(f"Erreur Ollama : {exc}") from exc
