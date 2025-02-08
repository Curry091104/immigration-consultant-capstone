from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END, START
from agents.document_search_agent import DocumentSearchAgent
from agents.faq_agent import FAQAgent
from agents.cross_check_agent import CrossCheckAgent
from langchain.schema import Document
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from io import BytesIO

class GraphState(TypedDict):
    sender: str
    receiver: str
    question: str
    generation: str
    documents: Optional[Document]
    crs_links: List[str]
    cross_check_needed: bool
    is_crs: bool
    is_sp_pgwp: bool
    revised_needed: bool
    revised_message: str
    request_user: Optional[str]

def rag_retrieval(state):
    print("RAG Retrieval")
    question = state['question']
    documents = None
    document_search_agent = DocumentSearchAgent()
    answer = document_search_agent.get_answers(question)
    if answer == "Not found":
        return {
            'question': question, 
            'documents': [], 
            'cross_check_needed': False,
            'sender': 'document_search_agent',
            'receiver': '', # Main agent
            'request_user': "Answer not found. Please ask user more details."
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
            'documents': documents, 
            'sender': 'document_search_agent', 
            'receiver': '', # Main agent
            'cross_check_needed': True
        }


def faq_retrieval(state):
    print("FAQ Retrieval")
    question = state['question']
    faq_agent = FAQAgent()
    answer = faq_agent.get_answer(question)
    if answer == "Not found":
        return {
            'question': question, 
            'documents': [], 
            'sender': 'faq_agent',
            'receiver': 'rag_retrieval',
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
            'documents': documents, 
            'sender': 'faq_agent',
            'receiver': '', # Main agent
        }
    
def cross_check(state):
    print("Cross Check")
    question = state['question']
    generation = state['generation']
    documents = state['documents']
    cross_check_agent = CrossCheckAgent()
    similarity_score = cross_check_agent.cross_check(generation, documents)
    if similarity_score > 0.75:
        return {
            'generation': generation, 
            'revised_needed': False,
            'sender': 'cross_check_agent',
            'receiver': END
            }
    else:
        revised_message = "The generated answer is not similar to the retrieved documents. Please revise the answer that matches the retrieved documents closely."
        return {
            'question': question, 
            'documents': documents, 
            'revised_needed': True, 
            'revised_message': revised_message,
            'sender': 'cross_check_agent',
            'receiver': '', # Main agent
            }
    
    
immigration_graph = StateGraph(GraphState)

# Define the nodes
#! Wait for the llm, decision agent, crs agent
immigration_graph.add_node("document_search_agent", rag_retrieval)
immigration_graph.add_node("faq_agent", faq_retrieval)
immigration_graph.add_node("cross_check_agent", cross_check)

# Build the graph
immigration_graph.add_edge(START, "faq_agent")
immigration_graph.add_conditional_edges(
    "faq_agent", lambda state: "document_search_agent" if state['rag_needed'] else "cross_check_agent"
)
immigration_graph.add_edge("faq_agent", END)


immigration_graph = immigration_graph.compile()




# Get image bytes from the graph
img_bytes = immigration_graph.get_graph().draw_mermaid_png()

# Convert bytes to an image
img = mpimg.imread(BytesIO(img_bytes), format="png")

# Display the image
plt.figure(figsize=(10, 6))
plt.imshow(img)
plt.axis("off")  # Hide axes
plt.show()