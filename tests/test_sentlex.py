import pytest

import sentlex


@pytest.fixture(scope='module')
def moby():
    return sentlex.MobyLexicon()


def test_set_name(moby):
    moby.set_name('UnitTest')
    assert moby.get_name() == 'UnitTest'


def test_adjectives(moby):
    assert moby.hasadjective('good')
    assert not moby.hasadjective('notaword')


def test_word_seeds(moby):
    assert moby.getadjective('good') == (1.0, 0.0)
    assert moby.getadjective('bad') == (0.0, 1.0)


def test_get_info(moby):
    assert moby.get_info()['a']['size'] > 0
    assert moby.get_info()['v']['size'] > 0
    assert moby.get_info()['n']['size'] > 0
    assert moby.get_info()['r']['size'] > 0


@pytest.fixture(scope='module')
def swn3():
    L = sentlex.SWN3Lexicon()
    L.compile_frequency()
    return L


@pytest.mark.parametrize('word, freq', [
    ('bad', 0.0005451764705882353),
    ('good', 0.002610137254901961),
    ('the', 0.029449176470588236),
    ('want', 0.0027591764705882354)])
def test_frequency(swn3, word, freq):
    assert swn3.get_freq(word) == freq
