'''
sentlex.py - Lexicon Management Classes

This module implements class structure for sentment lexicons used elsewhere in SentimentAnalysis.
Sentiment lexicons encapsulate information from publicly available Lexicons from research literature in a common Pythonic interface.

What a Lexicon object does:
 - for a given term, return positive/negative/neutral sentiment info, based on underlying lexicon.
 - terms are divided into parts of speech (Adj/Verb/Noun/Adverb).
 - some capability for comparing lexicons.

TODO:
- niceties - inform user of NLTK and corpus requirements
'''

import re,os,sys
import nltk
from nltk.corpus import brown
import sentlexutil

  
#
# Lexicon super-class
#
class Lexicon(object):
  '''
    Lexicon class is a generic class holding in memory databases for a sentiment lexicon.
    A lexicon is defined by 4 dictionaries mapping terms to sentiment data in the form of tuples:

       A['word'] = [(id, 1, 0), (id, 0.5, 0) ... ]

    Where tuple values are (sense_id, positive, negative), extracted from a knowledge source for that particular word/POS
  '''
  def __init__(self):
      # Initialize class vars
      self.A={}
      self.V={}
      self.R={}
      self.N={}
      self.LexName = 'Superclass'
      self.LexFreq = None
      self.is_loaded = False
      self.is_compiled = False
      
      #  Baseline words used to QA a lexicon
      self.baselinewords = ['good', 'bad', 'pretty', 'awful', 'excellent',
                             'misfortune', 'incompetent', 'tough',
                             'inadequate', 'terrible', 'blue', 'closed']

  def _termdistro(self,A):
      '''
        Given a dictionary of terms associated with a part-of-speech A, 
        Calculates valence distribution inside the lexicon.
      '''  
      postotal = 0
      negtotal = 0
      neutral = 0
      for itemlist in A:
        for item in A[itemlist]:
          if ( item[1] > item[2]):
            postotal=postotal+1
          elif ( item[2] > item[1]):
            negtotal=negtotal+1
          else:
            neutral=neutral+1
      return (postotal,negtotal,neutral)
  
  def print_info(self):
      '''
        Print information about this lexicon. Does not work for dynamic/composite lexicons.
      '''
      print "Lexicon Sizes:"
      print " - Adjective (A): " + str(len(self.A))
      print " - Verb (V) : " + str(len(self.V))
      print " - Adverb (R) : " + str(len(self.R))
      print " - Noun (N) : " + str(len(self.N))
      print " "
      print "Score Distributions:"
      (postotal,negtotal,neutral) = self._termdistro(self.A)
      print " - Adjectives (A): POS=" + str(postotal) + " , NEG=" + str(negtotal) + " , NEUTRAL="+ str(neutral)
      (postotal,negtotal,neutral) = self._termdistro(self.V)
      print " - Verbs (V): POS=" + str(postotal) + " , NEG=" + str(negtotal) + " , NEUTRAL="+ str(neutral)
      (postotal,negtotal,neutral) = self._termdistro(self.R)
      print " - Adverbs (R): POS=" + str(postotal) + " , NEG=" + str(negtotal) + " , NEUTRAL="+ str(neutral)
      (postotal,negtotal,neutral) = self._termdistro(self.N)
      print " - Noun (N): POS=" + str(postotal) + " , NEG=" + str(negtotal) + " , NEUTRAL="+ str(neutral)

  def get_info(self):
      '''
        Like printinfo, but returns json for machine processing
      '''
      infod = {}
      infod['a'], infod['v'], infod['r'], infod['n'] = {},{},{},{}
      
      # sizes
      infod['a']['size'] = len(self.A)
      infod['v']['size'] = len(self.V)
      infod['r']['size'] = len(self.R)
      infod['n']['size'] = len(self.N)
      
      # distros
      infod['a']['pos'], infod['a']['neg'], infod['a']['neutral'] =  self._termdistro(self.A)
      infod['v']['pos'], infod['v']['neg'], infod['v']['neutral'] =  self._termdistro(self.V)
      infod['r']['pos'], infod['r']['neg'], infod['r']['neutral'] =  self._termdistro(self.R)
      infod['n']['pos'], infod['n']['neg'], infod['n']['neutral'] =  self._termdistro(self.N)
      
      return infod

 
  def hasnoun(self,term):
    '''
      Returns True/False to query whether term is present in dict
    '''
    return self.N.has_key(term)

  def hasverb(self,term):
    return self.V.has_key(term)
      
  def hasadverb(self,term):
    return self.R.has_key(term)

  def hasadjective(self,term):
    return self.A.has_key(term)

  def get_name(self):
    '''
      Returns name for this lexicon
    '''
    return self.LexName

  def set_name(self, newname):
    '''
      Sets lexicon name other than default
    '''
    self.LexName = newname

  def compare(self, L, pos):
    '''
      Compares current lexicon with "L" on "pos" part of speech ('a','v','n','r')
    '''
    def getsign(x):
       if x > 0.0:
           return 1
       elif x == 0.0:
           return 0
       else:
           return -1

    if pos == 'a':
      lComp = self.A
    elif pos == 'v':
      lComp = self.V
    elif pos == 'n':
      lComp = self.N
    elif pos == 'r':
      lComp = self.R

    # Intersection
    I = []
    for term in lComp:
      if (pos == 'a' and L.hasadjective(term))\
         or (pos == 'v' and L.hasverb(term))\
         or (pos == 'r' and L.hasadverb(term))\
         or (pos == 'n' and L.hasnoun(term)):
        I.append(term)

    print " POS = "+pos+". Intersection of " + self.LexName + " and " + L.getName() + " -> " + str(len(I))

    # % Agreement between lexicons - we consider terms in agreement if overall valence (positive-negative) is of same sign.
    agree = 0.0
    for term in I:
      if    (pos == 'a' and (getsign( L.getadjective(term)[0] - L.getadjective(term)[1]) == getsign( self.getadjective(term)[0] - self.getadjective(term)[1]))) \
         or (pos == 'v' and (getsign( L.getverb(term)[0] - L.getverb(term)[1]) == getsign( self.getverb(term)[0] - self.getverb(term)[1]))) \
         or (pos == 'r' and (getsign( L.getadverb(term)[0] - L.getadverb(term)[1]) == getsign( self.getadverb(term)[0] - self.getadverb(term)[1]))) \
         or (pos == 'n' and (getsign( L.getnoun(term)[0] - L.getnoun(term)[1]) == getsign( self.getnoun(term)[0] - self.getnoun(term)[1]))):
        agree = agree+1

    if I:
      print " POS = "+pos+". % Agreement on (" + self.LexName + ") Intersec. (" + L.getName() + ") -> " + str( agree / (len(I)+0.0) )
      return {'intersect':len(I), 'agree': agree / (len(I)+0.0)}


  def getbestvalues(self, key, A):
    '''
     Returns score from dictionary as a proportion of how many pos/neg scores are found.
     This is necessary when terms are associated with more than 1 sense, and no disambiguation is possible.
  
     - Returns tuple (pos,neg)
     - Tuple is (0,0) if key not found
  
    '''
    if not A.has_key(key):
        return (0,0)

    posval=0.0
    negval=0.0
    items=0
    foundpos = 0.0
    foundneg = 0.0
    # loop through all orientation synsets for this key
    for T in A[key]:
        posval += T[1]
        negval += T[2]
        items += 1
        if T[1] > T[2]:
            foundpos += 1.0
        if T[2] > T[1]:
            foundneg += 1.0
    if ((foundpos == 0) and (foundneg == 0)): 
        return (0,0)
    else:
        return ((foundpos/(foundpos+foundneg))*(posval/max(items,1)), (foundneg/(foundpos+foundneg))*(negval/max(items,1)))

  def compile_frequency(self):
      '''
        Generate corpus based frequency distribution for terms in this lexicon.
        We use NLTK's brown corpus of (potentially) opinionated articles as our source data.
      '''
      # Load corpus
      # Mar-14 - extending to entire brown corpus for better coverage
      BC = brown.words()

      # Build freq dist only for terms found in lexicon
      self.LexFreq = nltk.FreqDist([t.lower() for t in BC if (self.hasnoun(t) or self.hasverb(t) or self.hasadverb(t) or self.hasadjective(t))])
      self.is_compiled = True

  def get_freq(self, term):
      '''
        Retrieves term's *relative* frequency in relation to lexicon's most frequent term as obtained from Brown corpus data
      '''
      assert self.LexFreq, "Please initialize frequency distributions with compileFrequency()"
      return self.LexFreq.freq(term)/self.LexFreq.freq(self.LexFreq.max())
    
  def printstdterms(self):
      '''
        Print scores for a list of standard terms for QA, we use only adjectives for now.
      '''
      print self.getName()
      for adj in self.baselinewords:
          print " %s (%.2f,%.2f) " % (adj, self.getadjective(adj)[0], self.getadjective(adj)[1]),
      print '\n'
      

