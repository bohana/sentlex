import sentlex.sentanalysis as sentdoc
import sentlex

TESTDOC_ADJ = 'good/JJ hate/VB'


def test_pos_adjustment():
    # load lexicon
    L = sentlex.UICLexicon()
    ds = sentdoc.BasicDocSentiScore()
    ds.verbose = False
    ds.set_lexicon(L)
    ds.set_parameters(a_adjust=1.0, v_adjust=1.0)

    (dpos, dneg) = ds.classify_document(TESTDOC_ADJ)
    # no adjustment
    assert dpos == dneg

    ds.set_parameters(a_adjust=0.0, v_adjust=1.0)
    (dpos, dneg) = ds.classify_document(TESTDOC_ADJ, verbose=False)
    assert dpos < dneg

    ds.set_parameters(a_adjust=1.0, v_adjust=0.0)
    (dpos, dneg) = ds.classify_document(TESTDOC_ADJ, verbose=False)
    assert dpos > dneg
