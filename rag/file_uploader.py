import os
import tempfile
import streamlit as st
from langchain_community.document_loaders import (
      PyPDFLoader, TextLoader, Docx2txtLoader, CSVLoader,                                       
      UnstructuredMarkdownLoader,                                                               
  )

LOADERS = {     
      ".pdf":  PyPDFLoader,
      ".txt":  TextLoader,                                                                      
      ".md":   UnstructuredMarkdownLoader,
      ".docx": Docx2txtLoader,                                                                  
      ".csv":  CSVLoader,                                                                       
  }

def upload_file():
    uploaded_file = st.file_uploader("Upload a file", type=["pdf", "txt", "md", "docx", "csv"])
    if uploaded_file is None:
        return None
    
    ext = os.path.splitext(uploaded_file.name)[1].lower()                                         
    loader_cls = LOADERS.get(ext)                                                                 
    if loader_cls is None:
        st.sidebar.error(f"Unsupported file type: {ext}")                                         
        return None

    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name

    loader = loader_cls(tmp_file_path)
    documents = loader.load()
    st.sidebar.success(f"Loaded {len(documents)} pages from the file.")
    st.write(documents)
    return documents