from triagebot.config import ESCALATION_PAYMENT_SEVERITY
from triagebot.models import Escalation, TriageResult


class EscalationPolicy:
    def decide(self, result: TriageResult) -> Escalation:
        if result.suspicious or result.status == "to_check" or result.analysis is None:
            return "human_review"

        if result.analysis.category == "toxicity":
            return "moderation"

        if (
            result.analysis.category == "payment"
            and result.analysis.severity >= ESCALATION_PAYMENT_SEVERITY
        ):
            return "support_manager"

        return "standard"
