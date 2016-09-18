import pytest

from sentlex.sentanalysis import DocSentiScore


@pytest.fixture
def basic_docscore():
    return DocSentiScore()


def test_default_config(basic_docscore):
    assert basic_docscore.config.negation
