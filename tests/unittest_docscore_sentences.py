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
TESTDOC_QUESTIONED = 'not/DT bad/JJ movie/NN ?/. blah/NN blah/NN good/JJ good/JJ ?/.'
TESTDOC_CORRUPT = 'this_DT doc_NN is_VB not_DT not_DT not_DT in great/JJ shape/JJ good_JJ good_JJ good_JJ'
TESTDOC_EMPTY = ''
LARGE1='''i/FW had/VBD been/VBN expecting/VBG more/JJR of/IN this/DT movie/NN than/IN the/DT less/JJR than/IN thrilling/NN twister/NN ./. twister/VB was/VBD good/JJ but/CC had/VBD no/DT real/JJ plot/NN and/CC no/DT one/CD to/TO simpithize/VB with/IN ./. but/CC twister/VB had/VBD amazing/JJ effects/NNS and/CC i/FW was/VBD hoping/VBG so/RB would/MD volcano/NN volcano/NN starts/VBZ with/IN tommy/JJ lee/NN jones/NNS at/IN emo/NN ./. he/PRP worrys/VBZ about/IN a/DT small/JJ earthquake/NN enough/RB to/TO leave/VB his/PRP$ daughter/NN at/IN home/NN with/IN a/DT baby/NN sitter/NN ./. there/EX is/VBZ one/CD small/JJ quake/NN then/RB another/DT quake/NN ./. then/RB a/DT geologist/NNpoints/VBZ out/RP to/TO tommy/VB that/IN its/PRP$ takes/VBZ a/DT geologic/JJ event/NN to/TO heat/VB millions/NNS of/IN gallons/NNS of/IN water/NN in/IN 12/CD hours/NNS./. a/DT few/JJ hours/NNS later/RB large/JJ amount/NN of/IN ash/NN start/NN to/TO fall/VB ./. then/RB .../: it/PRP starts/NNS ./. the/DT volcanic/NN eruption/NN .../: i/FW liked/VBD this/DT movie/NN .../: but/CC it/PRP was/VBD not/RB as/RB great/JJ as/IN i/FW hoped/VBD ./. i/FW was/VBD still/RB good/JJ none/NN the/DT less/JJR ./. it/PRP had/VBD excellent/JJ special/JJ effects/NNS ./. the/DT best/JJS view/NN .../: the/DT helecopters/NNS flying/VBG over/IN the/DT streets/NNS of/IN volcanos/NNS ./. also/RB .../: there/EX were/VBD interesting/JJ side/NN stories/NNS that/WDT made/VBD the/DT plot/NN more/RBR interesting/JJ ./. so/RB .../: it/PRP was/VBD good/JJ !/. !/.'''
LARGE2='''
at/IN one/CD point/NN during/IN brian/NN de/IN palma/NN 's/POS crime/NN epic/NN scarface/NN ,/, the/DT radiant/JJ michelle/NN pfeiffer/NN turns/VBZ to/TO a/DT ranting/NN al/IN pacino/NN and/CC pops/VBZ a/DT question/NN that/IN the/DT audience/NN has/VBZ no/DT doubt/NN been/VBN wanting/VBG to/TO ask/VB for/IN themselves/PRP :/: ''/'' ca/MD n't/RB you/PRP stop/VB saying/VBG `/`` fuck/VB '/'' all/DT the/DT time/NN ?/. ''/'' fucking/VBG good/JJ question/NN ,/, that/IN ./. it/PRP may/MD not/RB be/VB an/DT honor/NN that/WDT instills/VBZ the/DT filmmakers/NNS with/IN pride/NN ,/, but/CC as/RB far/RB as/IN i/FW can/MD tell/VB oliver/JJR stone/NN 's/POS script/NN contains/VBZ the/DT said/VBD expletitive/JJ more/JJR times/NNS than/IN any/DT other/JJ film/NN in/IN cinema/NN history/NN ./. yet/RB it/PRP would/MD be/VB a/DT shame/NN if/IN bad/JJ language/NN is/VBZ all/DT de/IN palma/NN 's/POS scarface/NN is/VBZ remembered/VBN for/IN ,/, because/IN this/DT is/VBZ a/DT damn/NN fine/NN gangstar/NN flick/NN ./. the/DT overall/JJ structure/NN is/VBZ similar/JJ to/TO howard/VB hawks/NNS '/POS 1932/CD original/JJ ,/, but/CC this/DT time/NN the/DT scene/NN has/VBZ switched/VBN to/TO miami/VB ,/, florida/NN and/CC our/PRP$ anti-hero/NN 's/POS chosen/JJ vice/NN is/VBZ cocaine/NN traffiking/VBG ./. pacino/NN ,/, sporting/VBG a/DT thick/JJ cuban/NN accent/NN ,/, gives/VBZ one/CD the/DT best/JJS performances/NNS of/IN his/PRP$ career/NN -LRB-/-LRB- golden/JJ globe/NN nominated/VBN -RRB-/-RRB- as/IN tony/JJ montana/NN ,/, a/DT cuban/NN refugee/NN with/IN a/DT criminal/JJ past/NN who/WP flees/VBZ castro/NN and/CC comes/VBZ to/TO america/VB to/TO live/VB the/DT american/NN dream/NN ./. and/CC live/VB it/PRP out/RP he/PRP does/VBZ ,/, with/IN lashings/NNS of/IN violence/NN ,/, abuse/NN ,/, murder/NN and/CC the/DT funny/JJ white/JJ powder/NN ./. from/IN his/PRP$ earliest/JJS jobs/NNS as/IN a/DT drug/NN runner/NN for/IN various/JJ middlemen/NNS ,/, tony/JJ montana/NN makes/VBZ it/PRP clear/JJ to/TO everyone/NN he/PRP meets/VBZ that/IN he/PRP 's/VBZ not/RB a/DT man/NN to/TO be/VB fucked/VBN -LRB-/-LRB- sorry/JJ -RRB-/-RRB- ./. soon/RB he/PRP 's/VBZ the/DT king/NN of/IN the/DT cocaine/NN heap/NN ,/, but/CC his/PRP$ hot/JJ head/NN and/CC an/DT increasingly/RB out/IN of/IN control/NN drug/NN addiction/NN prove/VB his/PRP$ undoing/NN ./. ''/'' never/RB do/VBP your/PRP$ own/JJ stash/NN ''/'' ,/, warns/VBZ one/CD character/NN early/RB in/IN the/DT film/NN ./. as/IN sure/JJ as/IN night/NN follows/VBZ day/NN ,/, the/DT emperor/NN of/IN miami/NN eventually/RB falls/VBZ ./. writer/NN oliver/NN stone/NN and/CC director/NN brian/NN de/IN palma/NN make/VBP an/DT explosive/JJ combination/NN here/RB ./. stone/NN 's/POS script/NN offers/VBZ solid/JJ storytelling/NN and/CC some/DT fine/JJ character/NN development/NN ./. montana/NN is/VBZ fascinating/JJ ;/: uneducated/JJ but/CC calculating/VBG ,/, a/DT straight/JJ shooter/NN who/WP speaks/VBZ from/IN the/DT heart/NN ;/: an/DT ambitious/JJ ,/, violent/JJ man/NN yet/RB one/CD with/IN a/DT conscience/NN ./. a/DT man/NN fiercely/RB protective/JJ of/IN his/PRP$ beautiful/JJ 20/CD year/NN old/JJ sister/NN ,/, not/RB wanting/VBG her/PRP to/TO be/VB sucked/VBN into/IN the/DT glitzy/NN ,/, dangerous/JJ world/NN which/WDT he/PRP inhabits/VBZ ./. pacino/NN is/VBZ dynamite/JJ ,/, taking/VBG to/TO the/DT role/NN with/IN a/DT brooding/NN ,/, bristling/VBG energy/NN which/WDT in/IN his/PRP$ more/JJR recent/JJ films/NNS has/VBZ often/RB degenerated/VBN into/IN just/RB simple/JJ overracting/VBG ./. pfeiffer/NN also/RB registers/VBZ strongly/RB as/IN the/DT gangstar/NN mole/NN with/IN no/DT inner/JJ life/NN ./. only/RB once/RB does/VBZ tony/JJ express/VB real/JJ affection/NN for/IN her/PRP and/CC his/PRP$ desire/NN to/TO have/VB children/NNS ,/, and/CC even/RB then/RB you/PRP sense/VBP all/DT he/PRP really/RB wants/VBZ is/VBZ a/DT regular/JJ screw/NN and/CC a/DT beautiful/JJ object/NN to/TO show/VB off/RP to/TO his/PRP$ friends/NNS ,/, and/CC she/PRP 's/VBZ happy/JJ to/TO oblige/VB ./. this/DT is/VBZ n't/RB as/IN meaty/NN a/DT role/NN for/IN pfieffer/NN as/IN sharon/NN stone/NN 's/POS was/VBD in/IN casino/NN ,/, but/CC its/PRP$ an/DT effective/JJ one/CD nonetheless/RB and/CC she/PRP aquits/VBZ herself/PRP well/RB ./. as/IN director/NN ,/, de/IN palma/NN sets/VBZ up/RP a/DT number/NN of/IN dramatic/JJ scenes/NNS with/IN his/PRP$ typical/JJ stylistic/JJ brauva/NN ./. the/DT escalating/VBG tension/NN he/PRP creates/VBZ in/IN various/JJ mob/NN situations/NNS -/: a/DT drug/NN deal/NN gone/VBN wrong/JJ ,/, an/DT assination/NN attempt/NN -/: is/VBZ often/RB thrilling/VBG ,/, and/CC in/IN this/DT respect/NN he/PRP is/VBZ every/DT bit/NN the/DT equal/JJ of/IN scorese/NN and/CC coppola/NN ./. where/WRB he/PRP differs/VBZ from/IN ,/, say/VB ,/, coppola/NN 's/POS godfather/NN trilogy/NN is/VBZ in/IN his/PRP$ overall/NN treatment/NN ./. coppola/NN gives/VBZ his/PRP$ crime/NN sagas/VBZ an/DT operatic/JJ sweep/NN ,/, whereas/IN in/IN scarface/NN de/IN palma/NN opts/NNS for/IN a/DT grittier/JJR feel/NN ./. and/CC it/PRP perfectly/RB suits/VBZ the/DT material/NN ./. the/DT only/RB major/JJ botch/NN is/VBZ giorgio/JJ moroder/NN 's/POS mostly/RB crap/NN synthesier/JJR score/NN ./. it/PRP 's/VBZ just/RB not/RB right/JJ ,/, and/CC unfortunately/RB compromises/VBZ the/DT impact/NN of/IN some/DT otherwise/RB good/JJ scenes/NNS ./. as/IN expected/VBN ,/, scarface/VBP is/VBZ very/RB violent/JJ at/IN times/NNS ,/, but/CC you/PRP should/MD n't/RB be/VB watching/VBG gangster/NN movies/NNS if/IN that/DT upsets/NNS you/PRP ./. at/IN over/IN two/CD and/CC a/DT half/NN hours/NNS in/IN length/NN it/PRP 's/VBZ a/DT true/JJ epic/NN ,/, and/CC if/IN you/PRP 're/VBP a/DT fan/NN of/IN the/DT genre/NN you/PRP 'll/MD love/VB f/SYM \\*/SYM \\*/SYM k-filled/JJ minute/NN of/IN it/PRP ./.
'''


