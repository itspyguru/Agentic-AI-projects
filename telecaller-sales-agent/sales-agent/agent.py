import logging

from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    cli,
    function_tool,
)
from livekit.plugins import google, silero

from summary import summarize_call, transcript_to_text, write_call_log
from rag import build_index, search as search_policy

logger = logging.getLogger("sales-agent")

from db.sqlitedb import (
    init_db,
    fetch_lead,
    insert_call,
    insert_callback,
    fetch_products,
    update_lead_status,
    update_lead_notes,
    fetch_call_history,
    list_callbacks,
)

# Load GOOGLE_API_KEY / LIVEKIT_* from .env.
load_dotenv()


# --- Tools: thin wrappers over the SQLite data layer -----------------------
# Each returns a short, speakable string so the Realtime model can read the
# result back to the lead on the call.

@function_tool
async def get_lead(name_or_phone: str) -> str:
    """Look up a lead in the CRM by their name or phone number.

    Call this at the start of a call to find out who you're talking to.

    Args:
        name_or_phone: The lead's name (or part of it) or phone number.
    """
    lead = fetch_lead(name_or_phone)
    if not lead:
        return f"No lead found matching '{name_or_phone}'."
    return (
        f"Lead #{lead['id']}: {lead['name']} from {lead['company']}. "
        f"Status: {lead['status']}. Notes: {lead['notes']}"
    )


@function_tool
async def get_products() -> str:
    """List the available products and their prices from the catalogue.

    Always call this before quoting any price — never invent prices.
    """
    products = fetch_products()
    if not products:
        return "No products are available right now."
    lines = [
        f"{p['name']}: ${p['price']:.0f} — {p['description']}"
        for p in products
    ]
    return "Products:\n" + "\n".join(lines)


@function_tool
async def schedule_callback(lead_id: int, scheduled_at: str, notes: str = "") -> str:
    """Book a follow-up callback for a lead.

    Confirm the date/time with the lead before calling this.

    Args:
        lead_id: The lead's id (from get_lead).
        scheduled_at: When to call back, e.g. "2026-06-15 15:00" or "tomorrow 3pm".
        notes: Optional context for the follow-up.
    """
    callback_id = insert_callback(lead_id, scheduled_at, notes)
    return f"Callback #{callback_id} booked for lead {lead_id} at {scheduled_at}."


@function_tool
async def log_call(lead_id: int, outcome: str, notes: str = "") -> str:
    """Record the outcome of the call. Call this at the end of every call.

    Args:
        lead_id: The lead's id (from get_lead).
        outcome: Short outcome, e.g. "interested", "not interested", "callback".
        notes: Optional summary of what was discussed.
    """
    call_id = insert_call(lead_id, outcome, notes)
    return f"Call #{call_id} logged for lead {lead_id} with outcome '{outcome}'."


@function_tool
async def get_call_history(lead_id: int) -> str:
    """Review the lead's recent call history before or during the conversation.

    Use this right after get_lead to recall what was discussed previously, so
    you don't repeat yourself and can pick up where the last call left off.

    Args:
        lead_id: The lead's id (from get_lead).
    """
    calls = fetch_call_history(lead_id)
    if not calls:
        return f"No previous calls logged for lead {lead_id}."
    lines = [
        f"{c['created_at']}: {c['outcome']}"
        + (f" — {c['notes']}" if c['notes'] else "")
        for c in calls
    ]
    return "Recent calls:\n" + "\n".join(lines)


@function_tool
async def set_lead_status(lead_id: int, status: str) -> str:
    """Update where the lead sits in the pipeline.

    Call this when the conversation changes their stage, e.g. mark them
    "qualified" once they show clear intent, or "won" if they sign up.

    Args:
        lead_id: The lead's id (from get_lead).
        status: New status, e.g. "contacted", "qualified", "won", "lost".
    """
    if update_lead_status(lead_id, status):
        return f"Lead {lead_id} status updated to '{status}'."
    return f"No lead found with id {lead_id}."


@function_tool
async def add_lead_note(lead_id: int, note: str) -> str:
    """Append a note to the lead's record without overwriting existing notes.

    Use this to capture useful context the lead shares (team size, budget,
    objections, preferred contact time) for the next call.

    Args:
        lead_id: The lead's id (from get_lead).
        note: The note to add.
    """
    if update_lead_notes(lead_id, note):
        return f"Note added to lead {lead_id}."
    return f"No lead found with id {lead_id}."


