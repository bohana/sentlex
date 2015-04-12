import sentlex
import sys,os
import unittest

#####
#
# Unit Testing for sentlex
#
####
 
# T0 - test all basic methods
class T0_generic(unittest.TestCase):
    def runTest(self):
        L = sentlex.MobyLexicon()
        L.set_name('UnitTest')

        self.assertEqual(L.get_name(), 'UnitTest', 'Could not retrieve name for this Lex')
        self.assertEqual(L.hasadjective('good'), True, 'Wheres the word good??')
        self.assertEqual(L.hasadjective('bad'), True, 'Wheres the word bad??')
        self.assertEqual(L.hasadjective('evil'), True, 'Wheres the word evil??')
        self.assertEqual(L.hasadjective('excellent'), True, 'Wheres the word excellent??')
        self.assertEqual(L.hasadjective('notaword'), False, 'Found non existant word. Weird...')
        # good and bad are seeds to Moby
        self.assertEqual(L.getadjective('good'), (1.0,0.0), 'Value for term good <> 1')
        self.assertEqual(L.getadjective('bad'), (0.0,1.0), 'Value for term <> 0')

        # get_info
        self.assertTrue(L.get_info()['a']['size'] > 0, 'get_info failed for a.')
        self.assertTrue(L.get_info()['n']['size'] > 0, 'get_info failed for n.')
        self.assertTrue(L.get_info()['v']['size'] > 0, 'get_info failed for v.')
        self.assertTrue(L.get_info()['r']['size'] > 0, 'get_info failed for r.')

class T2_freqdist(unittest.TestCase):
    def runTest(self):
        L = sentlex.MobyLexicon()
        L.compile_frequency()

        self.assertTrue(L.is_loaded, 'Lexicon did not load')
        self.assertTrue(L.is_compiled, 'Lexicon did not compile')
        self.assertTrue(L.get_freq('good') > 0, 'Frq dist looks broken')
        self.assertTrue(L.get_freq('notawordnowayjosay') == 0.0, 'Freq found a non existent word')

class T21_freqdist(unittest.TestCase):
    def runTest(self):
        L = sentlex.SWN3Lexicon()
        L.compile_frequency()

        baseline = [ ('bad', 0.0005451764705882353),
                     ('good', 0.002610137254901961),
                     ('the', 0.029449176470588236),
                     ('want', 0.0027591764705882354)]

        for (w,f) in baseline:
            self.assertTrue(L.get_freq(w) == f, 'Incorrect freq found for %s (%.8f <> %.8f)' % (w, f, L.get_freq(w)))

# T3. Multiple lexicons
class T3_multiplelexicons(unittest.TestCase):
    def runTest(self):
        L1 = sentlex.MobyLexicon()
        L2 = sentlex.MobyLexicon()
        L3 = sentlex.MobyLexicon()
        L4 = sentlex.MobyLexicon()
        L1.set_name('UnitTest1')
        L2.set_name('UnitTest2')
        L3.set_name('UnitTest3')
        L4.set_name('UnitTest4')

        self.assertEqual(L4.get_name(), 'UnitTest4', 'Something weird with lexicon instantiation.')
        self.assertEqual(L3.get_name(), 'UnitTest3', 'Something weird with lexicon instantiation.')
        self.assertEqual(L2.get_name(), 'UnitTest2', 'Something weird with lexicon instantiation.')
        self.assertEqual(L1.get_name(), 'UnitTest1', 'Something weird with lexicon instantiation.')

#
# Runs unit testing if module is called directly
#
if __name__ == "__main__":
    
   # Run those guys
   unittest.main()
