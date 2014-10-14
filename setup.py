'''
  setup.py for sentlex
'''
from distutils.core import setup

setup(
    name='SentLex',
    version='0.1.5dev',
    author='Bruno Ohana',
    author_email='bohana@gmail.com',
    packages=['sentlex', 'sentlex.tests'],
    package_data={'sentlex': ['data/*.dat', 'data/*.lex', 'data/*.txt']},
    scripts=['bin/sentutil'],
    url='https://github.com/bohana/sentlex',
    license='MIT',
    description='Tools and library for lexicon-based sentiment analysis.',
    long_description=open('README.md').read(),
    install_requires=[
        "nltk >= 2.0.4"
    ],
)
