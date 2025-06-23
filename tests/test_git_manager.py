from src.core.git_manager import GitManager


def test_extract_card_id():
    assert GitManager._extract_card_id('ABCD-11231131') == 11231131
    assert GitManager._extract_card_id('ABCD-46466464_dsfkjdf') == 46466464
    assert GitManager._extract_card_id('abasdbsad-4564654564-jdsfjlj-454') == 4564654564
    assert GitManager._extract_card_id('feature-123456789') == 123456789
    assert GitManager._extract_card_id('bugfix-987654321-test') == 987654321
    assert GitManager._extract_card_id('SUPER-123456789_fix') == 123456789
    assert GitManager._extract_card_id('NIOKR-987654321') == 987654321

    assert GitManager._extract_card_id('main') is None
    assert GitManager._extract_card_id('develop') is None
    assert GitManager._extract_card_id('feature-without-id') is None
    assert GitManager._extract_card_id('branch-with-no-numbers') is None
    assert GitManager._extract_card_id('branch_without_hyphen') is None
