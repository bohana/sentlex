try:
    import sentlex.sentanalysis as sentdoc
except Exception:
    import sentanalysis as sentdoc

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
TESTDOC_ADJ = 'good/JJ hate/VB' 


class T0_scoring_functions(unittest.TestCase):
    def runTest(self):
        # load lexicon
        L = sentlex.UICLexicon()
        self.assertTrue(L.is_loaded, 'Test lexicon did not load correctly')

        ds = sentdoc.BasicDocSentiScore()
        ds.verbose=False
        ds.set_active_pos(True, True, False, False)
        ds.set_lexicon(L)
        ds.set_parameters(a_adjust=1.0, v_adjust=1.0)
        (dpos, dneg) = ds.classify_document(TESTDOC_ADJ, verbose=False)
        self.assertTrue(dpos == dneg, 'No POS adjustment should have occurred')

        ds.set_parameters(a_adjust=0.0, v_adjust=1.0)
        (dpos, dneg) = ds.classify_document(TESTDOC_ADJ, verbose=False)
        self.assertTrue(dpos < dneg, 'Neg score expected after adjustment')

        ds.set_parameters(a_adjust=1.0, v_adjust=0.0)
        (dpos, dneg) = ds.classify_document(TESTDOC_ADJ, verbose=False)
        self.assertTrue(dpos > dneg, 'Pos score expected after adjustment')

#
# Runs unit testing if module is called directly
#
if __name__ == "__main__":
    
   # Run those guys
   unittest.main()
