'''

   Lexicon-Based Sentiment Analysis Library

   sentanalysis_potts.py - implements score adjustment based on negated terms
   derived from the work of [Potts, 2011]

'''

# library imports
import sentlex
import negdetect
import stopwords
from docscoreutil import *
from sentanalysis import BasicDocSentiScore

class PottsDocSentiScore(BasicDocSentiScore):
    '''
     Subclass of BasicDocSentiScore implementing score adjustment based on negated terms.
     The key assumption is negated terms are correlated with negative sentiment.

     This class *required* negation detection to be active.
    '''

    def __init__(self):
        # calls superclass
        super(PottsDocSentiScore, self).__init__()
        self.negated_term_adj = 0.1

    def _doc_score_adjust(self, posval, negval):
        '''
         Implements negated term additions based on adjustment weight
        '''
        (postmp, negtmp) = super(PottsDocSentiScore,self)._doc_score_adjust(posval, negval)
        if self.negation:
            # at this point we should have vNEG populated by the scoring algorithm
            if len(self.vNEG)>=3:
                negated_instances = len([self.vNEG[i:i+2] for i in range(len(self.vNEG)-1) if self.vNEG[i:i+2]==[0,1]])
            else:
                negated_instances = 0
            # with the total of negated instances we can compute the adjustment
            # each negating term counts "negated_term_adj" in scoring weight
            negtmp = negtmp + (self.negated_term_adj*negated_instances)
            self._debug('[PottsDocSentiScore] - Instances Found: %d. Negative score now adjusted from %2.2f to %2.2f'%(negated_instances, negval, negtmp))
        return (postmp, negtmp)

    def set_parameters(self, **kwargs):
        '''
          In this section we simply add logic for self.negated_term_adj and call super for everything else
        '''
        super(PottsDocSentiScore, self).set_parameters(**kwargs)
        if 'negation_adjustment' in kwargs.keys():
            self.negated_term_adj = kwargs['negation_adjustment']
        

#
# Pre-defined algorithms based on PottsDocSentiScore
#
class AV_LightPottsSentiScore(PottsDocSentiScore):
    '''
     Pre-configured PottsDocSentiScore to score all words, A,V POS tags
    '''
    def __init__(self, Lex):
        super(AV_LightPottsSentiScore, self).__init__()
        self.set_parameters(L=Lex, a=True, v=True, n=False, r=False, 
                            negation=True, negation_window=5, negation_adjustment=0.1,
                            score_mode=self.SCOREALL, score_stop=True, score_freq=True)


class A_LightPottsSentiScore(BasicDocSentiScore):
    '''
     Pre-configured BasicDocSentiScore to score all words, negation detection enabled, A POS tag
    '''
    def __init__(self, Lex):
        super(A_LightPottsSentiScore, self).__init__()
        self.set_parameters(L=Lex, a=True, v=False, n=False, r=False, 
                            negation=True, negation_window=5, negation_adjustment=0.1,
                            score_mode=self.SCOREALL, score_stop=True, score_freq=True)

class AV_AggressivePottsSentiScore(PottsDocSentiScore):
    '''
     Pre-configured PottsDocSentiScore to score all words, A,V POS tags
    '''
    def __init__(self, Lex):
        super(AV_AggressivePottsSentiScore, self).__init__()
        self.set_parameters(L=Lex, a=True, v=True, n=False, r=False, 
                            negation=True, negation_window=5, negation_adjustment=0.5,
                            score_mode=self.SCOREALL, score_stop=True, score_freq=True)


class A_AggressivePottsSentiScore(BasicDocSentiScore):
    '''
     Pre-configured BasicDocSentiScore to score all words, negation detection enabled, A POS tag
    '''
    def __init__(self, Lex):
        super(A_AggressivePottsSentiScore, self).__init__()
        self.set_parameters(L=Lex, a=True, v=False, n=False, r=False, 
                            negation=True, negation_window=5, negation_adjustment=0.5,
                            score_mode=self.SCOREALL, score_stop=True, score_freq=True)

class AVO_AggressivePottsSentiScore(PottsDocSentiScore):
    '''
     Pre-configured PottsDocSentiScore to score all words, A,V POS tags
    '''
    def __init__(self, Lex):
        super(AVO_AggressivePottsSentiScore, self).__init__()
        self.set_parameters(L=Lex, a=True, v=True, n=False, r=False, 
                            negation=True, negation_window=5, negation_adjustment=0.5,
                            score_mode=self.SCOREONCE, score_stop=True, score_freq=True)

class AVO_LightPottsSentiScore(PottsDocSentiScore):
    '''
     Pre-configured PottsDocSentiScore to score all words, A,V POS tags
    '''
    def __init__(self, Lex):
        super(AVO_LightPottsSentiScore, self).__init__()
        self.set_parameters(L=Lex, a=True, v=True, n=False, r=False, 
                            negation=True, negation_window=5, negation_adjustment=0.1,
                            score_mode=self.SCOREONCE, score_stop=True, score_freq=True)
