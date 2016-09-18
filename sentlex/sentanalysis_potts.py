'''

   Lexicon-Based Sentiment Analysis Library

   sentanalysis_potts.py - implements score adjustment based on negated terms
   derived from the work of [Potts, 2011]

'''
from __future__ import absolute_import
from .sentanalysis import BasicDocSentiScore
from six.moves import range


class PottsDocSentiScore(BasicDocSentiScore):
    '''
     Subclass of BasicDocSentiScore implementing score adjustment based on negated terms.
     The key assumption is negated terms are correlated with negative sentiment.

     This class *required* negation detection to be active.
    '''

    def _default_config(self):
        ddict = super(PottsDocSentiScore, self)._default_config()
        ddict.update({'negation_adjustment': 0.1})
        return ddict

    def _doc_score_adjust(self, posval, negval, config=None):
        '''
         Implements negated term additions based on adjustment weight
        '''
        config = config or self.config
        (postmp, negtmp) = super(PottsDocSentiScore, self)._doc_score_adjust(posval, negval)
        vNEG = self._document_maps['NEGATION']
        if config.negation:
            # at this point we should have vNEG populated by the scoring algorithm
            if len(vNEG) >= 3:
                negated_instances = len(
                    [vNEG[i:i + 2] for i in range(len(vNEG) - 1) if vNEG[i:i + 2] == [0, 1]])
            else:
                negated_instances = 0
            # with the total of negated instances we can compute the adjustment
            # each negating term counts "negated_term_adj" in scoring weight
            negtmp = negtmp + (config.negation_adjustment * negated_instances)
            self._debug('[PottsDocSentiScore] - Instances Found: %d. Negative score now adjusted from %2.2f to %2.2f' %
                        (negated_instances, negval, negtmp))
        return (postmp, negtmp)


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
