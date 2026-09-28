import re

INJECTION_PATTERNS = [
    r"ignore\s+.*instructions",
    r"ignore\s+(the\s+)?previous",
    r"previous\s+instructions",
    r"system\s+(prompt|message)",
    r"prompt\s+système",
    r"instructions\s+précédentes",
    r"classe\s+ce\s+ticket",
    r"ignore\s+.*anweisungen",
    r"vorherigen\s+anweisungen",
]


class InjectionDetector:
    def __init__(self) -> None:
        self.patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in INJECTION_PATTERNS
        ]

    def is_suspicious(self, message: str) -> bool:
        return any(pattern.search(message) for pattern in self.patterns)
