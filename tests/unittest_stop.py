from __future__ import absolute_import
try:
    import stopwords
except Exception:
    from sentlex import stopwords

import unittest


class TestStop(unittest.TestCase):
    def runTest(self):
        stopc = stopwords.Stopword()

        self.assertTrue(len(stopc.worddict) > 0, 'stop word list did not load')
        self.assertTrue(stopc.is_stop('and'), '"and" should be a stopword')

        self.assertFalse(stopc.is_stop('joseph'), 'non-stop word returned True')
        self.assertFalse(stopc.is_stop(''), 'non-stop word returned True')
