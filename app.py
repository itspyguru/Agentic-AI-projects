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
from tools.agent import create_agent
from multimodal.image_processing import upload_image

load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"

# =========================
# SESSION STATE
# =========================

# set session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "message_images" not in st.session_state:
    st.session_state.message_images = []

st.title("Langchain Chatbot with Gemini")
system_prompt, temperature, max_tokens = create_sidebar(st)
system_message = SystemMessage(content=system_prompt)

# =========================
# DISPLAY CHAT HISTORY
# =========================

for i, message in enumerate(st.session_state["messages"]):
    images = st.session_state.message_images[i] if i < len(st.session_state.message_images) else []
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(message.content)
            for img in images:
                st.image(img)

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
# MULTIMODAL - IMAGE UPLOAD & VISION
# =========================

if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None

uploaded_image = upload_image()
if uploaded_image:
    st.session_state.uploaded_image = uploaded_image

# =========================
# CHAT INPUT
# =========================

user_input = st.chat_input("Type your query here...")
if user_input:
    human_message = HumanMessage(content=user_input)
    st.session_state.messages.append(human_message)
    st.session_state.message_images.append([])
    generated_images: list[str] = []
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
        # =========================
        # RAG RETRIEVAL + GENERATION
        # =========================

        relevant_docs = retrieve_documents(embeddings, user_input)
        context = "\n\nRelevant Documents:\n" + "\n".join([doc.page_content for doc in relevant_docs])
        rag_prompt = f""" Answer the user question using ONLY the provided context.
                Context: {context}
                User Question:{user_input}
        """
        messages = [system_message, HumanMessage(content=rag_prompt)]

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

    else:
        # =========================
        # AGENT EXECUTION
        # =========================

        agent = create_agent(
            llm,
            uploaded_image=st.session_state.get("uploaded_image"),
            generated_images=generated_images,
        )
        steps_box = st.status("Thinking...", expanded=False)
        full_response = ""

        for update in agent.stream(
            {"messages": [system_message, HumanMessage(content=user_input)]},
            stream_mode="updates",
        ):
            for node_update in update.values():
                for m in node_update.get("messages", []):
                    cls = type(m).__name__
                    if getattr(m, "tool_calls", None):
                        for tc in m.tool_calls:
                            steps_box.write(f"**Tool:** `{tc['name']}` — {tc['args']}")
                    elif cls == "ToolMessage":
                        steps_box.write(f"**Result:** {m.text[:300]}…")
                    elif cls == "AIMessage" and m.text:
                        full_response = m.text

        steps_box.update(label="Done", state="complete")
        with st.chat_message("assistant"):
            st.markdown(full_response)
            for img in generated_images:
                st.image(img)

    st.session_state.messages.append(AIMessage(content=full_response))
    st.session_state.message_images.append(generated_images)

