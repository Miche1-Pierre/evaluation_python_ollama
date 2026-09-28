from triagebot.escalation import EscalationPolicy
from triagebot.models import Analysis, Ticket, TriageResult


def make_result(
    status="ok",
    category="bug",
    severity=1,
    toxicity=False,
):
    return TriageResult(
        ticket=Ticket(
            id=1,
            player="Player",
            message="Message",
        ),
        analysis=(
            Analysis(
                category=category,
                sentiment="neutral",
                severity=severity,
                summary="Résumé",
                toxicity=toxicity,
            )
            if status == "ok"
            else None
        ),
        status=status,
    )


def test_to_check_goes_to_human_review():
    result = make_result(status="to_check")

    assert EscalationPolicy().decide(result) == "human_review"


def test_toxicity_goes_to_moderation():
    result = make_result(toxicity=True)

    assert EscalationPolicy().decide(result) == "moderation"


def test_billing_high_severity_goes_to_support_manager():
    result = make_result(category="billing", severity=4)

    assert EscalationPolicy().decide(result) == "support_manager"


def test_standard_ticket_has_no_escalation():
    result = make_result(category="bug", severity=3)

    assert EscalationPolicy().decide(result) == "standard"


def test_to_check_has_priority_over_toxicity():
    result = make_result(
        status="to_check",
        toxicity=True,
    )

    assert EscalationPolicy().decide(result) == "human_review"


def test_toxicity_has_priority_over_billing():
    result = make_result(
        category="billing",
        severity=5,
        toxicity=True,
    )

    assert EscalationPolicy().decide(result) == "moderation"
