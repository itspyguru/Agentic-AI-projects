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

from db.sqlitedb import (
    init_db,
    fetch_lead,
    insert_call,
    insert_callback,
    fetch_products,
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


class SalesAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
            You are a friendly, professional outbound telecaller for our SaaS
            CRM product. You are speaking with a potential customer on the phone.

            Goals, in order:
            1. Greet warmly and identify who you're speaking with. Use the
               get_lead tool to look them up and personalise the conversation
               (use their name, company, and any prior notes).
            2. Briefly understand their needs and pitch the right plan. Use the
               get_products tool for accurate names, features, and prices —
               NEVER make up a price or feature.
            3. If they're interested but not ready, offer a follow-up. Confirm a
               day and time, then use schedule_callback to book it.
            4. At the END of every call, use log_call to record the outcome
               (interested / not interested / callback / etc.) with a short note.

            Style: conversational, concise, one question at a time. Don't be
            pushy. Confirm details out loud before saving anything to the CRM.
            """,
            tools=[get_lead, get_products, schedule_callback, log_call],
        )


async def entrypoint(ctx: JobContext):
    # Make sure the DB + seed data exist before taking calls.
    init_db()

    session = AgentSession(
        llm=google.realtime.RealtimeModel(
            model="gemini-3.1-flash-live-preview",
            voice="Puck",
        ),
        vad=silero.VAD.load(),
    )

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
