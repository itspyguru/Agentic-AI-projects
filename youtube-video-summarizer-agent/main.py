from langchain_core.runnables import RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from processor import process_youtube_video, create_retriever
from prompts import llm_prompts


import os
from dotenv import load_dotenv

load_dotenv()

os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-3.1-pro-preview", temperature=0.7)

def create_context(prompt):
    return ChatPromptTemplate.from_messages([("human", prompt + "\n\nTranscript:\n{context}")])

def create_chain(prompt_type):
    prompt = create_context(llm_prompts[prompt_type])
    chain = prompt | llm | StrOutputParser()
    return chain


def main(video_url):
    vector_store = process_youtube_video(video_url)
    retriever = create_retriever(vector_store)
    docs = retriever.invoke("get me the full transcript of this video")
    full_transcript = "\n\n".join([doc.page_content for doc in docs])

    summary_chain = create_chain("summary_prompt")
    notes_chain = create_chain("notes_prompt")
    quiz_chain = create_chain("quiz_prompt")
    flashcard_chain = create_chain("flashcard_prompt")


    parallel_chain = RunnableParallel(
        summary=summary_chain,
        notes=notes_chain,
        quiz=quiz_chain,
        flashcards=flashcard_chain
    )

    result = parallel_chain.invoke({
        "context": full_transcript
    })

    return result

youtube_video_url = "https://www.youtube.com/watch?v=zjkBMFhNj_g"
result = main(youtube_video_url)
print(result)