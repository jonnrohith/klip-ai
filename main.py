from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import os
import uuid
import time
import base64
import json
from typing import Optional, Dict, Any
from threading import Lock

from models import UploadResponse
from utils.parser import parse_resume, parse_job_description

try:
    import redis
except Exception:
    redis = None

SESSION_TTL_SECONDS = 60 * 30
REWRITER_URL = os.getenv("REWRITER_URL", "http://localhost:8001/generate")
PDF_URL = os.getenv("PDF_URL", "http://localhost:8002/generate")


class SessionStore:
    def __init__(self):
        self._lock = Lock()
        self._in_memory: Dict[str, Dict[str, Any]] = {}
        redis_url = os.getenv("REDIS_URL")
        self._redis = redis.from_url(redis_url, decode_responses=True) if redis_url and redis else None

    def save(self, session_id: str, html: str, pdf_b64: str, ats_score: int, transformations: list, keywords_matched: list, keywords_missing: list) -> None:
        data = {
            "html": html,
            "pdf": pdf_b64,
            "ats_score": ats_score,
            "transformations": transformations,
            "keywords_matched": keywords_matched,
            "keywords_missing": keywords_missing,
            "expires_at": time.time() + SESSION_TTL_SECONDS,
        }
        if self._redis:
            self._redis.setex(session_id, SESSION_TTL_SECONDS, json.dumps(data))
        else:
            with self._lock:
                self._in_memory[session_id] = data

    def fetch(self, session_id: str) -> Optional[Dict[str, Any]]:
        if self._redis:
            raw = self._redis.get(session_id)
            return json.loads(raw) if raw else None

        with self._lock:
            data = self._in_memory.get(session_id)
            if not data:
                return None
            if data["expires_at"] < time.time():
                self._in_memory.pop(session_id, None)
                return None
            return data

    def purge_expired(self) -> None:
        if self._redis:
            return
        with self._lock:
            expired = [key for key, value in self._in_memory.items() if value["expires_at"] < time.time()]
            for key in expired:
                self._in_memory.pop(key, None)


app = FastAPI(title="Resumate AI Gateway", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

session_store = SessionStore()


@app.post("/upload", response_model=UploadResponse)
async def upload_resume(
    original_resume: UploadFile = File(...),
    job_description: Optional[str] = Form(None),
    job_description_file: Optional[UploadFile] = File(None),
) -> JSONResponse:
    resume_text = parse_resume(original_resume)
    jd_text, _ = parse_job_description(job_description, job_description_file)

    async with httpx.AsyncClient(timeout=120.0) as client:
        # Call rewriter service
        rewriter_resp = await client.post(
            REWRITER_URL,
            json={"resume_text": resume_text, "job_description": jd_text},
        )
        if rewriter_resp.status_code != 200:
            raise HTTPException(status_code=502, detail="Rewriter service failed")
        rewriter_data = rewriter_resp.json()
        html_resume = rewriter_data["html_resume"]
        ats_score = rewriter_data["ats_score"]
        transformations = rewriter_data.get("transformations", [])
        keywords_matched = rewriter_data.get("keywords_matched", [])
        keywords_missing = rewriter_data.get("keywords_missing", [])

        # Call PDF service (optional - gracefully handle failures)
        pdf_b64 = ""
        try:
            pdf_resp = await client.post(
                PDF_URL,
                json={"html_content": html_resume},
                timeout=30.0,
            )
            if pdf_resp.status_code == 200:
                pdf_b64 = base64.b64encode(pdf_resp.content).decode("utf-8")
        except Exception:
            # PDF generation failed, but HTML resume is still available
            pass

    session_id = str(uuid.uuid4())
    session_store.save(session_id, html_resume, pdf_b64, ats_score, transformations, keywords_matched, keywords_missing)

    return JSONResponse(UploadResponse(session_id=session_id, ats_score=ats_score, status="ready").model_dump())


@app.get("/result/{session_id}")
async def get_result(session_id: str) -> JSONResponse:
    session_store.purge_expired()
    record = session_store.fetch(session_id)
    if not record:
        raise HTTPException(status_code=404, detail="Session expired or not found")

    return JSONResponse({
        "session_id": session_id,
        "ats_score": record["ats_score"],
        "html_resume": record["html"],
        "pdf_b64": record["pdf"],
        "transformations": record.get("transformations", []),
        "keywords_matched": record.get("keywords_matched", []),
        "keywords_missing": record.get("keywords_missing", []),
    })


@app.get("/healthz")
async def healthz() -> Dict[str, str]:
    return {"status": "ok"}
