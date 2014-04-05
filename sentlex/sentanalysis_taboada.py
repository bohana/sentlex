'''

   Lexicon-Based Sentiment Analysis Library

   sentanalysis_taboada.py - implements some lexicon based classifier features
   derived from the work of [Taboada et al, 2011]

'''

# library imports
import sentlex
import negdetect
import stopwords
from docscoreutil import *
from sentanalysis import BasicDocSentiScore

class TaboadaDocSentiScore(BasicDocSentiScore):
    '''
     Subclass of BasicDocSentiScore implementing score "shifts" for negated terms
     and a backoff mechanism for counting repeated terms.
    '''

    def __init__(self):
        # calls superclass
        super(TaboadaDocSentiScore, self).__init__()
        self.BACKOFF = -101
        self.negated_shift_adj = 0.25
        self.score_mode = self.BACKOFF

    def set_parameters(self, **kwargs):
        '''
          In this section we simply add logic for self.negated_shift_adj and call super for everything else
        '''
        super(TaboadaDocSentiScore, self).set_parameters(**kwargs)
        if 'negation_shift' in kwargs.keys():
            self.negated_shift_adj = kwargs['negation_shift']

        # overrides score counting with this class's method
        self.score_mode = self.BACKOFF


    def _get_word_contribution(self, thisword, tagword, scoretuple, i, doclen):
        '''
         Returns tuple (posval, negval) containing score contribution for i-th word in document, based
         on algorithm setup and scoretuple retrieved from lexicon.

         The Taboada version implements a backoff mechanism for counting repeated words such that the n-th
         occurrence of the word is adjusted by:

            score = original_score/n

         In addition, scores for negated terms are "shifted" by self.negated_shift_adj instead of inverted.
        '''
        posval = 0.0
        negval = 0.0
        posindex = 0
        negindex = 1

        # This algorithm defines a new score_mode (self.BACKOFF) and sets it by default at init time.
        if (self.score_mode == self.BACKOFF) and\
           ( 
            (self.score_stop and (not self.objectiveWords.is_stop(thisword))) or
            (not self.score_stop)
           ):
            # Calculate value with backoff
            posval = scoretuple[posindex]/(self.tag_counter[tagword]+1.0)
            negval = scoretuple[negindex]/(self.tag_counter[tagword]+1.0)
            # If negated, shift
            if self.negation:
                # these adjustments will not count unless word is negated
                if (posval>negval):
                    posval = posval - ((self.vNEG[i-1])*self.negated_shift_adj)
                if (negval>posval):
                    negval = negval - ((self.vNEG[i-1])*self.negated_shift_adj)
            # Adjust score
            posval = self.score_function(posval, i, doclen)
            negval = self.score_function(negval, i, doclen)
            if self.score_freq:
                # Scoring with frequency information
                # Frequency is a real valued at 0.0-1.0. We calculate sqrt function so that the value grows faster even for numbers close to 0 
                posval *= 1.0 - max(math.sqrt(self.L.get_freq(thisword)), 0.25)
                negval *= 1.0 - max(math.sqrt(self.L.get_freq(thisword)), 0.25)
            self._debug('[_get_word_contribution] word %s (%s) at %d-th place on docsize %d is eligible (%2.2f, %2.2f).' % (thisword, str(scoretuple), i, doclen, posval, negval))

        return (posval, negval)


#
# Pre-defined algorithms based on PottsDocSentiScore
#
class AV_LightTabSentiScore(TaboadaDocSentiScore):
    '''
     Pre-configured TaboadaDocSentiScore to score all words, A,V POS tags.
     This class uses a "light" threshold of 0.25 for shifting negated scores.
    '''
    def __init__(self, Lex):
        super(AV_LightTabSentiScore, self).__init__()
        self.set_parameters(L=Lex, a=True, v=True, n=False, r=False,
                            negation=True, negation_window=5, negation_shift=0.25,
                            score_stop=True, score_freq=True)

class AV_AggressiveTabSentiScore(TaboadaDocSentiScore):
    '''
     Pre-configured TaboadaDocSentiScore to score all words, A,V POS tags.
     This class uses a "aggressive" threshold of 0.5 for shifting negated scores.
    '''
    def __init__(self, Lex):
        super(AV_AggressiveTabSentiScore, self).__init__()
        self.set_parameters(L=Lex, a=True, v=True, n=False, r=False,
                            negation=True, negation_window=5, negation_shift=0.5,
                            score_stop=True, score_freq=True)
