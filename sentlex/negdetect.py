'''
 An implementation of the NegEx algorithm for negation detection in a document.

 Negex works by scanning for known explicit negating markers in the form of unigrams and bigrams.
 A found pattern triggers a negated 'window' of specific size in tokens.
 Anything within a negated window is considered a negated sentence.
 Negating windows are bounded by punctuation, known limiting tokens or a user-specified maximum window size.

 More about NegEx:
 http://rods.health.pitt.edu/LIBRARY/NLP%20Papers/chapman_JBI_2001_negation.pdf

 This implementation adds a few more tokens to the original implementation from Chapman et al.
'''
import re

# Pseudo-negations - to be ignored by the algorithm
NEG_PSEUDO = [
    'no increase',
    'no wonder',
    'no change',
    'not only',
    'not just'
    'not necessarily',
    'cannot describe'
]

# Pre-negating terms - negate what follows
NEG_PRENEGATION = [
    'not',
    'no',
    'n\'t',
    'cannot',
    'declined',
    'denied', 'denies', 'deny',
    'free of',
    'lack of',
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
    'isn',
    'hadnt', 'hadn\'t'
    'wasnt', 'wasn\'t'
    'werent', 'weren\'t'
    'neither', 'nor',
    'dont', 'don\'t',
    'didnt', 'didn\'t'
    'wont', 'won\'t'
    'reject', 'rejects', 'rejected',
    'refuse to', 'refused to', 'refuses to',
    'dismiss', 'dismissed', 'dismisses',
    'couldn', 'couldnt',
    'doesn', 'doesnt',
    'non', 'nothing',
    'aren', 'arent',
    'none',
    'anything but',
    'negligible',
    'unlikely to'
]

# pos negating terms - modifies what came before
# experiment - currently disabled
NEG_POSNEGATION = [
    'unlikely',
    'ruled out',
    'refused',
    'rejected',
    'dismissed',
    'not true',
    'false',
    'untrue',
    'unremarkable',
    'shot down']

NEG_ENDOFWINDOW = [
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
]

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
        docsize=len(doc)
        if docsize>0 and re.search('[/_]', doc[0]):
            separator = doc[0][re.search('[/_]', doc[0]).start()]
        elif docsize>1 and re.search('[/_]', doc[1]):
            # second try
            separator = doc[1][re.search('[/_]', doc[1]).start()]
        elif separator not in '_/':
            debug('Warning. Could not find a separator from input. Using "_"')
            separator = '_'
        return separator

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
    docsize = len(doc)
    i = 0
    found_pseudo = False
    found_neg_fwd = False
    found_neg_bck = False
    inwindow = 0
    separator = '_'
    if postag: separator = get_pos_separator(doc)

    for i in range(docsize):
        unigram = get_next_ngram(doc, docsize, i, 1, postag, separator)
        bigram = get_next_ngram(doc, docsize, i, 2, postag, separator)

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
