'''

   Lexicon-Based Sentiment Analysis Library

   sentanalysis_sent.py - a sentence-based sentiment classifier

'''
import sentlex
import collections
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
        self.question_neg_weight = 0.0
        self.min_question_size = 0.0       
        self.verbose = False

    def _sent_tokenize(self, doc, separator):
        '''
         Takes a pos-tagged doc and tag separator as input and return list of strings
         each containing a sentence from the original document.
        '''
        end_of_sentence = [x + separator + '.' for x in ('.', '!', '?')]
        
        cur_sent = []
        sentences = []
        for token in doc.split(' '):
            cur_sent.append(token)
            if token in end_of_sentence:
                sentences.append((' '.join(cur_sent), len(cur_sent)))
                cur_sent = []

        # finally, if cur_sent is not empty count as last sentence
        if cur_sent:
            sentences.append((' '.join(cur_sent), len(cur_sent)))

        return sentences

    def _is_question(self, sentence):
        if len(sentence) > 0:
            # looking for 1st char of the last pos-tagged token in sentence, format "char/POS"
            if len(sentence[-1]) > 0:
                return (sentence[-1][0] == '?')
        return False

    def classify_document(self, Doc, tagged=True, verbose=False, **kwargs):
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

        self._debug('[sent classifier] - Found %d sentences' % len(tagged_sentences))
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

        (tot_pos, tot_neg) = (0.0, 0.0)
        for (sentence, sent_sz) in tagged_sentences:
            try:
                self._debug('[sent classifier] %s' % sentence)
                self.sentence_classifier.set_lexicon(self.L)
                (cur_pos, cur_neg) = self.sentence_classifier.classify_document(sentence, tagged=True, verbose=verbose)

                # adjust for question
                if self._is_question(sentence.split(' ')) and sent_sz > self.min_question_size:
                    self._debug('[sent classifier] applying adjustment of %.2f to question sentence' % self.question_neg_weight)
                    cur_neg += self.question_neg_weight

                tot_pos += cur_pos
                tot_neg += cur_neg

                # update algorithm results
                self.resultdata['tokens_found'] += self.sentence_classifier.resultdata['tokens_found']
                self.resultdata['annotated_doc'] += self.sentence_classifier.resultdata['annotated_doc']
                self.resultdata['tokens_negated'] += self.sentence_classifier.resultdata['tokens_negated']
                self.resultdata['unscored_list'] += self.sentence_classifier.resultdata['unscored_list']
                self.resultdata['found_list'].update(self.sentence_classifier.resultdata['found_list'])
            except Exception, e:
                print '[sent classifier] - Error processing sentence (%s): %s' % (sentence, str(e))
                raise

        self.resultdata['resultpos'] = tot_pos
        self.resultdata['resultneg'] = tot_neg
        return (tot_pos, tot_neg)

    def set_parameters(self, **kwargs):
        '''
         Algorithm parameters are set for the underlying sentence classifier algorithm.
        '''
        if 'question_minsize' in kwargs:
            self.min_question_size = kwargs['question_minsize']
        if 'question_neg_weight' in kwargs:
            self.question_neg_weight = kwargs['question_neg_weight']

        self.sentence_classifier.set_parameters(**kwargs)
