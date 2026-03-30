"""Minimal FastAPI web interface for the AI agent pipeline."""

import asyncio
import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent.orchestrator import Orchestrator

app = FastAPI(title="AI-Pass Agent API")
orchestrator = Orchestrator()


class AskRequest(BaseModel):
    query: str


@app.get("/")
async def root():
    return {"status": "AI agent is running"}


@app.post("/ask")
async def ask(req: AskRequest):
    try:
        raw = await asyncio.to_thread(orchestrator.handle, req.query)
        return json.loads(raw)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
