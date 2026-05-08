from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser

import os
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

from sidebar import create_sidebar

load_dotenv()
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"

st.title("Langchain Chatbot with Gemini")
system_prompt, temperature, max_tokens = create_sidebar(st)

# =========================
# SESSION STATE
# =========================

# set session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# DISPLAY CHAT HISTORY
# =========================

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# =========================
# CHAT INPUT
# =========================

user_input = st.chat_input("Type your query here...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").markdown(user_input)

    # gemini ai
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-pro-preview", 
        temperature=temperature, 
        max_tokens=max_tokens, 
        streaming=True
    )
    parser = StrOutputParser()
    chain = llm | parser

    history = []
    # System message
    history.append(
        SystemMessage(
            content=system_prompt
        )
    )

    # Previous conversation
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            history.append(
                HumanMessage(content=msg["content"])
            )

        elif msg["role"] == "assistant":
            history.append(
                AIMessage(content=msg["content"])
            )

    # Assistant response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        # Stream response
        for chunk in chain.stream(history):
            full_response += chunk
            response_placeholder.markdown(
                full_response + "▌"
            )
        response_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

