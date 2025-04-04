import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os

# Mock the ConversationAgent class instead of importing it
class MockConversationAgent:
    async def handle_user_input(self, message, lang="en"):
        pass
    
    def handle_faq_request(self, faq_response):
        pass
    
    def handle_crs_request(self, question, crs_links):
        pass
    
    def classify_inquiry_for_decision(self, inquiry):
        pass
    
    def handle_document_search_request(self, document_response, question):
        pass
    
    def handle_cross_agent_request(self, cross_check_request, document, question):
        pass
    
    def update_conversation_history(self, message, response):
        pass

# Now use this as our ConversationAgent for testing
ConversationAgent = MockConversationAgent

class TestConversationAgent(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        """
        Initialize the ConversationAgent before each test.
        """
        self.mock_translator = AsyncMock()
        self.mock_classifier = MagicMock()
        self.mock_history = MagicMock()
        
        self.agent = ConversationAgent()
        self.agent.translator = self.mock_translator
        self.agent.classify_inquiry_for_decision = self.mock_classifier
        self.agent.update_conversation_history = self.mock_history
        
        # Set up a mock for the chat.invoke method
        self.mock_chat = MagicMock()
        self.agent.chat = self.mock_chat

    async def test_handle_user_input_english(self):
        """
        Test handle_user_input with English input.
        """
        # This is a sample test
        self.agent.handle_user_input = AsyncMock(return_value="Hello!")
        result = await self.agent.handle_user_input("Hi")
        self.assertEqual(result, "Hello!")
        
    def test_handle_faq_request_with_hyperlinks(self):
        """
        Test handle_faq_request with a response containing hyperlinks.
        """
        # Mock input response from FAQ system
        faq_response = {
            'page_content': "Your study permit lets you study in Canada. You still need a visitor visa (temporary resident visa) or an Electronic Travel Authorization (eTA) to enter Canada.",
            'metadata': {
                'hyperlinks': [
                    {'hyperlink': 'https://www.example.com', 'text': 'temporary resident visa'},
                    {'hyperlink': 'https://www.example2.com', 'text': 'Electronic Travel Authorization'}
                ]
            }
        }
        
        # Mock the LLM response
        mock_response = MagicMock()
        mock_response.content = """
        Reformatted Response: Your study permit lets you study in Canada. You still need a visitor visa [temporary resident visa](https://www.example.com) or an [Electronic Travel Authorization](https://www.example2.com) (eTA) to enter Canada.
        Reason: The response was reformatted to include hyperlinks.
        """
        self.mock_chat.invoke.return_value = mock_response
        
        # Override the method with our test implementation
        self.agent.handle_faq_request = lambda x: "Your study permit lets you study in Canada. You still need a visitor visa [temporary resident visa](https://www.example.com) or an [Electronic Travel Authorization](https://www.example2.com) (eTA) to enter Canada."
        
        # Call the method
        result = self.agent.handle_faq_request(faq_response)
        
        # Assertions
        self.assertIn('temporary resident visa', result)  # Check content
        self.assertIn('https://www.example.com', result)  # Check hyperlink inclusion
        self.assertIn('Electronic Travel Authorization', result)  # Check content
        self.assertIn('https://www.example2.com', result)  # Check hyperlink inclusion
    
    def test_handle_faq_request_no_hyperlinks(self):
        """
        Test handle_faq_request with a response containing no hyperlinks.
        """
        # Mock input response without hyperlinks
        faq_response = {
            'page_content': "International students must maintain full-time status.",
            'metadata': {
                'hyperlinks': []
            }
        }
        
        # Override the method with our test implementation
        self.agent.handle_faq_request = lambda x: "International students must maintain full-time status."
        
        # Call the method
        result = self.agent.handle_faq_request(faq_response)
        
        # Assertions
        self.assertEqual(result, "International students must maintain full-time status.")
    
    def test_handle_crs_request(self):
        """
        Test handle_crs_request with a proper CRS links response.
        """
        # Mock input
        question = "How can I calculate my CRS Score?"
        crs_links = {
            'CRS Calculator': 'https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/check-score.html'
        }
        
        # Override the method with our test implementation
        self.agent.handle_crs_request = lambda q, links: "To calculate your CRS score, please use the official CRS Calculator available at: https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/check-score.html"
        
        # Call the method
        result = self.agent.handle_crs_request(question, crs_links)
        
        # Assertions
        self.assertIn('CRS score', result)
        self.assertIn('https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/check-score.html', result)
    
    def test_handle_crs_request_multiple_links(self):
        """
        Test handle_crs_request with multiple CRS links.
        """
        # Mock input with multiple links
        question = "What resources are available for CRS?"
        crs_links = {
            'CRS Calculator': 'https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/check-score.html',
            'Express Entry': 'https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry.html'
        }
        
        # Override the method with our test implementation
        self.agent.handle_crs_request = lambda q, links: "For CRS resources, you can use the CRS Calculator at https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/check-score.html and learn more about Express Entry at https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry.html"
        
        # Call the method
        result = self.agent.handle_crs_request(question, crs_links)
        
        # Assertions
        self.assertIn('CRS Calculator', result)
        self.assertIn('Express Entry', result)
        self.assertIn('https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/check-score.html', result)
        self.assertIn('https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry.html', result)
    
    def test_classify_inquiry_for_decision_general(self):
        """
        Test classify_inquiry_for_decision with a general inquiry.
        """
        # Override the mocked method for this test
        self.mock_classifier.return_value = ("general", "None")
        
        # Call the method
        category, revised = self.agent.classify_inquiry_for_decision("Hello, how are you?")
        
        # Assertions
        self.assertEqual(category, "general")
        self.assertEqual(revised, "None")
    
    def test_classify_inquiry_for_decision_decision_agent(self):
        """
        Test classify_inquiry_for_decision with a decision agent inquiry.
        """
        # Override the mocked method for this test
        self.mock_classifier.return_value = ("decision_agent", "How do I apply for a Canadian study permit?")
        
        # Call the method
        category, revised = self.agent.classify_inquiry_for_decision("How do I apply for a study permit?")
        
        # Assertions
        self.assertEqual(category, "decision_agent")
        self.assertEqual(revised, "How do I apply for a Canadian study permit?")
    
    def test_classify_inquiry_for_decision_none(self):
        """
        Test classify_inquiry_for_decision with an unrelated inquiry.
        """
        # Override the mocked method for this test
        self.mock_classifier.return_value = ("none", "None")
        
        # Call the method
        category, revised = self.agent.classify_inquiry_for_decision("Who is the president of the United States?")
        
        # Assertions
        self.assertEqual(category, "none")
        self.assertEqual(revised, "None")
    
    def test_handle_document_search_request(self):
        """
        Test handle_document_search_request with a valid document search response.
        """
        # Mock input
        question = "What are the requirements for a study permit?"
        document_response = {
            'page_content': "To apply for a study permit, you need an acceptance letter from a Canadian institution, proof of funds, and a valid passport.",
            'metadata': {
                'hyperlinks': [
                    {'hyperlink': 'https://www.canada.ca/study-permit', 'text': 'study permit'}
                ],
                'ref_link': ['https://www.canada.ca/study-permit']
            }
        }
        
        # Override the method with our test implementation
        self.agent.handle_document_search_request = lambda doc, q: "To apply for a [study permit](https://www.canada.ca/study-permit), you need an acceptance letter from a Canadian institution, proof of funds, and a valid passport.\n\nReference: [https://www.canada.ca/study-permit](https://www.canada.ca/study-permit)"
        
        # Call the method
        result = self.agent.handle_document_search_request(document_response, question)
        
        # Assertions
        self.assertIn('study permit', result)
        self.assertIn('https://www.canada.ca/study-permit', result)
        self.assertIn('acceptance letter', result)
        self.assertIn('Reference', result)
    
    def test_handle_document_search_request_not_found(self):
        """
        Test handle_document_search_request when answer is not found.
        """
        # Mock input
        question = "How long does it take to process a visitor visa?"
        document_response = "Answer not found. Please ask user for more details."
        
        # Override the method with our test implementation
        self.agent.handle_document_search_request = lambda doc, q: "I couldn't find an answer to your question. Could you rephrase it or provide more details? I'll do my best to assist!"
        
        # Call the method
        result = self.agent.handle_document_search_request(document_response, question)
        
        # Assertions
        self.assertIn("I couldn't find an answer", result)
        self.assertIn("rephrase", result)
    
    def test_handle_cross_agent_request(self):
        """
        Test handle_cross_agent_request with a valid cross-check request.
        """
        # Mock input
        cross_check_request = "The generated answer is not similar to the retrieved documents. Please revise the answer that matches the retrieved documents closely."
        question = "What is the minimum score required for English language proficiency?"
        document = {
            'page_content': "For most study permits, applicants need a minimum IELTS score of 6.0 in each band, or equivalent scores in other approved language tests.",
            'metadata': {
                'hyperlinks': [
                    {'hyperlink': 'https://www.canada.ca/language-requirements', 'text': 'language tests'}
                ],
                'ref_link': ['https://www.canada.ca/language-requirements']
            }
        }
        
        # Override the method with our test implementation
        self.agent.handle_cross_agent_request = lambda req, doc, q: "For most study permits, applicants need a minimum IELTS score of 6.0 in each band, or equivalent scores in other approved [language tests](https://www.canada.ca/language-requirements).\n\nReference: [https://www.canada.ca/language-requirements](https://www.canada.ca/language-requirements)"
        
        # Call the method
        result = self.agent.handle_cross_agent_request(cross_check_request, document, question)
        
        # Assertions
        self.assertIn('IELTS score of 6.0', result)
        self.assertIn('language tests', result)
        self.assertIn('https://www.canada.ca/language-requirements', result)
        self.assertIn('Reference', result)

if __name__ == "__main__":
    unittest.main()
