import pytest
from src.ui.components import BranchTimeEntry


@pytest.mark.parametrize(
    'time, expected_time',
    [
        ('0:0', (0,0)),
        ('0:10', (0,10)),
        ('1:0', (1,0)),
        ('1h10m', (1, 10)),
        ('1h 10m', (1, 10)),
        ('10m', (0, 10)),
        ('', (0, 0)),
    ],
)
def test_parse_time(time, expected_time):
    assert BranchTimeEntry.parse_time(time) == expected_time
