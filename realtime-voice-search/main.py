from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    cli,
    function_tool,
)
from livekit.plugins import google, silero

# Load the agent's own .env first, then fall back to the repo-root .env
# (where GOOGLE_API_KEY lives). Existing vars are never overridden.
load_dotenv()


@function_tool
async def google_search(query: str) -> str:
    """Search the web with Google and return a text answer.

    Args:
        query: What to search for (e.g. "latest news on AI").
    """
    # Reads GOOGLE_API_KEY or GEMINI_API_KEY from the environment.
    client = genai.Client()

    response = client.models.generate_content(
        model="gemini-3.1-pro-preview",
        contents=query,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
        ),
    )

    return response.text


class SearchAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
            You are a helpful voice assistant that can search the web.

            When the user asks about latest news, current events, stock
            prices, weather, or any recent information, ALWAYS call the
            google_search tool first, then answer based on its result.

            When you join, briefly greet the user and tell them you can
            search the web.
            """,
            tools=[google_search],
        )


async def entrypoint(ctx: JobContext):
    session = AgentSession(
        llm=google.realtime.RealtimeModel(
            model="gemini-3.1-flash-live-preview",
            voice="Puck",
        ),
        vad=silero.VAD.load(),
    )

    await session.start(
        room=ctx.room,
        agent=SearchAgent(),
    )


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )
