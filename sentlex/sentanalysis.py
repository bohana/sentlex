"""

   Lexicon-Based Sentiment Analysis Library

   Performs sentiment classification on input
   documents with the assistance of sentiment lexicons.

"""

from __future__ import absolute_import
from __future__ import print_function
import re
import math
import nltk.stem
import collections

# library imports
from . import negdetect
from . import stopwords
from .docscoreutil import *


class DocSentiScore(object):
    """
     DocSentiScore

     This class performs lexicon-based sentiment classification on an input document
     given a set of parameters that configure the classification algorithm.
    """
    _BASE_INIT_CONFIG = {'a': True, 'v': True, 'n': False, 'r': False, 'atenuation': False}

    def __init__(self):
        # initialize the default stopwords list
        self.objectiveWords = stopwords.Stopword()
        self.L = None
        self.verbose = False
        self._resultdata = {}
        self._detector_map = {}

        # register detector functions (negation detection etc)
        self._register_detector('NEGATION', negdetect.getNegationArray, 'negation', 'negation_window', 'at',
                                {'negation': True, 'atenuation': False, 'at_pos': 1.0, 'at_neg': 1.0, 'negation_window': 5})

        self._init_config()

    def _register_detector(self, name, f_detector, enabled_param, window_param, atenuation_prefix, parameters_defaults):
        self._detector_map[name] = {'function': f_detector, 'enabled': enabled_param, 'prefix': atenuation_prefix,
                                    'window': window_param, 'parameters': parameters_defaults}

    def _run_detectors(self, tags):
        """Compute influence maps from input tags according to registered algorithms."""
        for map_type in self._detector_map:
            f_map = self._detector_map[map_type]['function']
            window = self._config[self._detector_map[map_type]['window']]
            self._document_maps[map_type] = f_map(tags, int(window))

    def _default_config(self):
        """Implement class-specific initial config here."""
        return dict()

    @property
    def config(self):
        return collections.namedtuple('config', field_names=self._config.keys())(**self._config)

    def set_config(self, k, v):
        self._config[k] = v

    def _init_config(self):
        res = self._BASE_INIT_CONFIG.copy()
        res.update(self._default_config())
        for map_type in self._detector_map:
            res.update(self._detector_map[map_type]['parameters'])

        self._config = res

    def classify_document(self, doc, tagged=True, verbose=True, **kwargs):
        """
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
        """
        raise NotImplementedError

    def set_parameters(self, **kwargs):
        """
         sets runtime parameters for this classification algorithm
        """
        raise NotImplementedError

    def set_lexicon(self, L):
        if not L.is_loaded:
            raise RuntimeError('Lexicon must be loaded before use.')

        self.L = L

    def _detect_tag(self, doc):
        """
         For an input doc, detect POS separator (Brown or UPenn), if any, based on first 3 tokens.
         Returns None if no consistent match is found.
        """
        def check_sep(sep, tokens):
            # does my separator generates tuples?
            seplist = [nltk.tag.str2tuple(i, sep=sep)[1] for i in tokens]
            if None in seplist:
                return None
            return sep

        tokens = doc.split()
        mintags = min(3, len(tokens))
        tokens = tokens[:mintags]
        for i in ['/', '_']:
            separator = check_sep(i, tokens)
            if separator:
                return separator

        return None

    def pos_tag(self, doc):
        """
         Returns POS-tagged document using NLTK's recommended tagger.
        """
        return ' '.join([x[0] + '/' + x[1] for x in nltk.pos_tag(nltk.word_tokenize(doc))])

    def _debug(self, msg):
        if self.verbose:
            print(msg)

    @property
    def resultdata(self):
        return self._resultdata


