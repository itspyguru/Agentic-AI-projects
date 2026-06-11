# Realtime Search Voice Agent

A voice assistant (LiveKit + Gemini Realtime) that can search the web with
Google. You talk to it from a browser; it answers and runs live web searches.

## Prerequisites

- Python 3.12 + [uv](https://docs.astral.sh/uv/)
- Docker (to run LiveKit locally)
- Node.js + npm (for the browser frontend)
- A `.env` in the repo root with:

  ```env
  GOOGLE_API_KEY=<your-gemini-api-key>
  LIVEKIT_URL=ws://localhost:7880
  LIVEKIT_API_KEY=devkey
  LIVEKIT_API_SECRET=secret
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
cd realtime-search
uv run python main.py dev
```

Wait for `registered worker` — it's now connected to the local LiveKit server
and waiting for someone to join.

### 3. Browser frontend (LiveKit Agents Playground)

```bash
cd realtime-search/agents-playground
npm run dev
```

Then open <http://localhost:3000>, click **Connect**, allow microphone access,
and start talking. The agent joins the room and you can ask it to search the web.

> The frontend's `.env.local` must point at the same local server:
>
> ```env
> NEXT_PUBLIC_LIVEKIT_URL=ws://localhost:7880
> LIVEKIT_API_KEY=devkey
> LIVEKIT_API_SECRET=secret
> ```

## Notes

- All three pieces — server, agent, and frontend — must use the **same**
  LiveKit URL, key, and secret, or they won't meet in the same room.
- The browser supplies the microphone, so open the frontend on a machine that
  has a mic. On a headless VM, forward the ports over SSH and open the
  frontend from your laptop.
