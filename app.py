from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser

import os
import streamlit as st
from dotenv import load_dotenv

from sidebar import create_sidebar
from rag.file_uploader import upload_file
from rag.text_splitter import split_documents
from rag.vector_store import create_vector_store
from rag.retriever import retrieve_documents

load_dotenv()
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"

# =========================
# SESSION STATE
# =========================

# set session state
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Langchain Chatbot with Gemini")
system_prompt, temperature, max_tokens = create_sidebar(st)
system_message = SystemMessage(content=system_prompt)

# =========================
# DISPLAY CHAT HISTORY
# =========================

for messages in st.session_state["messages"]:
    if isinstance(messages, HumanMessage):
        with st.chat_message("user"):
            st.markdown(messages.content)
    elif isinstance(messages, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(messages.content)

# =========================
# RAG - FILE UPLOAD, SPLIT, VECTOR STORE
# =========================

chunks, embeddings = None, None
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if documents:= upload_file():
    chunks = split_documents(documents) if documents else None
    embeddings = create_vector_store(chunks) if chunks else None
    st.session_state.vector_store = embeddings

# =========================
# CHAT INPUT
# =========================

user_input = st.chat_input("Type your query here...")
if user_input:
    human_message = HumanMessage(content=user_input)
    st.session_state.messages.append(human_message)
    with st.chat_message("user"):
        st.markdown(human_message.content)

    # gemini ai
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-pro-preview", 
        temperature=temperature, 
        max_tokens=max_tokens, 
        streaming=True
    )

    if embeddings:
        relevant_docs = retrieve_documents(embeddings, user_input)
        context = "\n\nRelevant Documents:\n" + "\n".join([doc.page_content for doc in relevant_docs])
        rag_prompt = f""" Answer the user question using ONLY the provided context.
                Context: {context}
                User Question:{user_input}
        """
        messages = [system_message, HumanMessage(content=rag_prompt)]
    else:
        messages = [system_message] + st.session_state["messages"]

    parser = StrOutputParser()
    chain = llm | parser
    response = chain.stream(messages)

    # Assistant response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        # Stream response
        for chunk in response:
            full_response += chunk
            response_placeholder.markdown(
                full_response + "▌"
            )
        response_placeholder.markdown(full_response)

    st.session_state.messages.append(AIMessage(content=full_response))

