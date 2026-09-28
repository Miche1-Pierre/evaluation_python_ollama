from triagebot.escalation import EscalationPolicy
from triagebot.models import Analysis, Ticket, TriageResult


def make_result(
    status="ok",
    category="bug",
    severity=1,
    suspicious=False,
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
            )
            if status == "ok"
            else None
        ),
        status=status,
        suspicious=suspicious,
    )


def test_to_check_goes_to_human_review():
    result = make_result(status="to_check")

    assert EscalationPolicy().decide(result) == "human_review"


def test_toxicity_goes_to_moderation():
    result = make_result(category="toxicity")

    assert EscalationPolicy().decide(result) == "moderation"


def test_payment_high_severity_goes_to_support_manager():
    result = make_result(category="payment", severity=4)

    assert EscalationPolicy().decide(result) == "support_manager"


def test_standard_ticket_has_no_escalation():
    result = make_result(category="bug", severity=3)

    assert EscalationPolicy().decide(result) == "standard"


def test_suspicious_has_priority():
    result = make_result(
        category="payment",
        severity=5,
        suspicious=True,
    )

    assert EscalationPolicy().decide(result) == "human_review"


def test_payment_low_severity_is_standard():
    result = make_result(category="payment", severity=3)

    assert EscalationPolicy().decide(result) == "standard"
