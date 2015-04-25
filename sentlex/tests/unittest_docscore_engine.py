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

class T1_repeat_backoff(unittest.TestCase):
    def runTest(self):
        ds = sentdoc.BasicDocSentiScore()
        ds.verbose=False

        scores = [1.0, 0.5, 0.0, -1.0]
        ds.set_parameters(score_mode = ds.SCOREBACKOFF, backoff_alpha = 0.0)
        self.assertEqual(ds.backoff_alpha, 0.0)

        for (i, s) in enumerate(scores):
            # test a harmless backoff
            self.assertTrue(s == ds._repeated_backoff(s, i+1, ds.backoff_alpha), 'This backoff should always return original score')

        
        ds.set_parameters(score_mode = ds.SCOREBACKOFF, backoff_alpha = 1.0)
        test = [(0.5, 1.0, 0.5), (0.5, 2.0, 0.25), (0.5, 3.0, 0.125)]
        for (score, repeat, result) in test:
            self.assertTrue(result == ds._repeated_backoff(score, repeat, ds.backoff_alpha))

        # finally check for bad input
        self.assertTrue(ds._repeated_backoff(1.0, 0.0, 1.0) == 0.0)


#
# Runs unit testing if module is called directly
#
if __name__ == "__main__":
    
   # Run those guys
   unittest.main()
