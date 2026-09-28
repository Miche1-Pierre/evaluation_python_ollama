import json
from typing import Any

from triagebot.errors import TriageError


def write_text(path: str, text: str) -> None:
    try:
        with open(path, "w", encoding="utf-8") as file:
            file.write(text)

    except OSError as exc:
        raise TriageError(f"Impossible d'écrire dans le fichier : {path}") from exc


class JsonFile:
    def __init__(self, path: str):
        self.path = path

    def read(self) -> list[Any]:
        try:
            with open(self.path, "r", encoding="utf-8-sig") as file:
                data = json.load(file)

        except FileNotFoundError as exc:
            raise TriageError(f"Fichier introuvable : {self.path}") from exc

        except UnicodeDecodeError as exc:
            raise TriageError(
                f"{self.path} illisible : enregistre le fichier en UTF-8"
            ) from exc

        except json.JSONDecodeError as exc:
            raise TriageError(
                f"{self.path} invalide (ligne {exc.lineno}, colonne {exc.colno})"
            ) from exc

        except OSError as exc:
            raise TriageError(f"Impossible de lire le fichier : {self.path}") from exc

        if not isinstance(data, list):
            raise TriageError(f"{self.path} invalide : le contenu doit être une liste")

        return data

    def write(self, data: list[Any]) -> None:
        write_text(self.path, json.dumps(data, ensure_ascii=False, indent=2))
