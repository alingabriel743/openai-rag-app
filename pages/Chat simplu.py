import streamlit as st
import openai
import os
from dotenv import load_dotenv
from datetime import datetime


# load_dotenv()

openai.api_key = st.secrets['OPENAI_API_KEY']
MODEL_NAME = st.secrets['MODEL_NAME']
PRODUCTION = st.secrets['PRODUCTION']

def generate_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Esti un asistent care raspunde la intrebarile utilizatorilor. Vei raspunde in limba utilizatorului."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"A aparut o eroare: {str(e)}"

def main():

     # Verificam daca suntem in modul productie
    is_production = PRODUCTION == "True" == "True"

    if is_production:
        # Verificam daca cheia API este setata
        if "api_key" not in st.session_state or not st.session_state.api_key:
            st.error("Nu aveti o cheie API valida. Reveniti la pagina principala pentru a introduce una.")
            return
    
    st.set_page_config(
        page_title="Chat simplu cu LLM-ul",
        page_icon="💬",
        layout="wide",
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "history" not in st.session_state:
        st.session_state.history = []
    if "selected_session_index" not in st.session_state:
        st.session_state.selected_session_index = None

    if not st.session_state.history:
        new_session = {
            "messages": [],
            "name": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        st.session_state.history.append(new_session)
        st.session_state.selected_session_index = 0

    query_params = st.query_params
    session_param = query_params.get("session", "new")  

    if session_param == "new":
        st.session_state.messages = []
        st.session_state.selected_session_index = len(st.session_state.history) - 1
    elif session_param.isdigit():
        session_index = int(session_param)
        if session_index < len(st.session_state.history):
            st.session_state.selected_session_index = session_index
            st.session_state.messages = st.session_state.history[session_index]["messages"]

    with st.sidebar:
        st.header("Istoric sesiuni")

        session_options = [
            f"{i + 1}. {session['name']}"  
            for i, session in enumerate(st.session_state.history)
        ]

        selected_session = st.selectbox(
            "Selectează o sesiune",
            options=session_options,
            index=st.session_state.selected_session_index or 0,
            key="session_selectbox",
        )

        new_session_index = int(selected_session.split(".")[0]) - 1
        if new_session_index != st.session_state.selected_session_index:
            st.session_state.selected_session_index = new_session_index
            st.session_state.messages = st.session_state.history[new_session_index]["messages"]
            st.query_params = {"session": str(new_session_index)}
            st.rerun() 

        if st.button("Începe o sesiune nouă"):
            st.session_state.messages = [] 
            st.session_state.selected_session_index = len(st.session_state.history) 
            new_session = {
                "messages": [],
                "name": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            st.session_state.history.append(new_session)
            st.query_params = {"session": str(len(st.session_state.history) - 1)} 
            st.rerun()  

        if st.button("Șterge istoricul"):
            st.session_state.history = []
            st.session_state.messages = []
            st.session_state.selected_session_index = None
            st.success("Istoricul a fost șters!")
            st.query_params = {"session": "cleared"} 
            st.rerun()  

    if st.session_state.messages:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if prompt := st.chat_input("Scrieți mesajul aici..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Răspunde..."):
                response = generate_response(prompt)
                st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

        if st.session_state.selected_session_index is not None:
            current_session = st.session_state.history[st.session_state.selected_session_index]
            current_session["messages"] = st.session_state.messages.copy()

if __name__ == "__main__":
    main()
