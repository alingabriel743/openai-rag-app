import streamlit as st
import openai
import os
import tomllib
import sys

__import__('pysqlite3')

sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import sqlite3
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
    st.title("Bine ati venit in aplicatie 💬")
    st.write("""
        Aceasta aplicatie are doua functionalitati principale:
        1. Chat simplu: interactionati cu LLM-ul intr-un mod simplu, conversational.
        2. Chat cu fisiere PDF: incarcati un fisier PDF si interactionati cu LLM-ul pentru a extrage informatii din el.
    """)


    is_production = os.getenv("PRODUCTION", "False") == "True"

    if is_production:
        st.subheader("Introduceti cheia API OpenAI")
        
        if "api_key" not in st.session_state:
            st.session_state.api_key = None
        api_key_input = st.text_input(
            "Cheia API OpenAI",
            type="password",
            placeholder="Introduceti cheia dvs. API",
        )

        if st.button("Valideaza cheia API"):
            if validate_api_key(api_key_input):
                st.session_state.api_key = api_key_input
                st.success("Cheia API este valida! Navigati la functionalitatile aplicatiei.")
            else:
                st.error("Cheia API nu este valida. Incercati din nou.")
        if not st.session_state.api_key:
            st.warning("Introduceti o cheie API valida pentru a accesa functionalitatile aplicatiei.")
        else:
            st.info("Cheia API este configurata. Puteti naviga la paginile aplicatiei.")
    else:
        st.info("Mod dezvoltare: toate paginile sunt disponibile fara autentificare API.")

if __name__ == "__main__":
    main()