import os
import secrets
from typing import Dict, Tuple
from uuid import uuid4

import pyotp
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel
from playwright.async_api import Browser, BrowserContext, Page, async_playwright

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


async def _login_chatgpt(playwright) -> Tuple[Browser, BrowserContext, Page]:
    """Launch a browser, log in to ChatGPT and return the session objects.

    Email and password are read from ``OPENAI_EMAIL`` and ``OPENAI_PASSWORD``
    environment variables. If ``OPENAI_MFA_SECRET`` is provided a TOTP code is
    generated automatically. Otherwise an interactive browser window is opened
    so the user can complete the second factor manually. The resulting storage
    state is then reused in a headless browser.
    """

    email = os.getenv("OPENAI_EMAIL")
    password = os.getenv("OPENAI_PASSWORD")
    if not email or not password:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_EMAIL and OPENAI_PASSWORD environment variables are required",
        )

    mfa_secret = os.getenv("OPENAI_MFA_SECRET")

    # If no MFA secret is supplied, launch a visible browser to let the user
    # complete the 2FA step manually.
    browser = await playwright.chromium.launch(headless=bool(mfa_secret))
    context = await browser.new_context()
    page = await context.new_page()

    await page.goto("https://chat.openai.com/")
    await page.get_by_role("button", name="Log in").click()
    await page.get_by_label("Email address").fill(email)
    await page.get_by_role("button", name="Continue").click()
    await page.get_by_label("Password").fill(password)
    await page.get_by_role("button", name="Continue").click()

    if mfa_secret:
        totp = pyotp.TOTP(mfa_secret).now()
        await page.get_by_label("Verification code").fill(totp)
        await page.get_by_role("button", name="Verify").click()
        await page.wait_for_url("https://chat.openai.com/?*", timeout=60_000)
        return browser, context, page

    # Manual MFA: wait indefinitely for user to complete verification
    print("Complete the login flow in the opened browser window…")
    await page.wait_for_url("https://chat.openai.com/?*", timeout=0)
    storage = await context.storage_state()
    await browser.close()

    # Relaunch headless browser with the authenticated storage state
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context(storage_state=storage)
    page = await context.new_page()
    return browser, context, page


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
    """Create a new logged-in headless browser session for ChatGPT."""
    playwright = await async_playwright().start()
    browser, context, page = await _login_chatgpt(playwright)

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
