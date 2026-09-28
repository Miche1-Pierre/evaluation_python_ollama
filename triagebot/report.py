from datetime import datetime

from triagebot.models import TriageResult
from triagebot.stats import TriageStats


class MarkdownReport:
    def __init__(
        self,
        results: list[TriageResult],
        received_count: int,
        ignored_count: int,
        model: str,
    ):
        self.results = results
        self.received_count = received_count
        self.ignored_count = ignored_count
        self.model = model

    def render(self) -> str:
        stats = TriageStats(self.results)

        analyzed_count = sum(1 for result in self.results if result.status == "ok")

        to_check_count = sum(
            1 for result in self.results if result.status == "to_check"
        )

        categories = stats.categories()

        lines = [
            "# Rapport de triage",
            "",
            f"**Date :** {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            f"**Modèle :** {self.model}",
            "",
            "## Synthèse",
            "",
            f"- Tickets reçus : **{self.received_count}**",
            f"- Tickets analysés : **{analyzed_count}**",
            f"- Tickets ignorés : **{self.ignored_count}**",
            f"- Tickets à vérifier : **{to_check_count}**",
            "",
            "### Tickets par catégorie",
            "",
            "| Catégorie | Nombre |",
            "|---|---:|",
        ]

        for category, count in categories.items():
            label = {
                "bug": "Bug",
                "feature_request": "Demande de fonctionnalité",
                "billing": "Facturation",
                "account": "Compte",
                "how_to": "Aide / mode d'emploi",
                "other": "Autre",
                "to_check": "À vérifier",
            }.get(category, category)

            lines.append(f"| {label} | {count} |")

        lines.extend(
            [
                "",
                f"**Urgence moyenne :** {stats.average_severity():.2f}",
                "",
                "## Tickets à escalader",
                "",
                "| N° | Joueur | Catégorie | Urgence | Destinataire | Résumé |",
                "|---:|---|---|---:|---|---|",
            ]
        )

        escalated = [
            result for result in self.results if result.escalation != "standard"
        ]

        for result in escalated:
            analysis = result.analysis

            if analysis is None:
                continue

            destination = {
                "moderation": "Modération",
                "support_manager": "Responsable support",
                "human_review": "Revue humaine",
            }.get(result.escalation, result.escalation)

            category_label = {
                "bug": "Bug",
                "feature_request": "Demande de fonctionnalité",
                "billing": "Facturation",
                "account": "Compte",
                "how_to": "Aide / mode d'emploi",
                "other": "Autre",
            }.get(analysis.category, analysis.category)

            summary = analysis.summary.replace("|", "\\|")

            lines.append(
                f"| {result.ticket.id} "
                f"| {result.ticket.player} "
                f"| {category_label} "
                f"| {analysis.severity} "
                f"| {destination} "
                f"| {summary} |"
            )

        lines.extend(
            [
                "",
                "## Tickets à vérifier",
                "",
            ]
        )

        to_check = [result for result in self.results if result.status == "to_check"]

        if not to_check:
            lines.append("Aucun ticket à vérifier.")

        for result in to_check:
            lines.append(
                f"- **Ticket {result.ticket.id}** — " f"{result.ticket.player}"
            )

        return "\n".join(lines)
