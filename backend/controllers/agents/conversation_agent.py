from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain.schema import HumanMessage, AIMessage
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
        self.model_name = "meta-llama/Meta-Llama-3-8B-Instruct" # "meta-llama/Meta-Llama-3-8B-Instruct" "mistralai/Mistral-7B-Instruct-v0.2"
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
        1️⃣ Any inquiry mentioning **IRCC**, but the question must be **meaningful**, must **ALWAYS** be classified as **'decision_agent'**.
        2️⃣ Any inquiry mentioning **CRS score, CRS ranking, Express Entry**, but the question must be **meaningful**, must **ALWAYS** be classified as **'decision_agent'**.
        3️⃣ If the inquiry is **clearly not related to immigration**, do not answer it, classify it as **'general'**.
        4️⃣ If the question is not meaningful although it is related to  **IRCC, CRS score, CRS ranking, Express Entry**, classify it as **'general'**, and ask the user to clarify the question.

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

        # # Print the classification and reasoning for debugging
        # print(f"🔹 **Inquiry:** {user_input}")
        # print(f"✅ **Classified as:** {category}")
        # print(f"📝 **Reason:** {reason}")
        # print(f"🔍 **Revised Inquiry:** {revised_inquiry}")
        # print(f"📝 **Reason for Revision:** {reason_for_revision}\n")
        

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
        
        if revised_inquiry.lower() == "none" or revised_inquiry.lower() == "n/a":
            revised_inquiry = user_input
        
        return detected_lang, inquiry_category, user_input, revised_inquiry
    
    
    def handle_faq_request(self, faq_response):
        """
        Handles the FAQ response
        
        Do not change the original response from the FAQ system.
        Only change the format of the response to the user.
        """
        
        handle_faq_prompt = f"""You receive a response from the FAQ agent, and you should reformat the FAQ agent's response into a human-like conversation that 
        is easy to understand by college students. In your response, you should embed hyperlinks in the terms.

        *** Strict Rules ***
        1️⃣ Only change the format of the faq_response following the rules below.
        2️⃣ Do not change the original response from the FAQ system.
        3️⃣ Must embed the hyperlinks in the terms.
        4️⃣ Do not add any additional content to the response.
        5️⃣ Do not remove any content from the response.


        ### Example FAQ Responses and Reformatted Outputs:

        #### Example 1:
        **Input:**
        ```
        {{'page_content'="This is the content of the FAQ response." 'metadata'={{ "hyperlinks": [ {{ "hyperlink": "https://www.example.com", "text": "content" }} ] }}}}
        ```

        **Output:**
        ```
        Reformatted Response: This is the [content](https://www.example.com) of the FAQ response.
        ```

        #### Example 2:
        **Input:**
        ```
        {{'page_content'="Your study permit lets you study in Canada. You still need a visitor visa (temporary resident visa) or an Electronic Travel Authorization (eTA) to enter Canada." 'metadata'={{ "hyperlinks": [ {{ "hyperlink": "https://www.example.com", "text": "temporary resident visa" }}, {{ "hyperlink": "https://www.example2.com", "text": "Electronic Travel Authorization" }} ] }}}}
        ```

        **Output:**
        ```
        Reformatted Response: Your study permit lets you study in Canada. You still need a visitor visa [temporary resident visa](https://www.example.com) or an [Electronic Travel Authorization](https://www.example2.com) (eTA) to enter Canada.
        ```
        
        *** HOW TO FORMAT THE RESPONSE ***
        1️⃣ Extract the 'page_content' and 'metadata' from the FAQ agent's response.
        2️⃣ Identify the terms in the 'page_content' that need hyperlinks based on the 'metadata'.
        3️⃣ Embed the hyperlinks in the terms within the 'page_content'.
        4️⃣ Maintain the original content and order of the 'page_content'.
        5️⃣ Format the response as shown in the example outputs.

        
        This is the response from the FAQ agent:
        {faq_response}

        Return the reformatted response in the exact format below:

        ```
        Reformatted Response: <Reformatted Response>
        Reason: if the faq_response is not reformatted, provide a reason why it was not reformatted. 
        ```
        """

        
        # Send the classification request to the LLM
        response = self.chat.invoke([HumanMessage(content=handle_faq_prompt)])
        
        llm_output = response.content.strip()
        
        reformated_response = None
        reason = "No explanation provided."
        
        if "Reformatted Response:" in llm_output and "Reason:" in llm_output:
            try:
                reformated_response = llm_output.split("Reformatted Response:")[1].split("Reason:")[0].strip()
                reason = llm_output.split("Reason:")[1].strip()
            except:
                pass
        return reformated_response
        
    def handle_crs_request(self, question, crs_links):
        """
        Handles the CRS response
        
        Get the title and the link from the response
        Generate a response that includes the title and the link, make sure the context is clear
        """

        handle_crs_prompt = f"""

        You receive a response from the crs_links_agent agent, and you should reformat the FAQ agent's response into a human-like conversation that 
        is easy to understand by college students. 

        *** Strict Rules ***
        1️⃣ Respond the inquiry from the student with title and links from the crs_links_agent
        2️⃣ 


        ### Example received input and Reformatted Outputs:

        #### Example 1:
        ** Student query: **
        ```
        How can I calculate my CRS Score?
        ```

        **crs_links:**
         ```   
        {{'CRS Calculator': 'https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/check-score.html'}}
         ```
        

        **Output:**
        ```
        Reformatted Response: To calculate your CRS score, please go to 'https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/check-score.html
        ```


        
        This is the user question
        {question}

        This is the crs_links
        {crs_links}

        Return the reformatted response in the exact format below:

        ```
        Reformatted Response: <Reformatted Response>
        ```
        """

        # Send the classification request to the LLM
        response = self.chat.invoke([HumanMessage(content=handle_crs_prompt)])
        llm_output = response.content.strip()

        reformated_response = None
        
        if "Reformatted Response:" in llm_output:
            try:
                reformated_response = llm_output.split("Reformatted Response:")[1].strip()
            except:
                pass
        return reformated_response
    
    def handle_document_search_request(self, document_response):
        """
        Handles the document search response
        
        Two situations:
        1. If the document is found
        2. If the document is not found, ask the user to clarify the question
        """
        pass
    
    def handle_cross_agent_request(self, cross_check_request):
        """
        Handles the cross-check request
        
        When this agent asks for revision of the previous inquiry, which means the previous inquiry was not matched with the document search.add()
        Generate a response again that must be closed to the documents, then return to cross-check agent to re-check
        """
        pass