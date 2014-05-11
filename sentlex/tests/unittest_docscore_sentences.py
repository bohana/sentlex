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
LARGE1='''i/FW had/VBD been/VBN expecting/VBG more/JJR of/IN this/DT movie/NN than/IN the/DT less/JJR than/IN thrilling/NN twister/NN ./. twister/VB was/VBD good/JJ but/CC had/VB
D no/DT real/JJ plot/NN and/CC no/DT one/CD to/TO simpithize/VB with/IN ./. but/CC twister/VB had/VBD amazing/JJ effects/NNS and/CC i/FW was/VBD hoping/VBG so/RB would/
MD volcano/NN volcano/NN starts/VBZ with/IN tommy/JJ lee/NN jones/NNS at/IN emo/NN ./. he/PRP worrys/VBZ about/IN a/DT small/JJ earthquake/NN enough/RB to/TO leave/VB h
is/PRP$ daughter/NN at/IN home/NN with/IN a/DT baby/NN sitter/NN ./. there/EX is/VBZ one/CD small/JJ quake/NN then/RB another/DT quake/NN ./. then/RB a/DT geologist/NN
points/VBZ out/RP to/TO tommy/VB that/IN its/PRP$ takes/VBZ a/DT geologic/JJ event/NN to/TO heat/VB millions/NNS of/IN gallons/NNS of/IN water/NN in/IN 12/CD hours/NNS
./. a/DT few/JJ hours/NNS later/RB large/JJ amount/NN of/IN ash/NN start/NN to/TO fall/VB ./. then/RB .../: it/PRP starts/NNS ./. the/DT volcanic/NN eruption/NN .../: i
/FW liked/VBD this/DT movie/NN .../: but/CC it/PRP was/VBD not/RB as/RB great/JJ as/IN i/FW hoped/VBD ./. i/FW was/VBD still/RB good/JJ none/NN the/DT less/JJR ./. it/P
RP had/VBD excellent/JJ special/JJ effects/NNS ./. the/DT best/JJS view/NN .../: the/DT helecopters/NNS flying/VBG over/IN the/DT streets/NNS of/IN volcanos/NNS ./. als
o/RB .../: there/EX were/VBD interesting/JJ side/NN stories/NNS that/WDT made/VBD the/DT plot/NN more/RBR interesting/JJ ./. so/RB .../: it/PRP was/VBD good/JJ !/. !/.'''
LARGE2='''These_DT earbuds_NNS are_VBP not_RB worth_JJ $_$ 1_CD ._.
Yes_RB ,_, they_PRP look_VBP like_IN the_DT I-pod_JJ headphones_NNS but_CC they_PRP sound_VBP horrible_JJ ._.
You_PRP have_VBP to_TO turn_VB the_DT volume_NN up_RP all_PDT the_DT way_NN to_TO even_RB hear_VB the_DT music_NN ,_, and_CC the_DT music_NN sounds_VBZ like_IN it_PRP '
s_VBZ coming_VBG from_IN a_DT tin_NN can_MD ,_, with_IN absolutely_RB no_DT bass_NN and_CC you_PRP can_MD hear_VB a_DT hissing_NN during_IN some_DT of_IN the_DT singing
_NN ._.
Save_NNP your_PRP$ money_NN and_CC go_VB get_VB a_DT pair_NN of_IN JVC_NNP Gumys_NNPS -_: they_PRP 're_VBP $_$ 10_CD and_CC although_IN they_PRP do_VBP n't_RB look_VB l
ike_IN Ipod_NNP earbuds_VBZ the_DT sound_JJ quality_NN and_CC price_NN ca_MD n't_RB be_VB beaten_VBN ._.
'''

class T1_scoring_documents(unittest.TestCase):
    def runTest(self):
        # load lexicon
        L = sentlex.MobyLexicon()
        self.assertTrue(L.is_loaded, 'Test lexicon did not load correctly')

        # create a class that scores only adjectives
        ds = sentdoc.SentenceDocSentiScore(L)
        ds.verbose=True
        ds.set_lexicon(L)

        # now score!
        (dpos, dneg) = ds.classify_document(TESTDOC_ADJ, verbose=True)
        self.assertTrue(ds.resultdata and ds.resultdata.has_key('doc') and ds.resultdata.has_key('annotated_doc')\
            and ds.resultdata.has_key('resultpos') and ds.resultdata.has_key('resultneg'), 'Did not populate resultdata after scoring doc')

        self.assertTrue(dpos > 0.0, 'Did not find positive words on positive doc')
        print 'TESTDOC_ADJ (pos,neg): %2.2f %2.2f' % (dpos, dneg)

        # again, for negative text
        (dpos, dneg) = ds.classify_document(TESTDOC_BADADJ, verbose=True)
        self.assertTrue(dneg > 0.0, 'Did not find negative words on negative doc')
        print 'TESTDOC_BADADJ (pos,neg): %2.2f %2.2f' % (dpos, dneg)

        # negated text
        ds.set_neg_detection(True, 5)
        (dpos, dneg) = ds.classify_document(TESTDOC_NEGATED, verbose=True)
        self.assertTrue(dpos > 0.0, 'Did not find positive words on TESTDOC_NEGATED')
        print 'TESTDOC_NEGATED (pos,neg): %2.2f %2.2f' % (dpos, dneg)

        # currupt data - should still work
        (dpos, dneg) = ds.classify_document(TESTDOC_CORRUPT, verbose=True)
        self.assertTrue(dpos > dneg, 'Did not process corrupt document correctly')


class T4_large_docs(unittest.TestCase):
    def runTest(self):
        # load lexicon
        L=sentlex.SWN3Lexicon()
        self.assertTrue(L.is_loaded, 'Test lexicon did not load correctly')
        algo=sentdoc.SentenceDocSentiScore(L)
        for doc in [LARGE1, LARGE2]:
            (p,n) = algo.classify_document(doc, verbose=True)

#
# Runs unit testing if module is called directly
#
if __name__ == "__main__":
    
   # Run those guys
   unittest.main()
