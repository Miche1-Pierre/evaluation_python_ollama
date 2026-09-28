from triagebot.stats import TriageStats


class Dashboard:
    def __init__(self, stats: TriageStats):
        self.stats = stats

    def display(self) -> None:
        print("\n=== Tickets par catégorie ===")

        for category, count in self.stats.categories().items():
            print(f"{category:<12} {count}")

        print("\n=== Urgence moyenne ===")
        print(f"{self.stats.average_severity():.2f}")

        print("\n=== Top 3 urgences ===")

        for result in self.stats.top_3():
            print(
                f"ticket {result.ticket.id:<4} " f"urgence {result.analysis.severity}"
            )
