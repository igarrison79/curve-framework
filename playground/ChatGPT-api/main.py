import secrets
from typing import Dict
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel
from playwright.async_api import async_playwright

app = FastAPI()

# Token is generated on startup and printed to the console for users
AUTH_TOKEN = secrets.token_urlsafe(16)

# In-memory store of active browser sessions
sessions: Dict[str, Dict] = {}


async def verify_token(x_auth_token: str = Header(...)):
    """Simple header based authentication."""
    if x_auth_token != AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")


class ChatRequest(BaseModel):
    session_id: str
    prompt: str


@app.on_event("startup")
async def startup_event():
    """Notify users of the generated auth token."""
    print(f"[ChatGPT API] Auth token: {AUTH_TOKEN}")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up any active browser sessions on shutdown."""
    for session in sessions.values():
        await session["context"].close()
        await session["browser"].close()
        await session["playwright"].stop()
    sessions.clear()


@app.post("/session", dependencies=[Depends(verify_token)])
async def create_session():
    """Create a new headless browser session for chatting with ChatGPT."""
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()
    # TODO: perform real login against https://chat.openai.com here.

    session_id = str(uuid4())
    sessions[session_id] = {
        "playwright": playwright,
        "browser": browser,
        "context": context,
        "page": page,
    }
    return {"session_id": session_id}


@app.post("/chat", dependencies=[Depends(verify_token)])
async def chat(request: ChatRequest):
    """Send a prompt to ChatGPT via the stored browser session."""
    session = sessions.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Invalid session id")

    page = session["page"]

    # TODO: implement the real logic for sending the prompt and retrieving
    # the response from ChatGPT's web UI.
    # Example outline (non-functional placeholder):
    # await page.fill("textarea", request.prompt)
    # await page.keyboard.press("Enter")
    # response = await page.wait_for_selector("div.response")
    # content = await response.inner_text()
    content = "Not implemented"

    return {"response": content}


@app.delete("/session/{session_id}", dependencies=[Depends(verify_token)])
async def delete_session(session_id: str):
    """Close an existing browser session."""
    session = sessions.pop(session_id, None)
    if not session:
        raise HTTPException(status_code=404, detail="Invalid session id")

    await session["context"].close()
    await session["browser"].close()
    await session["playwright"].stop()
    return {"status": "closed"}
