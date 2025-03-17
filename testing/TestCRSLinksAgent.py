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
        print(f"xxxx: {self.agent.get_recommendations(user_input)}")
        self.assertEqual(self.agent.get_recommendations(user_input), expected_recommendation)

    def test_get_recommendations_profile(self):
        user_input = "How can I calculate my CRS score based on my specific qualifications and situation?"
        expected_recommendation = {'CRS Criteria': 'https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/check-score/crs-criteria.html'}
        self.assertEqual(self.agent.get_recommendations(user_input), expected_recommendation)

    def test_get_recommendations_invitation(self):
        user_input = "How can I improve my score?"
        expected_recommendation = {'CRS Score Improvement': 'https://www.canadim.com/blog/how-to-increase-crs-score/'}
        self.assertEqual(self.agent.get_recommendations(user_input), expected_recommendation)

    def test_get_recommendations_multiple_matches(self):
        user_input = "calculate express entry score"
        expected_recommendation = {
            'CRS Calculator': 'https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/check-score.html'
        }
        self.assertEqual(self.agent.get_recommendations(user_input), expected_recommendation)

if __name__ == '__main__':
    unittest.main(exit=False)