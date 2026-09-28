from typing import Literal

from triagebot.config import ESCALATION_PAYMENT_SEVERITY
from triagebot.models import TriageResult

Escalation = Literal[
    "moderation",
    "support_manager",
    "human_review",
    "standard",
]


class EscalationPolicy:
    def decide(self, result: TriageResult) -> Escalation:
        if result.status == "to_check":
            return "human_review"

        if result.analysis is not None and result.analysis.toxicity:
            return "moderation"

        if (
            result.analysis is not None
            and result.analysis.category == "billing"
            and result.analysis.severity >= ESCALATION_PAYMENT_SEVERITY
        ):
            return "support_manager"

        return "standard"
