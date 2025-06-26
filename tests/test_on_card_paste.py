import pytest

from src.ui.components import ManualTimeEntry


@pytest.mark.parametrize(
    'pasted_text, expected_card_id',
    [
        ('https://rtsoft-sg.kaiten.ru/space/12345/boards/card/51587968', '51587968'),
        ('https://rtsoft-sg.kaiten.ru/51587968', '51587968'),
        ('51587968', '51587968'),
        ('https://rtsoft-sg.kaiten.ru/space/12345', None),
        ('', None),
    ],
)
def test_on_card_paste(pasted_text, expected_card_id):
    card_id = ManualTimeEntry._fetch_card_id(pasted_text)
    assert card_id == expected_card_id
