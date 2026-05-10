import os
import streamlit as st
import tempfile

from langchain_community.document_loaders import (
    PyPDFLoader, TextLoader, Docx2txtLoader, CSVLoader,UnstructuredMarkdownLoader
)

LOADERS = {
    ".pdf" : PyPDFLoader,
    ".txt" : TextLoader,
    ".docx" : Docx2txtLoader,
    ".csv" : CSVLoader,
    ".md" : UnstructuredMarkdownLoader
}

def upload_file():
    upload_files = st.file_uploader("Upload a file", type=["pdf", "txt", "docx", "csv", "md"],
                                   accept_multiple_files=True)
    if upload_files is None:
        return None
    
    all_docs = []
    for upload_file in upload_files:
        ext = os.path.splitext(upload_file.name)[1]
        loader_cls = LOADERS.get(ext)
        if loader_cls is None:
            st.sidebar.error("Unsupported file type!")
            return None

        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(upload_file.read())
            tmp_file_path = tmp_file.name

        loader = loader_cls(tmp_file_path)
        documents = loader.load()
        all_docs.extend(documents)

    st.sidebar.success(f"Files uploaded successfully with {len(all_docs)} pages!")
    return all_docs