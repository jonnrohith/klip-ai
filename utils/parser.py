from __future__ import annotations

import io
import re
from typing import Optional, Tuple

import pdfplumber
from docx import Document
from fastapi import UploadFile


def _read_upload(upload: UploadFile) -> bytes:
    """Read the entire UploadFile payload and reset cursor."""
    upload.file.seek(0)
    payload = upload.file.read()
    upload.file.seek(0)
    return payload


def _pdf_to_text(payload: bytes) -> str:
    with pdfplumber.open(io.BytesIO(payload)) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    return "\n".join(pages)


def _docx_to_text(payload: bytes) -> str:
    document = Document(io.BytesIO(payload))
    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def parse_resume(upload: UploadFile) -> str:
    """Return raw textual content from the uploaded resume."""
    payload = _read_upload(upload)
    content_type = (upload.content_type or "").lower()

    if content_type.endswith("pdf") or upload.filename.lower().endswith(".pdf"):
        return _pdf_to_text(payload)
    if "word" in content_type or upload.filename.lower().endswith((".docx", ".doc")):
        return _docx_to_text(payload)

    # Fallback to naive decode
    try:
        return payload.decode("utf-8")
    except UnicodeDecodeError:
        return payload.decode("latin-1", errors="ignore")


def parse_job_description(
    jd_text: Optional[str], jd_file: Optional[UploadFile]
) -> Tuple[str, str]:
    """Return (raw_text, source_hint)."""
    if jd_text and jd_text.strip():
        return jd_text.strip(), "text"

    if jd_file:
        payload = _read_upload(jd_file)
        if jd_file.filename.lower().endswith(".pdf"):
            return _pdf_to_text(payload), "file"
        if jd_file.filename.lower().endswith(".docx"):
            return _docx_to_text(payload), "file"
        try:
            return payload.decode("utf-8"), "file"
        except UnicodeDecodeError:
            return payload.decode("latin-1", errors="ignore"), "file"

    return "", "missing"


def sanitize_whitespace(text: str) -> str:
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n\n", text)
    return text.strip()

