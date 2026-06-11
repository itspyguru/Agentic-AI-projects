# Telecaller Sales Agent

An outbound **telecaller sales voice agent** built on LiveKit + Gemini Realtime.
You talk to it from the browser; it plays the role of a friendly SaaS CRM sales
rep — it looks leads up in a CRM, pitches the right plan from a catalogue,
answers policy/billing questions from a knowledge base, books follow-up
callbacks, and writes a summary of every call to a log file.

The repo also contains an earlier **realtime web-search** voice demo
(`sales-agent/main.py` + the shared `agents-playground` frontend); this README
focuses on the sales agent (`sales-agent/agent.py`), which is the main app.

## Features

- **Voice conversations** — Gemini Realtime (`gemini-3.1-flash-live-preview`)
  with Silero VAD, served over LiveKit.
- **CRM tools (SQLite)** — look up leads, log call outcomes, update a lead's
  pipeline status, append notes, and schedule callbacks. See `db/sqlitedb.py`.
- **Product catalogue** — the agent quotes real plan names, features, and
  prices from the DB instead of inventing them.
- **Policy RAG (FAISS)** — company policies / ToS live in a markdown file and
  are retrieved with a small FAISS index so the agent answers billing, refund,
  trial, and cancellation questions accurately. See `rag.py` +
  `knowledge/company_policy.md`.
- **Post-call summaries** — when a call ends, the transcript is summarised by a
  Gemini text model and written to `logs/call-*.log` for reference. See
  `summary.py`.

## Project layout

```
telecaller-sales-agent/
├── pyproject.toml          # uv project + dependencies (root)
├── sales-agent/
│   ├── agent.py            # the sales agent worker (entrypoint)
│   ├── summary.py          # post-call transcript summariser + log writer
│   ├── rag.py              # FAISS retrieval over the policy doc
│   ├── db/
│   │   ├── sqlitedb.py     # schema, seed data, CRM data-access functions
│   │   └── sales.db        # SQLite database (created/seeded on first run)
│   ├── knowledge/
│   │   └── company_policy.md   # policies & ToS the RAG indexes
│   ├── logs/               # per-call summary + transcript logs (generated)
│   ├── main.py             # older realtime web-search demo (separate app)
│   ├── .env                # your secrets (gitignored)
│   └── .env.example        # template — copy to .env
└── agents-playground/      # LiveKit Agents Playground browser frontend
```

## Agent tools

The agent (`SalesAgent` in `agent.py`) is given these function tools:

| Tool | What it does |
|------|--------------|
| `get_lead` | Find a lead by name or phone |
| `get_call_history` | Recall previous calls with the lead |
| `get_products` | List plans, features, and prices from the catalogue |
| `lookup_policy` | Retrieve relevant policy/ToS text (FAISS RAG) |
| `add_lead_note` | Append context to the lead's record |
| `set_lead_status` | Move the lead through the pipeline |
| `schedule_callback` | Book a follow-up; `get_callbacks` reads existing ones |
| `log_call` | Record the call outcome at the end |

## Prerequisites

- Python 3.12 + [uv](https://docs.astral.sh/uv/)
- Docker (to run LiveKit locally)
- Node.js + npm (for the browser frontend)
- A Google Gemini API key — <https://aistudio.google.com/apikey>

## Setup

Copy the env template and fill in your values:

```bash
cd sales-agent
cp .env.example .env
# edit .env and set GOOGLE_API_KEY (+ LiveKit creds, defaults below work for --dev)
```

```env
GOOGLE_API_KEY=<your-gemini-api-key>
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
```

Dependencies are managed with uv (`uv` auto-syncs the env on first `uv run`).
The CRM database is created and seeded automatically the first time the agent
starts; to seed it manually:

```bash
cd sales-agent
uv run python -m db.sqlitedb
```

## Running (3 terminals)

Run each command in its own terminal and leave it running.

### 1. LiveKit server (local)

```bash
docker run --rm \
  -p 7880:7880 -p 7881:7881 -p 7882:7882/udp \
  livekit/livekit-server --dev --bind 0.0.0.0
```

`--dev` mode hardcodes the credentials `devkey` / `secret` (matching `.env`).

### 2. Agent worker

```bash
cd sales-agent
uv run python agent.py dev
```

Wait for `registered worker` — it's now connected to the local LiveKit server
and waiting for someone to join.

### 3. Browser frontend (LiveKit Agents Playground)

```bash
cd agents-playground
npm install   # first time only
npm run dev
```

Then open <http://localhost:3000>, click **Connect**, allow microphone access,
and start the conversation. The agent joins the room and greets you as a lead.

> The frontend's `.env.local` must point at the same local server:
>
> ```env
> NEXT_PUBLIC_LIVEKIT_URL=ws://localhost:7880
> LIVEKIT_API_KEY=devkey
> LIVEKIT_API_SECRET=secret
> ```

When you hang up, look in `sales-agent/logs/` for the call summary + transcript.

## Notes

- All three pieces — server, agent, and frontend — must use the **same**
  LiveKit URL, key, and secret, or they won't meet in the same room.
- The browser supplies the microphone, so open the frontend on a machine that
  has a mic. On a headless VM, forward the ports over SSH and open the
  frontend from your laptop.
- `GOOGLE_API_KEY` is used in three places: the realtime voice model, the
  post-call summary model (`summary.py`), and the policy embeddings (`rag.py`).
- Editing `knowledge/company_policy.md` changes what the agent can quote — the
  FAISS index is rebuilt from it each time the worker starts.
