from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain.schema import HumanMessage
import os
from dotenv import load_dotenv
import googletrans
import asyncio

# Load environment variables
load_dotenv()

class ConversationAgent:
    """Main agent responsible for handling multi-agent communication."""

    def __init__(self, max_tokens=512, temperature=0.5):
        # Initialize the LLM Model
        self.model_name = "mistralai/Mistral-7B-Instruct-v0.2"
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
        classification_prompt = f"""
        You are an intelligent assistant that classifies user inquiries into two categories:
        - 'general': Basic questions not related to immigration, such as greetings, general knowledge, or unrelated topics.
        - 'decision_agent': Questions about immigration, student visas, permits, IRCC, CRS score, CRS ranking, Express Entry, or any topic requiring immigration-related decision-making.

        ### **Strict Classification Rules**
        1️⃣ Any inquiry mentioning **IRCC** must **ALWAYS** be classified as **'decision_agent'**.
        2️⃣ Any inquiry mentioning **CRS score, CRS ranking, Express Entry** must **ALWAYS** be classified as **'decision_agent'**.
        3️⃣ If the inquiry is **clearly not related to immigration**, classify it as **'general'**.

        **User Inquiry:**  
        {user_input}

        Return the classification in the exact format below:


        Inquiry: {user_input}

        Return the response in the following format:
        ```
        Category: <general or decision_agent>
        Reason: <Brief explanation why this category was chosen>
        ```
        """

        # Send the classification request to the LLM
        response = self.chat.invoke([HumanMessage(content=classification_prompt)])

        # Extract LLM response
        llm_output = response.content.strip()
        
        # Extract category and reason using string parsing
        category = "general"  # Default in case extraction fails
        reason = "No explanation provided."

        # Try to extract category and reasoning
        if "Category:" in llm_output and "Reason:" in llm_output:
            try:
                parts = llm_output.split("Reason:")
                category = parts[0].replace("Category:", "").strip().lower()
                reason = parts[1].strip()
            except:
                pass  # If parsing fails, keep defaults

        # Print the classification and reasoning for debugging
        print(f"🔹 **Inquiry:** {user_input}")
        print(f"✅ **Classified as:** {category}")
        print(f"📝 **Reason:** {reason}\n")

        return category if category in ["general", "decision_agent"] else "decision_agent"

    async def handle_request(self, user_input):
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
        inquiry_category = self.classify_inquiry_for_decision(user_input)
        
        history_text = "\n".join(
            [f"**User:** {msg['user']}" for msg in self.history]
        )
        
        
        #! NEED TO FIX THIS
        conversation_prompt = f"""
        You are a helpful assistant that considers previous conversations to revise ambiguous follow-up questions if they are missing keywords, but still relevant to previous messages.
        Basic questions not related to immigration, such as greetings, general knowledge, or unrelated topics, do not require any revision.
        If the inquiry is **related to IRCC, CRS score, CRS ranking, Express Entry**, but the keyword is missing, revise the inquiry to include the keyword.
        You must not answer any inquiry directly.
        ONLY revise the inquiry, DO NOT add any additional content or reason to the revised inquiry section.
        DO NOT REPEAT the inquiry in the revised inquiry section if it is not revised.

        **Conversation History:**
        {history_text}

        **New User Inquiry:**
        {user_input}

        If the inquiry is **clearly not related to immigration**, respond with "None" and do not include the inquiry again. 
        If the inquiry is **related to IRCC, CRS score, CRS ranking, Express Entry**, and is missing the relevant keyword, revise it to include the keyword.

        
        Return the classification in the exact format below:
        The Inquiry is always a question from the user.
        Revised Inquiry: <Revised Inquiry ONLY ONLY> *** Revised Inquiry MUST be different from the original inquiry*** Return "None" if the inquiry is not revised
        Do not add any additional content or reason to the revised inquiry section.
        PLase Do Not include "The Inquiry is: <New User Inquiry>" under Revised Inquiry!
        Reason: <Brief explanation why the inquiry was revised or not> even if the inquiry is not revised.
        """

        
        response = self.chat.invoke([HumanMessage(content=conversation_prompt)])
        llm_output = response.content.strip()
        
        revised_inquiry = None
        reason = None
        
        if "Revised Inquiry:" in llm_output:
            try:
                if "Reason:" in llm_output:
                    parts = llm_output.split("Reason:")
                    revised_inquiry = parts[0].replace("Revised Inquiry:", "").strip()
                    reason = parts[1].strip()
                else:
                    revised_inquiry = llm_output.replace("Revised Inquiry:", "").strip()
                    reason = "No explanation provided."
            except:
                pass
            
        print(f"🔹 **Inquiry:** {user_input}")
        print(f"✅ **Revised Inquiry:** {revised_inquiry}")
        print(f"📝 **Reason:** {reason}")
        
        self.update_conversation_history(user_input)
        
        return detected_lang, inquiry_category, user_input, revised_inquiry
    
    #! Have not checked grammar, ...