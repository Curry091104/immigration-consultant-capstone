import unittest
import sys
import os

# Get the parent directory of backend
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add it to sys.path
sys.path.append(parent_dir)

from backend.controllers.agents.conversation_agent import ConversationAgent

class TestConversationAgent(unittest.TestCase):

    def setUp(self):
        """
        Initialize the ConversationAgent before each test.
        """
        self.agent = ConversationAgent()


    def test_classify_inquiry_for_decision_unexpected_response(self):
        """
        Test if the function handles unexpected input correctly.
        """
        user_input = "How to bake a cake?"
        expected_category = "none"  # Should not be classified as decision_agent

        category, revised_inquiry = self.agent.classify_inquiry_for_decision(user_input)

        self.assertEqual(category.lower(), expected_category)
   

    def test_classify_inquiry_for_confusing_questions(self):
        """
        Test if a confusing question similar to questions relating to study permit is classified as 'none'.
        """
        user_input = "In australia, How to apply for student permit if i am from Canada"
        expected_category = "none"

        category, revised_inquiry = self.agent.classify_inquiry_for_decision(user_input)

        self.assertEqual(category.lower(), expected_category)
    
    def test_classify_multiple_inquiry(self):
        """
        Test if a multiple questions can be classifies  as 'none' if one of the question is unrelated to imigrarion.
        """
        user_input = "who is donald trump and  How to calculate my crs score?"
        
        expected_category = "none"

        category, revised_inquiry = self.agent.classify_inquiry_for_decision(user_input)

        self.assertEqual(category.lower(), expected_category)
        
    

if __name__ == "__main__":
    import unittest
    unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(__import__("conversation_agent_test")))