class T1_scoring_documents(unittest.TestCase):
    def runTest(self):
        # load lexicon
        L=sentlex.MobyLexicon()
        self.assertTrue(L.is_loaded, 'Test lexicon did not load correctly')

        # create a class that scores only adjectives
        ds=sentdoc.SentenceDocSentiScore(L)
        ds.verbose=False
        ds.set_lexicon(L)

        # now score!
        (dpos, dneg) = ds.classify_document(TESTDOC_ADJ, verbose=False)
        self.assertTrue(ds.resultdata and ds.resultdata.has_key('doc') and ds.resultdata.has_key('annotated_doc')\
            and ds.resultdata.has_key('resultpos') and ds.resultdata.has_key('resultneg'), 'Did not populate resultdata after scoring doc')

        self.assertTrue(dpos > 0.0, 'Did not find positive words on positive doc')

        # again, for negative text
        (dpos, dneg) = ds.classify_document(TESTDOC_BADADJ, verbose=False)
        self.assertTrue(dneg > 0.0, 'Did not find negative words on negative doc')

        # negated text
        (dpos, dneg) = ds.classify_document(TESTDOC_NEGATED, verbose=False)
        self.assertTrue(dpos > 0.0, 'Did not find positive words on TESTDOC_NEGATED')

        # currupt data - should still work
        (dpos, dneg) = ds.classify_document(TESTDOC_CORRUPT, verbose=False)


