import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os

# Get the parent directory of backend
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add it to sys.path
sys.path.append(parent_dir)

from backend.controllers.agents.conversation_agent import ConversationAgent

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

    async def test_handle_user_input_english(self):
        """
        Test handle_user_input with English input.
        """
        self.mock_translator.detect = AsyncMock(return_value=MagicMock(lang="en"))
        self.mock_classifier.return_value = ("study permit", "What are the visa application requirements?")
        
        detected_lang, inquiry_category, user_input, revised_inquiry = await self.agent.handle_user_request("What are the visa application requirements?")
        
        self.assertEqual(detected_lang, "en")
        self.assertEqual(inquiry_category, "study permit")
        self.assertEqual(user_input, "What are the visa application requirements?")
        self.assertEqual(revised_inquiry, "What are the visa application requirements?") 
        self.mock_history.assert_called_once_with(user_input)
        
        
    async def test_handle_user_input_french(self):
        """
        Test handle_user_input with French input.
        """
        self.mock_translator.detect = AsyncMock(return_value=MagicMock(lang="fr"))
        self.mock_translator.translate = AsyncMock(return_value=MagicMock(text="What are the visa application requirements?"))
        self.mock_classifier.return_value = ("study permit", "What are the visa application requirements?")
        
        detected_lang, inquiry_category, user_input, revised_inquiry = await self.agent.handle_user_request("Quels sont les exigences de demande de visa?")
        
        self.assertEqual(detected_lang, "fr")
        self.assertEqual(inquiry_category, "study permit")
        self.assertEqual(user_input, "What are the visa application requirements?")
        self.assertEqual(revised_inquiry, "What are the visa application requirements?")
        self.mock_history.assert_called_once_with(user_input)
        
    async def test_handle_user_input_unsupported_language(self):
        """
        Test handle_user_input with unsupported language.
        """
        self.mock_translator.detect = AsyncMock(return_value=MagicMock(lang="es"))
        
        detected_lang, message = await self.agent.handle_user_request("¿Cuáles son los requisitos de solicitud de visa?")
        
        self.assertEqual(detected_lang, "es")
        self.assertEqual(message, "I'm sorry, but I can only respond in English or French.")
        
    async def test_handle_user_input_none(self):
        """
        Test handle_user_input with None input.
        """
        with self.assertRaises(TypeError):
            await self.agent.handle_user_request(None)
            
    async def test_handle_user_input_empty_string(self):
        """
        Test handle_user_input with empty string input.
        """
        with self.assertRaises(ValueError):
            await self.agent.handle_user_request("")
            
    async def test_handle_user_input_numeric_input(self):
        """
        Test handle_user_input with numeric input.
        """
        with self.assertRaises(ValueError):
            await self.agent.handle_user_request(123)
        
        

if __name__ == "__main__":
    unittest.main()
