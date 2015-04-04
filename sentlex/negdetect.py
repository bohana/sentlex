'''
  An negation detection algorithm based on known negation markers. This implementation is inspired by the NegEx algorithm (Chapman et al 2001)

  It works by scanning for known explicit negating markers in the form of unigrams and bigrams.
  A found pattern triggers a negated 'window' of specific size in tokens.
  Anything within a negated window is considered a negated sentence.
  Negating windows are bounded by punctuation, known limiting tokens or a user-specified maximum window size.

  About NegEx:
 
      Chapman, Wendy W., et al. 
      "A simple algorithm for identifying negated findings and diseases in discharge summaries." 
      Journal of biomedical informatics 34.5 (2001): 301-310.

      http://rods.health.pitt.edu/LIBRARY/NLP%20Papers/chapman_JBI_2001_negation.pdf

  The tokens used in this algorithm were extended based on experimentation and the list described on:

      Councill, Isaac G., Ryan McDonald, and Leonid Velikovich. 
      "What's great and what's not: learning to classify the scope of negation for improved sentiment analysis." 
      Proceedings of the workshop on negation and speculation in natural language processing. Association for Computational Linguistics, 2010.
  
'''
import re

# Pseudo-negations - to be ignored by the algorithm
NEG_PSEUDO = set([
    'no increase',
    'no wonder',
    'no change',
    'not only',
    'not just'
    'not necessarily',
    'cannot describe'
])

# Pre-negating terms - negate what follows
NEG_PRENEGATION = set([
    'not',
    'no',
    'n\'t',
    'cannot', 'cant', 'can\'t',
    'declined',
    'denied', 'denies', 'deny',
    'free of',
    'lack of', 'lacks', 'lacking',
    'fails to', 'failed to', 'fail to'
    'no evidence',
    'no sign',
    'no suspicious',
    'no suggestion',
    'rather than',
    'with no',
    'unremarkable',
    'without',
    'rules out', 'ruled out', 'rule out',
    'isn', 'isnt', 'isn\'t', 'aint', 'ain\'t'
    'hadnt', 'hadn\'t',
    'wasnt', 'wasn\'t',
    'werent', 'weren\'t',
    'havent', 'haven\'t',
    'wouldnt', 'wouldn\'t',
    'havnt',
    'shant',
    'neither', 'nor',
    'dont', 'don\'t',
    'didnt', 'didn\'t'
    'wont', 'won\'t'
    'darent', 'daren\'t',
    'shouldnt', 'shouln\'t',
    'reject', 'rejects', 'rejected',
    'refuse to', 'refused to', 'refuses to',
    'dismiss', 'dismissed', 'dismisses',
    'couldn', 'couldnt', 'couldn\'t'
    'doesn', 'doesnt', 'doesn\'t',
    'non', 'nothing',
    'nobody',
    'nowhere',
    'aren', 'arent', 'aren\'t',
    'none',
    'anything but',
    'negligible',
    'unlikely to'
])

# pos negating terms - modifies what came before
# experiment - currently disabled
NEG_POSNEGATION = set([
    'unlikely',
    'ruled out',
    'refused',
    'rejected',
    'dismissed',
    'not true',
    'false',
    'untrue',
    'unremarkable',
    'shot down'])

NEG_ENDOFWINDOW = set([
    '.', ':', ';', ',', ')', '!', ';', '?', ']',
    'but', 
    'however', 
    'nevertheless', 
    'yet',
    'though', 'although',
    'still', 
    'aside from', 
    'except', 
    'apart from', 
    'because', 
    'unless',
    'therefore'
])

def getNegationArray(doc, windowsize, debugmode=False, postag=True):
    '''
      NegEx-based negation detection algorithm for text.
      Receives a POS-tagged document in list form and size of negating window. A POS-tagged document takes the form:
      
         Do_VBP n't_RB tell_VB her_PRP who_WP I_PRP am_VBP seeing_VBG

      Returns array A where A[i] indicates whether this position in the document has been negated by an expression (1), or not (0).

      Arguments
      ---------
         doc        - input doc as *list* of tokens, with or w/out part of speech
         windowsize - the default cut off window size that limits the scope of a negation.
         debugmode  - prints more stuff
         postag     - True/False, whether input document has been POS-tagged 
    '''

    def debug(msg):
        if debugmode: print '[getNegationArray] - %s' % msg

    def get_pos_separator(doc):
        '''
         given a list of tokens "guesses" the part of speech separator based on first tokens
        '''
        for i in xrange(min(2,len(doc))):
            if '_' in doc[i]:
                return '_'
            elif '/' in doc[i]:
                return '/'
        return '_'

    def get_next_ngram(doc, docsize, position, n, postag, separator):
        '''
         Returns next n-gram from document, stripping part of speech.
         If position+n is larger than doc lenght, returns smallest n-gram that fits end of document.
        '''
        grams = []
        for igram in range(n):
            if position < (docsize - igram):
                if postag:
                    grams.append(doc[position + igram].split(separator)[0])
                else:
                    grams.append(doc[position + igram])
        return ' '.join(grams).lower()

    # check input is a list
    assert type(doc) is list, 'Input document must be a list of POS-tagged tokens'

    # Initialise array
    vNEG = [0 for t in range(len(doc))]
    # Initialise window counters
    winstart = 0
    i = 0
    found_pseudo = False
    found_neg_fwd = False
    found_neg_bck = False
    inwindow = 0
    separator = '_'
    if postag: 
        separator = get_pos_separator(doc)
        untagged_doc = [w.split(separator)[0] for w in doc]
    else:
        untagged_doc = doc

    docsize = len(untagged_doc)
    for i in xrange(docsize):
        unigram = untagged_doc[i]
        if i < (docsize - 1):
            bigram = unigram + ' ' + untagged_doc[i+1]
        else:
            bigram = unigram

        # Search for pseudo negations
        if bigram in NEG_PSEUDO:
            found_pseudo = True

        # Look for pre negations
        if not found_pseudo:
            if (unigram in NEG_PRENEGATION) or (bigram in NEG_PRENEGATION):
                found_neg_fwd = True
                debug('Found fwd negation at vicinity of: %s ' % bigram)
            if (unigram in NEG_POSNEGATION) or (bigram in NEG_POSNEGATION):
                found_neg_bck = True
                debug('Found back negation at vicinity of: %s' % bigram)

        # If found fwd/backw negation, then negate window
        if found_neg_fwd:
            # negate terms forward up to window
            if inwindow < windowsize:
                vNEG[i] = 1
                inwindow += 1
            else:
                # out of window space. Reset fwd negation and window
                found_neg_fwd = False
                inwindow = 0

        # now move window
        if (unigram in NEG_ENDOFWINDOW) or (bigram in NEG_ENDOFWINDOW):
            # found end of negation, must reset window and negation state
            debug('End of negating window at %d, %s.' % (i, unigram))
            inwindow = 0
            found_neg_fwd = False
            winstart = i

        # Always reset pseudo
        found_pseudo = False

    return vNEG
