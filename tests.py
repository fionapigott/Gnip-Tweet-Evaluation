import unittest
import json

import insights


class InputTestCase(unittest.TestCase):
    def setUp(self):
        # test_tweets.json contains 100 lines of JSON-formatted tweet data
        self.generator = open('test_tweets.json')  

    def test(self):
        self.assertEqual(len([_ for _ in self.generator]),100)

class TweetTestCase(unittest.TestCase):
    def setUp(self):
        # get first tweet
        self.tweet = open('test_tweets.json').next()
        # first tweet has the following distribution of counts of top words:
        self.body_term_counts = [2,1,1,1,1,1,1,1,1,1,1,1]
        self.bio_term_counts = [2,1] 
    
class AnalyzeConvoTweetTestCase(TweetTestCase):
    def test(self):
        conversation_results = {"unique_id": "TEST"}
        insights.run_full_tweet_input([self.tweet], conversation_results, None)
        
        self.assertEqual(self.body_term_counts,[item[0] for item in conversation_results['body_term_count'].get_tokens()] ) 

class AnalyzeAudienceTweetTestCase(TweetTestCase):
    def test(self):
        audience_results = {"unique_id": "TEST"}
        insights.run_full_tweet_input([self.tweet], None, audience_results) 
        
        self.assertEqual(self.bio_term_counts,[item[0] for item in audience_results['bio_term_count'].get_tokens()] ) 

if __name__ == '__main__':
    unittest.main()
