import sys
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import sqlite3

import streamlit as st
import openai
import os
from dotenv import load_dotenv
from utils.chromadb_utils import create_or_get_collection, add_documents_to_collection, query_collection, sanitize_collection_name
from utils.pdf_processing import extract_pdf_text, split_text_into_chunks
import tomllib



# load_dotenv()



openai.api_key = st.secrets['OPENAI_API_KEY']
MODEL_NAME = st.secrets['MODEL_NAME']
PRODUCTION = st.secrets['PRODUCTION']

def embed_text(text):
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response['data'][0]['embedding']


def main():
    # Verificam daca suntem in modul productie
    is_production = PRODUCTION == "True"

    if is_production:
        # Verificam daca cheia API este setata
        if "api_key" not in st.session_state or not st.session_state.api_key:
            st.error("Nu aveti o cheie API valida. Reveniti la pagina principala pentru a introduce una.")
            return
    
    st.set_page_config(
        page_title="Chat cu PDF-ul 📄",
        page_icon="📄",
        layout="wide",
    )

    st.title("Chat cu PDF-ul 📄")


    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "collection_name" not in st.session_state:
        st.session_state.collection_name = None
    if "previous_file" not in st.session_state:
        st.session_state.previous_file = None


    uploaded_file = st.file_uploader("Incarcati un fisier PDF", type=["pdf"])
    if uploaded_file is not None:

        if uploaded_file.name != st.session_state.previous_file:
            st.session_state.messages = []
            st.session_state.collection_name = None
            st.session_state.previous_file = uploaded_file.name

            with st.spinner("Se proceseaza PDF-ul..."):
                pdf_text = extract_pdf_text(uploaded_file)

                if st.checkbox("Arata textul PDF-ului"):
                    st.text_area("Text extras din PDF", pdf_text, height=300)

                collection_name = sanitize_collection_name(f"pdf_{uploaded_file.name}")
                st.session_state.collection_name = collection_name
                collection = create_or_get_collection(collection_name)


                if not collection.get()["documents"]:
                    chunks = split_text_into_chunks(pdf_text)
                    embeddings = [embed_text(chunk) for chunk in chunks]
                    add_documents_to_collection(collection, chunks, embeddings)
                    st.success("Textul din PDF a fost indexat!")


    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


    if prompt := st.chat_input("Scrieti o intrebare despre PDF aici..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)


        if st.session_state.collection_name:
            collection = create_or_get_collection(st.session_state.collection_name)
            query_embedding = embed_text(prompt)
            relevant_chunks = query_collection(collection, query_embedding)

            if relevant_chunks:
                context = "\n\n".join(relevant_chunks)
                prompt_with_context = f"Intrebare: {prompt}\n\nConținut relevant din PDF:\n{context}\n\nRaspuns:"
                with st.chat_message("assistant"):
                    with st.spinner("Se genereaza raspunsul..."):
                        response = openai.ChatCompletion.create(
                            model="gpt-4o-mini-2024-07-18",
                            messages=[
                                {"role": "system", "content": "Esti un asistent care raspunde pe baza unui PDF."},
                                {"role": "user", "content": prompt_with_context},
                            ],
                        )
                        answer = response['choices'][0]['message']['content'].strip()
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                st.warning("Nu s-a gasit continut relevant in PDF pentru aceasta intrebare.")

if __name__ == "__main__":
    main()