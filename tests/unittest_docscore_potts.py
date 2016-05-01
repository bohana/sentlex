try:
    import sentlex.sentanalysis_potts as sentdoc
except Exception:
    import sentanalysis_potts as sentdoc

try:
    import sentlex.sentlex as sentlex
except Exception:
    import sentlex as sentlex

import sys,os
import unittest

#####
#
# Unit Testing for doc sentiment analysis
#
####

#
# Data
#
TESTDOC_ADJ = 'good/JJ good/JJ good/JJ good/JJ good/JJ good/JJ good/JJ good/JJ good/JJ good/JJ' 
TESTDOC_UNTAGGED = 'this cookie is good. it is very good indeed'
TESTDOC_BADADJ = 'bad_JJ Bad_JJ bAd_JJ'
TESTDOC_NEGATED = 'not/DT bad/JJ movie/NN ./. blah/NN blah/NN not/DT really/RR good/JJ either/DT ./.'
TESTDOC_CORRUPT = 'this_DT doc_NN is_VB not_DT not_DT not_DT in great/JJ shape/JJ good_JJ good_JJ good_JJ'
TESTDOC_EMPTY = ''

# T0 - Basic Class functionality
class T0_parameter_setting(unittest.TestCase):
    def runTest(self):
        # empty list
        ds = sentdoc.PottsDocSentiScore()
        ds.verbose=False

        ds.set_active_pos(True, False, False, False)
        ds.set_parameters(negation_adjustment = 0.5, negation=True, negation_window=15)

        self.assertEqual((ds.a, ds.v, ds.n, ds.r), (True, False, False, False), 'Failed set POS parameters')
        self.assertEqual((ds.negation, ds.negation_window), (True, 15), 'Failed set negation')

        ds.set_parameters(score_mode=ds.SCOREONCE, score_freq=True)
        self.assertEqual(ds.score_mode, ds.SCOREONCE, 'Unable to set parameters via kwards')
        self.assertEqual(ds.score_freq, True, 'Unable to set parameters via kwards')

class T_atenuation_setting(unittest.TestCase):
    def runTest(self):
        # empty list
        ds = sentdoc.PottsDocSentiScore()
        L = sentlex.MobyLexicon()
        ds.verbose=True
        ds.set_lexicon(L)

        negated_sent = 'not/DT good/JJ'  

        ds.set_active_pos(True, False, False, False)
        ds.set_parameters(negation=True, negation_window=15)
        (dpos, dneg) = ds.classify_document(negated_sent)
        self.assertTrue(dneg > dpos, 'Negation did not invert scores.')

        ds.set_parameters(negation=True, negation_window=15, atenuation=True, at_pos=0.5, at_neg=0.5)
        (dpos, dneg) = ds.classify_document(negated_sent)
        ds.set_parameters(negation=True, negation_window=15, atenuation=True, at_pos=1.0, at_neg=1.0)
        (dposfull, dnegfull) = ds.classify_document(negated_sent)
        self.assertTrue(dpos > dneg, 'Negation did not atenuate scores.')
        self.assertTrue(dposfull > dpos, 'Negation did not atenuate scores.')


class T1_scoring_documents(unittest.TestCase):
    def runTest(self):
        # load lexicon
        L = sentlex.MobyLexicon()
        self.assertTrue(L.is_loaded, 'Test lexicon did not load correctly')

        # create a class that scores only adjectives
        ds = sentdoc.PottsDocSentiScore()
        ds.verbose=False
        ds.set_active_pos(True, False, False, False)
        ds.set_parameters(score_mode=ds.SCOREALL, score_freq=False, negation=True, negation_adjustment=0.5)
        ds.set_lexicon(L)

        # separator ok?
        self.assertEqual(ds._detect_tag(TESTDOC_ADJ), '/', 'Unable to detect correct separator')

        # now score!
        (dpos, dneg) = ds.classify_document(TESTDOC_ADJ)
        self.assertTrue(ds.resultdata and ds.resultdata.has_key('doc') and ds.resultdata.has_key('annotated_doc')\
            and ds.resultdata.has_key('resultpos') and ds.resultdata.has_key('resultneg'), 'Did not populate resultdata after scoring doc')

        self.assertTrue(dpos > 0.0, 'Did not find positive words on positive doc')

        # again, for negative text
        (dpos, dneg) = ds.classify_document(TESTDOC_BADADJ)
        self.assertTrue(dneg > 0.0, 'Did not find negative words on negative doc')

        # negated text
        (dpos, dneg) = ds.classify_document(TESTDOC_NEGATED)
        self.assertTrue(dpos > 0.0, 'Did not find positive words on TESTDOC_NEGATED')

        # currupt data - should still work
        (dpos, dneg) = ds.classify_document(TESTDOC_CORRUPT)
        self.assertTrue(dpos > dneg, 'Did not process corrupt document correctly')


class T4_sample_classes(unittest.TestCase):
    def runTest(self):
        # load lexicon
        L = sentlex.MobyLexicon()
        self.assertTrue(L.is_loaded, 'Test lexicon did not load correctly')
        for algo in [ sentdoc.AV_LightPottsSentiScore(L), 
                      sentdoc.A_LightPottsSentiScore(L),
                      sentdoc.AV_AggressivePottsSentiScore(L),
                      sentdoc.A_AggressivePottsSentiScore(L)
                    ]:
            algo.verbose=False
            (p,n) = algo.classify_document(TESTDOC_NEGATED)
            self.assertTrue(n>0.0, 'Sample document not scored correctly in %s' % str(algo.__class__))

#
# Runs unit testing if module is called directly
#
if __name__ == "__main__":
    
   # Run those guys
   unittest.main()
