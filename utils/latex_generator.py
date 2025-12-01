from __future__ import annotations

import base64
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Tuple

from jinja2 import Environment, FileSystemLoader, select_autoescape

from models import ResumePayload

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"


env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(enabled_extensions=(), default=False),
    trim_blocks=True,
    lstrip_blocks=True,
)


def render_resume(payload: ResumePayload) -> str:
    template = env.get_template("resume.tex")
    return template.render(data=payload.model_dump())


def build_pdf(tex_source: str) -> Tuple[str, str]:
    tmp_dir = Path(tempfile.mkdtemp(prefix="resume_tex_"))
    tex_path = tmp_dir / "final_resume.tex"
    tex_path.write_text(tex_source, encoding="utf-8")

    command = [
        "pdflatex",
        "-interaction=nonstopmode",
        "-output-directory",
        str(tmp_dir),
        str(tex_path),
    ]
    try:
        subprocess.run(command, check=True, capture_output=True)
    except subprocess.CalledProcessError as exc:  # pragma: no cover - system dep
        raise RuntimeError("pdflatex compilation failed") from exc

    pdf_path = tmp_dir / "final_resume.pdf"
    pdf_bytes = pdf_path.read_bytes()
    return tex_path.read_text(encoding="utf-8"), base64.b64encode(pdf_bytes).decode("ascii")


def generate_resume_files(payload: ResumePayload) -> Tuple[str, str]:
    tex_content = render_resume(payload)
    try:
        _, pdf_b64 = build_pdf(tex_content)
    except RuntimeError:
        # If pdflatex is not available or compilation fails, still return LaTeX
        # so the frontend can show the rewritten resume, but leave PDF empty.
        pdf_b64 = base64.b64encode(b"").decode("ascii")
    return tex_content, pdf_b64

