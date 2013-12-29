'''
 An implementation of the NegEx algorithm for negation detection in a document.

 Negex works by scanning for known negating patterns in text.
 A found pattern triggers a negated 'window' of specific size in tokens.
 Anything within a negated window is considered a negated sentence.
 Negating windows can be forwards or backwards from the negated pattern,
 and are bounded by punctuation, known limiting tokens or a user-specified maximum window size.

 More about NegEx:
 http://rods.health.pitt.edu/LIBRARY/NLP%20Papers/chapman_JBI_2001_negation.pdf

 This implementation adds more tokens to the original implementation from Chapman et al.
'''
import re

# Pseudo-negations - to be ignored by the algorithm
NEG_PSEUDO = [
    'no increase',
    'no wonder',
    'no change',
    'not only',
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
    'fails to', 'failed to',
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
    'hadn',
    'wasn',
    'weren',
    'neither', 'nor',
    'didn',
    'don', 'dont',
    'won', 'wont',
    '\'t',
    'reject', 'rejects', 'rejected',
    'refuse', 'refused', 'refuses',
    'dismiss', 'dismissed', 'dismisses',
    'couldn', 'couldnt',
    'doesn', 'doesnt',
    'non', 'nothing',
    'aren', 'arent',
    'none',
    'anything but'
]

# pos negating terms - modifies what came before
NEG_POSNEGATION = ['unlikely',
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
    '.', ':', ',', ')', '!', ';',
    'but', 'however', 'nevertheless', 'yet', 'though', 'although',
    'still', 'aside from', 'except', 'apart from'
]

#
# populates array of negated terms based on document terms
# negation[i] indicates if term in doc[i] is negated
#
def getNegationArray(doc, windowsize, debugmode=False):
    '''
      NegEx-based negation detection algorithm for text.
      Receives a POS-tagged document in list form and size of negating window. A POS-tagged document takes the form:
        
         the/DT hype/NN and/CC is/VBZ a/DT very/RB seductive/JJ

      or:
        
        the_DT hype_NN and_CC is_VBZ a_DT very_RB seductive_JJ

      Returns array A where A[i] indicates whether this position in the document has been negated by an expression (value = 1), or not (value = 0).
    '''

    def debug(msg):
        if debugmode: print '[getNegationArray] - %s' % msg

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

    # detect POS separator from 1st token. Use '_' if none found
    separator = '_'
    if docsize>0 and re.search('[/_]', doc[1]):
        separator = doc[1][re.search('[/_]', doc[1]).start()]
    elif docsize>1 and re.search('[/_]', doc[2]):
        # second try
        separator = doc[2][re.search('[/_]', doc[2]).start()]
    elif separator not in '_/': 
        debug('Warning. Could not find a separator from input. Using "_"')
        separator = '_'

    for i in range(docsize):
        # Build 1-term and 2-term strings.
        unigram = doc[i].split(separator)[0]
        bigram = ''   
        if i < (docsize - 1):
            bigram = ' '.join([unigram, doc[i+1].split(separator)[0]])
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

        # backward negation
        if found_neg_bck:
            # negate back until window start
            for counter in range(max(winstart, i-windowsize), i):
                vNEG[counter] = 1
            # done with backwards negation
            found_neg_bck = False

        # now move window
        if (unigram in NEG_ENDOFWINDOW) or (bigram in NEG_ENDOFWINDOW):
            # found end of negation, must reset window and negation state
            debug('End of negating window at %d, %s.' % (i, bigram))
            inwindow = 0
            found_neg_fwd = False
            winstart = i

        # Always reset pseudo
        found_pseudo = False

    return vNEG
