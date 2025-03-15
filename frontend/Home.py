import streamlit as st
from auth.SessionManager import SessionManager
import base64

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
    main_content()
    

def configue():
    st.sidebar.write("IRIS")

def main_content():
    logo_path = "static/IRIS.png"
    logo = base64.b64encode(open(logo_path, 'rb').read()).decode()
    background_path = "static/bg.png"
    background = base64.b64encode(open(background_path, 'rb').read()).decode()
    st.html(f"""
        <div style="display: flex; flex-direction: column; height: 100vh; margin: 0; overflow: hidden;">
            <!-- Logo Section -->
            <div style="display: flex; justify-content: center; align-items: center; flex-shrink: 0;">
                <img src="data:image/png;base64,{logo}" style="width: 250px; height: 250px; margin-top: 10px;">
            </div>
            
            <!-- Background Section -->
            <div style="flex-grow: 1; background-image: url('data:image/png;base64,{background}'); 
                        background-size: cover; background-position: center; background-repeat: no-repeat;">
            </div>
        </div>
    """)

        

session_manager = SessionManager()
home_page()
