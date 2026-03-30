"""Minimal FastAPI web interface for the AI agent pipeline."""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from agent.orchestrator import Orchestrator
from config import TELEGRAM_BOT_TOKEN
from memory import add_message, clear_history
from main import start, help_command, clear, status, stats, handle_message

logger = logging.getLogger(__name__)


def _build_bot():
    """Build the Telegram Application (without starting it)."""
    bot_app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("help", help_command))
    bot_app.add_handler(CommandHandler("clear", clear))
    bot_app.add_handler(CommandHandler("status", status))
    bot_app.add_handler(CommandHandler("stats", stats))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    return bot_app


@asynccontextmanager
async def lifespan(app):
    """Start Telegram bot polling alongside the web server."""
    if TELEGRAM_BOT_TOKEN:
        bot_app = _build_bot()
        await bot_app.initialize()
        await bot_app.start()
        await bot_app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        logger.info("Telegram bot started (polling)")
    else:
        bot_app = None
        logger.warning("TELEGRAM_BOT_TOKEN not set – bot disabled")

    yield

    if bot_app is not None:
        await bot_app.updater.stop()
        await bot_app.stop()
        await bot_app.shutdown()
        logger.info("Telegram bot stopped")


app = FastAPI(title="AI-Pass Agent API", lifespan=lifespan)
orchestrator = Orchestrator()

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI-PASS Web Interface</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:'Segoe UI',system-ui,sans-serif;background:#f5f7fa;color:#1a1a2e;display:flex;justify-content:center;padding:40px 16px}
  .container{width:100%;max-width:640px}
  h1{font-size:1.6rem;margin-bottom:24px;text-align:center;color:#16213e}
  .card{background:#fff;border-radius:12px;padding:24px;box-shadow:0 2px 8px rgba(0,0,0,.08)}
  textarea{width:100%;min-height:100px;padding:12px;border:1px solid #d1d5db;border-radius:8px;font-size:.95rem;resize:vertical;font-family:inherit}
  textarea:focus{outline:none;border-color:#4361ee;box-shadow:0 0 0 3px rgba(67,97,238,.15)}
  button{margin-top:12px;padding:12px;border:none;border-radius:8px;font-size:1rem;cursor:pointer;font-weight:600;transition:background .2s}
  .btn-row{display:flex;gap:8px;margin-top:12px}
  .btn-row button{flex:1;margin-top:0}
  #btn{background:#4361ee;color:#fff}
  #btn:hover{background:#3a56d4}
  button:disabled{background:#94a3b8;cursor:not-allowed}
  #clearBtn{background:#e2e8f0;color:#475569;flex:0 0 auto;padding:12px 20px}
  #clearBtn:hover{background:#cbd5e1}
  .result{margin-top:20px;display:none}
  .result h2{font-size:1.1rem;margin-bottom:12px;color:#16213e}
  .field{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #f0f0f0;font-size:.93rem}
  .field:last-child{border-bottom:none}
  .label{font-weight:600;color:#475569}
  .value{color:#1e293b;text-align:right;max-width:60%;word-break:break-word}
  .error{margin-top:16px;padding:12px;background:#fef2f2;color:#991b1b;border-radius:8px;font-size:.9rem;display:none}
  .info{margin-top:16px;padding:12px;background:#f0fdf4;color:#166534;border-radius:8px;font-size:.9rem;display:none}
  .spinner{display:inline-block;width:16px;height:16px;border:2px solid #fff;border-top-color:transparent;border-radius:50%;animation:spin .6s linear infinite;vertical-align:middle;margin-right:6px}
  @keyframes spin{to{transform:rotate(360deg)}}
</style>
</head>
<body>
<div class="container">
  <h1>AI-PASS Web Interface</h1>
  <div class="card">
    <textarea id="query" placeholder="Type your message here..."></textarea>
    <div class="btn-row">
      <button id="btn" onclick="submit()">Send</button>
      <button id="clearBtn" onclick="clearMemory()">Clear Memory</button>
    </div>
    <div class="error" id="error"></div>
    <div class="info" id="info"></div>
    <div class="result" id="result">
      <h2>Response</h2>
      <div id="fields"></div>
    </div>
  </div>
</div>
<script>
function sid(){let s=localStorage.getItem('ai_pass_sid');if(!s){s=crypto.randomUUID();localStorage.setItem('ai_pass_sid',s)}return s}
async function submit(){
  const q=document.getElementById('query').value.trim();
  if(!q)return;
  const btn=document.getElementById('btn'),res=document.getElementById('result'),err=document.getElementById('error'),info=document.getElementById('info');
  err.style.display='none';info.style.display='none';res.style.display='none';
  btn.disabled=true;btn.innerHTML='<span class="spinner"></span>Processing...';
  try{
    const r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({query:q,session_id:sid()})});
    if(!r.ok)throw new Error((await r.json()).detail||r.statusText);
    const d=await r.json();
    const fields=[['Task Type',d.task_type],['Summary',d.summary],['Priority',d.priority],['Suggested Action',d.suggested_action],['Confidence',d.confidence]];
    document.getElementById('fields').innerHTML=fields.map(([l,v])=>'<div class="field"><span class="label">'+l+'</span><span class="value">'+(v!=null?v:'\u2014')+'</span></div>').join('');
    res.style.display='block';
  }catch(e){err.textContent=e.message;err.style.display='block'}
  finally{btn.disabled=false;btn.textContent='Send'}
}
async function clearMemory(){
  const err=document.getElementById('error'),info=document.getElementById('info');
  err.style.display='none';info.style.display='none';
  try{
    const r=await fetch('/clear',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session_id:sid()})});
    if(!r.ok)throw new Error((await r.json()).detail||r.statusText);
    info.textContent='Memory cleared.';info.style.display='block';
  }catch(e){err.textContent=e.message;err.style.display='block'}
}
document.getElementById('query').addEventListener('keydown',e=>{if(e.ctrlKey&&e.key==='Enter')submit()});
</script>
</body>
</html>"""


class AskRequest(BaseModel):
    query: str
    session_id: Optional[str] = None


class ClearRequest(BaseModel):
    session_id: str


@app.get("/", response_class=HTMLResponse)
async def root():
    return HTML_PAGE


@app.post("/ask")
async def ask(req: AskRequest):
    try:
        chat_id = f"web_{req.session_id}" if req.session_id else None
        raw = await asyncio.to_thread(orchestrator.handle, req.query, chat_id)
        if chat_id:
            add_message(chat_id, "user", req.query)
            try:
                data = json.loads(raw)
                add_message(chat_id, "assistant", data.get("summary", ""))
            except (json.JSONDecodeError, TypeError):
                pass
        return json.loads(raw)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/clear")
async def clear(req: ClearRequest):
    chat_id = f"web_{req.session_id}"
    clear_history(chat_id)
    return {"status": "memory cleared"}
