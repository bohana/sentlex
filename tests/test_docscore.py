import pytest

import sentlex
import sentlex.sentanalysis as sentdoc

TESTDOC_ADJ = 'good/JJ good/JJ good/JJ good/JJ good/JJ good/JJ good/JJ good/JJ good/JJ good/JJ'
TESTDOC_UNTAGGED = 'this cookie is good. it is very good indeed'
TESTDOC_BADADJ = 'bad_JJ Bad_JJ bAd_JJ'
TESTDOC_NEGATED = 'not/DT bad/JJ ./. not/DT really/RR bad/JJ'
TESTDOC_CORRUPT = 'this_DT doc_NN is_VB not_DT not_DT not_DT in great/JJ shape/JJ good_JJ good_JJ good_JJ'
TESTDOC_EMPTY = ''


@pytest.fixture
def ds():
    ds = sentdoc.BasicDocSentiScore()
    ds.verbose = False
    return ds


def test_docscore_parameters(ds):
    ds.set_parameters(negation=True)
    ds.set_parameters(negation_window=15)
    ds.set_parameters(a=True, v=False, n=False, r=False)

    assert (ds.config.a, ds.config.v, ds.config.n, ds.config.r) ==\
                     (True, False, False, False)

    assert ds.config.negation
    assert ds.config.negation_window == 15


def test_docscore_reset_parameters(ds):
    ds.set_parameters(score_freq=True)
    assert ds.config.score_freq
    ds.set_parameters(score_freq=False)
    assert not ds.config.score_freq


def test_detect_tag(ds):
    assert ds._detect_tag(TESTDOC_ADJ) == '/'


def test_scoring(ds):
    # load lexicon
    L = sentlex.MobyLexicon()

    ds.set_parameters(score_mode=ds.SCOREALL, score_freq=False, negation=False, a=True, v=False)
    ds.set_lexicon(L)

    # now score!
    (dpos, dneg) = ds.classify_document(TESTDOC_ADJ)
    assert dpos > dneg

    # again, for negative text
    (dpos, dneg) = ds.classify_document(TESTDOC_BADADJ)
    assert dneg > dpos

    # negated text
    ds.set_parameters(negation=True)
    ds.set_parameters(negation_window=15)
    (dpos, dneg) = ds.classify_document(TESTDOC_NEGATED)
    assert dpos > dneg


@pytest.fixture(scope='module')
def moby():
    return sentlex.MobyLexicon()


@pytest.fixture(scope='module')
def ds_loaded(moby):
    ds = sentdoc.BasicDocSentiScore()
    ds.set_lexicon(moby)
    ds.verbose = False
    return ds


def test_scoring_untagged_raises(ds_loaded):
    with pytest.raises(RuntimeError):
        ds_loaded.classify_document(TESTDOC_UNTAGGED)


def test_scoring_untagged(ds_loaded):
    (dpos, dneg) = ds_loaded.classify_document(TESTDOC_UNTAGGED, tagged=False)
    assert dpos > 0


def test_sample_classes(moby):
    for algo in [sentdoc.AV_AllWordsDocSentiScore(moby),
                 sentdoc.A_AllWordsDocSentiScore(moby),
                 sentdoc.A_OnceWordsDocSentiScore(moby),
                 sentdoc.AV_OnceWordsDocSentiScore(moby)]:
        (p, n) = algo.classify_document(TESTDOC_ADJ, verbose=True)
        assert p > n
