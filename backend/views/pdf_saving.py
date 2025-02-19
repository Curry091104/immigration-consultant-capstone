import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.getcwd(), 'immigration-consultant-capstone'))


from fastapi import WebSocket, WebSocketDisconnect, File, UploadFile, BackgroundTasks, Form, Request, APIRouter
from config.mypinecone import MyPinecone
from fastapi.responses import JSONResponse
import time
from typing import List
import uuid
import asyncio
from controllers.data_processing import detect_headers_and_footers, extract_hyperlinks, detect_section_with_content, split_subsections, combine_tbl_content, finalize_document, convert_to_langchain_docformat

router = APIRouter(prefix="/api")


# Function to receive PDF file
# Function to return the processed text to check before saving
def data_preprocessing(pdf_path, skip_tags = None, category = None, txt_removed = None):
    header, footers, ref_link = detect_headers_and_footers(pdf_path)
    hyperlinks = extract_hyperlinks(pdf_path)
    sections = detect_section_with_content(pdf_path, skip_tags=skip_tags, category=category, header=header, footers=footers, txt_removed=txt_removed)
    sections = split_subsections(sections)
    sections = combine_tbl_content(sections, pdf_path)
    docs = finalize_document(hyperlinks, sections, ref_link)
    
    return docs

@router.post("/upload-pdf")
async def upload_pdf(pdf_file: UploadFile = File(...), skip_tags: List[str] = Form([]), category: List[str] = Form([]), txt_removed: List[str] = Form([]), update_pdf_id: str = Form(None)):
    file_name = pdf_file.filename
    
    if update_pdf_id is not None:
        update_pdf_id = update_pdf_id.strip()
        pinecone = MyPinecone()
        pinecone.delete_data_by_ofc_doc_id('studypermit-pgwp-visa', update_pdf_id)
        
    
    temp_pdf_path = f'{file_name}.pdf'
    with open(temp_pdf_path, 'wb') as f:
        f.write(await pdf_file.read())
        
    docs = data_preprocessing(temp_pdf_path, skip_tags=skip_tags, category=category, txt_removed=txt_removed)
    
    os.remove(temp_pdf_path)
    
    return JSONResponse({'message': f'File {file_name} uploaded successfully', 'docs': docs}, status_code=201)  
    
    
@router.post("/save-pdf-to-pinecone")
def save_pdf_to_pinecone(docs: List[dict] = Form(...), index_name: str = Form('studypermit-pgwp-visa'), ofc_doc_id: str = Form(...)):
    try:
        final_docs = convert_to_langchain_docformat(docs, ofc_doc_id)
        pinecone = MyPinecone()
        response = pinecone.insert_data(index_name, final_docs)
        return response
    except Exception as e:
        return JSONResponse({'error': str(e)}, status_code=500)