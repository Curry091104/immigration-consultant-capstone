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
process_status = {}

async def data_preprocessing(task_id, pdf_path, skip_tags = None, category = None, txt_removed = None):
    process_status[task_id] = 0
    
    total_processing_tasks = 6
    task_completed = 0
    
    async def update_progress():
        nonlocal task_completed
        process_status[task_id] = int((task_completed/total_processing_tasks)*100)
        
    async def execute_task(step_name, func, *args):
        nonlocal task_completed
        step_start_time = time.time()
        result = await func(*args)
        task_completed += 1
        await update_progress()
        print(f'{step_name} completed in {time.time()-step_start_time} seconds')
        return result
    

    headers, footers, ref_link = await execute_task('Detect Headers and Footers', detect_headers_and_footers, pdf_path)
    hyperlinks = await execute_task('Extract Hyperlinks', extract_hyperlinks, pdf_path)
    sections = await execute_task('Detect Sections with Content', detect_section_with_content, pdf_path, skip_tags=skip_tags, category=category, headers=headers, footers=footers, txt_removed=txt_removed)
    sections = await execute_task('Split Subsections', split_subsections, sections)
    sections = await execute_task('Combine Table Content', combine_tbl_content, sections, pdf_path)
    docs = await execute_task('Finalize Document', finalize_document, hyperlinks, sections, ref_link)
    
    process_status[task_id] = 100
    process_status[f'{task_id}_docs'] = docs
    
    os.remove(pdf_path)
    
    return docs


@app.post("/upload-pdf")
async def upload_pdf(backgroud_tasks: BackgroundTasks, pdf_file: UploadFile = File(...), skip_tags: List[str] = Form([]), category: str = Form([]), txt_removed: List[str] = Form([])):
    task_id = str(uuid.uuid4()) # Generate a unique task id
    file_name = pdf_file.filename
    
    temp_pdf_path = f'{file_name}.pdf'
    with open(temp_pdf_path, 'wb') as f:
        f.write(await pdf_file.read())
        
    backgroud_tasks.add_task(data_preprocessing, task_id, temp_pdf_path, skip_tags, category, txt_removed)
    
    return JSONResponse({'task_id': task_id, 'message': f'File {file_name} uploaded successfully'}, status_code=201)  
    


@app.websocket("/ws-pdf-processing/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await websocket.accept()
    
    try:
        current_progress = process_status.get(task_id, 0)
        while process_status.get(task_id, 0) < 100:
            progress = process_status.get(task_id, 0)
            if progress > current_progress:
                await websocket.send_json({'task_id': task_id, 'progress': progress})
                current_progress = progress
            await asyncio.sleep(0.5)
        
        await websocket.send_json({'task_id': task_id, 'progress': 100})
        await websocket.send_text('Processing Completed')
        
        docs = process_status.get(f'{task_id}_docs')
        if docs:
            await websocket.send_json({'task_id': task_id, 'docs': docs})
            del process_status[f'{task_id}_docs']
            del process_status[task_id]
        else:
            await websocket.send_text('Error: No processed data found')
    except Exception as e:
        await websocket.send_text(f'Error: {str(e)}')
    
    finally:
        await websocket.close(code=WebSocketDisconnect)
    
@app.post("/save-pdf-to-pinecone")
def save_pdf_to_pinecone(docs: List[dict] = Form(...), index_name: str = Form('studypermit-pgwp-visa'), ofc_doc_id: str = Form(...)):
    try:
        final_docs = convert_to_langchain_docformat(docs, ofc_doc_id)
        pinecone = MyPinecone()
        response = pinecone.insert_data(index_name, final_docs)
        return response
    except Exception as e:
        return JSONResponse({'error': str(e)}, status_code=500)