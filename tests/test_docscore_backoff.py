import pytest

import sentlex.sentanalysis as sentdoc


@pytest.fixture
def ds():
    ds = sentdoc.BasicDocSentiScore()
    ds.verbose = False
    return ds


def test_backoff_noop(ds):
    ds.set_parameters(score_mode=ds.SCOREBACKOFF, backoff_alpha=0.0)
    assert ds.config.backoff_alpha == 0.0

    scores = [1.0, 0.5, 0.0, -1.0]
    for (i, s) in enumerate(scores):
        # test a harmless backoff
        assert s == ds._repeated_backoff(s, i + 1, ds.config.backoff_alpha)


def test_backoff(ds):
    ds.set_parameters(score_mode=ds.SCOREBACKOFF, backoff_alpha=1.0)
    test = [(0.5, 1.0, 0.5), (0.5, 2.0, 0.25), (0.5, 3.0, 0.125)]
    for (score, repeat, result) in test:
        assert result == ds._repeated_backoff(score, repeat, ds.config.backoff_alpha)


def test_backoff_badinput(ds):
    # finally check for bad input
    assert ds._repeated_backoff(1.0, 0.0, 1.0) == 0.0
