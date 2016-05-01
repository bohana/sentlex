import sentlex
import sys,os
import unittest

#####
#
# Unit Testing for sentlex
#
####
 
# T0 - test all basic methods
class T0_test_basics(unittest.TestCase):
    def setUp(self):
        self.L1 = sentlex.UICLexicon()
        self.L2 = sentlex.SWN3Lexicon()
        self.L = sentlex.CompositeLexicon()

        self.L.add_lexicon(self.L1)
        self.L.add_lexicon(self.L2)
        self.L.compile_frequency()

    def test_basics(self):
 
        self.assertTrue(len(self.L.LLIST) == 2, 'Did not add lexicons as expecetd')
        self.assertTrue(self.L.is_loaded, 'Not all lexicons loaded')
        self.assertTrue(self.L.is_compiled, 'Not all lexicons compiled')

        self.assertTrue(self.L.get_freq('good') > 0.0, 'Unable to fetch frequency')

        # look for words not in UIC
        for a in ['undeniable', 'unfeasible']:
            self.assertEqual(self.L1.hasadjective('undeniable'), False, 'Word should NOT be in UIC lexicon')
            self.assertEqual(self.L.hasadjective('undeniable'), True, 'Word should be in complsite lexicon')
            self.assertNotEqual(self.L.getadjective('bad'), (0.0,0.0), 'Value should be here')

    def test_factor(self):

        # this should not be affeectd by changing factors as they exist in lexicon #1
        self.assertEqual(self.L.getadjective('bad'), (0.0,1.0), 'Value should be here')
        self.L.set_factor(0.5)
        self.assertEqual(self.L.getadjective('bad'), (0.0,1.0), 'Value should be here')

        # these will be affected
        self.L.set_factor(1.0)
        nval = self.L.getadjective('undeniable')[1]
        self.L.set_factor(0.25)
        self.assertTrue(self.L.getadjective('undeniable')[1] < nval, 'Value should be less after factor %.2f' % self.L.factor)

#
# Runs unit testing if module is called directly
#
if __name__ == "__main__":
    
   # Run those guys
   unittest.main()
