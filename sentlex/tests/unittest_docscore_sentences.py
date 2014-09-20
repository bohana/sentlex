try:
    import sentlex.sentanalysis_sent as sentdoc
except Exception:
    import sentanalysis_sent as sentdoc

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
LARGE1='''i/FW had/VBD been/VBN expecting/VBG more/JJR of/IN this/DT movie/NN than/IN the/DT less/JJR than/IN thrilling/NN twister/NN ./. twister/VB was/VBD good/JJ but/CC had/VBD no/DT real/JJ plot/NN and/CC no/DT one/CD to/TO simpithize/VB with/IN ./. but/CC twister/VB had/VBD amazing/JJ effects/NNS and/CC i/FW was/VBD hoping/VBG so/RB would/MD volcano/NN volcano/NN starts/VBZ with/IN tommy/JJ lee/NN jones/NNS at/IN emo/NN ./. he/PRP worrys/VBZ about/IN a/DT small/JJ earthquake/NN enough/RB to/TO leave/VB his/PRP$ daughter/NN at/IN home/NN with/IN a/DT baby/NN sitter/NN ./. there/EX is/VBZ one/CD small/JJ quake/NN then/RB another/DT quake/NN ./. then/RB a/DT geologist/NNpoints/VBZ out/RP to/TO tommy/VB that/IN its/PRP$ takes/VBZ a/DT geologic/JJ event/NN to/TO heat/VB millions/NNS of/IN gallons/NNS of/IN water/NN in/IN 12/CD hours/NNS./. a/DT few/JJ hours/NNS later/RB large/JJ amount/NN of/IN ash/NN start/NN to/TO fall/VB ./. then/RB .../: it/PRP starts/NNS ./. the/DT volcanic/NN eruption/NN .../: i/FW liked/VBD this/DT movie/NN .../: but/CC it/PRP was/VBD not/RB as/RB great/JJ as/IN i/FW hoped/VBD ./. i/FW was/VBD still/RB good/JJ none/NN the/DT less/JJR ./. it/PRP had/VBD excellent/JJ special/JJ effects/NNS ./. the/DT best/JJS view/NN .../: the/DT helecopters/NNS flying/VBG over/IN the/DT streets/NNS of/IN volcanos/NNS ./. also/RB .../: there/EX were/VBD interesting/JJ side/NN stories/NNS that/WDT made/VBD the/DT plot/NN more/RBR interesting/JJ ./. so/RB .../: it/PRP was/VBD good/JJ !/. !/.'''

class T1_scoring_documents(unittest.TestCase):
    def runTest(self):
        # load lexicon
        L=sentlex.MobyLexicon()
        self.assertTrue(L.is_loaded, 'Test lexicon did not load correctly')

        # create a class that scores only adjectives
        ds=sentdoc.SentenceDocSentiScore(L)
        ds.verbose=True
        ds.set_lexicon(L)

        # now score!
        (dpos, dneg) = ds.classify_document(TESTDOC_ADJ, verbose=True)
        self.assertTrue(ds.resultdata and ds.resultdata.has_key('doc') and ds.resultdata.has_key('annotated_doc')\
            and ds.resultdata.has_key('resultpos') and ds.resultdata.has_key('resultneg'), 'Did not populate resultdata after scoring doc')

        print 'TESTDOC_ADJ (pos,neg): %2.2f %2.2f' % (dpos, dneg)
        self.assertTrue(dpos > 0.0, 'Did not find positive words on positive doc')

        # again, for negative text
        (dpos, dneg) = ds.classify_document(TESTDOC_BADADJ, verbose=True)
        print 'TESTDOC_BADADJ (pos,neg): %2.2f %2.2f' % (dpos, dneg)
        self.assertTrue(dneg > 0.0, 'Did not find negative words on negative doc')

        # negated text
        (dpos, dneg) = ds.classify_document(TESTDOC_NEGATED, verbose=True)
        print 'TESTDOC_NEGATED (pos,neg): %2.2f %2.2f' % (dpos, dneg)
        self.assertTrue(dpos > 0.0, 'Did not find positive words on TESTDOC_NEGATED')

        # currupt data - should still work
        (dpos, dneg) = ds.classify_document(TESTDOC_CORRUPT, verbose=True)


class T4_large_docs(unittest.TestCase):
    def runTest(self):
        # load lexicon
        L=sentlex.SWN3Lexicon()
        self.assertTrue(L.is_loaded, 'Test lexicon did not load correctly')
        algo=sentdoc.SentenceDocSentiScore(L)
        for doc in [LARGE1]:
            (p,n) = algo.classify_document(doc, verbose=True)

#
# Runs unit testing if module is called directly
#
if __name__ == "__main__":
    
   # Run those guys
   unittest.main()
