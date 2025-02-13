from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain.schema import HumanMessage
import os
from dotenv import load_dotenv
import googletrans
import asyncio
import warnings
warnings.filterwarnings("ignore")

# Load environment variables
load_dotenv()

class ConversationAgent:
    """Main agent responsible for handling multi-agent communication."""

    def __init__(self, max_tokens=1028, temperature=0.5): # max_tokens = 512, temperature = 0.5, top_k = 1, top_p = 0.9, frequency_penalty = 0.0, presence_penalty = 0.0
        # Initialize the LLM Model
        self.model_name = "mistralai/Mistral-7B-Instruct-v0.2" # "meta-llama/Meta-Llama-3-8B-Instruct"
        self.llm = HuggingFaceEndpoint(
            repo_id=self.model_name,
            api_key=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
            max_new_tokens=max_tokens,
            temperature=temperature
        )
        self.chat = ChatHuggingFace(llm=self.llm, verbose=True)
        self.translator = googletrans.Translator()
        self.history = []
        
    def update_conversation_history(self, user_input):
        self.history.append({"user": user_input})
        
        if len(self.history) > 5:
            self.history.pop(0)
        
        

    def classify_inquiry_for_decision(self, user_input):
        """
        Uses the LLM to classify the user's inquiry into either 'general' or 'decision_agent'.
        Also prints the LLM's reasoning for debugging.
        """
        
        history_text = "\n".join(
            [f"**User:** {msg['user']}" for msg in self.history]
        )
        
        classification_prompt = f"""
        You are an intelligent and helpful assistant that classifies user inquiries into two categories:
        - 'general': Basic questions not related to immigration, such as greetings, general knowledge, or unrelated topics.
        - 'decision_agent': Questions about immigration, student visas, permits, IRCC, CRS score, CRS ranking, Express Entry, or any topic requiring immigration-related decision-making.

        ### **Strict Classification Rules**
        1️⃣ Any inquiry mentioning **IRCC** must **ALWAYS** be classified as **'decision_agent'**.
        2️⃣ Any inquiry mentioning **CRS score, CRS ranking, Express Entry** must **ALWAYS** be classified as **'decision_agent'**.
        3️⃣ If the inquiry is **clearly not related to immigration**, classify it as **'general'**.
        4️⃣ If the user asks a question that is not related to immigration, do not answer it and classify it as **'general'**.

        ### **Conversation Revision Rules**
        You consider previous conversations to revise ambiguous follow-up questions if they are missing keywords, but still relevant to previous messages.
        Basic questions not related to immigration, such as greetings, general knowledge, or unrelated topics, do not require any revision.
        If the inquiry is **related to IRCC, CRS score, CRS ranking, Express Entry**, but the keyword is missing, revise the inquiry to include the keyword.
        You must not answer any inquiry directly.
        ONLY revise the inquiry, DO NOT add any additional content or reason to the revised inquiry section.
        DO NOT REPEAT the inquiry in the revised inquiry section if it is not revised.

        **Conversation History:**
        {history_text}

        **New User Inquiry:**
        {user_input}

        **Classification and Revision:**
        If the inquiry is **clearly not related to immigration**, respond with "None" and do not include the inquiry again. 
        If the inquiry is **related to IRCC, CRS score, CRS ranking, Express Entry**, and is missing the relevant keyword, revise it to include the keyword.

        Return the classification and revision in the exact format below:
        
        Inquiry: {user_input}
        ```
        Category: <general or decision_agent>
        Reason: <Brief explanation why this category was chosen>
        Revised Inquiry: <Revised Inquiry ONLY> *** Revised Inquiry MUST be different from the original inquiry*** Return "None" if the inquiry is not revised
        Reason for Revision: <Brief explanation why the inquiry was revised or not> even if the inquiry is not revised.
        ```
        
        PLEASE DO NOT add any additional content or reason to the revised inquiry section.
        For example:
        - Previous Inquiry: "What is the CRS score?"
        - Current Inquiry: "How can I calculate it?", then it needs to be revised to "How can I calculate the CRS score?"
        - If user asks "How can I calculate the CRS score?" then it does not need to be revised, return "None".
        Please Do Not include "The Inquiry is: <New User Inquiry>" under Revised Inquiry!
        Reason: <Brief explanation why the inquiry was revised or not> even if the inquiry is not revised.
        """


        # Send the classification request to the LLM
        response = self.chat.invoke([HumanMessage(content=classification_prompt)])

        # Extract LLM response
        llm_output = response.content.strip()
        
        # Extract category and reason using string parsing
        category = "general"  # Default in case extraction fails
        reason = "No explanation provided."
        revised_inquiry = None
        reason_for_revision = "No explanation provided."

        # Try to extract category and reasoning
        if "Category:" in llm_output and "Reason:" in llm_output and "Revised Inquiry:" in llm_output and "Reason for Revision:" in llm_output:
            try:
                category_part = llm_output.split("Reason:")[0].strip()
                category = category_part.split("Category:")[1].strip().lower()
                reason = llm_output.split("Reason:")[1].split("Revised Inquiry:")[0].strip()
                revised_inquiry = llm_output.split("Revised Inquiry:")[1].split("Reason for Revision:")[0].strip()
                reason_for_revision = llm_output.split("Reason for Revision:")[1].strip() 
            except:
                pass  # If parsing fails, keep defaults
            
        if "The Inquiry is:" in revised_inquiry:
            revised_inquiry = revised_inquiry.split("The Inquiry is:")[1].strip()

        # Print the classification and reasoning for debugging
        print(f"🔹 **Inquiry:** {user_input}")
        print(f"✅ **Classified as:** {category}")
        print(f"📝 **Reason:** {reason}")
        print(f"🔍 **Revised Inquiry:** {revised_inquiry}")
        print(f"📝 **Reason for Revision:** {reason_for_revision}\n")
        

        return category if category in ["general", "decision_agent"] else "decision_agent", revised_inquiry

    async def handle_user_request(self, user_input):
        """
        Handles all tasks:
        1. Language Detection (Only English & French)
        2. Classification of Inquiry (General or Decision Agent)
        3. Routing to the correct handler (self or Decision Agent)
        4. Receives final responses from CRS/FAQ/Document Search and sends them to the user.
        """

        # Step 1: Language Check (Fix: Handle detection failures)
        try:
            lang_detection = await self.translator.detect(user_input)
            detected_lang = lang_detection.lang
        except Exception as e:
            print("Language detection failed:", e)
            raise e
            

        if detected_lang not in ["en", "fr"]:
            return detected_lang, "I'm sorry, but I can only respond in English or French."
        
        if detected_lang == "fr":
            user_input = await self.translator.translate(user_input, dest="en")
            user_input = user_input.text

        # Step 2: Classify as 'general' or 'decision_agent'
        inquiry_category, revised_inquiry = self.classify_inquiry_for_decision(user_input)
        
        self.update_conversation_history(user_input)
        
        return detected_lang, inquiry_category, user_input, revised_inquiry
    
    
    def handle_faq_request(self, faq_response):
        """
        Handles the FAQ response
        
        Do not change the original response from the FAQ system.
        Only change the format of the response to the user.
        
        Example:
        Document(
            page_content="This is the content of the FAQ response."
            metadata={
                "hyperlinks": ["https://www.example.com: content"],
            }
        )
        
        Change the response to: This is the [https://www.example.com](content) of the FAQ response.
        """
        pass
    
    def handle_crs_request(self, crs_response):
        pass
    
    def handle_document_search_request(self, document_response):
        pass
    
    def handle_cross_agent_request(self, user_input):
        pass