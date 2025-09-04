# ChatGPT Headless Browser API

This playground project exposes a simple FastAPI server that proxies
requests to the ChatGPT web interface using a headless browser. It is
**not** an official OpenAI API client. It demonstrates how sessions can be
maintained and how lightweight authentication can be enforced.

## Features

- Session-based access to a shared headless browser instance.
- Random authentication token generated on startup and printed to the
  console. All requests must supply this token via the `X-Auth-Token`
  header.
- Endpoints to create, use, and destroy sessions.

## Endpoints

- `POST /session` – create a new browser session.
- `POST /chat` – send a prompt and receive a response.
- `DELETE /session/{session_id}` – close a session.

All endpoints require the `X-Auth-Token` header.

## Running

Install dependencies and launch the API server:

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

The server prints an auth token on startup. This token changes every time
the server starts and is invalidated when it stops.
