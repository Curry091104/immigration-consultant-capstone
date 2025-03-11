import streamlit as st
from auth.SessionManager import SessionManager

def home_page():
    configue()
    st.title("IRIS - Home Page")

def configue():
    st.set_page_config(
        page_title="IRIS - Home Page",
        page_icon="🍁",
        layout="wide",
    )

        

session_manager = SessionManager()
home_page()