class T4_large_docs(unittest.TestCase):
    def runTest(self):
        # load lexicon
        L=sentlex.SWN3Lexicon()
        self.assertTrue(L.is_loaded, 'Test lexicon did not load correctly')
        algo=sentdoc.SentenceDocSentiScore(L)
        for doc in [LARGE1, LARGE2]:
            (p,n) = algo.classify_document(doc, verbose=True)


class T3_questioned_docs(unittest.TestCase):
    def runTest(self):
        L=sentlex.SWN3Lexicon()
        self.assertTrue(L.is_loaded, 'Test lexicon did not load correctly')
        algo=sentdoc.SentenceDocSentiScore(L)
        algo.set_parameters(question_minsize=1.0, question_neg_weight=1000.0)

        DUMMYQ = ['not/DT', 'bad/JJ', 'movie/NN', '?/.']
        self.assertTrue(algo._is_question(DUMMYQ))

        (p, n) = algo.classify_document(TESTDOC_QUESTIONED, verbose=False)
        self.assertTrue(n > p, 'Did not pick up negation weight')
       
        # with a very large threshold this should not come into affect
        algo.set_parameters(question_minsize=1000)
        (p, n) = algo.classify_document(TESTDOC_QUESTIONED, verbose=False)
        self.assertTrue(p > n, 'Negation weight was not ignored')



#
# Runs unit testing if module is called directly
#
if __name__ == "__main__":
   # Run those guys
   unittest.main()
