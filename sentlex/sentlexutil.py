'''
sentlex-util.py - Lexicon Management Classes

Utility functions used by main Lexicon objects.

'''

import re,os,sys

##
#
# Reader Functions
#
# - Note there are reader functions to other resources here - these are not shipped with the package.
#   (you will have to source those yourself from the appropriate research teams)
#
##

def readSWN(postag, datafile=None):
    '''
      Reads SWN database into a dictionary 

       - postag: POS array being created: 'a', 'v', 'n', 'r'
       - Return value is a dictionary object where:
       - each entry is a array of 1+ tuples corresponding to all synsets of a given term for a given pos
       - the tuple itself contains the SWN offset, positive value and negative value

    '''
    A={}	
    SWNf=open(datafile,'r',1024000)
    # Loop through every line in SWN file
    for line in SWNf:
        # Tokenize line.
        entry = line.split()
        synset_type=entry[0]
        # synset_data is a tuple (offset, posval, negval)
        synset_data=( entry[1], float(entry[2]), float(entry[3]) )
        # now add this entry to the correct list
        if synset_type==postag:
	    # here we extract all terms with this polarity
            for k in entry[4:]:
                key=k.split('#')[0]
                if not A.has_key(key):
                    A[key]=[]
		A[key].append(synset_data)
    return A


def readSWN3(postag, datafile=None):
    '''
      Reads SWN 3.0 database into a dictionary 

       - postag: POS array being created: 'a', 'v', 'n', 'r'
       - Return value is a dictionary object where:
       - each entry is a array of 1+ tuples corresponding to all synsets of a given term for a given pos
       - the tuple itself contains the SWN offset, positive value and negative value

    '''
    A={}	
    SWNf=open(datafile)
    # Loop through every line in SWN file
    for line in SWNf:
        # Tokenize line. Lines take the form:
        # # POS   ID        PosScore NegScore SynsetTerms   Gloss
        # a       00001740  0.125    0        able#1        (usually followed by `to') ...
        # a       00002098  0        0.75     unable#1      (usually followed by `to') not having ... 
        entry = line.split()
        if entry[0] == '#':
           continue # skip line w/ comment

        synset_type=entry[0]
        # synset_data is a tuple (offset, posval, negval)
        synset_data=(entry[1], float(entry[2]), float(entry[3]))
        # now add this entry to the correct list
        if synset_type==postag:
	    # here we extract all terms with this polarity
            for k in [token.split('#')[0] for token in entry[4:] if '#' in token]:
                if not A.has_key(k):
                    A[k]=[]
		A[k].append(synset_data)
    return A

def readSubjectivityClues(postag, datafile=None):
  '''
    Reads Wiebe's subjectivity clues into a dictionary

    Typical line read from file:
    type=weaksubj len=1 word1=wrestle pos1=verb stemmed1=y priorpolarity=negative
  '''
  A={}
  
  if datafile == None:
    return None

  if postag == 'a':
    posname='adj'
  elif postag == 'v':
    posname='verb'
  elif postag == 'n':
    posname='noun'
  else:
    posname='anypos'

  Wfile=open(datafile,'r',1024000)
  
  for line in Wfile:
    # Tokenize a line
    entry = line.split()

    posval=0
    negval=0

    pos_type=entry[3].split('=')[1]
    polarity=entry[5].split('=')[1]
    term=entry[2].split('=')[1]

    if polarity == 'negative':
      posval=0
      negval=1
    elif polarity == 'positive':
      posval=1
      negval=0

    if (pos_type == posname or pos_type == 'anypos') and polarity <> 'neutral':
       # Add entry if polarity is non neutral
       if not A.has_key(term):
          A[term]=[]
       # Append a tuple (term, pos val, neg val)   
       A[term].append((term,posval,negval))
  return A
  
  
def readMoby(postag, datafile=None):
    """
      Reads POS tag from a Mobi-derived sentiment lexicon. Returns dictionary of items
    """
    A={}
    if datafile == None:
       return None
	
    f=open(datafile,'r',1024000)
	
    # Loop through every line in SWN file
    for line in f:
        # Tokenize line.
        entry = line.split(',')
        term=entry[0]
        term_type=entry[1]
        # now add this entry to the correct list
        if term_type==postag.upper():
	    if not A.has_key(term):
              A[term]=[]
                # Add a tuple (term, pos, neg)    
	    A[term].append( ( term, float(entry[2]), float(entry[3]) ) )
    return A


def readGI(postag, datafile=None):
    """
      Reads term information from General Enquirer database. Returns dictionary of items
    """
    A={}
    if not datafile: return None
    f=open(datafile,'r',1024000)
	
    # Loop through every line in SWN file
    for line in f:
        # Tokenize line.
        entry = line.split(',')
        term=entry[0].split('#')[0].lower()   # Disregard term info past # sign
        term_type=entry[3][0]                 # POS is on first char - disregard other info
        term_pos=entry[1]
        term_neg=entry[2]
        
        # now add this entry to the correct list
        if term_type==postag:
	    if not A.has_key(term):
              A[term]=[]
            # Add a tuple (term, pos, neg)
            # - assumes there are no entries with both Positiv or Negativ, but accepts multiple entries for same term in whatever combination   
	    if term_pos.upper()=='POSITIV':
	      A[term].append((term, 1, 0)) 
	    elif term_neg.upper()=='NEGATIV':
              A[term].append((term, 0, 1))
            else:
              A[term].append((term, 0, 0))
	
    return A


def readUIC(postag, datafile=None):
    '''
     Reads UIC lexicon words for a given part of speech. This lexicon is based on http://www.cs.uic.edu/~liub/FBS/sentiment-analysis.html
    '''
    A={}
    if not datafile: return None
    f = open(datafile,'r')
    for line in f:
        # get tokens
        # input file is in format: 
        #  [pos|neg],word,pos
        items = line.replace('\n','').split(',')
        termpos = items[2]
        valence = items[0]
        word = items[1]
        if termpos==postag:
            if not word in A:
                A[word] = []
            if valence=='pos':
                A[word].append((word, 1, 0))
            else:
                A[word].append((word, 0, 1))
    return A
