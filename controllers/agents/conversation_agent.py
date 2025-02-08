from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import ChatPromptTemplate
import dotenv
import os

dotenv.load_dotenv()

class ConversationAgent:
    def __init__(self, max_tokens = 512, temperature = 0.5, top_k = 1, top_p = 0.9, frequency_penalty = 0.0, presence_penalty = 0.0):
        self.model_name = "meta-llama/Meta-Llama-3-8B-Instruct"
        self.llm = HuggingFaceEndpoint(
            repo_id=self.model_name,
            api_key=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
            max_new_tokens= max_tokens,
            temperature= temperature,
            top_k= top_k,
            top_p= top_p,
            frequency_penalty= frequency_penalty,
            presence_penalty= presence_penalty
        )
