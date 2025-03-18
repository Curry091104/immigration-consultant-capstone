import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import streamlit as st
from screens import *
from Home import session_manager
import time
import os
from dotenv import load_dotenv
load_dotenv()

def upload_faq_page():
    st.title("Upload FAQs")
    st.sidebar.button("⬅ Back", on_click=go_back)
    initialize_session_state()
    get_user_inputs()
    
def get_user_inputs():
    faq_docs = []
    for i in range(st.session_state.num_questions):
        faq_doc = {}
        with st.expander(f"Question {i + 1}", expanded=True):
            categories = st.text_input("Categories *", key=f"category_{i}")
            faq_id = st.text_input("ID *", key=f"faq_id_{i}")
            question = st.text_input("Question *", key=f"question_{i}")
            answer = st.text_area("Answer *", key=f"answer_{i}")
            st.write("Hyperlink:")
            hyperlinks = []
            c1, c2 = st.columns([1, 25])
            c1.button("Add", on_click=handle_add_hyperlink_click, key=f"add_hyperlink_{i}")
            if st.session_state.num_hyperlinks > 1:
                c2.button("Remove", on_click=handle_remove_hyperlink_click, key=f"remove_hyperlink_{i}")
            hyperlink_col, text_col = st.columns(2)
            for j in range(st.session_state.num_hyperlinks):
                with hyperlink_col:
                    edited_hyperlink = st.text_area(f"Hyperlink:", key=f"hyperlink_q{i}_{j}", label_visibility="collapsed", placeholder="https://www.example.com")
                with text_col:
                    edited_hyperlink_text = st.text_area(f"Hyperlink Text:", key=f"hyperlink_text_q{i}_{j}", label_visibility="collapsed", placeholder="Example")

                combined_hyperlink = f"{edited_hyperlink}: {edited_hyperlink_text}"
                hyperlinks.append(combined_hyperlink)
                
        # Add the faq doc to faq_docs
        faq_doc["tags"] = categories.lower().split(", ")
        faq_doc["faq_id"] = faq_id
        faq_doc["question"] = question
        faq_doc["answer"] = answer
        faq_doc["hyperlinks"] = hyperlinks
        faq_docs.append(faq_doc)
        
        
    col1, col2 = st.columns([1, 12]) 
    col1.button("Add question", on_click=handle_add_question_click)
    if st.session_state.num_questions > 1:
        col2.button("Remove question", on_click=handle_remove_question_click)
        
    st.button("Submit", on_click=lambda: on_submit(faq_docs))
def initialize_session_state():
    if 'num_questions' not in st.session_state:
        st.session_state.num_questions = 1
    if 'num_hyperlinks' not in st.session_state:
        st.session_state.num_hyperlinks = 1
    
    
def on_submit(faq_docs):
    for faq_doc in faq_docs:
        if faq_doc["tags"] == "" or faq_doc["faq_id"] == "" or faq_doc["question"] == "" or faq_doc["answer"] == "":
            st.error("Please fill in all the required fields")
            return
        
    session = session_manager.get_session()
    token = session.cookies.get_dict().get("access_token")
    x_api_key = os.getenv("ADMIN_API_KEY")
    response = session.post("/api/create-faq", json={"faq_docs": faq_docs}, headers={"x-api-key": x_api_key}, cookies={"access_token": token})
    if response.status_code == 201:
        success_msg = st.success("FAQs uploaded successfully")
        time.sleep(2)
        success_msg.empty()
        st.session_state.num_questions = 1
        st.session_state.num_hyperlinks = 1
        st.session_state.page = ADMIN_DASHBOARD
        
    else:
        st.error("An error occurred while uploading FAQs")

def handle_add_question_click():
    st.session_state.num_questions += 1
    
def handle_remove_question_click():
    if st.session_state.num_questions > 1:
        st.session_state.num_questions -= 1
        
def handle_add_hyperlink_click():
    st.session_state.num_hyperlinks += 1
    
def handle_remove_hyperlink_click():
    if st.session_state.num_hyperlinks > 1:
        st.session_state.num_hyperlinks -= 1
    
def go_back():
    st.session_state.num_questions = 1
    st.session_state.num_hyperlinks = 1
    st.session_state.page = ADMIN_DASHBOARD