@function_tool
async def lookup_policy(question: str) -> str:
    """Look up company policy, terms of service, billing, or refund rules.

    Use this whenever the lead asks about trials, billing, refunds,
    cancellation, support levels, data/privacy, or anything about how the
    company operates. Answer ONLY from what this returns — don't guess. If it
    doesn't cover the question, offer to have a specialist follow up.

    Args:
        question: The lead's question, e.g. "do you offer refunds?".
    """
    sections = search_policy(question)
    if not sections:
        return "No matching policy found. Offer to have a specialist follow up."
    return "Relevant policy:\n\n" + "\n\n---\n\n".join(sections)


@function_tool
async def get_callbacks(lead_id: int) -> str:
    """Read back the callbacks already scheduled for a lead.

    Use this to confirm or avoid double-booking a follow-up.

    Args:
        lead_id: The lead's id (from get_lead).
    """
    callbacks = list_callbacks(lead_id)
    if not callbacks:
        return f"No callbacks scheduled for lead {lead_id}."
    lines = [
        f"{c['scheduled_at']}" + (f" — {c['notes']}" if c['notes'] else "")
        for c in callbacks
    ]
    return "Scheduled callbacks:\n" + "\n".join(lines)


class SalesAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
            You are a friendly, professional outbound telecaller for our SaaS
            CRM product. You are speaking with a potential customer on the phone.

            Goals, in order:
            1. Greet warmly and identify who you're speaking with. Use the
               get_lead tool to look them up and personalise the conversation
               (use their name, company, and any prior notes). Then use
               get_call_history to recall what was discussed on previous calls
               so you can pick up where you left off and avoid repeating yourself.
            2. Briefly understand their needs and pitch the right plan. Use the
               get_products tool for accurate names, features, and prices —
               NEVER make up a price or feature. As you learn useful context
               (team size, budget, objections), use add_lead_note to save it.
               If they ask about trials, billing, refunds, cancellation,
               support, or data/privacy, use the lookup_policy tool and answer
               only from what it returns — never invent a policy.
            3. As the conversation progresses, use set_lead_status to keep the
               pipeline accurate — e.g. "qualified" once they show clear intent,
               "won" if they agree to sign up, or "lost" if they decline.
            4. If they're interested but not ready, offer a follow-up. Check
               get_callbacks first to avoid double-booking, then confirm a day
               and time and use schedule_callback to book it.
            5. At the END of every call, use log_call to record the outcome
               (interested / not interested / callback / etc.) with a short note.

            Style: conversational, concise, one question at a time. Don't be
            pushy. Confirm details out loud before saving anything to the CRM.
            """,
            tools=[
                get_lead,
                get_products,
                schedule_callback,
                log_call,
                get_call_history,
                set_lead_status,
                add_lead_note,
                get_callbacks,
                lookup_policy,
            ],
        )


async def entrypoint(ctx: JobContext):
    # Make sure the DB + seed data exist before taking calls.
    init_db()
    # Build the policy retrieval index once, up front, so lookups during the
    # call are just a single query embedding + FAISS search.
    build_index()

    session = AgentSession(
        llm=google.realtime.RealtimeModel(
            model="gemini-3.1-flash-live-preview",
            voice="Puck",
        ),
        vad=silero.VAD.load(),
    )

    # When the call ends, summarise the transcript and write it to a log file.
    async def write_summary_log() -> None:
        transcript = transcript_to_text(session.history)
        if not transcript.strip():
            logger.info("No transcript captured; skipping summary log.")
            return
        try:
            summary = await summarize_call(transcript)
        except Exception:
            # Don't lose the call if summarisation fails — log the error and
            # still write the raw transcript so it's there for reference.
            logger.exception("Call summarisation failed; writing raw transcript.")
            summary = "Summary generation failed — see transcript below."
        path = write_call_log(summary, transcript)
        logger.info("Call summary written to %s", path)

    ctx.add_shutdown_callback(write_summary_log)

    await session.start(
        room=ctx.room,
        agent=SalesAgent(),
    )


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )
