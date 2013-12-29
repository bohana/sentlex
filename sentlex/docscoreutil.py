'''

   docscore-util - Lexicon-Based Sentiment Analysis Library

   Utility methods for lexicon based sentiment analysis

'''

import sentlex
import re
import math
import os
import negdetect
import stopwords

# Score adjustment functions

def scoreSimple(score, position, totaltags):
    '''
     simple - returns original score
    '''
    return score

# Returns adjusted score based on linear function of word distance to end of document
def scoreAdjLinear(score, position, totaltags):
    '''
     Linear adjustment - adjusts a given numeric score linearly, based on its position in the document.
    '''
    C = 1.0
    return (score * (position * C) / totaltags)

# Returns 50% of score value if the term is found at 1st half of document
def scoreAdjModular(score, position, totaltags):
    '''
      Returns 50% of score if the term is found at 1st half of document.
      Returns original value if term found at 2nd half of document.
    ''' 
    if (position) >= (totaltags/2.0):
        return score
    else:
        return (score + 0.0) / 2.0


# Voting schemes

def majorityVote(resultList, shift, threshold):
    '''
      Given a list of tuples (posscore, negscore) determine pos/neg sentiment by majority voting.
      Works best with odd number of classifiers!
      Each classifier gives 1 vote for either pos/neg class.
      Returns prediction result in form (pos,neg,posscore,negscore)
    '''

    posvotes = 0
    negvotes = 0
    for L in resultList:
        totalpos = L[0]
        totalneg = L[1]
        if (totalneg - shift) - totalpos > threshold:
           # predicted a negative
           negvotes += 1
        else:
           if totalpos - (totalneg - shift) >= threshold:
               posvotes += 1
    scores = (posvotes / len(resultList) + 0.0, negvotes / len(resultList) + 0.0)
    if negvotes > posvotes:
        return (0, 1) + scores
    elif posvotes > negvotes:
        return (1, 0) + scores
    else:
        return (0, 0) + scores


def sumVote(resultList, shift, threshold):
   """
     Given a list of predition result tuples (posscore, negscore) determines overall sentiment by
     the sum of scores from each classifier decision score (valued [0,1]).
     Returns tuple (posflag, negflag, posscore, negscore)
   """
   postotal = 0.0
   negtotal = 0.0
   lenf = float(len(resultList))

   for L in resultList:
      pos = L[0]
      neg = L[1]
      postotal += pos
      negtotal += neg

   if postotal - (negtotal - shift) >= threshold:
      return (1, 0, postotal/lenf, negtotal/lenf)
   else:
      return (0, 1, postotal/lenf, negtotal/lenf)


def maxVote(resultList, shift, threshold):
  """
    Given a list of prediction result tuples (pos, neg, hitratio) determine overall sentiment based on maximum
    value obtained in either class on across all predictions.
  """
  maxp = max ([x[0] for x in resultList])
  maxn = max ([x[1] for x in resultList])

  if maxp - (maxn - shift) >= threshold:
    return (1,0, maxp, maxn)
  else:
    return (0,1, maxp, maxn)

