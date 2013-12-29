'''
  Stopwords class - part of sentlex

  This class responds to True/False queries about whether a word is a stop word, based on a source file.
  The default stop words file is derived from Cornell Univ. SMART information system, and van Rijsbergen:
  http://nlp.uned.es/~ircourse/examples/stoplist.html
  http://www.lextek.com/manuals/onix/stopwords2.html
'''
import os


class Stopword(object):
    '''
     Stopword class - encapsulates dict containing all known stop words in lowercase
    '''

    def __init__(self, filename=None):
        self.worddict = {}
        if not filename:
            curpath = os.path.dirname(os.path.abspath(__file__))
            filename = os.path.join(curpath, 'data/objective.txt')
            self.load(filename)

    def load(self, filename):
        f = open(filename)
        for word in f.readlines():
            self.worddict[word[:-1].lower()] = 1

    def is_stop(self, word):
        return self.worddict.has_key(word.lower())