##
#
# Resource Lexicon
#
##
class ResourceLexicon(Lexicon):
    '''
     Sentiment lexicon based on an existing data source (resource)
     This lexicon obtains sentiment information via the load() method.
     A loader function that understands the underlying data format is passed as init argument.
     Word sentiment information uses getbestvalues() - an average of tuples (pos, neg) for all known senses of the word.

     Loader functions take the form: 

          f(pos, datafile)

     And return a dict mapping words to tuples of (pos,neg) pairs:

          D[word] = [ (p,n), (p,n) ... ]

     Representing all known (p,n) values for word in the given part of speech.
     Note that it is common for a word to map to more than a single sense, thus multiple data points are allowed.

     Sample loader functions for various knowledge resources can be found in the sentlexutil module.
    '''
    def __init__(self, name=None, loader=None):
        super(ResourceLexicon,self).__init__()
        if name: self.LexName = name
        if loader: self.f_loader=loader
    
    def load(self,datafile):
        '''
           Loads lexicon from file into dictionaries
        '''
        assert self.f_loader, 'This lexicon does not have an associated loader function.'

        self.A = self.f_loader('a',datafile)
        self.V = self.f_loader('v',datafile)
        self.R = self.f_loader('r',datafile)
        self.N = self.f_loader('n',datafile)
        self.compile_frequency()
        self.is_loaded = True
        return True

    def getadjective(self,term):
        '''
          Returns tuple (pos,neg) for sentiment scores for adjective. (0,0) if not found.
        '''
        return self.getbestvalues(term, self.A)

    def getadverb(self,term):
        '''
          Returns tuple (pos,neg) for sentiment scores for adverb. (0,0) if not found.
        '''
        return self.getbestvalues(term, self.R)

    def getverb(self,term):
        '''
          Returns tuple (pos,neg) for sentiment scores for verb. (0,0) if not found.
          Verb must be in canonical form.
        '''
        return self.getbestvalues(term, self.V)

    def getnoun(self,term):
        '''
          Returns tuple (pos,neg) for sentiment scores for noun. (0,0) if not found.
        '''
        return self.getbestvalues(term, self.N)


