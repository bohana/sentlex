import pytest

from sentlex.stopwords import Stopword


@pytest.mark.parametrize('word, result',[
    ('and', True), ('joseph', False), ('', False)])
def test_stop(word, result):
    assert Stopword().is_stop(word) == result
