import pytest

import sentlex.sentanalysis_potts as sentdoc
import sentlex


TESTDOC_ADJ = 'good/JJ good/JJ good/JJ good/JJ good/JJ good/JJ good/JJ good/JJ good/JJ good/JJ'
TESTDOC_UNTAGGED = 'this cookie is good. it is very good indeed'
TESTDOC_BADADJ = 'bad_JJ Bad_JJ bAd_JJ'
TESTDOC_NEGATED = 'not/DT bad/JJ movie/NN ./. blah/NN blah/NN not/DT really/RR good/JJ either/DT ./.'
TESTDOC_CORRUPT = 'this_DT doc_NN is_VB not_DT not_DT not_DT in great/JJ shape/JJ good_JJ good_JJ good_JJ'
TESTDOC_EMPTY = ''


@pytest.fixture(scope='module')
def moby():
    return sentlex.MobyLexicon()


@pytest.fixture(scope='module')
def ds(moby):
    ds = sentdoc.PottsDocSentiScore()
    ds.verbose = False
    ds.set_lexicon(moby)
    ds.set_parameters(a=True, v=False, n=False, r=False, negation=True, negation_window=15, negation_adjustment=0.5)
    return ds


def test_potts_parameters(ds):
    assert ds.config.negation
    assert ds.config.negation_window == 15
    assert ds.config.negation_adjustment == 0.5


def test_atenuation(ds):
    negated_sent = 'not/DT good/JJ'

    (dpos, dneg) = ds.classify_document(negated_sent)
    assert dneg > dpos

    ds.set_parameters(negation=True, negation_window=15, atenuation=True, at_pos=0.5, at_neg=0.5)
    (dpos, dneg) = ds.classify_document(negated_sent)
    ds.set_parameters(negation=True, negation_window=15, atenuation=True, at_pos=1.0, at_neg=1.0)
    (dposfull, dnegfull) = ds.classify_document(negated_sent)

    assert dpos > dneg
    assert dposfull > dpos


def test_score_potts(ds):
    (dpos, dneg) = ds.classify_document(TESTDOC_ADJ)
    assert dpos > 0.0

    # again, for negative text
    (dpos, dneg) = ds.classify_document(TESTDOC_BADADJ)
    assert dneg > 0.0

    # negated text
    (dpos, dneg) = ds.classify_document(TESTDOC_NEGATED)
    assert dpos > 0.0

    # currupt data - should still work
    (dpos, dneg) = ds.classify_document(TESTDOC_CORRUPT)
    assert dpos > dneg


def test_sample_classes(moby):
    for algo in [sentdoc.AV_LightPottsSentiScore(moby),
                 sentdoc.A_LightPottsSentiScore(moby),
                 sentdoc.AV_AggressivePottsSentiScore(moby),
                 sentdoc.A_AggressivePottsSentiScore(moby)]:
        algo.verbose = False
        (p, n) = algo.classify_document(TESTDOC_NEGATED)
        assert n > 0.0
