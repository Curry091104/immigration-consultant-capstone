import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import streamlit as st
from screens import SECURITY_PAGE


def reset_password_button(username: str, disable = False):
    st.button("Reset Password", on_click=lambda: reset_password(username), disabled=disable)
    
def reset_password(username: str):
    pass

def delete_account_button(username: str, disable = False):
    st.button("Delete Account", on_click=lambda: delete_account(username), disabled=disable)
    
def delete_account(username: str):
    pass

def change_password_button(disable = False):
    st.button("Change Password", on_click=redirect_to_change_password_page, disabled=disable)
    
def redirect_to_change_password_page():
    st.session_state.page = SECURITY_PAGE