import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.getcwd(), 'immigration-consultant-capstone'))

from fastapi import Form, APIRouter, Depends, Request
from config.mypinecone import MyPinecone
from auth.admin_api_validation import validate_admin_api_key
from fastapi.responses import JSONResponse
from typing import List
from controllers.data_processing import convert_faq_to_langchain_docformat

router = APIRouter(prefix="/api")

@router.post("/create-faq")
def create_faq(request: Request, faq_docs: List[str] = Form(...), index_name: str = Form('faqs'), x_api_key: str = Depends(validate_admin_api_key)):
    if not x_api_key:
        return JSONResponse({'error': 'Invalid API Key'}, status_code=401)
    token = request.cookies.get('access_token')
    if not token:
        return JSONResponse({'error': 'Invalid Token'}, status_code=401)
    try:
        langchain_faq_docs = convert_faq_to_langchain_docformat(faq_docs)
        pinecone = MyPinecone()
        response = pinecone.insert_data(index_name, langchain_faq_docs)
        return response
    except Exception as e:
        return JSONResponse({'error': str(e)}, status_code=500)