##
#
# Composite Lexicon
#
##
class CompositeLexicon(Lexicon):
  '''
    CompositeLexicon - a subclass of Lexicon, extracts sentiment from a series of lexicons organised hierarchically.
    Lexicons are added via addlexicon() call. To retrieve sentiment of a term, each added lexicon will be consulted
    per order of inclusion:
  
      .addLexicon(L1)
      .addLexicon(L2)
      .addLexicon(L3)

    means lexicon will be searched in order:

      L1 -> L2 -> L3

    this ensures if iformation about a word exists in L1, it will be used first. 
    Lexicons should be added from most accurate to least accurate.
 
  '''
  def __init__(self):
      super(CompositeLexicon,self).__init__()
      self.LexName = "Composite"
      self.LLIST=[]
      self.factor = 1.0

  def add_lexicon(self, L):
    self.LLIST.append(L)
    self.LexName += " " + L.getName()

  def set_factor(newval):
    '''
     updates confidence factor used when looking for values over the lexicon list
    '''
    self.factor = newval

  def _scan_lexlist_val(self, lexlist, term, f_checker, f_getter, notfound_val):
    '''
     Generic scanner, iterates lexicon list for term, using "checker" and "getter"
     functions to check presence and return specific value as needed.
     notfound_cal is returned if no lexicons contain term (as per checker func)
     At each iteration, confidence is decremeted by self.factor
    '''
    confidence_val=1.0 
    for L in lexlist:
        if getattr(L, f_checker)(term): 
            termval=getattr(L, f_getter)(term)
            # return found values for this term, times the lexicon confidence
            return (termval[0]*confidence_val, termval[1]*confidence_val)
        confidence_val *= self.factor
              
    return notfound_val 
            
  def _scan_lexlist_presence(self, lexlist, term, f_checker):
    '''
     Generic scanner, iterates lexicon list for term presence
    '''
    for L in lexlist:
        if getattr(L, f_checker)(term): 
            return True
    return False 
              
  
  def getnoun(self, term):
    return self._scan_lexlist_val(self.LLIST, term, "hasnoun", "getnoun", (0,0))  
      
  def getverb(self, term):
    return self._scan_lexlist_val(self.LLIST, term, "hasverb", "getverb", (0,0))
    
  def getadverb(self, term):
    return self._scan_lexlist_val(self.LLIST, term, "hasadverb", "getadverb", (0,0))
      
  def getadjective(self, term):
    return self._scan_lexlist_val(self.LLIST, term, "hasadjective", "getadjective", (0,0))
  
  def hasnoun(self, term):
    return self._scan_lexlist_presence(self.LLIST, term, "hasnoun") 
        
  def hasverb(self, term):
    return self._scan_lexlist_presence(self.LLIST, term, "hasverb")
    
  def hasadverb(self, term):
    return self._scan_lexlist_presence(self.LLIST, term, "hasadverb")
    
  def hasadjective(self, term):
    return self._scan_lexlist_presence(self.LLIST, term, "hasadjective")
    
 
