try:
    import sentlex.sentanalysis_inst as sentdoc
    import sentlex.sentanalysis as sentanalysis
    import sentlex.sentlex as sentlex
except Exception:
    import sentanalysis_inst as sentdoc
    import sentanalysis
    import sentlex

import sys,os
import unittest

#####
#
# Unit Testing for doc sentiment analysis
#
####

TESTDOC_ADJ = 'good/JJ good/JJ good/JJ good/JJ good/JJ good/JJ good/JJ good/JJ good/JJ good/JJ' 

class T_instance_based_classifier(unittest.TestCase):

    def _build_classifier(self):
        ds = sentdoc.InstSentiScore(k=3, metric='found_ratio')
        L = sentlex.SWN3Lexicon()
        c1 = sentanalysis.AV_AllWordsDocSentiScore(L)
        c2 = sentanalysis.A_AllWordsDocSentiScore(L)
        ds.add_classifier('C1', c1)
        ds.add_classifier('C2', c2)
        return ds
        
    def test_basic(self):
        ds = self._build_classifier()
        good_classifier = [(i, 1) for i in xrange(100)]
        bad_classifier = [(i, 0) for i in xrange(100)]
        ds.add_training_data('C1', good_classifier)
        ds.add_training_data('C2', bad_classifier)

        for i in xrange(10):
            (dpos, dneg) = ds.classify_document(TESTDOC_ADJ + ' good/JJ '*i, verbose=False)
            self.assertTrue(dpos > dneg, 'Did not find positive words on positive doc')
        self.assertTrue(ds.cl_counter['C1'] > 1 and ds.cl_counter['C2'] == 0, 'Did not pick correct classifier')
    
    def test_basic_reversed(self):
        ds = self._build_classifier()
        good_classifier = [(i, 1) for i in xrange(100)]
        bad_classifier = [(i, 0) for i in xrange(100)]
        ds.add_training_data('C2', good_classifier)
        ds.add_training_data('C1', bad_classifier)

        for i in xrange(10):
            (dpos, dneg) = ds.classify_document(TESTDOC_ADJ + ' good/JJ '*i, verbose=False)
            self.assertTrue(dpos > dneg, 'Did not find positive words on positive doc')
        self.assertTrue(ds.cl_counter['C2'] > 1 and ds.cl_counter['C1'] == 0, 'Did not pick correct classifier')
        
if __name__ == "__main__":
   # Run those guys
   unittest.main()
