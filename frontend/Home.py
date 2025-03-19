import streamlit as st
from auth.SessionManager import SessionManager
import base64
from pathlib import Path

st.set_page_config(
        page_title="IRIS",
        page_icon="🍁",
        layout="wide",
        initial_sidebar_state="collapsed"
)
st.logo(
    "static/iris-side.png",
    size="large"
)

def home_page():
    configue()
    read_css()
    main_content()
    

def configue():
    pass
    
def read_css():
    css_path = Path(__file__).parent / "styles.css"
    with open(css_path, "r") as file:
        st.markdown(f"<style>{file.read()}</style>", unsafe_allow_html=True)
def main_content():
    logo_path = "static/IRIS.png"
    logo = base64.b64encode(open(logo_path, 'rb').read()).decode()
    background_path = "static/bg.png"
    background = base64.b64encode(open(background_path, 'rb').read()).decode()
    st.markdown(f"""
        <style>
        div.stMainBlockContainer.block-container.st-emotion-cache-t1wise.eht7o1d4 {{
            background-image: url('data:image/png;base64,{background}');
            background-repeat: no-repeat;
            background-attachment: fixed;
            height: 100vh;
        }}
        </style>
    """, unsafe_allow_html=True)
    html_code = f"""
        <!-- Logo Section -->
        <div style="display: flex; justify-content: center; align-items: center; flex-shrink: 0;">
            <img src="data:image/png;base64,{logo}" style="width: 250px; height: 250px; margin-top: 10px;">
        </div>
        <!-- Chat Now Button -->
        <div class="container">
            <h1 style="font-family: 'Calistoga', cursive; font-size: 3em; color: white; margin-top: 30px;">Hi there,</h1>
            <form action="http://localhost:8501/Get_Consultation_with_IRIS">
                <button class="chat-now-btn" type="submit">Chat Now</button>
            </form>
        </div>
    """
    
    st.markdown(html_code, unsafe_allow_html=True)
    

        

session_manager = SessionManager()
home_page()
