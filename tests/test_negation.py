import pytest

import sentlex.negdetect as neg


STR_NONEGATION = 'this/DT example/DT contains/DT only/DT positive/DT remarks/DT !/DT'
STR_UNTAGGED = 'this example does not contain any tags. algorithm will assume one.'
STR_NEGATION = 'this/DT example/DT does/DT not/DT cause/DT the/DT algorithm/DT to/DT detect/DT something/DT positive/DT ./DT'
STR_DOUBLE = 'this/DT example/DT does/DT not/DT mean/DT there/DT are/DT no/DT negations/DT ./DT'
STR_PSEUDO = 'not/DT only/DT this/DT example/DT contains/DT a/DT double/DT ./DT it/DT is/DT no/DT wonder/DT language/DT is/DT a/DT problem/DT ./DT'
STR_WINDOW = 'with/DT no/DT certainty/DT this/DT will/DT negate/DT as/DT far/DT as/DT the/DT window/DT allows/DT'
STR_OTHERTAG = 'in_DT this_DT example_DT nothing_DT means_DT the_DT algorithm_DT still_DT works_DT'


def test_edge_cases():
    # empty list
    assert neg.getNegationArray([], 4) == []

    # untagged - processes as normal
    assert neg.getNegationArray(STR_UNTAGGED.split(), 4)


@pytest.mark.parametrize('sentence', [STR_NEGATION, STR_DOUBLE])
def test_negation_detection(sentence):
    assert sum(neg.getNegationArray(sentence.split(), 4)) > 0


@pytest.mark.parametrize('sentence', [STR_NONEGATION, STR_PSEUDO])
def test_negation_detection_notfound(sentence):
    assert sum(neg.getNegationArray(sentence.split(), 4)) == 0


def test_window():
    # loop increasing window sizes
    negatedsums = []
    for i in range(1, 6):
        A = neg.getNegationArray(STR_WINDOW.split(), i, False)
        negatedsums.append(sum(A))

    for i in range(4):
        assert negatedsums[i] < negatedsums[i + 1]
