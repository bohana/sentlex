try:
    import stopwords
except Exception:
    from sentlex import stopwords
 
import unittest

#####
#
# Unit Testing for stopwords
#
####


#
# Runs unit testing if module is called directly
#
if __name__ == "__main__":
   
   class T_stop(unittest.TestCase):
       def runTest(self):
           stopc = stopwords.Stopword()

           self.assertTrue(len(stopc.worddict)>0, 'stop word list did not load')
           self.assertTrue(stopc.is_stop('and'), '"and" should be a stopword')

           self.assertFalse(stopc.is_stop('joseph'), 'non-stop word returned True')
           self.assertFalse(stopc.is_stop(''), 'non-stop word returned True')

   # Run those guys
   unittest.main()
           
   

