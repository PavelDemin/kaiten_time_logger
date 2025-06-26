import pytest

from src.core.git_manager import GitManager


@pytest.mark.parametrize(
    'branch_name, expected_id',
    [
        ('ABCD-11231131', 11231131),
        ('ABCD-46466464_dsfkjdf', 46466464),
        ('abasdbsad-4564654564-jdsfjlj-454', 4564654564),
        ('feature-123456789', 123456789),
        ('bugfix-987654321-test', 987654321),
        ('SUPER-123456789_fix', 123456789),
        ('NIOKR-987654321', 987654321),
        ('main', None),
        ('develop', None),
        ('feature-without-id', None),
        ('branch-with-no-numbers', None),
        ('branch_without_hyphen', None),
    ],
)
def test_extract_card_id(branch_name, expected_id):
    assert GitManager._extract_card_id(branch_name) == expected_id