class BasicDocSentiScore(DocSentiScore):
    """
      BasicDocSentiScore
      This class implements algorithm that scans and sums sentiment scores
      found in the document, based on a sentiment lexicon.

      The default parameters (pos, negation) affect this algorithm.

      In addition, 2 more tunable parameters can be used:
      - scan mode: how to add sentiment data from lexicons (once, always, frequency-adjusted)
      - weight function: function to adjust scores based on location within document.
        (some basic functions are supplied in the class, but they can be user defined)

    """
    # Constants driving term-counting behavior
    SCOREALL = 0
    SCOREONCE = 1
    SCOREBACKOFF = 2

    def __init__(self):
        # calls superclass
        super(BasicDocSentiScore, self).__init__()

        # Setup stem preprocessing for verbs
        self.wnl = nltk.stem.WordNetLemmatizer()
        self.lemma_cache = {}

    def _default_config(self):
        return {'score_mode': self.SCOREALL,
                'score_freq': False,
                'score_stop': False,
                'score_function': self._score_noop,
                'negated_term_adj': 0.0,
                'freq_weight': 1.0,
                'backoff_alpha': 0.0,
                'a_adjust': 1.0,
                'v_adjust': 1.0}

    def _get_word_contribution(self, thisword, tagword, scoretuple, i, doclen, config=None):
        """
         Returns tuple (posval, negval) containing score contribution for i-th word in document, based
         on algorithm setup and scoretuple retrieved from lexicon.
        """
        config = config or self.config
        posval = 0.0
        negval = 0.0

        # determine if this word should be scored
        if (
            (
                (config.score_mode == self.SCOREALL) or (config.score_mode == self.SCOREBACKOFF) or
                (config.score_mode == self.SCOREONCE and (self.tag_counter[tagword] == 1))
            )
            and
            (
                (config.score_stop and (not self.objectiveWords.is_stop(thisword))) or
                (not config.score_stop)
            )
        ):
            # flip indexes for pos/neg values if atenuation is disabled (negation maps only)
            if config.negation and not config.atenuation:
                vMAP = self._document_maps['NEGATION']
                posindex = vMAP[i - 1]
                negindex = (1 + vMAP[i - 1]) % 2
            else:
                posindex = 0
                negindex = 1

            posval = config.score_function(scoretuple[posindex], i, doclen)
            negval = config.score_function(scoretuple[negindex], i, doclen)

            if config.score_freq:
                # Scoring with frequency information
                posval = self._freq_adjust(posval, self.L.get_freq(thisword))
                negval = self._freq_adjust(negval, self.L.get_freq(thisword))

            if config.score_mode == self.SCOREBACKOFF:
                # when backoff is enabled we apply exponential backoff to the word contribution
                posval = self._repeated_backoff(posval, self.tag_counter[tagword], self.backoff_alpha)
                negval = self._repeated_backoff(negval, self.tag_counter[tagword], self.backoff_alpha)

            for map_type in self._document_maps:
                # loop every active map
                vMAP = self._document_maps[map_type]
                at_prefix = self._detector_map[map_type]['prefix']
                map_enabled = getattr(config, self._detector_map[map_type]['enabled'])
                map_enabled &= config.atenuation or (not config.atenuation and map_type == 'NEGATION')

                if map_enabled and config.atenuation and vMAP[i - 1]:
                    # adjust score val when inside an active window and atenuation is enabled
                    posval *= getattr(config, at_prefix + '_pos')
                    negval *= getattr(config, at_prefix + '_neg')

            self._debug('[_get_word_contribution] word %s (%s) at %d-th place on docsize %d is eligible (%2.2f, %2.2f).' %
                        (thisword, str(scoretuple), i, doclen, posval, negval))

        return (posval, negval)

    def _repeated_backoff(self, val, repeatcount, alpha):
        """
          Adjusts score *val* using exponential backoff and adjustment factor *alpha*
        """
        if repeatcount == 0:
            # should not be scoring a word that never ocurred
            return 0.0

        return val * (1.0 / math.pow(2, alpha * (repeatcount - 1)))

    def _doc_score_adjust(self, posval, negval, config=None):
        """
         Final adjustments to doc scoring once scan completes
        """
        return (posval, negval)

    def _freq_adjust(self, score, p, freq_weight=1.0):
        """
          Adjust contribution of a word score based on frequency information given by the formula for self-information:
            I(x) = -log(p(x))
          Where p(x) is estimated based on a word frequency list.

          The frequency is also weight-adjusted according to freq_weight ( 0.0..1.0, defaults to 1.0) using the formula:
            score = (weight * I(x)) + (1 - weight)

        """
        # unknown words get a mid-range value
        if p == 0.0:
            p = 0.0005

        I = -1 * math.log(p, 2)
        return score * ((1 - freq_weight) + (I * (freq_weight)))

    def _reset_runtime_vars(self):
        self._resultdata = {}
        self.tag_counter = collections.Counter()
        self._document_maps = {}

    def _lemmatize_verb(self, word):
        """
         Returns lemma of a given word, if verb
        """
        # first query local cache in case this lemma already exists
        if word in self.lemma_cache:
            return self.lemma_cache[word]
        else:
            lemma = self.wnl.lemmatize(word, pos='v')
            if lemma:
                self.lemma_cache[word] = lemma
            return lemma

    def classify_document(self, doc, tagged=True, verbose=False, annotations=False, **kwargs):
        """
         Performs lexicon-based sentiment classification of input document.

         Parameters
         ----------
         doc : str
            Input document.
         tagged : bool
            boolean indicating document is already POS-tagged.
         verbose : bool
            output verbose logging.
         annotations : bool
            generate annotations (can be queried with self.resultdata property)
         **kwargs : dict
            optional keyword arguments to configure the classifier.

         Returns: (pos_score, neg_score) - total scores obtained from the scan.
        """
        # Process input parameters, if any
        self.set_parameters(**kwargs)
        self.verbose = verbose
        if not self.L.is_loaded:
            raise RuntimeError('Lexicon has not been assigned, or not loaded')

        config = self.config

        # POS-taging and tag detection
        if not tagged:
            tagged_doc = self.pos_tag(doc)
        else:
            tagged_doc = doc

        tagsep = self._detect_tag(tagged_doc)
        if not tagsep:
            raise RuntimeError('Unable to detect tag separator in {}'.format(' '.join(doc[:100])))

        # ready to start - reset runtime vars
        self._reset_runtime_vars()
        self._debug('[classify_document] - tag separator is %s' % tagsep)
        tags = tagged_doc.split()
        annotatedTags = []
        doclen = len(tags)
        i = 0
        postotal = 0.0
        negtotal = 0.0
        foundcounter = 0
        negcount = 0
        self.tag_counter = collections.Counter()
        tagUnscored = []

        # Negation detection pre-processing - return an array w/ position of negated terms
        self._run_detectors(tags)
        vNEG = self._document_maps['NEGATION']

        # Scan for scores for each POS
        # After POS-tagging a term will appear as either term/POS or term_POS
        # We assume such weirdnesses will not naturally occur on plain text.
        for tagword in tags:
            i += 1
            scoretuple = (0, 0)
            tagfound = False
            # retrieves tuple (word, POS tag) from current word+tag string
            (thisword, thistag) = nltk.tag.str2tuple(tagword, sep=tagsep)
            if (not thistag) or (not thisword):
                continue  # discard corrupt data
            thisword = thisword.lower()

            # Adjectives
            if config.a and re.search('(JJ|JJ.)$', thistag):
                tagfound = True
                scoretuple = [config.a_adjust * x for x in self.L.getadjective(thisword)]

            # Verbs (VBP / VBD/ etc...)
            if config.v and re.search('(VB|VB.)$', thistag):
                tagfound = True
                thislemma = self._lemmatize_verb(thisword)
                scoretuple = [config.v_adjust * x for x in self.L.getverb(thislemma)]

            # Adverbs
            if config.r and re.search('RB$', thistag):
                tagfound = True
                scoretuple = self.L.getadverb(thisword)

            # Nouns
            if config.n and re.search('NN$', thistag):
                tagfound = True
                scoretuple = self.L.getnoun(thisword)

            #
            # Add this word contribution to total
            #
            if tagfound:
                self.tag_counter.update([tagword])
                (posval, negval) = self._get_word_contribution(thisword, tagword, scoretuple, i, doclen, config)
                postotal += posval
                negtotal += negval
                self._debug('Running total (pos,neg): %2.2f, %2.2f' % (postotal, negtotal))

                if scoretuple == (0, 0):
                    tagUnscored.append(tagword)
                foundcounter += 1
                if config.negation and vNEG[i - 1] == 1:
                    negcount += 1
                if config.negation:
                    negtag = str(vNEG[i - 1])
                else:
                    negtag = 'NONEG'

                if annotations:
                    annotatedTags.append(tagword + '##NEGAT:' + negtag +
                                         '##POS:' + str(posval) + '##NEG:' + str(negval))
            else:
                if annotations:
                    annotatedTags.append(tagword)

        # Completed scan - execute final score adjustments
        (resultpos, resultneg) = self._doc_score_adjust(postotal, negtotal, config)

        # updates class data structures containing results
        self._resultdata = {
            'annotated_doc': ' '.join(annotatedTags),
            'doc': doc,
            'resultpos': resultpos,
            'resultneg': resultneg,
            'tokens_found': foundcounter,
            'tokens_negated': sum(vNEG),
            'found_list': self.tag_counter,
            'unscored_list': tagUnscored
        }

        self._debug('Result data: %s' % str(self._resultdata))
        return (resultpos, resultneg)

    def set_parameters(self, **kwargs):
        """
          Parameters that can be set on this type of algorithm:
          L, lexicon
          a,n,v,r: POS tags to enable
          negation: True/False for negation detection
          negation_window: tokens to consider in negated window
          score_function: score adjustment function (looks for self._score_<score_function>)
          score_mode: score each word once/always
          score_freq: frequency adjust word scores
          score_stop: discard stop words
        """
        # calls superclass set_parameters
        if 'L' in kwargs:
            self.set_lexicon(kwargs['L'])

        # update all known parameters
        self._config.update({k: kwargs[k] for k in kwargs if k in self._config})

        # Implicitly update negation
        if any([k in kwargs for k in ['negation_window', 'atenuation']]):
            self.negation = True

        if 'score_function' in kwargs:
            self.score_function = getattr(self, '_score_' + kwargs['score_function'])

    #
    # score weight adjustment functions
    #
    def _score_noop(self, score, i, N):
        """
          no-op function: returns score given as-is
        """
        return score


