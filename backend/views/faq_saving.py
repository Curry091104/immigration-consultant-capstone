import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.getcwd(), 'immigration-consultant-capstone'))

from fastapi import Form, APIRouter
from config.mypinecone import MyPinecone
from fastapi.responses import JSONResponse
from typing import List
from controllers.data_processing import convert_faq_to_langchain_docformat

router = APIRouter(prefix="/api")

@router.post("/create-faq")
def create_faq(faq_docs: List[str] = Form(...), index_name: str = Form('faqs')):
    try:
        langchain_faq_docs = convert_faq_to_langchain_docformat(faq_docs)
        pinecone = MyPinecone()
        response = pinecone.insert_data(index_name, langchain_faq_docs)
        return response
    except Exception as e:
        return JSONResponse({'error': str(e)}, status_code=500)