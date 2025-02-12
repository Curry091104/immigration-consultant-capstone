from typing import TypedDict, List, Optional
import os
from langgraph.graph import StateGraph, END, START
from agents.document_search_agent import DocumentSearchAgent
from agents.conversational_agent import ConversationAgent
from agents.faq_agent import FAQAgent
from agents.cross_check_agent import CrossCheckAgent
from agents.decision_agent import DecisionAgent
from langchain.schema import HumanMessage, AIMessage
from langchain.schema import Document
from langgraph.checkpoint.memory import MemorySaver
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import langsmith as ls
from io import BytesIO
import asyncio
import warnings
warnings.filterwarnings("ignore")

LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT")

memory = MemorySaver()
langsmith_client = ls.Client(api_url=LANGSMITH_ENDPOINT, api_key=LANGSMITH_API_KEY)
conv_agent = ConversationAgent()
document_search_agent = DocumentSearchAgent()
faq_agent = FAQAgent()
cross_check_agent = CrossCheckAgent()
dec_agent = DecisionAgent()

class GraphState(TypedDict):
    sender: Optional[str]
    receiver: Optional[str]
    question: str
    generation: Optional[str]
    documents: Optional[Document]
    crs_links: Optional[List[str]]
    cross_check_needed: Optional[bool]
    revised_message: Optional[str]
    request_user: Optional[str]
    category: Optional[str]
    
    
@ls.traceable(langsmith_client, name="conversation_agent")
async def conversation_agent(state, **kwargs):
    print("Conversation Agent")
    question = state['question']
    sender = state['sender']
    category = state.get('category', None)
    if sender not in ['document_search_agent', 'faq_agent', 'cross_check_agent']:
        response = await conv_agent.handle_request(question)
        if response[1] != "general":
            if response[0] == "fr" and response[3] == None:
                question = response[2]
            elif response[0] == "fr" and response[3] != None:
                question = response[3]
            elif response[0] == "en" and response[3] != None:
                question = response[3]
        
        if response[0] not in ["en", "fr"]:
            return {
                'question': question,  
                'sender': 'conversation_agent',
                'receiver': '_end_',
            }
        elif response[1] == "general":
            detected_lang = response[0]
            prompt = f"Answer in {detected_lang}: {question}"
            agent_response = conv_agent.chat.invoke([HumanMessage(content=prompt)])
            return {
                'question': question, 
                'generation': agent_response.content,
                'sender': 'conversation_agent',
                'receiver': '_end_',
            }
        elif response[1] == "decision_agent":
            return {
                'question': question, 
                'sender': 'conversation_agent',
                'receiver': 'decision_agent',
            }
    elif sender == 'document_search_agent':
        cross_check_needed = state['cross_check_needed']
        #! Implement text generation in this line
        if cross_check_needed:
            return {
                'question': question, 
                'generation': state['generation'],
                'documents': state['documents'],
                'category': category,
                'sender': 'conversation_agent',
                'receiver': 'cross_check_agent'
            }
        else:
            request_user = state['request_user']
            #! Implement text generation in this line -- No cross check needed because answer is not found
            return {
                'question': question, 
                'generation': state['generation'],
                'category': category,
                'sender': 'conversation_agent',
                'receiver': '_end_',
            }
    elif sender == 'cross_check_agent':
        revised_message = state['revised_message']
        #! Implement text generation in this line
        return {
            'question': question, 
            'generation': state['generation'],
            'documents': state['documents'],
            'category': category,
            'sender': 'conversation_agent',
            'receiver': 'cross_check_agent'
        }
    elif sender == 'faq_agent':
        faq_docs = state['documents']
        #! Implement text generation in this line
        return {
            'question': question, 
            'generation': state['generation'],
            'category': category,
            'sender': 'conversation_agent',
            'receiver': '_end_',
        }

@ls.traceable(langsmith_client, name="decision_agent")
def decision_agent(state, **kwargs):
    print("Decision Agent")
    question = state['question']
    category = dec_agent.classify_question(question)
    is_sp_pgwp_visa = dec_agent.is_the_query_related_to_study_permit_pgwp_or_visa(question)
    if is_sp_pgwp_visa:
        return {
            'question': question,
            'category': category,
            'sender': 'decision_agent',
            'receiver': 'faq_agent'
        }
    else:
        return {
            'question': question,
            'category': category,
            'sender': 'decision_agent',
            'receiver': '' #CRS Agent
        }

