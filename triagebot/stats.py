from collections import Counter
from heapq import nlargest

from triagebot.models import Analysis, TriageResult


class TriageStats:
    def __init__(self, results: list[TriageResult]):
        self.results = results

    def categories(self) -> dict[str, int]:
        counter: Counter[str] = Counter(
            "to_check" for result in self.results if result.needs_review
        )

        for _, analysis in self._trusted():
            counter[analysis.category] += 1

        return dict(counter)

    def average_severity(self) -> float:
        severities = [analysis.severity for _, analysis in self._trusted()]

        if not severities:
            return 0.0

        return sum(severities) / len(severities)

    def top_3(self) -> list[tuple[TriageResult, Analysis]]:
        return nlargest(3, self._trusted(), key=lambda pair: pair[1].severity)

    def _trusted(self) -> list[tuple[TriageResult, Analysis]]:
        """Tickets analysés dont on peut croire l'analyse (ni to_check ni suspects)."""
        return [
            (result, result.analysis)
            for result in self.results
            if result.analysis is not None and not result.needs_review
        ]
