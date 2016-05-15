from __future__ import absolute_import
from __future__ import print_function
try:
    import sentlex.sentanalysis as sentdoc
except Exception:
    import sentanalysis as sentdoc

try:
    import sentlex.sentlex as sentlex
except Exception:
    import sentlex as sentlex

import sys
import os
import unittest

TESTDOC_ADJ = 'good/JJ good/JJ good/JJ good/JJ good/JJ good/JJ good/JJ good/JJ good/JJ good/JJ'
TESTDOC_UNTAGGED = 'this cookie is good. it is very good indeed'
TESTDOC_BADADJ = 'bad_JJ Bad_JJ bAd_JJ'
TESTDOC_NEGATED = 'not/DT bad/JJ ./. not/DT really/RR bad/JJ'
TESTDOC_CORRUPT = 'this_DT doc_NN is_VB not_DT not_DT not_DT in great/JJ shape/JJ good_JJ good_JJ good_JJ'
TESTDOC_EMPTY = ''


class TestParameterSetting(unittest.TestCase):
    def runTest(self):
        # empty list
        ds = sentdoc.BasicDocSentiScore()
        ds.verbose = False

        ds.set_parameters(negation=True)
        ds.set_parameters(negation_window=15)
        ds.set_active_pos(True, False, False, False)

        self.assertEqual((ds.a, ds.v, ds.n, ds.r), (True, False,
                                                    False, False), 'Failed set POS parameters')
        self.assertEqual((ds.negation, ds.negation_window), (True, 15), 'Failed set negation')

        ds.set_parameters(score_mode=ds.SCOREONCE, score_freq=True, negation=False)
        self.assertEqual(ds.score_mode, ds.SCOREONCE, 'Unable to set parameters via kwards')
        self.assertEqual(ds.score_freq, True, 'Unable to set parameters via kwards')
        self.assertEqual(ds.negation, False, 'Unable to set parameters via kwards')


class TestScoring(unittest.TestCase):
    def runTest(self):
        # load lexicon
        L = sentlex.MobyLexicon()
        self.assertTrue(L.is_loaded, 'Test lexicon did not load correctly')

        # create a class that scores only adjectives
        ds = sentdoc.BasicDocSentiScore()
        ds.verbose = False
        ds.set_active_pos(True, False, False, False)
        ds.set_parameters(score_mode=ds.SCOREALL, score_freq=False, negation=False)
        ds.set_lexicon(L)

        # separator ok?
        self.assertEqual(ds._detect_tag(TESTDOC_ADJ), '/', 'Unable to detect correct separator')

        # now score!
        (dpos, dneg) = ds.classify_document(TESTDOC_ADJ)
        self.assertTrue(ds.resultdata and 'doc' in ds.resultdata and 'annotated_doc' in ds.resultdata
                        and 'resultpos' in ds.resultdata and 'resultneg' in ds.resultdata, 'Did not populate resultdata after scoring doc')

        self.assertTrue(dpos > dneg, 'Did not find positive words on positive doc')

        # again, for negative text
        (dpos, dneg) = ds.classify_document(TESTDOC_BADADJ)
        self.assertTrue(dneg > dpos, 'Did not find negative words on negative doc')

        # negated text
        ds.set_parameters(negation=True)
        ds.set_parameters(negation_window=15)
        (dpos, dneg) = ds.classify_document(TESTDOC_NEGATED)
        self.assertTrue(dpos > dneg, 'Did not find positive words on TESTDOC_NEGATED')


class TestScoringUntagged(unittest.TestCase):
    def runTest(self):
        # load lexicon
        L = sentlex.MobyLexicon()
        self.assertTrue(L.is_loaded, 'Test lexicon did not load correctly')

        # create a class that scores only adjectives
        ds = sentdoc.BasicDocSentiScore()
        ds.verbose = False
        ds.set_active_pos(True, True, False, False)
        ds.set_lexicon(L)

        # score untagged doc - this should cause an exception
        self.assertRaises(RuntimeError, ds.classify_document, TESTDOC_UNTAGGED, verbose=False)

        # this should work
        (dpos, dneg) = ds.classify_document(TESTDOC_UNTAGGED, verbose=False, tagged=False)
        self.assertTrue(dpos > 0, 'Did not score "good" in untagged doc')

        # score again, now changing all tags to false
        (dpos, dneg) = ds.classify_document(TESTDOC_UNTAGGED,
                                            verbose=False, tagged=False, a=False, v=False, n=False, r=False)
        self.assertTrue(dpos == 0 and dneg == 0, 'Scprng with no active tags should not happen')


class TestScoringFunctions(unittest.TestCase):
    def runTest(self):
        # load lexicon
        L = sentlex.MobyLexicon()
        self.assertTrue(L.is_loaded, 'Test lexicon did not load correctly')

        ds = sentdoc.BasicDocSentiScore()
        ds.verbose = False
        ds.set_active_pos(True, True, False, False)
        ds.set_lexicon(L)
        ds.set_parameters(score_function='linear')
        (dpos, dneg) = ds.classify_document(TESTDOC_ADJ, verbose=False)


class TestSampleClasses(unittest.TestCase):
    def runTest(self):
        # load lexicon
        L = sentlex.MobyLexicon()
        self.assertTrue(L.is_loaded, 'Test lexicon did not load correctly')
        for algo in [sentdoc.AV_AllWordsDocSentiScore(L),
                     sentdoc.A_AllWordsDocSentiScore(L),
                     sentdoc.A_OnceWordsDocSentiScore(L),
                     sentdoc.AV_OnceWordsDocSentiScore(L),
                     sentdoc.AV_Lin_AllWordsDocSentiScore(L),
                     sentdoc.A_Lin_AllWordsDocSentiScore(L)
                     ]:
            algo.verbose = True
            (p, n) = algo.classify_document(TESTDOC_ADJ, verbose=True)
            print(p, n)
            self.assertTrue(p > n, 'Sample document not scored correctly in %s' %
                            str(algo.__class__))
