import pytest

import sentlex


@pytest.fixture(scope='module')
def comp():
    L1 = sentlex.UICLexicon()
    L2 = sentlex.SWN3Lexicon()
    L = sentlex.CompositeLexicon()

    L.add_lexicon(L1)
    L.add_lexicon(L2)
    L.compile_frequency()
    return L


def test_composite_basic_setup(comp):
    assert len(comp.LLIST) == 2
    assert comp.is_compiled
    assert comp.is_loaded
    assert comp.get_freq('good') > 0.0


def test_composite(comp):
    assert comp.getadjective('bad') != (0.0, 0.0)


def test_factor(comp):
    comp.set_factor(0.5)
    assert comp.getadjective('bad') == (0.0, 1.0)

    comp.set_factor(1.0)
    nval = comp.getadjective('undeniable')[1]
    comp.set_factor(0.25)
    assert comp.getadjective('undeniable')[1] < nval
