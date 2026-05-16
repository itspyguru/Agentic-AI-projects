import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableParallel
from services.pdf_parser import extract_pdf_text
from services.resume_extractor import clean_resume_text
from chains.ats_chain import analyze_resume_chain
from chains.skill_chain import extract_skills_from_resume_chain

import os
from dotenv import load_dotenv

load_dotenv()
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(model="gemini-3.1-pro-preview")

SECTIONS = ["ATS Analysis", "Skills", "Mock Interview"]

for key in ("resume_text", "ats", "skills", "source_file"):
    st.session_state.setdefault(key, None)


def run_analysis(cleaned_text: str):
    ats_chain = analyze_resume_chain(cleaned_text, llm)
    skill_chain = extract_skills_from_resume_chain(cleaned_text, llm)
    parallel_chain = RunnableParallel(ats=ats_chain, skills=skill_chain)
    result = parallel_chain.invoke({})
    st.session_state.ats = result["ats"]
    st.session_state.skills = result["skills"]


def render_ats(ats):
    st.header("ATS Analysis")
    st.metric("ATS Score", ats.ats_score)

    st.subheader("Strengths")
    for item in ats.strengths:
        st.write(f"✅ {item}")

    st.subheader("Weaknesses")
    for item in ats.weaknesses:
        st.write(f"❌ {item}")

    st.subheader("Missing Keywords")
    for item in ats.missing_keywords:
        st.write(f"⚠️ {item}")

    st.subheader("Improvements")
    for item in ats.improvements:
        st.write(f"💡 {item}")

    st.subheader("Summary")
    st.write(ats.summary)


def render_skills(skills_result):
    st.header("Skills Overview")

    if skills_result.candidate_name:
        st.markdown(f"**Candidate:** {skills_result.candidate_name}")
    if skills_result.target_role:
        st.markdown(f"**Target Role:** {skills_result.target_role}")

    st.subheader("Profile Summary")
    st.write(skills_result.extraction_summary)

    st.subheader("Skills by Category")
    skill_groups = {
        "Programming Languages": skills_result.skills.programming_languages,
        "Frameworks & Libraries": skills_result.skills.frameworks_and_libraries,
        "Databases": skills_result.skills.databases,
        "Cloud & DevOps": skills_result.skills.cloud_and_devops,
        "Tools & Platforms": skills_result.skills.tools_and_platforms,
        "AI & ML": skills_result.skills.ai_and_ml,
        "Domains & Concepts": skills_result.skills.domains_and_concepts,
        "APIs & Protocols": skills_result.skills.apis_and_protocols,
    }
    for group_name, items in skill_groups.items():
        if not items:
            continue
        with st.expander(f"{group_name} ({len(items)})"):
            for skill in items:
                st.markdown(
                    f"- **{skill.name}** — "
                    f"`{skill.confidence.value}` · `{skill.proficiency_signal.value}`  \n"
                    f"  _{skill.evidence}_"
                )

    if skills_result.interview_focus_areas:
        st.subheader("Interview Focus Areas")
        for focus in skills_result.interview_focus_areas:
            st.markdown(
                f"🎯 **{focus.skill}** (`{focus.suggested_depth.value}`)  \n"
                f"{focus.reason}"
            )

    if skills_result.skills_flat_list:
        st.subheader("All Skills")
        st.markdown(" ".join(f"`{s}`" for s in skills_result.skills_flat_list))



def main():
    st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

    with st.sidebar:
        st.title("AI Resume Analyzer")
        uploaded_file = st.file_uploader("Upload a pdf file", type=["pdf"])

        if uploaded_file and uploaded_file.name != st.session_state.source_file:
            with st.spinner("Extracting Resume..."):
                raw_text = extract_pdf_text(uploaded_file)
                cleaned_text = clean_resume_text(raw_text)
            if not cleaned_text:
                st.error("Could not extract text from PDF")
                return
            st.session_state.resume_text = cleaned_text
            st.session_state.source_file = uploaded_file.name
            with st.spinner("Analyzing Resume..."):
                run_analysis(cleaned_text)
            st.success("Analysis complete")

        section = st.radio("Section", SECTIONS, disabled=st.session_state.ats is None)

    if st.session_state.ats is None:
        st.title("AI Resume ATS Analyzer")
        st.info("Upload a PDF resume from the sidebar to get started.")
        return

    if section == "ATS Analysis":
        render_ats(st.session_state.ats)
    elif section == "Skills":
        render_skills(st.session_state.skills)


main()
