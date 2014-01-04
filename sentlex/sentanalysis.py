'''

   Lexicon-Based Sentiment Analysis Library

   Performs sentiment classification on input
   documents with the assistance of sentiment lexicons.

'''

import re
import math
import nltk.stem

# library imports
import sentlex
import negdetect
import stopwords
from docscoreutil import *


class DocSentiScore(object):
    '''
     DocSentiScore

     This class performs lexicon-based sentiment classification on an input document
     given a set of parameters that configure the classification algorithm.
    '''

    def __init__(self):
        # initialize the default stopwords list
        self.objectiveWords = stopwords.Stopword()
        # default configuration
        self.set_active_pos(True, True, False, False)
        self.set_neg_detection(True)
        self.L = None
        self.verbose = False

    def classify_document(self, Doc, tagged=True, verbose=True, **kwargs):
        '''
         Classify an input document with classifier parameters per kwargs.
           Doc - string, inoput document.
           tagged - indicate wheter document is POS-tagged (False will call NLTK's default tagger)
           verbose - debug messages printed.
           **kwargs - classifier-specific parameters (optional). 

         When subclassing the default classifier, classify_doc (the algorithm)
         and set_parameters (parse algo parameters) need to be implemented.

         The following are mandatory parameters for every classifier algorithm:
           L - a sentiment lexicon (sentlex.Lexicon object);
           a,v,r,n - POS tags to scan (booleans);
           negation - boolean
           negation_window - integer
        '''
        pass

    def set_parameters(self, **kwargs):
        '''
         sets runtime parameters for this classification algorithm
        '''
        self._set_default_parameters(**kwargs)

    def _set_default_parameters(self, **kwargs):
        '''
         configures default parameters (Lexicon, POS, negation) for this classifier.
         Expects the following as arguments: L, a,v,r,n, negation, negation_window
        '''

        if 'L' in kwargs.keys():
            self.set_lexicon(kwargs['L'])

        # POS tags to enable
        tags = {'a': self.a, 'n': self.n, 'v': self.v, 'r': self.r}
        for tag in tags.keys():
            if tag in kwargs.keys():
                tags[tag] = kwargs[tag]
        self.set_active_pos(a=tags['a'], v=tags['v'], n=tags['n'], r=tags['r'])

        # Negation
        if 'negation' in kwargs.keys():
            window = 0
            if 'negation_window' in kwargs.keys(): window = kwargs['negation_window']
            self.set_neg_detection(kwargs['negation'], window)

    def set_lexicon(self, newL):
        assert newL.is_loaded, 'Lexicon must be loaded before use.'
        self.L = newL

    def set_neg_detection(self, mode, window=5):
        '''
         Enable negation detection for this algorithm
        '''
        self.negation = mode
        self.negation_window = window

    def set_active_pos(self, a=True, v=True, n=False, r=False):
        '''
         determine which POS tags to apply during classification
        '''
        self.a = a
        self.v = v
        self.n = n
        self.r = r

    def _detect_tag(self, Doc):
        '''
         For an input doc, detect POS separator (Brown or UPenn), if any, based on first 3 tokens.
         Returns None if no consistent match is found.
        '''
        def check_sep(sep, tokens):
            # does my separator generates tuples?
            seplist = [nltk.tag.str2tuple(i, sep=sep)[1] for i in tokens]
            if None in seplist:
                return None
            return sep

        tokens = Doc.split()[:5]
        for i in ['/', '_']:
            separator = check_sep(i, tokens)
            if separator: return separator

        return None 

    def pos_tag(self, Doc):
        '''
         Returns POS-tagged document using NLTK's recommended tagger.
        '''
        return ' '.join([x[0]+'/'+x[1] for x in nltk.pos_tag(nltk.word_tokenize(Doc))])

    def _debug(self, msg):
        if self.verbose: print msg


