from datetime import datetime

from triagebot.models import TriageResult
from triagebot.stats import TriageStats

CATEGORY_LABELS = {
    "bug": "Bug",
    "payment": "Paiement",
    "account": "Compte",
    "suggestion": "Suggestion",
    "toxicity": "Toxicité",
    "autre": "Autre",
    "to_check": "À vérifier",
}

ESCALATION_LABELS = {
    "moderation": "Modération",
    "support_manager": "Responsable support",
    "human_review": "Relecture humaine",
}


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
        self.stats = TriageStats(results)
        self.to_check = [result for result in results if result.needs_review]

    def render(self) -> str:
        lines = self._header() + self._summary() + self._escalated() + self._to_check()
        return "\n".join(lines)

    def _header(self) -> list[str]:
        return [
            "# Rapport de triage",
            "",
            f"**Date :** {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            f"**Modèle :** {self.model}",
        ]

    def _summary(self) -> list[str]:
        analyzed = sum(1 for result in self.results if result.status == "ok")

        lines = [
            "",
            "## Synthèse",
            "",
            f"- Tickets reçus : **{self.received_count}**",
            f"- Tickets analysés : **{analyzed}**",
            f"- Tickets ignorés (vides, invalides ou doublons) : **{self.ignored_count}**",
            f"- Tickets à vérifier : **{len(self.to_check)}**",
            f"- Urgence moyenne : **{self.stats.average_severity():.2f} / 5**",
            "",
            "| Catégorie | Nombre |",
            "|---|---:|",
        ]

        for category, count in self.stats.categories().items():
            lines.append(f"| {CATEGORY_LABELS.get(category, category)} | {count} |")

        return lines

    def _escalated(self) -> list[str]:
        lines = [
            "",
            "## Tickets à escalader",
            "",
            "| N° | Joueur | Catégorie | Urgence | Destinataire | Résumé |",
            "|---:|---|---|---:|---|---|",
        ]

        for result in self.results:
            if result.escalation == "standard":
                continue

            analysis = result.analysis
            category = analysis.category if analysis else "to_check"
            severity = analysis.severity if analysis else "-"
            summary = analysis.summary.replace("|", "\\|") if analysis else "-"

            lines.append(
                f"| {result.ticket.id} "
                f"| {result.ticket.player} "
                f"| {CATEGORY_LABELS[category]} "
                f"| {severity} "
                f"| {ESCALATION_LABELS.get(result.escalation or '', '-')} "
                f"| {summary} |"
            )

        return lines

    def _to_check(self) -> list[str]:
        lines = ["", "## Tickets à vérifier", ""]

        if not self.to_check:
            lines.append("Aucun ticket à vérifier.")

        for result in self.to_check:
            reason = (
                "tentative de manipulation du bot"
                if result.suspicious
                else "analyse automatique impossible"
            )
            lines.append(
                f"- **Ticket {result.ticket.id}** ({result.ticket.player}) : {reason}"
            )

        return lines
