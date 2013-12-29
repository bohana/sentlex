'''

   Lexicon-Based Sentiment Analysis Library

   Performs sentiment classification on POS-tagged input
   documents with the assistance of sentiment lexicons.

'''

import re
import math
import os
import nltk.stem

# library imports
import sentlex
import negdetect
import stopwords
from docscoreutil import *

# Constants that drive scoring behavior
SCOREALL = 0
SCOREONCE = 1
SCOREONCEINPARAGRAPH = 2
SCOREWITHFREQ = 3
SCOREWITHSTOP = 4

# Load default stopwords
objectiveWords = stopwords.Stopword()

# Document score calculation
def docSentiScore(L, Doc, aflag, vflag, rflag, nflag, negflag, negwindow=5, 
                  w = lambda x,y,z:x, 
                  scoringmethod = SCOREALL):
    '''
     docSentiScore - Computes document sentiment score for POS-tagged Doc using sentiment lexicon L.
     The following mandatory flags specify which POS tags to take into account:
      - aflag
      - vflag
      - rflag (adverbs)
      - nflag
     In addition, negflag is a boolean indicating whether to use negation detection, with window scope negwindow.
     w(x,i,N) is a weight adjustment function based on word position within the document.
     scoringmethod is a list of non-exlcusive parameters used to switch on/off scoring features.

     Returns tuple (posscore, negscore, doc) containing final document scores and annotated document.
    '''

    # 0. Initialize
    tags = Doc.split()
    annotatedTags = []
    doclen = len(tags)
    i=0
    postotal=0
    negtotal=0
    notfoundcounter=0
    foundcounter=0
    negcount=0
 
    # Setup stem preprocessing for verbs
    wnl = nltk.stem.WordNetLemmatizer()
    
    # 1. Negation detection pre-processing - return an array w/ position of negated terms
    vNEG = negdetect.getNegationArray(tags, negwindow)

    #
    # 2. Scan for scores for each POS
    # After POS-tagging a term will appear as either term/POS or term_POS
    # We assume such weirdnesses will not naturally occur on plain text.
    #
    posindex=0
    negindex=1
    tagList = []
    for tagword in tags:
       i+=1
       scoretuple = (0,0)
       tagfound = False
       tagseparator = ''

       # Adjectives 
       if aflag==True and re.search('[_/](JJ|JJ.)$',tagword):
          tagfound=True
          tagseparator = tagword[ re.search('[_/](JJ|JJ.)$',tagword).start() ]
          thisterm = tagword.split( tagseparator )[0]
          scoretuple = L.getadjective( thisterm )

       # Verbs (VBP / VBD/ etc...)
       if vflag==True and re.search('[_/](VB|VB.)$',tagword) :
          tagfound=True
          tagseparator = tagword[ re.search('[_/](VB|VB.)$',tagword).start() ]
          thisterm = tagword.split( tagseparator )[0]
          thisterm = wnl.lemmatize(thisterm, pos='v')
          scoretuple = L.getverb( thisterm )
          
       # Adverbs
       if rflag==True and re.search('[_/]RB$',tagword) :
          tagfound=True
          tagseparator = tagword[ re.search('[_/]RB$',tagword).start() ]
          thisterm = tagword.split( tagseparator )[0]
          scoretuple = L.getadverb(thisterm)
          
       # Nouns
       if nflag==True and re.search('[_/]NN$',tagword) :
          tagfound=True
          tagseparator = tagword[ re.search('[_/]NN$',tagword).start() ]
          thisterm = tagword.split( tagseparator )[0]
          scoretuple = L.getnoun(thisterm)
          
       # Process negation detection
       if negflag==True:
            posindex=vNEG[i-1]
            negindex=(1+vNEG[i-1])%2

       #
       # Add to total with weight score
       #
       posval = 0.0
       negval = 0.0 
       if tagfound and \
          ( 
            (scoringmethod == SCOREALL) or 
            (scoringmethod == SCOREWITHFREQ) or 
            (scoringmethod == SCOREONCE and (not tagword in tagList)) or
            (scoringmethod == SCOREWITHSTOP and (not objectiveWords.is_stop(thisterm)) )
          ):

           if (scoringmethod in [ SCOREWITHFREQ, SCOREWITHSTOP ] ):
              # Scoring with frequency information
              # Frequency is a real valued at 0.0-1.0. We calculate sqrt function so that the value grows faster even for numbers close to 0 
              posval += w(scoretuple[posindex],i,doclen) * (1.0 - math.sqrt(L.getFreq( thisterm )) )
              negval += w(scoretuple[negindex],i,doclen) * (1.0 - math.sqrt(L.getFreq( thisterm )) )
              
           else:
              # Just plain scoring from lexicon - add
              posval += w(scoretuple[posindex],i,doclen)
              negval += w(scoretuple[negindex],i,doclen)
       
       postotal += posval
       negtotal += negval

       # Found a tag - increase counters and add tag to list
       if tagfound:
           tagList.append( tagword )
           foundcounter += 1.0
           if negflag==True and vNEG[i-1]==1:
              negcount += 1
           if scoretuple == (0,0):
              notfoundcounter += 1.0
       
       # add this tag back to annotated version
       if tagfound:
          if negflag: 
             negtag = str(vNEG[i-1])
          else:
             negtag = 'NONEG'
          annotatedTags.append( tagword + '##NEGAT:' + negtag + '##POS:' + str(posval) + '##NEG:' + str(negval) )
       else:
          annotatedTags.append( tagword )

    # Completed scan

    # Add negated words to negative score (Potts 2011)
    # alpha is a scaling factor based on how much of the document has been negated
    if foundcounter > 0.0:
       alpha = (negcount)/(foundcounter)
    else:
       alpha = 0.0
    ##negtotal += negcount * ( 0.5 * (1 - alpha) )
    #negtotal += negcount * 0.3 

    if (foundcounter - notfoundcounter) > 0.0:
       # resulting scores are the normalized proportions of all *scored* terms (ignoring neutrals/unknowns)
       resultpos =  float(postotal)/(foundcounter - notfoundcounter )
       resultneg =  float(negtotal)/(foundcounter - notfoundcounter )
    else:
       resultpos = 0.0
       resultneg = 0.0
 
    return (resultpos, resultneg, ' '.join(annotatedTags))