class BasicDocSentiScore(DocSentiScore):
    '''
      BasicDocSentiScore
      This class implements algorithm that scans and sums sentiment scores
      found in the document, based on a sentiment lexicon.

      The default parameters (pos, negation) affect this algorithm.

      In addition, 2 more tunable parameters can be used:
      - scan mode: how to add sentiment data from lexicons (once, always, frequency-adjusted)
      - weight function: function to adjust scores based on location within document.
        (some basic functions are supplied in the class, but they can be user defined)

    '''

    def __init__(self):
        # calls superclass
        super(BasicDocSentiScore,self).__init__()
        # Constants driving term-counting behavior 
        self.SCOREALL = 0
        self.SCOREONCE = 1
        # default configuration for Basic
        self.score_mode = self.SCOREALL
        self.score_freq = False
        self.score_stop = False
        self.score_function = self._score_noop

    def classify_document(self, Doc, tagged=True, verbose=True, **kwargs):
        '''
         Performs lexicon-based sentiment classification of input document.
         Doc is a POS-tagged document, which can optionally be tagged on-the-fly when tagged=False.
         **kwards are parameter settings for this algorithm. (optional)

         In addition to default parameters, this class accepts the following
         as tunables for this algorithm:
          - score_mode: one of SCOREALL/ONCE
          - score_freq: enable frequency-adjusted scores
          - score_stop: enable stop-word detection (stop words are discarded, override what lexicon may say)

         Returns: (pos_Score, neg_score) - total scores obtained from the scan.

        '''
        # Process input parameters, if any
        self.set_parameters(**kwargs)
        self.verbose = verbose
        w = self.score_function

        assert self.L and self.L.is_loaded, 'Lexicon has not been assigned, or not loaded'

        # POS-taging and tag detection
        if not tagged:
            taggedDoc = self.pos_tag(Doc)
        else:
            taggedDoc = Doc
        tagsep = self._detect_tag(taggedDoc)
        assert tagsep, 'Unable to detect tag separator'
        self._debug('[classify_document] - tag separator is %s' % tagsep)
        tags = taggedDoc.split()

        annotatedTags = []
        doclen = len(tags)
        i = 0
        postotal = 0
        negtotal = 0
        foundcounter = 0
        negcount = 0
 
        # Setup stem preprocessing for verbs
        wnl = nltk.stem.WordNetLemmatizer()
    
        # Negation detection pre-processing - return an array w/ position of negated terms
        vNEG = negdetect.getNegationArray(tags, self.negation_window)

        # Scan for scores for each POS
        # After POS-tagging a term will appear as either term/POS or term_POS
        # We assume such weirdnesses will not naturally occur on plain text.
        posindex = 0
        negindex = 1
        tagList = []
    
        for tagword in tags:
            i += 1
            scoretuple = (0,0)
            tagfound = False
            # retrieves tuple (word, POS tag) from current word+tag string
            (thisword, thistag) = nltk.tag.str2tuple(tagword, sep=tagsep)
            thisword = thisword.lower()

            # Adjectives 
            if self.a and re.search('(JJ|JJ.)$', thistag):
                tagfound = True
                scoretuple = self.L.getadjective(thisword)

            # Verbs (VBP / VBD/ etc...)
            if self.v and re.search('(VB|VB.)$', thistag):
                tagfound = True
                thislemma = wnl.lemmatize(thisword, pos='v')
                scoretuple = self.L.getverb(thislemma)
          
            # Adverbs
            if self.r and re.search('RB$', thistag):
                tagfound = True
                scoretuple = self.L.getadverb(thisword)

            # Nouns
            if self.n and re.search('NN$', thistag):
                tagfound = True
                scoretuple = self.L.getnoun(thisword)

            # Process negation detection
            if self.negation:
                posindex = vNEG[i-1]
                negindex = (1+vNEG[i-1])%2

            #
            # Add to total with weight score
            #
            posval = 0.0
            negval = 0.0 
            if tagfound and \
                ( 
                  (
                    (self.score_mode == self.SCOREALL) or 
                    (self.score_mode == self.SCOREONCE and (tagword not in tagList))
                  )
                  and
                  ( 
                    (self.score_stop and (not objectiveWords.is_stop(thisword))) or
                    (not self.score_stop)
                  )
                ):
                if self.score_freq:
                    # Scoring with frequency information
                    # Frequency is a real valued at 0.0-1.0. We calculate sqrt function so that the value grows faster even for numbers close to 0 
                    posval += w(scoretuple[posindex], i, doclen) * (1.0 - math.sqrt(self.L.getFreq(thisword)))
                    negval += w(scoretuple[negindex], i, doclen) * (1.0 - math.sqrt(self.L.getFreq(thisword)))
                else:
                    # Just plain scoring from lexicon - add
                    posval += w(scoretuple[posindex], i, doclen)
                    negval += w(scoretuple[negindex], i, doclen)
       
            postotal += posval
            negtotal += negval
            self._debug('Running total (pos,neg): %2.2f, %2.2f'%(postotal,negtotal))

            # Found a tag - increase counters and add tag to list
            if tagfound:
                tagList.append(tagword)
                foundcounter += 1
                if self.negation and vNEG[i-1]==1:
                    negcount += 1
                if self.negation: 
                    negtag = str(vNEG[i-1])
                else:
                    negtag = 'NONEG'
                annotatedTags.append(tagword + '##NEGAT:' + negtag + '##POS:' + str(posval) + '##NEG:' + str(negval))
            else:
                annotatedTags.append(tagword)

        # Completed scan
        if foundcounter == 0.0: foundcounter = 1.0

        # TODO: remove this?? resulting scores are the normalized proportions of all *scored* terms (ignoring neutrals/unknowns)
        ##resultpos = float(postotal)/float(foundcounter)
        ##resultneg = float(negtotal)/float(foundcounter)
        ##self._debug('Totals after adjustment %2.2f, %2.2f'%(resultpos, resultneg))
        resultpos = postotal
        resultneg = negtotal
 
        # updates class data structures containing results
        self.resultdata = {
            'annotated_doc': ' '.join(annotatedTags),
            'doc': Doc,
            'resultpos': resultpos,
            'resultneg': resultneg,
            'tokens_found': foundcounter,
            'tokens_negated': sum(vNEG)
        }

        self._debug('Result data: %s'%str(self.resultdata))
        return (resultpos, resultneg)


    def set_parameters(self, **kwargs):
        # calls superclass set_parameters
        super(BasicDocSentiScore,self).set_parameters(**kwargs)

        #TODO: this needs stronger validation
        if kwargs.has_key('score_mode'): self.score_mode = kwargs['score_mode']
        if kwargs.has_key('score_freq'): self.score_freq = kwargs['score_freq']
        if kwargs.has_key('score_stop'): self.score_stop = kwargs['score_stop']

        if kwargs.has_key('score_function'):
            try:
                self.score_function = getattr(self, '_score_'+kwargs['score_function'])
            except Exception:
                self.score_function = self._score_noop

    #
    # score weight adjustment functions
    #
    def _score_noop(self, score, i, N):
        '''
          no-op function: returns score given
        '''
        return score
