from langchain.tools import tool
from multimodal.image_processing import analyze_image, generate_image

def analyze_image_tool(llm, uploaded_image=None):
    @tool
    def analyze_uploaded_image(question: str) -> str:
        """Answer a question about the image the user uploaded in the sidebar.
        Use ONLY when the user has uploaded an image and is asking about its contents."""
        if not uploaded_image:
            return "No image has been uploaded by the user."
        try:
            if hasattr(uploaded_image, "seek"):
                uploaded_image.seek(0)
            result = analyze_image(uploaded_image, question, llm)
            return result.text
        except Exception as e:
            return f"Error analyzing image: {e}"

    return analyze_uploaded_image

def generate_image_tool(generated_images=None):
    if generated_images is None:
        generated_images = []

    @tool("generate_image_tool")
    def _generate_image(prompt: str) -> str:
        """Generate an image from a descriptive text prompt. The image is shown to
        the user automatically. Use when the user asks to create, draw, design, or
        visualize something."""
        try:
            path = generate_image(prompt)
            generated_images.append(path)
            return "Image generated and shown to the user."
        except Exception as e:
            return f"Error generating image: {e}"

    return _generate_image
