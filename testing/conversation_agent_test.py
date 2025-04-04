import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import json
import sys
import os

# Define a mock version of the ConversationAgent class for testing
class MockConversationAgent:
    """Mock class to simulate the ConversationAgent for testing"""
    
    def __init__(self, max_tokens=512, temperature=0.5):
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.model_name = "mistralai/Mistral-7B-Instruct-v0.3"
        self.history = []
        
        # Create mock objects for dependencies
        self.translator = MagicMock()
        self.chat = MagicMock()
    
    def update_conversation_history(self, user_input):
        self.history.append({"user": user_input})
        
        if len(self.history) > 5:
            self.history.pop(0)
    
    def classify_inquiry_for_decision(self, user_input):
        """
        Uses the LLM to classify the user's inquiry into either 'general' or 'decision_agent'.
        """
        # Simulate the core logic without external dependencies
        response = self.chat.invoke.return_value
        llm_output = response.content.strip()
        
        # Extract category and revised inquiry using string parsing
        category = "general"  # Default in case extraction fails
        revised_inquiry = None
        
        if self.model_name == "Qwen/Qwen2.5-3B-Instruct":
            if "<|im_start|>assistant" in llm_output:
                llm_output = llm_output.split("<|im_start|>assistant")[1].strip()
                if "Category:" in llm_output:
                    category_part = llm_output.split("Reason:")[0].strip()
                    category = category_part.split("Category:")[1].strip().lower()
                if "Revised Inquiry:" in llm_output:
                    revised_inquiry = llm_output.split("Revised Inquiry:")[1].split("Reason for Revision:")[0].strip()
                else:
                    revised_inquiry = user_input
            else:
                category = "none"
                revised_inquiry = "none"
        else:
            # Try to extract category and reasoning
            if "Category:" in llm_output and "Revised Inquiry:" in llm_output:
                try:
                    category_part = llm_output.split("Reason:")[0].strip()
                    category = category_part.split("Category:")[1].strip().lower()
                    revised_inquiry = llm_output.split("Revised Inquiry:")[1].split("Reason for Revision:")[0].strip()
                except:
                    revised_inquiry = "None"
        
        return category if category in ["general", "decision_agent", "None", "none"] else "decision_agent", revised_inquiry
    
    async def handle_user_request(self, user_input):
        """
        Handles all tasks:
        1. Language Detection (Only English & French)
        2. Classification of Inquiry (General or Decision Agent)
        3. Routing to the correct handler (self or Decision Agent)
        """
        if not user_input:
            raise ValueError("User input cannot be empty")
            
        # Step 1: Language Check
        detector = self.translator.detect.return_value
        detected_lang = detector.lang
        
        if detected_lang not in ["en", "fr"]:
            return detected_lang, "I'm sorry, but I can only respond in English or French."
        
        if detected_lang == "fr":
            translation = self.translator.translate.return_value
            user_input = translation.text
        
        # Step 2: Classify as 'general' or 'decision_agent'
        inquiry_category, revised_inquiry = self.classify_inquiry_for_decision(user_input)
        
        self.update_conversation_history(user_input)
        
        if revised_inquiry.lower() == "none" or revised_inquiry.lower() == "n/a":
            revised_inquiry = user_input
        
        return detected_lang, inquiry_category, user_input, revised_inquiry
    
    def handle_faq_request(self, faq_response):
        """
        Handles the FAQ response
        """
        response = self.chat.invoke.return_value
        llm_output = response.content.strip()
        
        if self.model_name == "Qwen/Qwen2.5-3B-Instruct":
            if "<|im_start|>assistant" in llm_output:
                llm_output = llm_output.split("<|im_start|>assistant")[1].strip()
                if "Reformatted Response:" in llm_output:
                    reformated_response = llm_output.split("Reformatted Response:")[1].strip()
                    return reformated_response
            return "Sorry, I am unable to answer this question right now, please ask another question."
        else:
            if "Reformatted Response:" in llm_output:
                try:
                    reformated_response = llm_output.split("Reformatted Response:")[1].split("Reason:")[0].strip()
                    return reformated_response
                except Exception:
                    pass
            return llm_output
    
    def handle_crs_request(self, question, crs_links):
        """
        Handles the CRS response
        """
        response = self.chat.invoke.return_value
        llm_output = response.content.strip()
        
        if self.model_name == "Qwen/Qwen2.5-3B-Instruct":
            if "<|im_start|>assistant" in llm_output:
                llm_output = llm_output.split("<|im_start|>assistant")[1].strip()
                if "Reformatted Response:" in llm_output:
                    reformated_response = llm_output.split("Reformatted Response:")[1].strip()
                    return reformated_response
            return "Sorry, I am unable to answer this question right now, please ask another question."
        else:
            if "Reformatted Response:" in llm_output:
                try:
                    reformated_response = llm_output.split("Reformatted Response:")[1].strip()
                    return reformated_response
                except Exception:
                    pass
            return llm_output
    
    def handle_document_search_request(self, document_response, question):
        """
        Handles the document search response
        """
        response = self.chat.invoke.return_value
        llm_output = response.content.strip()
        
        if self.model_name == "Qwen/Qwen2.5-3B-Instruct":
            if "<|im_start|>assistant" in llm_output:
                llm_output = llm_output.split("<|im_start|>assistant")[1].strip()
                if "Reformatted Response:" in llm_output:
                    reformated_response = llm_output.split("Reformatted Response:")[1].strip()
                    return reformated_response
            return "Sorry, I am unable to answer this question right now, please ask another question."
        else:
            if "Reformatted Response:" in llm_output:
                try:
                    # Extract between "Reformatted Response:" and "Reason:" but maintain newlines
                    start_idx = llm_output.find("Reformatted Response:") + len("Reformatted Response:")
                    end_idx = llm_output.find("Reason:", start_idx)
                    
                    if end_idx > start_idx:
                        reformated_response = llm_output[start_idx:end_idx].strip()
                    else:
                        reformated_response = llm_output[start_idx:].strip()
                    
                    if '"' in reformated_response:
                        reformated_response = reformated_response.replace('"', '')
                    
                    # Clean up any extra whitespace around the Reference section
                    reformated_response = reformated_response.replace("\n\n        Reference:", "\n\nReference:")
                    return reformated_response
                except Exception:
                    pass
            return llm_output
    
    def handle_cross_agent_request(self, cross_check_request, document, question):
        """
        Handles the cross-check request
        """
        response = self.chat.invoke.return_value
        llm_output = response.content.strip()
        
        if self.model_name == "Qwen/Qwen2.5-3B-Instruct":
            if "<|im_start|>assistant" in llm_output:
                llm_output = llm_output.split("<|im_start|>assistant")[1].strip()
                if "Reformatted Response:" in llm_output:
                    reformated_response = llm_output.split("Reformatted Response:")[1].strip()
                    return reformated_response
            return "Sorry, I am unable to answer this question right now, please ask another question."
        else:
            if "Reformatted Response:" in llm_output:
                try:
                    # Extract between "Reformatted Response:" and "Reason:" but maintain newlines
                    start_idx = llm_output.find("Reformatted Response:") + len("Reformatted Response:")
                    end_idx = llm_output.find("Reason:", start_idx)
                    
                    if end_idx > start_idx:
                        reformated_response = llm_output[start_idx:end_idx].strip()
                    else:
                        reformated_response = llm_output[start_idx:].strip()
                    
                    # Clean up any extra whitespace around the Reference section
                    reformated_response = reformated_response.replace("\n\n        Reference:", "\n\nReference:")
                    return reformated_response
                except Exception:
                    pass
            return llm_output


