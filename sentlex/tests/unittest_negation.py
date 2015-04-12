try:
  import sentlex.negdetect as neg
except Exception:
  import negdetect as neg

import sys,os
import unittest

#####
#
# Unit Testing for negation detection
#
####
 
# data for tests - ignore POS tags
STR_NONEGATION = 'this/DT example/DT contains/DT only/DT positive/DT remarks/DT !/DT'
STR_UNTAGGED = 'this example does not contain any tags. algorithm will assume one.'
STR_NEGATION = 'this/DT example/DT does/DT not/DT cause/DT the/DT algorithm/DT to/DT detect/DT something/DT positive/DT ./DT'
STR_DOUBLE = 'this/DT example/DT does/DT not/DT mean/DT there/DT are/DT no/DT negations/DT ./DT'
STR_PSEUDO = 'not/DT only/DT this/DT example/DT contains/DT a/DT double/DT ./DT it/DT is/DT no/DT wonder/DT language/DT is/DT a/DT problem/DT ./DT'
STR_WINDOW = 'with/DT no/DT certainty/DT this/DT will/DT negate/DT as/DT far/DT as/DT the/DT window/DT allows/DT'
STR_OTHERTAG = 'in_DT this_DT example_DT nothing_DT means_DT the_DT algorithm_DT still_DT works_DT'

# T0 - Edge cases
class T0_edgecases(unittest.TestCase):
    def runTest(self):
        # empty list
        self.assertEqual(neg.getNegationArray([], 4, True), [], 'Failed to deal with empty list')
  
        # untagged - processes as normal
        self.assertTrue(neg.getNegationArray(STR_UNTAGGED.split(), 4, True), 'Unable to process untagged doc')

        # string should raise an error
        self.assertRaises(AssertionError, neg.getNegationArray, STR_UNTAGGED, 4, True)  

# T1 - Negation algorithm
class T1_negationalgo(unittest.TestCase):
    def runTest(self):
        # no negation
        A = neg.getNegationArray(STR_NONEGATION.split(), 4, True)
        self.assertEqual(sum(A), 0, 'No negation string failed')

        # simple negation
        A = neg.getNegationArray(STR_NEGATION.split(), 4, True)
        self.assertTrue(sum(A)>0, 'Negation algo failed on STR_NEGATION')

        # double negation
        A = neg.getNegationArray(STR_DOUBLE.split(), 4, True)
        self.assertTrue(sum(A)>0, 'Negation algo failed on STR_DOUBLE')

        # pseudo
        A = neg.getNegationArray(STR_PSEUDO.split(), 4, True)
        self.assertTrue(sum(A)==0, 'Negation algo failed on STR_PSEUDO')
        
        # other tag
        A = neg.getNegationArray(STR_OTHERTAG.split(), 4, True)
        self.assertTrue(sum(A)>0, 'Negation algo failed on STR_OTHERTAG')
        
# T2 - window
class T2_negationwindow(unittest.TestCase):
    def runTest(self):
        # loop increasing window sizes
        negatedsums = []
        for i in range(1,6):
            A = neg.getNegationArray(STR_WINDOW.split(), i, False)
            negatedsums.append(sum(A))
        for i in range(4):
            self.assertTrue(negatedsums[i] < negatedsums[i+1], 'Something wrong with window size %d'%i)

#
# Runs unit testing if module is called directly
#
if __name__ == "__main__":
    
   # Run those guys
   unittest.main()
