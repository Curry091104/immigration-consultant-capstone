import os 
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from admin_stuff.pdf_upload_pages.upload_pdf_page import upload_pdf_page
from admin_stuff.pdf_upload_pages.edit_extracted_pdf_page import edit_extracted_pdf_page
from screens import *
from streamlit_card import card

def admin_run():
    #! Check authentication
    initialize_session_state()
    st.set_page_config(page_title="Admin", page_icon="🔒", layout="wide")
    if st.session_state.page == ADMIN_DASHBOARD:
        admin_dashboard()
    elif st.session_state.page == UPLOAD_PDF_PAGE:
        upload_pdf_page()
    elif st.session_state.page == EDIT_EXTRACTED_PDF_PAGE:
        edit_extracted_pdf_page()
    st.sidebar.button("🚪Logout")
    
        
def initialize_session_state():
    if 'page' not in st.session_state:
        st.session_state.page = ADMIN_DASHBOARD
        
def on_card_click(page_name):
    st.session_state.page = page_name
    
def admin_dashboard():
    with st.container():
        
        # Custom CSS to center the title
        st.markdown(
            """
            <style>
            .title {
                text-align: center;
                font-size: 36px;
                font-weight: bold;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Display the centered title
        st.markdown('<h1 class="title">Admin Dashboard</h1>', unsafe_allow_html=True)
        
        p1, p2 = st.columns(2)
        
        with p1:
            card(
                title="Upload PDF Document",
                text="",
                on_click=lambda: on_card_click("upload_pdf_page"),
            )
            
        with p2:
            card(
                title = "Upload FAQ",
                text = "",
                on_click = lambda: on_card_click("upload_faq_page"),
            )
            
        p3, p4 = st.columns(2)
        
        with p3:
            card(
                title = "Manage Accounts",
                text = "",
                on_click = lambda: on_card_click("manage_accounts_page"),
            )
            
        with p4:
            card(
                title = "Security Settings",
                text = "",
                on_click = lambda: on_card_click("security_page"),
            )
    
if __name__ == "__main__":
    admin_run()