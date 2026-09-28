from triagebot.cleaning import TicketCleaner


def test_empty_message_is_rejected():
    cleaner = TicketCleaner()

    tickets = cleaner.clean(
        [
            {
                "id": 1,
                "player": "Player",
                "message": "   ",
            }
        ]
    )

    assert tickets == []
    assert len(cleaner.rejected) == 1


def test_duplicate_is_rejected():
    cleaner = TicketCleaner()

    tickets = cleaner.clean(
        [
            {
                "id": 1,
                "player": "Player",
                "message": "Le jeu plante.",
            },
            {
                "id": 2,
                "player": "Player",
                "message": "  LE JEU PLANTE.  ",
            },
        ]
    )

    assert len(tickets) == 1
    assert tickets[0].id == 1
    assert len(cleaner.rejected) == 1


def test_same_message_from_different_player_is_kept():
    cleaner = TicketCleaner()

    tickets = cleaner.clean(
        [
            {
                "id": 1,
                "player": "PlayerOne",
                "message": "Le jeu plante.",
            },
            {
                "id": 2,
                "player": "PlayerTwo",
                "message": "Le jeu plante.",
            },
        ]
    )

    assert len(tickets) == 2
    assert len(cleaner.rejected) == 0
