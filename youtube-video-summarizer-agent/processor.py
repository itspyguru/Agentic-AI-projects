from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from youtube import get_youtube_video_trasncript

def split_text(text, chunk_size=1000, chunk_overlap=200):
    docs = [Document(page_content=text)]
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    splitted_text = text_splitter.split_documents(docs)
    return splitted_text

def create_vector_store(chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
    vector_store = FAISS.from_documents(chunks, embeddings)
    return vector_store

def process_youtube_video(url):
    trasncript = get_youtube_video_trasncript(url)
    chunks = split_text(trasncript)
    vector_store = create_vector_store(chunks)
    return vector_store

def create_retriever(vector_store):
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 8}
    )
    return retriever