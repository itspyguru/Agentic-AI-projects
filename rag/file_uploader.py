import tempfile
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader

def upload_file():
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    if uploaded_file is None:
        return None
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name

    loader = PyPDFLoader(tmp_file_path)
    documents = loader.load()
    st.sidebar.success(f"Loaded {len(documents)} pages from the PDF.")
    st.write(documents)
    return documents