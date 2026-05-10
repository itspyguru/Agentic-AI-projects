import os
import uuid
import base64
from pathlib import Path
import streamlit as st
from io import BytesIO
from PIL import Image
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from google import genai
from dotenv import load_dotenv

load_dotenv()
if api_key := os.getenv("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = api_key

client = genai.Client()

GENERATED_DIR = Path(__file__).resolve().parent.parent / "generated_images"
GENERATED_DIR.mkdir(exist_ok=True)

def upload_image():
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        return uploaded_file
    return None

def convert_image_to_base64(image_file):
    image = Image.open(image_file)
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def analyze_image(uploaded_file, prompt, llm):
    base64_image = convert_image_to_base64(uploaded_file)
    response = llm.invoke([
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
            ]
        )
    ])
    return AIMessage(content=response.text)

def generate_image(prompt: str) -> str:
    response = client.models.generate_content(
        model="gemini-3.1-flash-image-preview",
        contents=[prompt],
    )
    for part in response.parts or []:
        if part.inline_data is not None:
            image = part.as_image()
            if image is None:
                continue
            path = GENERATED_DIR / f"{uuid.uuid4().hex}.png"
            image.save(str(path))
            return str(path)
    raise RuntimeError("Model did not return an image.")