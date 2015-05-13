'''

   Lexicon-Based Sentiment Analysis Library

   sentanalysis_inst.py - an instance based classifier selector based on performance data from a training set

'''

# library imports
import sentlex
from sentanalysis import BasicDocSentiScore

import pandas as pd
import numpy as np
import nltk
from collections import Counter

class InstSentiScore(BasicDocSentiScore):
    '''
     Subclass of BasicDocSentiScore implementing score "shifts" for negated terms
     and a backoff mechanism for counting repeated terms.
    '''
    def __init__(self, k=3, metric='found_ratio'):
        super(InstSentiScore, self).__init__()
        self.classifiers = {}
        self.models = {}
        self.K = int(k)
        self.metric = metric
        self.best_avg_model = None
        self.cl_counter = Counter()

    def add_classifier(self, key, classifier):
        self.classifiers[key] = classifier

    def _recompute(self):
        '''
         Discover which model has best average performance - this is a tie-breaker for selecting model in the absence of data
        '''
        best_so_far = 0.0
        for m in self.models:
            avgperf = self.models[m]['performance'].mean()
            if avgperf > best_so_far:
                best_so_far = avgperf
                self.best_avg_model = m 

    def add_training_data(self, key, data):
        '''
          For a classifier name given by key, add data to the model.
          Data is a list of examples in the form (param_val, success)
        '''
        assert key in self.classifiers, 'Unrecognized classifier %s ' % key
        
        self.models[key] = pd.DataFrame(data, columns = [self.metric, 'performance'])
        self._recompute()

    def classify_document(self, Doc, tagged=True, verbose=False, annotations=False, **kwargs):
        '''
         Classify document by selecting most promising result according to training data
        '''
        if not tagged:
            tokens = len(nltk.word_tokenize(Doc))
        else:
            tagsep = self._detect_tag(Doc)
            tokens = len(nltk.word_tokenize(' '.join([x.split(tagsep)[0] for x in Doc.split()])))

        cl_res = {}
        # compute found ratio for all known classifiers
        for cl in self.classifiers:
            self.classifiers[cl].set_parameters(**kwargs)
            res = self.classifiers[cl].classify_document(Doc, tagged, verbose, annotations)
            tokens_found = float(self.classifiers[cl].resultdata['tokens_found'])
            cl_res[cl] = {'res': res,
                          'tokens_found': tokens_found,
                          'found_ratio': tokens_found / tokens}

            cl_res[cl]['performance'] = self._get_classifier_performance(cl, cl_res[cl]['found_ratio'])

        # best classifier has the best expected performance based on found ratio on training data
        chosen = max([(cl_res[c]['performance'], c) for c in cl_res], key=lambda x:x[0])
        best_cl = chosen[1]
        self.resultdata = self.classifiers[best_cl].resultdata
        self.cl_counter.update([best_cl])
        return cl_res[best_cl]['res']

    def _get_classifier_performance(self, cl, m_val):
        metric = self.metric
        # normalize k for a ratio
        k = float(self.K)/100.0
        mintk = max(0, m_val - k)
        pd_neighbors = self.models[cl][self.models[cl][metric] >= mintk][self.models[cl][metric] <= (m_val + k)]['performance']
        return pd_neighbors.mean()
