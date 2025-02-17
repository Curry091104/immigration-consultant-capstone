import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.getcwd(), 'immigration-consultant-capstone'))

from app import app
from fastapi import WebSocket, WebSocketDisconnect, File, UploadFile, BackgroundTasks, Form
from config.mypinecone import MyPinecone
from fastapi.responses import JSONResponse
import time
from typing import List
import uuid
import asyncio
from controllers.data_processing import detect_headers_and_footers, extract_hyperlinks, detect_section_with_content, split_subsections, combine_tbl_content, finalize_document, convert_to_langchain_docformat



# Function to receive PDF file
# Function to return the processed text to check before saving
async def data_preprocessing(pdf_path, skip_tags = None, category = None, txt_removed = None):
    headers, footers, ref_link = await detect_headers_and_footers(pdf_path)
    hyperlinks = await extract_hyperlinks(pdf_path)
    sections = await detect_section_with_content(pdf_path, skip_tags=skip_tags, category=category, headers=headers, footers=footers, txt_removed=txt_removed)
    sections = await split_subsections(sections)
    sections = await combine_tbl_content(sections, pdf_path)
    docs = await finalize_document(hyperlinks, sections, ref_link)
    
    os.remove(pdf_path)
    
    return docs

@app.post("/upload-pdf")
async def upload_pdf(pdf_file: UploadFile = File(...), skip_tags: List[str] = Form([]), category: str = Form([]), txt_removed: List[str] = Form([])):
    file_name = pdf_file.filename
    
    temp_pdf_path = f'{file_name}.pdf'
    with open(temp_pdf_path, 'wb') as f:
        f.write(await pdf_file.read())
        
    docs = await data_preprocessing(temp_pdf_path, skip_tags=skip_tags, category=category, txt_removed=txt_removed)
    
    return JSONResponse({'message': f'File {file_name} uploaded successfully', 'docs': docs}, status_code=201)  
    
    
@app.post("/save-pdf-to-pinecone")
def save_pdf_to_pinecone(docs: List[dict] = Form(...), index_name: str = Form('studypermit-pgwp-visa'), ofc_doc_id: str = Form(...)):
    try:
        final_docs = convert_to_langchain_docformat(docs, ofc_doc_id)
        pinecone = MyPinecone()
        response = pinecone.insert_data(index_name, final_docs)
        return response
    except Exception as e:
        return JSONResponse({'error': str(e)}, status_code=500)