from triagebot.models import Analysis, Ticket, TriageResult
from triagebot.stats import TriageStats


def make_result(ticket_id, severity, suspicious=False):
    return TriageResult(
        ticket=Ticket(id=ticket_id, player="Player", message="Message"),
        analysis=Analysis(
            category="payment",
            sentiment="negative",
            severity=severity,
            summary="Résumé",
        ),
        status="ok",
        suspicious=suspicious,
    )


def test_suspicious_ticket_is_excluded_from_stats():
    stats = TriageStats(
        [
            make_result(1, severity=2),
            make_result(2, severity=5, suspicious=True),
        ]
    )

    assert stats.average_severity() == 2
    assert [result.ticket.id for result, _ in stats.top_3()] == [1]
    assert stats.categories() == {"to_check": 1, "payment": 1}
