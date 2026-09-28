from typing import Any

import ollama

from triagebot.config import HOST
from triagebot.errors import TriageError
from triagebot.models import Analysis, Ticket
from triagebot.prompts import DRAFT_REPLY_SYSTEM_PROMPT, SYSTEM_PROMPT

SIGNATURE = "PixelForge"


class OllamaClient:
    def __init__(self, model: str):
        self.client = ollama.Client(host=HOST)
        self.model = model

    def check_ready(self) -> None:
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

    def analyze(self, ticket: Ticket, feedback: str | None = None) -> Analysis:
        user_message = f"<ticket>{ticket.message}</ticket>"

        if feedback:
            user_message += f"\n\nTa réponse précédente était invalide : {feedback}"

        content = self._chat(
            SYSTEM_PROMPT,
            user_message,
            format=Analysis.model_json_schema(),
            options={"temperature": 0},
        )

        return Analysis.model_validate_json(content)

    def draft_reply(self, ticket: Ticket) -> str:
        content = self._chat(
            DRAFT_REPLY_SYSTEM_PROMPT,
            f"<ticket>{ticket.message}</ticket>",
            options={"temperature": 0.3},
        )

        return f"{content.strip()}\n\n{SIGNATURE}"

    def _chat(self, system_prompt: str, user_message: str, **kwargs: Any) -> str:
        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                **kwargs,
            )

        except ConnectionError as exc:
            raise TriageError("Connexion à Ollama perdue.") from exc

        except ollama.ResponseError as exc:
            raise TriageError(f"Erreur Ollama : {exc}") from exc

        return response.message.content or ""
