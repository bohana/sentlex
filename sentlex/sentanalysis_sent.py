'''

   Lexicon-Based Sentiment Analysis Library

   sentanalysis_sent.py - a sentence-based sentiment classifier

'''

# library imports
import sentlex
from docscoreutil import *
from sentanalysis import DocSentiScore
from sentanalysis_potts import AV_AggressivePottsSentiScore


class SentenceDocSentiScore(DocSentiScore):
    '''
     Subclass of DocSentiScore implementing a sentence-based lexicon-based classifier.
     this approach breaks a document into sentences and generates sentiment scores based on aggregate
     sentiment of each sentence, instead of individual tokens.
    '''
    def __init__(self, Lex, classifier_obj=None):
        # calls superclass
        super(DocSentiScore, self).__init__()
        if not classifier_obj:
            # default classifier to be used on sentences
            self.sentence_classifier=AV_AggressivePottsSentiScore(Lex)
        else:
            self.sentence_classifier=classifier_obj
            self.sentence_classifier.set_lexicon(Lex)

        self.set_lexicon(Lex)

    def _sent_tokenize(self, doc, separator):
        '''
         Takes a pos-tagged doc and tag separator as input and return list of strings
         each containing a sentence from the original document.
        '''
        # list of all POS-tagged indicators of end of sentence
        end_of_sentence = [x+separator+'.' for x in ['.','!','?']]
        cur_sent = []
        sentences = []
        for token in doc.split(' '):
            cur_sent.append(token)
            if token in end_of_sentence:
                sentences.append(' '.join(cur_sent))
                cur_sent = []
        return sentences

    def _calc_sentence_scores(sent_scores):
        pos_total = sum([x[0] for x in sent_scores])
        neg_total = sum([x[1] for x in sent_scores])
        return (pos_total, neg_total)

    def classify_document(self, Doc, tagged=True, verbose=True, **kwargs):
        '''
          Tokenize input document into sentences, then call classifier on each sentence separately.
          Return aggregate positive and negative scores in tuple (postotal,negtotal)
        '''
        # Process input parameters, if any
        self.set_parameters(**kwargs)
        self.verbose = verbose
        assert self.L and self.L.is_loaded, 'Lexicon has not been assigned, or not loaded'

        # POS-taging and tag detection
        if not tagged:
            tagged_doc = self.pos_tag(Doc)
        else:
            tagged_doc = Doc
        tagsep = self._detect_tag(tagged_doc)
        assert tagsep, 'Unable to detect tag separator'

        # tokenize into sentences
        tagged_sentences = self._sent_tokenize(tagged_doc, tagsep)
        sent_scores = []
        # initialize data structure containing results
        self.resultdata = {
            'annotated_doc': '',
            'doc': Doc,
            'resultpos': 0,
            'resultneg': 0,
            'tokens_found': 0,
            'tokens_negated': 0,
            'found_list': collections.Counter(),
            'unscored_list': []
        }
        for sentence in tagged_sentences:
            # classify sentence
            (cur_pos, cur_neg) = self.sentence_classifier.classify_document(sentence, tagged=True)
            if cur_pos>cur_neg:
               sent_scores.append((1,0))
            elif cur_neg>cur_pos:
               sent_scores.append((0,1))
            else:
               sent_scores.append((0,0))

            self._debug('[sent classifier] - sentence scores: %s' % str(sent_scores))

            # update algorithm results
            self.resultdata['tokens_found'] += self.sentence_classifier.resultdata['tokens_found']
            self.resultdata['annotated_doc'] += self.sentence_classifier.resultdata['annotated_doc']
            self.resultdata['tokens_negated'] += self.sentence_classifier.resultdata['tokens_negated']
            self.resultdata['unscored_list'] += self.sentence_classifier.resultdata['unscored_list']
            self.resultdata['found_list'].update(self.sentence_classifier.resultdata['found_list'])

        (resultpos, resultneg) = self._calc_sentence_scores(sent_scores)
        self.resultdata['resultpos'] = resultpos
        self.resultdata['resultneg'] = resultneg
        return (resultpos, resultneg)

    def set_parameters(self, **kwargs):
        '''
         Algorithm parameters are set for the underlying sentence classifier algorithm.
        '''
        self.sentence_classifier.set_parameters(**kwargs)
