import streamlit as st
import requests
import json
import asyncio
import aiohttp



st.set_page_config(
        page_title="IRIS",
        page_icon="🍁",
        layout="wide"
)
st.logo(
    "static/iris-side.png",
    size="large"
)

st.markdown(
    """
    <style>
    [data-testid="stChatMessageContent"] p{
        font-size: 1.3rem;
    }
    
    .ea2tk8x2 {
        width: 60px;
        height: 60px; 
        font-size: 2rem;
    }
    </style>
    """, unsafe_allow_html=True
)

def get_consultation_page():
    get_iris_id()
        
    if st.session_state.error_chat:
        st.session_state.disabled_chat = True
        
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=message["avatar"]):
            st.markdown(message["text"])
        
    if not any(message["text"] == "Hello! I am IRIS, your virtual assistant. I am here to help you with your queries. Please type your query below." for message in st.session_state.messages):
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown("Hello! I am IRIS, your virtual assistant. I am here to help you with your queries. Please type your query below.")
        st.session_state.messages.append({"role": "assistant", "text": "Hello! I am IRIS, your virtual assistant. I am here to help you with your queries. Please type your query below.", "avatar": "🤖"})
    
    if prompt := st.chat_input("Type your message here...", disabled=st.session_state.disabled_chat):
        try:
            if any(word in prompt.lower() for word in ["bye", "goodbye", "exit", "quit", "thank", "thanks"]):
                with st.chat_message("human", avatar="🧑‍🎓"):
                    st.markdown(prompt)
                st.session_state.messages.append({"role": "human", "text": prompt, "avatar": "🧑‍🎓"})
                
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown("Please don’t hesitate to use our live chat service again in future – we’re always here to help. I hope to hear from you soon. Take care!")
                st.session_state.messages.append({"role": "assistant", "text": "Please don’t hesitate to use our live chat service again in future – we’re always here to help. I hope to hear from you soon. Take care!", "avatar": "🤖"})
                
                st.session_state.disabled_chat = True
                return
            
            with st.chat_message("human", avatar="🧑‍🎓"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "human", "text": prompt, "avatar": "🧑‍🎓"})
            
            waiting_message = st.empty()
            waiting_message.markdown("IRIS is typing...")
            
            response = asyncio.run(get_iris_response(prompt))
            
            
            with st.chat_message("assistant", avatar="🤖"):
                waiting_message.empty()
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "text": response, "avatar": "🤖"})
            
            
        except Exception as e:
            st.session_state.error_chat = True
            st.session_state.disabled_chat = True
            st.error(f"An error occurred: {e}")
            st.write("Please refresh the page and try again.")
            return

    
def get_iris_id():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        
    if 'error_chat' not in st.session_state:
        st.session_state.error_chat = False
    
    if 'disabled_chat' not in st.session_state:
        st.session_state.disabled_chat = False
        
    response = requests.get("http://localhost:8000/api/iris-id")
    if 'iris_id' not in st.session_state:
        st.session_state.iris_id = response.json()["iris_id"]
        

async def get_iris_response(input):
    if st.session_state.iris_id is None:
        st.error("Error: Could not connect to IRIS")
        return
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://localhost:8000/iris/{st.session_state.iris_id}?user_input={input}") as response:
            response = await response.json()
            response = response["agent_response"]
            if '"' in response:
                if response[0] == '"':
                    response = response[1:]
                if response[-1] == '"':
                    response = response[:-1]
            if '`' in response:
                response = response.replace('`', '')
            return response
        


get_consultation_page()