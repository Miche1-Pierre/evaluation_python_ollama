import pytest
from pydantic import ValidationError

from triagebot.models import Analysis


@pytest.mark.parametrize(
    "data",
    [
        {
            "category": "bug",
            "sentiment": "negative",
            "severity": 3,
            "summary": "Le jeu plante.",
            "toxicity": False,
        },
    ],
)
def test_valid_analysis(data):
    analysis = Analysis.model_validate(data)

    assert analysis.category == "bug"


@pytest.mark.parametrize(
    "data",
    [
        {
            "category": "unknown",
            "sentiment": "neutral",
            "severity": 3,
            "summary": "Résumé",
            "toxicity": False,
        },
        {
            "category": "bug",
            "sentiment": "neutral",
            "severity": 0,
            "summary": "Résumé",
            "toxicity": False,
        },
        {
            "category": "bug",
            "sentiment": "neutral",
            "severity": 6,
            "summary": "Résumé",
            "toxicity": False,
        },
        {
            "category": "bug",
            "sentiment": "neutral",
            "severity": 3,
            "toxicity": False,
        },
    ],
)
def test_invalid_analysis(data):
    with pytest.raises(ValidationError):
        Analysis.model_validate(data)


def test_invalid_json():
    with pytest.raises(ValidationError):
        Analysis.model_validate_json("{invalid json")