##
# Lexicon SubClasses
#
# - Use the classes below to create lexicons from specific knowledge resources shipped with the package.
#
##
class MobyLexicon(ResourceLexicon):
    '''
      This lexicon uses the Moby thesaurus to build a sentiment lexicon by expansion of
      seeded words.
    
      More on the Moby project: http://en.wikipedia.org/wiki/Moby_Project
        
      Lexicon is first used as part of research in:
        
      Ohana, Bruno, Brendan Tierney, and S. Delany. "Domain Independent Sentiment Classification with Many Lexicons." 
      Advanced Information Networking and Applications (WAINA), 
      2011 IEEE Workshops of International Conference on. IEEE, 2011.
    '''

    def __init__(self):
        curpath = os.path.dirname(os.path.abspath(__file__))
        datapath = os.path.join(curpath, 'data/GB1_S.lex')
        super(MobyLexicon,self).__init__('Moby-GB', sentlexutil.readMoby)
        self.load(datapath)


class SWN3Lexicon(ResourceLexicon):
    '''
      Implements SWN3.0 lexicon as a class. SentiWordNet is available from:
      http://sentiwordnet.isti.cnr.it

      And is distributed with a CC-SA license:
      http://creativecommons.org/licenses/by-sa/3.0/

      See further details on file SentiWordNet_3.0.0.lex in the data directory.
    '''
    def __init__(self):
        curpath = os.path.dirname(os.path.abspath(__file__))
        datapath = os.path.join(curpath, 'data/SentiWordNet_3.0.0.lex')
        super(SWN3Lexicon,self).__init__('SWN3', sentlexutil.readSWN3)
        self.load(datapath)


##
#
# Experimental Stuff
#
##
class MorphLexicon(Lexicon):
  '''
   Derives term sentiment from morphological prefix/suffix information.
   
   This lexicon gives an answer dynamically - ie there is no underlyng knowledge
   resource other than the embedded prefix/suffic lists.
   
  '''
  def __init__(self):
    super(MorphLexicon,self).__init__()  
    self.LexName = 'Morph' 
    self.is_loaded=True

    # collected prefix info with high correlation to positive class
    self.POS_PREFIX = {
         4 : [ 'well', 'appr', 'comp', 'acco', 'admi', 'comm', 'prof' ],
         3 : [ 'com', 'ent', 'pro', 'res', 'acc' ],
         2 : [ 're', 'pr', 'ad', 'en' ]
    }

    self.NEG_PREFIX = {
         4 : [ 'diss', 'over', 'disp', 'disc', 'inco', 'desp', 'disa' ],
         3 : [ 'dis','ove','ine','mis','inc' ],
         2 : [ 'co','mi','in','de','di','un' ]
    }

    self.POS_SUFFIX = {
         4 : [ 'lity', 'ance' ],
         3 : [ 'ity', 'nce' ],
         2 : []
    }

    self.NEG_SUFFIX = {
         4 : [ 'able', 'ated', 'tive' ],
         3 : [ 'ted', 'ble', 'ent' ],
         2 : [ 'te', 'ed' ]
    }
    
  def load(self,datafile=None):
    self.is_loaded=True
    return True

  def _morph_score(self,term):
     '''
      Analyses prefix and sufix to determine sentiment.
      Rules to follow:
        - more descriptive prefix/suffix first (ie 4-letter, then 3-letter, ...)
        - prefix information first, then suffix
     '''

     # determines scoring based on pre/suffix len
     # the more descriptive the prefix, the higher the value (or confidence)
     SCORERULE = { 4 : 0.9, 
                   3 : 0.6, 
                   2 : 0.3 }

     for suflen in [4,3,2]:
         if len(term) >= suflen:
            termpre = term[:suflen]
            termsuf = term[-suflen:]

            # iterate over our known rules
            if termpre in self.POS_PREFIX[suflen]:
               return ( SCORERULE[suflen], 0.0 )

            if termpre in self.NEG_PREFIX[suflen]:
               return ( 0.0, SCORERULE[suflen] )

            if termsuf in self.POS_SUFFIX[suflen]:
               return ( SCORERULE[suflen], 0.0 )

            if termsuf in self.NEG_SUFFIX[suflen]:
               return ( 0.0, SCORERULE[suflen] )

     # found nothing
     return (0.0, 0.0)
 
  def getadjective(self,term):
     return self._morph_score(term)

  def getverb(self,term):
     return self._morph_score(term)

  def getnoun(self,term):
     return (0.0,0.0)

  def getadverb(self,term):
     return (0.0,0.0)

  def hasadjective(self,term):
     x = self._morph_score(term)
     if x == (0.0,0.0):
        return False
     else:
        return True

  def hasverb(self,term):
     x = self._morph_score(term)
     if x == (0.0,0.0):
        return False
     else:
        return True

  def hasadverb(self,term):
     return False

  def hasnoun(self,term):
     return False
