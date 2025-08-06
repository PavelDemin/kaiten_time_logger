import pytest

from src.ui.components import BranchTimeEntry


@pytest.mark.parametrize(
    'time, expected_time',
    [
        ('5', (5, 0)),
        ('0:0', (0, 0)),
        ('0:10', (0, 10)),
        ('1:0', (1, 0)),
        ('1h10m', (1, 10)),
        ('1ч10м', (1, 10)),
        ('1h 10m', (1, 10)),
        ('1ч 10м', (1, 10)),
        ('1h', (1, 0)),
        ('10m', (0, 10)),
        ('1ч', (1, 0)),
        ('10м', (0, 10)),
        ('', (0, 0)),
    ],
)
def test_parse_time(time, expected_time):
    assert BranchTimeEntry.parse_time(time) == expected_time
