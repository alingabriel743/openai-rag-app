import streamlit as st
import openai
import os
import tomllib
import sqlite3
import sys

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

PRODUCTION = st.secrets['PRODUCTION']

st.set_page_config(
    page_title="Streamlit RAG App",
    page_icon="💬",
    layout="wide"
)

def validate_api_key(api_key):
    try:
        openai.api_key = api_key
        openai.Model.list() 
        return True
    except Exception:
        return False

def main():
    st.title("Welcome to the Application 💬")
    st.write("""
        This application has two main functionalities:
        1. **Simple Chat**: Interact with the LLM in a simple, conversational way.
        2. **Chat with PDF files**: Upload a PDF file and interact with the LLM to extract information from it.
    """)

    is_production = PRODUCTION == "True"

    if is_production:
        st.subheader("Enter OpenAI API Key")
        
        if "api_key" not in st.session_state:
            st.session_state.api_key = None
        api_key_input = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="Enter your API key",
        )

        if st.button("Validate API Key"):
            if validate_api_key(api_key_input):
                st.session_state.api_key = api_key_input
                st.success("The API key is valid! Navigate to the application functionalities.")
            else:
                st.error("The API key is not valid. Please try again.")
        if not st.session_state.api_key:
            st.warning("Please enter a valid API key to access the application's functionalities.")
        else:
            st.info("The API key is configured. You can now navigate to the application pages.")
    else:
        st.info("Development mode: All pages are available without API authentication.")

if __name__ == "__main__":
    main()
