import json
from typing import Any

from triagebot.errors import TriageError


class JsonFile:
    def __init__(self, path: str):
        self.path = path

    def read(self) -> list[Any]:
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                data = json.load(file)

        except FileNotFoundError as exc:
            raise TriageError(f"Fichier introuvable : {self.path}") from exc

        except json.JSONDecodeError as exc:
            raise TriageError(
                f"{self.path} invalide (ligne {exc.lineno}, colonne {exc.colno})"
            ) from exc

        if not isinstance(data, list):
            raise TriageError(f"{self.path} invalide : le contenu doit être une liste")

        return data

    def write(self, data: list[Any]) -> None:
        try:
            with open(self.path, "w", encoding="utf-8") as file:
                file.write(
                    json.dumps(
                        data,
                        ensure_ascii=False,
                        indent=2,
                    )
                )

        except OSError as exc:
            raise TriageError(
                f"Impossible d'écrire dans le fichier : {self.path}"
            ) from exc
