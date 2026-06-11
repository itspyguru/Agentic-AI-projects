"""Post-call summariser.

Turns a finished call's transcript into a short summary using a lightweight
Gemini text model, then appends both the summary and the full transcript to a
log file under sales-agent/logs/ for later reference.

This is deliberately NOT a LiveKit voice Agent — there's no second voice on the
call. It's a plain async helper that the main agent runs once, at call end, via
a shutdown callback. Reuses GOOGLE_API_KEY from .env (already loaded in agent.py).
"""

import datetime
from pathlib import Path

from google import genai

# Where the per-call log files land.
LOG_DIR = Path(__file__).parent / "logs"

# Cheap text model for the summary — separate from the realtime voice model.
# Change this if you prefer a different Gemini text model.
SUMMARY_MODEL = "gemini-2.5-flash"


def transcript_to_text(history) -> str:
    """Flatten a LiveKit ChatContext (session.history) into a plain transcript.

    Produces lines like "Lead: ..." / "Agent: ...". Non-message items
    (tool calls, tool results) are skipped — we only want the spoken turns.
    """
    lines: list[str] = []
    for item in history.items:
        role = getattr(item, "role", None)
        if role not in ("user", "assistant"):
            continue
        content = getattr(item, "content", None)
        if not content:
            continue
        # content is a list of parts; keep only the plain-text parts.
        text = " ".join(p for p in content if isinstance(p, str)).strip()
        if not text:
            continue
        speaker = "Lead" if role == "user" else "Agent"
        lines.append(f"{speaker}: {text}")
    return "\n".join(lines)


async def summarize_call(transcript: str) -> str:
    """Ask Gemini for a short, structured summary of the call transcript."""
    if not transcript.strip():
        return "No conversation was captured for this call."

    client = genai.Client()  # reads GOOGLE_API_KEY from the environment
    prompt = (
        "You are a sales-operations assistant. Summarise this outbound sales "
        "call transcript as a few short bullet points. Capture: who the lead "
        "is and their interest level, which products/plans were discussed, any "
        "objections or concerns, whether a callback was scheduled, and the "
        "agreed next step. Be concise and factual.\n\n"
        f"Transcript:\n{transcript}"
    )
    resp = await client.aio.models.generate_content(
        model=SUMMARY_MODEL,
        contents=prompt,
    )
    return (resp.text or "").strip() or "Summary unavailable."


def write_call_log(summary: str, transcript: str, lead_id: int | None = None) -> Path:
    """Append the summary + full transcript to a timestamped log file.

    Returns the path written. Caller passes lead_id when known, for the header.
    """
    LOG_DIR.mkdir(exist_ok=True)
    now = datetime.datetime.now()
    path = LOG_DIR / f"call-{now:%Y%m%d-%H%M%S}.log"

    header = f"Call summary — {now:%Y-%m-%d %H:%M:%S}"
    if lead_id is not None:
        header += f" — lead {lead_id}"

    path.write_text(
        f"{header}\n"
        f"{'=' * len(header)}\n\n"
        f"SUMMARY\n-------\n{summary}\n\n"
        f"FULL TRANSCRIPT\n---------------\n{transcript}\n"
    )
    return path
