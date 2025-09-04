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

### OpenAI login

The server automates logging into [chat.openai.com](https://chat.openai.com).
Provide your account details via environment variables before starting it:

```bash
export OPENAI_EMAIL="you@example.com"
export OPENAI_PASSWORD="your-password"
# optional: supply MFA secret for automatic TOTP generation
export OPENAI_MFA_SECRET="BASE32SECRET"  # omit to perform 2FA manually

pip install -r requirements.txt
playwright install chromium  # first time only
uvicorn main:app --reload
```

If `OPENAI_MFA_SECRET` is not set a regular browser window will open during
session creation so you can complete the two factor authentication step. The
window can be closed once the ChatGPT interface loads; subsequent requests use
headless automation.
