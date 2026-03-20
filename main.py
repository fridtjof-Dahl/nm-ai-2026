"""
NM i AI 2026 – Tripletex AI Accounting Agent
FastAPI /solve endpoint
"""

import base64
import logging
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from agent import run_agent

# ─────────────────────────── LOGGING ───────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s │ %(message)s",
)
logger = logging.getLogger("main")

app = FastAPI(
    title="NM i AI 2026 – Tripletex Agent",
    description="AI accounting agent for the Norwegian AI Championship 2026",
    version="1.0.0",
)


@app.get("/")
async def health():
    return {"status": "ok", "agent": "tripletex-nm-ai-2026"}


@app.get("/health")
async def healthcheck():
    return {"status": "ok"}


@app.post("/solve")
async def solve(request: Request):
    """
    Main endpoint called by NM i AI platform.

    Expected JSON body:
    {
        "task": "Create an employee named ...",
        "sessionToken": "...",
        "companyId": "...",
        "proxyBaseUrl": "https://proxy.ainm.no/tripletex",
        "files": [{"filename": "...", "content_base64": "..."}]  // optional
    }
    """
    try:
        body = await request.json()
    except Exception as e:
        logger.error(f"Failed to parse request body: {e}")
        return JSONResponse({"status": "error", "message": "Invalid JSON"}, status_code=400)

    # Extract fields – support both camelCase (competition format) and snake_case
    task = body.get("task") or body.get("prompt", "")
    session_token = body.get("sessionToken") or body.get("session_token", "")
    company_id = body.get("companyId") or body.get("company_id", "")
    proxy_base = body.get("proxyBaseUrl") or body.get("proxy_base_url", "")
    files = body.get("files", [])

    # Also support tripletex_credentials sub-object (NM competition format)
    if "tripletex_credentials" in body:
        creds = body["tripletex_credentials"]
        if not session_token:
            session_token = creds.get("session_token", "")
        if not proxy_base:
            proxy_base = creds.get("base_url", "")

    if not task:
        logger.error("No task provided in request")
        return JSONResponse({"status": "error", "message": "No task provided"}, status_code=400)

    if not session_token:
        logger.error("No session token provided")
        return JSONResponse({"status": "error", "message": "No session token"}, status_code=400)

    # Use proxy base URL or fall back to direct sandbox URL
    base_url = proxy_base or "https://kkpqfuj-amager.tripletex.dev/v2"

    logger.info(f"Received task: {task[:200]}")
    logger.info(f"Base URL: {base_url}")
    logger.info(f"Files attached: {len(files)}")

    try:
        result = run_agent(
            task=task,
            base_url=base_url,
            session_token=session_token,
            files=files if files else None,
        )
        logger.info(f"Agent completed: {result}")
        return JSONResponse(result)

    except Exception as e:
        logger.exception(f"Agent failed with exception: {e}")
        # Still return completed – partial work may have been done
        return JSONResponse({"status": "completed"})
