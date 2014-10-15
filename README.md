sentlex
=======

Sentlex is a python library for performing lexicon based sentiment analysis. It currently ships:
- A lexicon class library with implementations for a home grown sentiment lexicon, and [SentiWordNet v3.0](http://sentiwordnet.isti.cnr.it/)
- A sentiment classifier class library with various algorithm implementations, including a negation detection algorithm.


## Getting Started
```python
In [1]: import sentlex
 
In [2]: import sentlex.sentanalysis
 
In [3]: input_text='''we had a great time at the tirreno hotel, very friendly and helpful, nothing was ever too much trouble. 
the rooms were in excellent condition, very clean and comfortable.'''
 
In [4]: SWN = sentlex.SWN3Lexicon()
 
In [5]: classifier = sentlex.sentanalysis.BasicDocSentiScore()
 
In [6]: classifier.classify_document(input_text, tagged=False, L=SWN, a=True, v=True, n=False, r=False, negation=False, verbose=False)
Out[6]: (1.1118254346272922, 0.16043343653250774)
 
In [7]: classifier.resultdata
Out[7]:
{'annotated_doc': 'we/PRP had/VBD##NEGAT:NONEG##POS:0.00986842105263##NEG:0.0263157894737 a/DT great/JJ##NEGAT:NONEG##POS:0.3125##NEG:0.0 time/NN at/IN the/DT tirreno/NN hotel/NN ,/, very/RB friendly/RB and/CC helpful/JJ##NEGAT:NONEG##POS:0.25##NEG:0.0 ,/, nothing/NN was/VBD##NEGAT:NONEG##POS:0.0288461538462##NEG:0.0 ever/RB too/RB much/RB trouble./NNP the/DT rooms/NNS were/VBD##NEGAT:NONEG##POS:0.0288461538462##NEG:0.0 in/IN excellent/NN condition/NN ,/, very/RB clean/JJ##NEGAT:NONEG##POS:0.286764705882##NEG:0.0441176470588 and/CC comfortable/JJ##NEGAT:NONEG##POS:0.195##NEG:0.09 ./.',
 'doc': 'we had a great time at the tirreno hotel, very friendly and helpful, nothing was ever too much trouble. the rooms were in excellent condition, very clean and comfortable.',
 'found_list': ['had/VBD',
  'great/JJ',
  'helpful/JJ',
  'was/VBD',
  'were/VBD',
  'clean/JJ',
  'comfortable/JJ'],
 'resultneg': 0.16043343653250774,
 'resultpos': 1.1118254346272922,
 'tokens_found': 7,
 'tokens_negated': 0,
 'unscored_list': []}
 ```
 
## Sentiment Lexicons
```python
In [1]: import sentlex
 
In [2]: SWN = sentlex.SWN3Lexicon()
 
In [3]: SWN.getadjective('good')
Out[3]: (0.6190476190476191, 0.0)
 
In [4]: SWN.getverb('amuse')
Out[4]: (0.75, 0.0)
 
In [5]: SWN.getadjective('terrible')
Out[5]: (0.0, 0.65625)
```

##SentiWordNet v3.0
This library ships the [SentiWordNet v3.0](http://sentiwordnet.isti.cnr.it/), distributed under [Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0) license.](http://creativecommons.org/licenses/by-sa/3.0/). 