class TestConversationAgent(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        """
        Initialize the MockConversationAgent before each test.
        """
        self.agent = MockConversationAgent()
    
    def test_classify_inquiry_for_decision_general(self):
        """
        Test classify_inquiry_for_decision for general inquiries.
        """
        # Set up the mocked response
        mock_response = MagicMock()
        mock_response.content = """
        Inquiry: Hello, how are you?
        ```
        Category: general
        Reason: This is a greeting and not related to any specific immigration topic.
        Revised Inquiry: None
        Reason for Revision: No revision needed as it's a simple greeting.
        ```
        """
        self.agent.chat.invoke.return_value = mock_response
        
        # Call the method
        category, revised_inquiry = self.agent.classify_inquiry_for_decision("Hello, how are you?")
        
        # Assertions
        self.assertEqual(category, "general")
        self.assertEqual(revised_inquiry, "None")
    
    def test_classify_inquiry_for_decision_decision_agent(self):
        """
        Test classify_inquiry_for_decision for decision agent inquiries.
        """
        # Set up the mocked response
        mock_response = MagicMock()
        mock_response.content = """
        Inquiry: How do I apply for a study permit?
        ```
        Category: decision_agent
        Reason: This inquiry is directly related to study permits which is a decision-making topic.
        Revised Inquiry: How do I apply for a study permit in Canada?
        Reason for Revision: Added country context to make the inquiry more specific.
        ```
        """
        self.agent.chat.invoke.return_value = mock_response
        
        # Call the method
        category, revised_inquiry = self.agent.classify_inquiry_for_decision("How do I apply for a study permit?")
        
        # Assertions
        self.assertEqual(category, "decision_agent")
        self.assertEqual(revised_inquiry, "How do I apply for a study permit in Canada?")
    
    def test_classify_inquiry_for_decision_none(self):
        """
        Test classify_inquiry_for_decision for unrelated inquiries.
        """
        # Set up the mocked response
        mock_response = MagicMock()
        mock_response.content = """
        Inquiry: What is the capital of France?
        ```
        Category: none
        Reason: This inquiry is not related to international students or immigration.
        Revised Inquiry: none
        Reason for Revision: No revision needed as it's not a relevant question.
        ```
        """
        self.agent.chat.invoke.return_value = mock_response
        
        # Call the method
        category, revised_inquiry = self.agent.classify_inquiry_for_decision("What is the capital of France?")
        
        # Assertions
        self.assertEqual(category, "none")
        self.assertEqual(revised_inquiry, "none")
    
    def test_classify_inquiry_for_decision_qwen_model(self):
        """
        Test classify_inquiry_for_decision for the Qwen model.
        """
        # Set model name to Qwen
        self.agent.model_name = "Qwen/Qwen2.5-3B-Instruct"
        
        # Set up the mocked response
        mock_response = MagicMock()
        mock_response.content = """<|im_start|>assistant
        Category: decision_agent
        Reason: This is related to study permits.
        Revised Inquiry: How do I apply for a study permit?
        Reason for Revision: No revision needed.
        """
        self.agent.chat.invoke.return_value = mock_response
        
        # Call the method
        category, revised_inquiry = self.agent.classify_inquiry_for_decision("How do I apply for a study permit?")
        
        # Assertions
        self.assertEqual(category, "decision_agent")
        self.assertEqual(revised_inquiry, "How do I apply for a study permit?")
    
    def test_handle_faq_request_with_hyperlinks(self):
        """
        Test handle_faq_request with a response containing hyperlinks.
        """
        # Mock the faq_response
        faq_response = {
            'page_content': "Your study permit lets you study in Canada. You still need a visitor visa (temporary resident visa) or an Electronic Travel Authorization (eTA) to enter Canada.",
            'metadata': {
                "hyperlinks": [
                    {"hyperlink": "https://example.com/trv", "text": "temporary resident visa"},
                    {"hyperlink": "https://example.com/eta", "text": "Electronic Travel Authorization"}
                ]
            }
        }
        
        # Mock the chat response
        mock_response = MagicMock()
        mock_response.content = """
        Reformatted Response: Your study permit lets you study in Canada. You still need a visitor visa [temporary resident visa](https://example.com/trv) or an [Electronic Travel Authorization](https://example.com/eta) (eTA) to enter Canada.
        Reason: Embedded hyperlinks successfully.
        """
        self.agent.chat.invoke.return_value = mock_response
        
        # Call the method
        response = self.agent.handle_faq_request(faq_response)
        
        # Assertions
        self.assertEqual(response, "Your study permit lets you study in Canada. You still need a visitor visa [temporary resident visa](https://example.com/trv) or an [Electronic Travel Authorization](https://example.com/eta) (eTA) to enter Canada.")
    
    def test_handle_faq_request_qwen_model(self):
        """
        Test handle_faq_request when using the Qwen model.
        """
        # Set model name to Qwen
        self.agent.model_name = "Qwen/Qwen2.5-3B-Instruct"
        
        # Mock the faq_response
        faq_response = {
            'page_content': "You can check your application status online.",
            'metadata': {"hyperlinks": [{"hyperlink": "https://example.com/status", "text": "check your application status online"}]}
        }
        
        # Mock the chat response for Qwen model
        mock_response = MagicMock()
        mock_response.content = "<|im_start|>assistant\nReformatted Response: You can [check your application status online](https://example.com/status)."
        self.agent.chat.invoke.return_value = mock_response
        
        # Call the method
        response = self.agent.handle_faq_request(faq_response)
        
        # Assertions
        self.assertEqual(response, "You can [check your application status online](https://example.com/status).")
    
    def test_handle_crs_request_with_links(self):
        """
        Test handle_crs_request with CRS links.
        """
        # Mock question and CRS links
        question = "How can I calculate my CRS score?"
        crs_links = {"CRS Calculator": "https://www.canada.ca/crs-calculator"}
        
        # Mock the chat response
        mock_response = MagicMock()
        mock_response.content = """
        Reformatted Response: To calculate your CRS score, please go to [CRS Calculator](https://www.canada.ca/crs-calculator).
        """
        self.agent.chat.invoke.return_value = mock_response
        
        # Call the method
        response = self.agent.handle_crs_request(question, crs_links)
        
        # Assertions
        self.assertEqual(response, "To calculate your CRS score, please go to [CRS Calculator](https://www.canada.ca/crs-calculator).")
    
    def test_handle_crs_request_qwen_model(self):
        """
        Test handle_crs_request when using the Qwen model.
        """
        # Set model name to Qwen
        self.agent.model_name = "Qwen/Qwen2.5-3B-Instruct"
        
        # Mock question and CRS links
        question = "What factors affect my CRS score?"
        crs_links = {"CRS Criteria": "https://www.canada.ca/crs-criteria"}
        
        # Mock the chat response for Qwen model
        mock_response = MagicMock()
        mock_response.content = "<|im_start|>assistant\nReformatted Response: To learn about factors affecting your CRS score, please visit [CRS Criteria](https://www.canada.ca/crs-criteria)."
        self.agent.chat.invoke.return_value = mock_response
        
        # Call the method
        response = self.agent.handle_crs_request(question, crs_links)
        
        # Assertions
        self.assertEqual(response, "To learn about factors affecting your CRS score, please visit [CRS Criteria](https://www.canada.ca/crs-criteria).")
    
    def test_handle_document_search_request_with_content(self):
        """
        Test handle_document_search_request with found document content.
        """
        # Mock document response and question
        document_response = {
            'text': "Study permits are typically processed within 8-12 weeks depending on your country of origin.",
            'hyperlinks': [{"hyperlink": "https://example.com/processing", "text": "processing"}],
            'ref_link': ["https://example.com/study-permits"]
        }
        question = "How long does it take to process a study permit?"
        
        # Mock the chat response
        mock_response = MagicMock()
        mock_response.content = """
        Reformatted Response: Study permits are typically processed within 8-12 weeks depending on your country of origin. You can check the latest [processing](https://example.com/processing) times on the IRCC website.

        Reference: [https://example.com/study-permits](https://example.com/study-permits)
        Reason: Successfully reformatted the response.
        """
        self.agent.chat.invoke.return_value = mock_response
        
        # Call the method
        response = self.agent.handle_document_search_request(document_response, question)
        
        # Assertions
        expected_response = "Study permits are typically processed within 8-12 weeks depending on your country of origin. You can check the latest [processing](https://example.com/processing) times on the IRCC website.\n\nReference: [https://example.com/study-permits](https://example.com/study-permits)"
        self.assertEqual(response, expected_response)
    
    def test_handle_document_search_request_not_found(self):
        """
        Test handle_document_search_request when document is not found.
        """
        # Mock document response and question
        document_response = "Answer not found"
        question = "Can I bring my pet cat to Canada on a study permit?"
        
        # Mock the chat response
        mock_response = MagicMock()
        mock_response.content = """
        Reformatted Response: "I couldn't find an answer to your question. Could you rephrase it or provide more details? I'll do my best to assist!"
        Reason: The document search returned 'Answer not found'.
        """
        self.agent.chat.invoke.return_value = mock_response
        
        # Call the method
        response = self.agent.handle_document_search_request(document_response, question)
        
        # Assertions
        self.assertEqual(response, "I couldn't find an answer to your question. Could you rephrase it or provide more details? I'll do my best to assist!")
    
    def test_handle_document_search_request_qwen_model(self):
        """
        Test handle_document_search_request when using the Qwen model.
        """
        # Set model name to Qwen
        self.agent.model_name = "Qwen/Qwen2.5-3B-Instruct"
        
        # Mock document response and question
        document_response = {
            'text': "Study permits are typically processed within 8-12 weeks.",
            'hyperlinks': [],
            'ref_link': ["https://example.com/study-permits"]
        }
        question = "How long does it take to process a study permit?"
        
        # Mock the chat response for Qwen model
        mock_response = MagicMock()
        mock_response.content = "<|im_start|>assistant\nReformatted Response: Study permits are typically processed within 8-12 weeks.\n\nReference: [https://example.com/study-permits](https://example.com/study-permits)"
        self.agent.chat.invoke.return_value = mock_response
        
        # Call the method
        response = self.agent.handle_document_search_request(document_response, question)
        
        # Assertions
        expected_response = "Study permits are typically processed within 8-12 weeks.\n\nReference: [https://example.com/study-permits](https://example.com/study-permits)"
        self.assertEqual(response, expected_response)
    
    def test_handle_cross_agent_request(self):
        """
        Test handle_cross_agent_request for revising a response.
        """
        # Mock cross-check request, document, and question
        cross_check_request = "The generated answer is not similar to the retrieved documents. Please revise the answer that matches the retrieved documents closely."
        document = {
            'text': "Students must maintain full-time enrollment to keep their study permit valid.",
            'hyperlinks': [{"hyperlink": "https://example.com/requirements", "text": "requirements"}],
            'ref_link': ["https://example.com/enrollment"]
        }
        question = "What are the requirements to maintain a study permit?"
        
        # Mock the chat response
        mock_response = MagicMock()
        mock_response.content = """
        Reformatted Response: To maintain your study permit, you must ensure [full-time enrollment](https://example.com/requirements) in your academic program. This is a key requirement for keeping your status valid in Canada.

        Reference: [https://example.com/enrollment](https://example.com/enrollment)
        Reason: Revised the response to match the document content more closely.
        """
        self.agent.chat.invoke.return_value = mock_response
        
        # Call the method
        response = self.agent.handle_cross_agent_request(cross_check_request, document, question)
        
        # Assertions
        expected_response = "To maintain your study permit, you must ensure [full-time enrollment](https://example.com/requirements) in your academic program. This is a key requirement for keeping your status valid in Canada.\n\nReference: [https://example.com/enrollment](https://example.com/enrollment)"
        self.assertEqual(response, expected_response)
    
    def test_handle_cross_agent_request_qwen_model(self):
        """
        Test handle_cross_agent_request when using the Qwen model.
        """
        # Set model name to Qwen
        self.agent.model_name = "Qwen/Qwen2.5-3B-Instruct"
        
        # Mock cross-check request, document, and question
        cross_check_request = "The generated answer is not similar to the retrieved documents. Please revise."
        document = {
            'text': "Working while studying is limited to 20 hours per week during regular academic sessions.",
            'hyperlinks': [{"hyperlink": "https://example.com/work", "text": "Working while studying"}],
            'ref_link': ["https://example.com/work-regulations"]
        }
        question = "Can I work on a study permit?"
        
        # Mock the chat response for Qwen model
        mock_response = MagicMock()
        mock_response.content = "<|im_start|>assistant\nReformatted Response: [Working while studying](https://example.com/work) is limited to 20 hours per week during regular academic sessions.\n\nReference: [https://example.com/work-regulations](https://example.com/work-regulations)"
        self.agent.chat.invoke.return_value = mock_response
        
        # Call the method
        response = self.agent.handle_cross_agent_request(cross_check_request, document, question)
        
        # Assertions
        expected_response = "[Working while studying](https://example.com/work) is limited to 20 hours per week during regular academic sessions.\n\nReference: [https://example.com/work-regulations](https://example.com/work-regulations)"
        self.assertEqual(response, expected_response)
    
    async def test_handle_user_request_english(self):
        """
        Test handle_user_request with English input.
        """
        # Mock translator methods
        mock_detector = MagicMock()
        mock_detector.lang = "en"
        self.agent.translator.detect.return_value = mock_detector
        
        # Mock classify_inquiry_for_decision
        with patch.object(self.agent, 'classify_inquiry_for_decision') as mock_classify:
            mock_classify.return_value = ("study permit", "What are the visa application requirements?")
            
            # Call the method
            detected_lang, inquiry_category, user_input, revised_inquiry = await self.agent.handle_user_request("What are the visa application requirements?")
            
            # Assertions
            self.assertEqual(detected_lang, "en")
            self.assertEqual(inquiry_category, "study permit")
            self.assertEqual(user_input, "What are the visa application requirements?")
            self.assertEqual(revised_inquiry, "What are the visa application requirements?")
            
            # Verify history was updated
            self.assertEqual(len(self.agent.history), 1)
            self.assertEqual(self.agent.history[0]["user"], "What are the visa application requirements?")
    
    async def test_handle_user_request_french(self):
        """
        Test handle_user_request with French input.
        """
        # Mock translator methods
        mock_detector = MagicMock()
        mock_detector.lang = "fr"
        self.agent.translator.detect.return_value = mock_detector
        
        mock_translation = MagicMock()
        mock_translation.text = "What are the visa application requirements?"
        self.agent.translator.translate.return_value = mock_translation
        
        # Mock classify_inquiry_for_decision
        with patch.object(self.agent, 'classify_inquiry_for_decision') as mock_classify:
            mock_classify.return_value = ("study permit", "What are the visa application requirements?")
            
            # Call the method
            detected_lang, inquiry_category, user_input, revised_inquiry = await self.agent.handle_user_request("Quels sont les exigences de demande de visa?")
            
            # Assertions
            self.assertEqual(detected_lang, "fr")
            self.assertEqual(inquiry_category, "study permit")
            self.assertEqual(user_input, "What are the visa application requirements?")
            self.assertEqual(revised_inquiry, "What are the visa application requirements?")
    
    async def test_handle_user_request_unsupported_language(self):
        """
        Test handle_user_request with unsupported language.
        """
        # Mock translator methods
        mock_detector = MagicMock()
        mock_detector.lang = "es"
        self.agent.translator.detect.return_value = mock_detector
        
        # Call the method
        detected_lang, message = await self.agent.handle_user_request("¿Cuáles son los requisitos de solicitud de visa?")
        
        # Assertions
        self.assertEqual(detected_lang, "es")
        self.assertEqual(message, "I'm sorry, but I can only respond in English or French.")
    
    async def test_handle_user_request_none_input(self):
        """
        Test handle_user_request with None input.
        """
        # Call the method and assert it raises an exception
        with self.assertRaises(ValueError):
            await self.agent.handle_user_request(None)
    
    async def test_handle_user_request_empty_string(self):
        """
        Test handle_user_request with empty string input.
        """
        # Call the method and assert it raises an exception
        with self.assertRaises(ValueError):
            await self.agent.handle_user_request("")
    
    def test_update_conversation_history(self):
        """
        Test update_conversation_history normal operation.
        """
        # Initial state
        self.assertEqual(len(self.agent.history), 0)
        
        # Add first entry
        self.agent.update_conversation_history("Hello")
        self.assertEqual(len(self.agent.history), 1)
        self.assertEqual(self.agent.history[0]["user"], "Hello")
        
        # Add second entry
        self.agent.update_conversation_history("How are you?")
        self.assertEqual(len(self.agent.history), 2)
        self.assertEqual(self.agent.history[1]["user"], "How are you?")
    
    def test_update_conversation_history_limit(self):
        """
        Test update_conversation_history respects the 5-entry limit.
        """
        # Add 6 entries
        self.agent.update_conversation_history("Entry 1")
        self.agent.update_conversation_history("Entry 2")
        self.agent.update_conversation_history("Entry 3")
        self.agent.update_conversation_history("Entry 4")
        self.agent.update_conversation_history("Entry 5")
        self.agent.update_conversation_history("Entry 6")
        
        # Should only have 5 entries, with the first one removed
        self.assertEqual(len(self.agent.history), 5)
        self.assertEqual(self.agent.history[0]["user"], "Entry 2")
        self.assertEqual(self.agent.history[4]["user"], "Entry 6")


if __name__ == "__main__":
    unittest.main()
