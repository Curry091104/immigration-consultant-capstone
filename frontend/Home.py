import streamlit as st

def home_page():
    configue()
    st.title("IRIS - Home Page")

def configue():
    st.set_page_config(
        page_title="IRIS - Home Page",
        page_icon="🍁",
        layout="wide",
    )

        
if __name__ == "__main__":
    home_page()