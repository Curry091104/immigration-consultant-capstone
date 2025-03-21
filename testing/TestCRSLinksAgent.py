import unittest
import os
import sys

# Get the parent directory of backend
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add it to sys.path
sys.path.append(parent_dir)

from backend.controllers.agents.crs_links_agent import CRSLinksAgent

class TestCRSLinksAgent(unittest.TestCase):

    def setUp(self):
        self.agent = CRSLinksAgent()

    def test_get_recommendations_score(self):
        user_input = "How to calculate CRS score points?"
        expected_recommendation = {'CRS Calculator': 'https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/check-score.html'}
        self.assertDictEqual(self.agent.get_recommendations(user_input), expected_recommendation)

    def test_get_recommendations_criteria(self):
        user_input = "How can I find the CRS Criteria?"
        expected_recommendation = {'CRS Criteria': 'https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/check-score/crs-criteria.html'}
        self.assertDictEqual(self.agent.get_recommendations(user_input), expected_recommendation)

    def test_get_recommendations_improvement(self):
        user_input = "How can I improve my score?"
        expected_recommendation = {'CRS Score Improvement': 'https://www.canadim.com/blog/how-to-increase-crs-score/'}
        self.assertDictEqual(self.agent.get_recommendations(user_input), expected_recommendation)
        
    def test_get_recommendations_entry_score(self):
        user_input = "calculate express entry score"
        expected_recommendation = {
            'CRS Calculator': 'https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/check-score.html'
        }
        self.assertDictEqual(self.agent.get_recommendations(user_input), expected_recommendation)
        
    def test_get_recommendations_empty_string(self):
        user_input = ""
        
        with self.assertRaises(ValueError):
            self.agent.get_recommendations(user_input)
        
if __name__ == '__main__':
    unittest.main(exit=False)