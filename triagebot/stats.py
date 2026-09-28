from collections import Counter
from heapq import nlargest

from triagebot.models import TriageResult


class TriageStats:
    def __init__(self, results: list[TriageResult]):
        self.results = results

    def categories(self) -> dict[str, int]:
        counter = Counter()

        for result in self.results:
            if result.status == "to_check":
                counter["to_check"] += 1
            elif result.analysis is not None:
                counter[result.analysis.category] += 1

        return dict(counter)

    def average_severity(self) -> float:
        severities = [
            result.analysis.severity
            for result in self.results
            if result.status == "ok" and result.analysis is not None
        ]

        if not severities:
            return 0.0

        return sum(severities) / len(severities)

    def top_3(self) -> list[TriageResult]:
        analyzed = [
            result
            for result in self.results
            if result.status == "ok" and result.analysis is not None
        ]

        return nlargest(
            3,
            analyzed,
            key=lambda result: result.analysis.severity,
        )
