import pytest

from core.scenarios import TEST_SCENARIOS


@pytest.mark.parametrize("test", [row[4] for row in TEST_SCENARIOS],
                         ids=[f"{row[0]:02d} {row[2]}" for row in TEST_SCENARIOS])
def test_scenario(test):
    passed, detail = test()
    assert passed, detail