@ls.traceable(langsmith_client, name="document_search_agent")
def rag_retrieval(state, **kwargs):
    print("RAG Retrieval")
    question = state['question']
    category = state['category']
    documents = None
    answer = document_search_agent.get_answers(question)
    if answer == "Not found":
        return {
            'question': question,
            'category': category,
            'cross_check_needed': False,
            'sender': 'document_search_agent',
            'receiver': 'conversation_agent',
            'request_user': "Answer not found. Please ask user for more details."
        }
    else:
        documents = Document(
            page_content=answer.get('text', ''),
            metadata={
                'hyperlinks': answer.get('hyperlinks', []),
                'reference': answer.get('ref_link', '')
            }
        )
        return {
            'question': question, 
            'category': category,
            'documents': documents, 
            'sender': 'document_search_agent', 
            'receiver': 'conversation_agent',
            'cross_check_needed': True
        }

@ls.traceable(langsmith_client, name="faq_agent")
def faq_retrieval(state, **kwargs):
    print("FAQ Retrieval")
    question = state['question']
    category = state['category']
    answer = faq_agent.get_answer(question)
    if answer == "Not found":
        return {
            'question': question,
            'category': category,
            'documents': [], 
            'sender': 'faq_agent',
            'receiver': 'document_search_agent',
        }
    else:
        documents = Document(
            page_content=answer.get('answer', ''),  
            metadata={
                'hyperlinks': answer.get('hyperlinks', [])
            }
        )
        return {
            'question': question,
            'category': category,
            'documents': documents, 
            'sender': 'faq_agent',
            'receiver': 'conversation_agent',
        }
    
@ls.traceable(langsmith_client, name="cross_check_agent")
def cross_check(state, **kwargs):
    print("Cross Check")
    question = state['question']
    category = state['category']
    generation = state['generation']
    documents = state['documents']
    similarity_score = cross_check_agent.cross_check(generation, documents)
    if similarity_score > 0.75:
        return {
            'question': question,
            'generation': generation,
            'category': category,
            'sender': 'cross_check_agent',
            'receiver': '_end_',
        }
    else:
        revised_message = "The generated answer is not similar to the retrieved documents. Please revise the answer that matches the retrieved documents closely."
        return {
            'question': question, 
            'documents': documents,
            'category': category,
            'revised_message': revised_message,
            'sender': 'cross_check_agent',
            'receiver': 'conversation_agent'
        } 
    
immigration_graph = StateGraph(GraphState)

# Define the nodes
#! Wait for the decision agent, crs agent
immigration_graph.add_node("conversation_agent", conversation_agent)
immigration_graph.add_node("document_search_agent", rag_retrieval)
immigration_graph.add_node("faq_agent", faq_retrieval)
immigration_graph.add_node("cross_check_agent", cross_check)
immigration_graph.add_node("decision_agent", decision_agent)

# Build the graph
immigration_graph.add_edge(START, "conversation_agent")
immigration_graph.add_conditional_edges(
    "conversation_agent",
    lambda state: state['receiver'],
    {
        "decision_agent": "decision_agent",
        "cross_check_agent": "cross_check_agent",
        '_end_': END
    }
)

immigration_graph.add_conditional_edges(
    "decision_agent",
    lambda state: state['receiver'],
    {
        "faq_agent": "faq_agent",
        'document_search_agent': "document_search_agent" #CRS Agent - temporary
    }
)

immigration_graph.add_conditional_edges(
    "faq_agent",
    lambda state: state['receiver'],
    {
        "document_search_agent": "document_search_agent",
        "conversation_agent": "conversation_agent"
    }
)


immigration_graph.add_edge("document_search_agent", "conversation_agent")
immigration_graph.add_edge("cross_check_agent", END)


agents = immigration_graph.compile(checkpointer=memory)

# #Get image bytes from the graph
# img_bytes = agents.get_graph().draw_mermaid_png()

# # Convert bytes to an image
# img = mpimg.imread(BytesIO(img_bytes), format="png")

# # Display the image
# plt.figure(figsize=(10, 6))
# plt.imshow(img)
# plt.title("Multi-agent collaboration graph", fontsize=20)
# plt.axis("off")  # Hide axes
# plt.show()

config = {"configurable": {"thread_id": "1"}} # Add thread_id to the config, must be unique for each conversation
inputs = {}

async def main():
    while True:
        try:
            user_input = input("Enter your question: ")
            if user_input == "q":
                print("Goodbye!")
                break
            inputs['question'] = user_input
            inputs['sender'] = "user"
            async for output in agents.astream(inputs, config):
                print(output)
        except Exception as e:
            print(e)
            break

asyncio.run(main())