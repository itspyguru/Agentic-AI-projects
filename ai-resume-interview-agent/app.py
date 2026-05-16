import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from services.pdf_parser import extract_pdf_text
from services.resume_extractor import clean_resume_text
from chains.ats_chain import analyze_resume

import os
from dotenv import load_dotenv

load_dotenv()
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(model="gemini-3.1-pro-preview")

def main():
    st.set_page_config(
        page_title="AI Resume Analyzer",
        layout="wide"
    )

    st.title("AI Resume ATS Analyzer")

    uploaded_file = st.file_uploader("Upload a pdf file", type=["pdf"])
    if uploaded_file:
        with st.spinner("Extracting Resume..."):
            raw_text = extract_pdf_text(uploaded_file)
            cleaned_text = clean_resume_text(raw_text)
            if not cleaned_text:
                st.error("Could not extract text from PDF")

        with st.spinner("Analyzing Resume..."):
            result = analyze_resume(cleaned_text, llm)

        st.success("Analysis Complete")
        st.metric("ATS Score", result.ats_score)

        st.subheader("Strengths")
        for item in result.strengths:
            st.write(f"✅ {item}")

        st.subheader("Weaknesses")
        for item in result.weaknesses:
            st.write(f"❌ {item}")

        st.subheader("Missing Keywords")
        for item in result.missing_keywords:
            st.write(f"⚠️ {item}")

        st.subheader("Improvements")
        for item in result.improvements:
            st.write(f"💡 {item}")

        st.subheader("Summary")
        st.write(result.summary)

main()