#
# Sample Pre-defined algorithms based on BasicDocSentiScore
#
class AV_AllWordsDocSentiScore(BasicDocSentiScore):
    """
     Pre-configured BasicDocSentiScore to score all words, negation detection enabled, A,V POS tags
    """
    def __init__(self, Lex):
        super(AV_AllWordsDocSentiScore, self).__init__()
        self.set_parameters(L=Lex, a=True, v=True, n=False, r=False,
                            negation=True, negation_window=5,
                            score_mode=self.SCOREALL, score_stop=True, score_freq=True)


class A_AllWordsDocSentiScore(BasicDocSentiScore):
    """
     Pre-configured BasicDocSentiScore to score all words, negation detection enabled, A POS tag
    """
    def __init__(self, Lex):
        super(A_AllWordsDocSentiScore, self).__init__()
        self.set_parameters(L=Lex, a=True, v=False, n=False, r=False,
                            negation=True, negation_window=5,
                            score_mode=self.SCOREALL, score_stop=True, score_freq=True)


class A_OnceWordsDocSentiScore(BasicDocSentiScore):
    """
     Pre-configured BasicDocSentiScore to score once, negation detection enabled, A POS tags
    """
    def __init__(self, Lex):
        super(A_OnceWordsDocSentiScore, self).__init__()
        self.set_parameters(L=Lex, a=True, v=False, n=False, r=False,
                            negation=True, negation_window=5,
                            score_mode=self.SCOREONCE, score_stop=True, score_freq=True)


class AV_OnceWordsDocSentiScore(BasicDocSentiScore):
    """
     Pre-configured BasicDocSentiScore to score once, negation detection enabled, A,V POS tags
    """
    def __init__(self, Lex):
        super(AV_OnceWordsDocSentiScore, self).__init__()
        self.set_parameters(L=Lex, a=True, v=True, n=False, r=False,
                            negation=True, negation_window=5,
                            score_mode=self.SCOREONCE, score_stop=True, score_freq=True)
