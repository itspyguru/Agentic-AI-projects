from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent as build_agent

from processor import process_youtube_video, create_retriever
from prompts import llm_prompts

import os
from dotenv import load_dotenv

load_dotenv()

os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-3.1-pro-preview", temperature=0.7)


_transcript_cache = {}


def _get_transcript(video_url: str) -> str:
    if video_url not in _transcript_cache:
        vector_store = process_youtube_video(video_url)
        retriever = create_retriever(vector_store)
        docs = retriever.invoke("get me the full transcript of this video")
        _transcript_cache[video_url] = "\n\n".join(d.page_content for d in docs)
    return _transcript_cache[video_url]


def _run_prompt(prompt_type: str, transcript: str) -> str:
    prompt = ChatPromptTemplate.from_messages(
        [("human", llm_prompts[prompt_type] + "\n\nTranscript:\n{context}")]
    )
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"context": transcript})


@tool
def fetch_transcript(video_url: str) -> str:
    """Fetch the transcript text for a YouTube video URL."""
    return _get_transcript(video_url)


@tool
def summarize_video(video_url: str) -> str:
    """Generate a clear summary of a YouTube video (main ideas, concepts, takeaway)."""
    return _run_prompt("summary_prompt", _get_transcript(video_url))


@tool
def make_notes(video_url: str) -> str:
    """Generate structured study notes (headings, bullets, key terms) from a YouTube video."""
    return _run_prompt("notes_prompt", _get_transcript(video_url))


@tool
def make_quiz(video_url: str) -> str:
    """Generate 10 quiz questions (MCQs + short answers, with answers) from a YouTube video."""
    return _run_prompt("quiz_prompt", _get_transcript(video_url))


@tool
def make_flashcards(video_url: str) -> str:
    """Generate Q/A flashcards from a YouTube video."""
    return _run_prompt("flashcard_prompt", _get_transcript(video_url))


def create_agent(system_prompt=""):
    tools = [
        fetch_transcript,
        summarize_video,
        make_notes,
        make_quiz,
        make_flashcards,
    ]

    return build_agent(
        model=llm,
        tools=tools,
        system_prompt=(
            system_prompt +
            """
            You are a YouTube study assistant. Given a YouTube video URL, use the tools to produce study material the user asks for.
            To fetch the raw transcript text of a video use the fetch_transcript tool. Do not use it for any other purpose.
            When the user asks for a summary of a video, use the summarize_video tool. Do not use it for any other purpose.
            When the user asks for notes / study notes from a video, use the make_notes tool. Do not use it for any other purpose.
            When the user asks for a quiz / questions from a video, use the make_quiz tool. Do not use it for any other purpose.
            When the user asks for flashcards from a video, use the make_flashcards tool. Do not use it for any other purpose.
            If the user asks for multiple artifacts (e.g. summary and flashcards), call the relevant tools and combine their outputs in your reply.
            Always pass the YouTube URL provided by the user to the tools verbatim.
            """
        )
    )


if __name__ == "__main__":
    agent = create_agent()
    youtube_video_url = "https://www.youtube.com/watch?v=zjkBMFhNj_g"
    result = agent.invoke({
        "messages": [
            ("human", f"For this video {youtube_video_url}, give me a summary and flashcards.")
        ]
    })
    print(result["messages"][-1].content)
