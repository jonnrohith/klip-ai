from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Tuple

from openai import OpenAI
from spacy.language import Language

from models import ResumePayload
from utils.latex_generator import generate_resume_files
from utils.rewriter import ResumeRewriter, METRIC_REGEX
from utils.scorer import score_ats


@dataclass
class RewriteResult:
    payload: ResumePayload
    ats_score: int


class ResumeRewritingAgent:
    """Agent responsible for ATS-aware resume rewriting."""

    def __init__(self, nlp: Language):
        self._rewriter = ResumeRewriter(nlp)

    def rewrite(self, resume_text: str, job_text: str) -> RewriteResult:
        payload = self._rewriter.rewrite(resume_text, job_text)
        ats_score = score_ats(payload, job_text)
        return RewriteResult(payload=payload, ats_score=ats_score)


class OpenAIResumeRewritingAgent:
    """
    Agent that delegates rewriting to OpenAI while enforcing your schema and rules:
    - No invented roles/companies/dates
    - Bullets follow: "Solved X by Y, resulting in Z"
    - Metrics present in 50–65% of bullets, never fabricated numbers
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required for OpenAIResumeRewritingAgent")
        self._client = OpenAI(api_key=api_key)
        self._model = model

    def rewrite(self, resume_text: str, job_text: str) -> RewriteResult:
        system_prompt = (
            "You are an expert ATS-optimized resume rewriting engine.\n"
            "You MUST obey ALL of these rules:\n"
            "1) Use SIMPLE American English, Flesch Reading Ease > 60.\n"
            "2) NEVER invent job titles, company names, dates, or extra roles/promotions.\n"
            "3) You MUST treat the original resume as the ground truth:\n"
            "   - For each original job role and company you detect, you MUST emit exactly one experience\n"
            "     object with the same role, company, dates and location.\n"
            "   - For each such role, generate AT LEAST as many bullets as the original (up to 6), but you\n"
            "     may merge or slightly shorten overlapping bullets. Keep all key projects/systems mentioned.\n"
            "   - You may NOT drop whole roles, companies, or projects, even if they look less relevant.\n"
            "4) EVERY bullet in Experience and Projects MUST follow EXACTLY this pattern while staying faithful\n"
            "   to the original content:\n"
            '   \"Solved [problem or challenge] by [action + tools/skills], resulting in [quantifiable or\n'
            "   clearly observable outcome]\".\n"
            "5) 50–65% of ALL bullets across Experience + Projects MUST contain REAL numbers taken from the\n"
            "   original resume or job description (%, $, count, time, team size, etc.).\n"
            "   - If the source text does not contain a safe, real number, you MUST NOT invent one.\n"
            "   - In that case, use a qualitative outcome instead (e.g. 'more stable releases', 'fewer incidents').\n"
            "6) Do NOT change person’s name, job titles, companies, locations, or dates.\n"
            "7) ATS score (computed separately) must stay between 80 and 95, so do not stuff unnatural keywords.\n"
            "8) Output MUST be valid JSON for the following Pydantic model named ResumePayload:\n"
            "   {\n"
            '     \"heading\": {\n'
            '       \"name\": str,\n'
            '       \"title\": str,\n'
            '       \"phone\": str,\n'
            '       \"email\": str,\n'
            '       \"linkedin\": str,\n'
            '       \"github\": str\n'
            "     },\n"
            '     \"experiences\": [\n'
            "       {\n"
            '         \"role\": str,\n'
            '         \"company\": str,\n'
            '         \"location\": str,\n'
            '         \"start\": str,\n'
            '         \"end\": str,\n'
            '         \"bullets\": [\n'
            "           {\"text\": str, \"has_metric\": bool}\n"
            "         ]\n"
            "       }\n"
            "     ],\n"
            '     \"skills\": [str],\n'
            '     \"projects\": [\n'
            "       {\n"
            '         \"name\": str,\n'
            '         \"stack\": str,\n'
            '         \"timeline\": str,\n'
            '         \"bullets\": [\n'
            "           {\"text\": str, \"has_metric\": bool}\n"
            "         ]\n"
            "       }\n"
            "     ],\n"
            '     \"education\": str,\n'
            '     \"certifications\": [str]\n'
            "   }\n"
            "9) Return ONLY the JSON object, with no markdown, no comments, no extra text.\n"
        )

        user_payload = {
            "resume_text": resume_text,
            "job_description": job_text,
        }

        completion = self._client.chat.completions.create(
            model=self._model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": (
                        "Here is the raw candidate resume text and the target job description.\n"
                        "Rewrite the resume into the JSON ResumePayload format, obeying ALL rules.\n"
                        f"INPUT_JSON:\n{json.dumps(user_payload, ensure_ascii=False)}"
                    ),
                },
            ],
        )

        content = completion.choices[0].message.content or "{}"
        data = json.loads(content)
        payload = ResumePayload(**data)
        ats_score = score_ats(payload, job_text)
        return RewriteResult(payload=payload, ats_score=ats_score)


class OpenAIEnhancedRewritingAgent:
    """
    Hybrid agent:
    - Uses spaCy-based ResumeRewriter to extract structured sections (heading, experiences, projects, etc.).
    - Uses OpenAI only to rewrite bullet TEXT, keeping structure, roles, companies, and dates fixed.
    """

    def __init__(self, nlp: Language, model: str = "gpt-4o-mini"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required for OpenAIEnhancedRewritingAgent")
        self._client = OpenAI(api_key=api_key)
        self._model = model
        self._rewriter = ResumeRewriter(nlp)

    def rewrite(self, resume_text: str, job_text: str) -> RewriteResult:
        # First, build a safe structured payload from our deterministic rules.
        payload = self._rewriter.rewrite(resume_text, job_text)

        # Then, enrich bullet texts with OpenAI while preserving structure.
        for exp in payload.experiences:
            original_texts = [b.text for b in exp.bullets]
            rewritten = self._rewrite_bullets_with_openai(
                original_texts,
                job_text,
                context=f"Role: {exp.role}, Company: {exp.company}",
            )
            for b, new_text in zip(exp.bullets, rewritten):
                b.text = new_text
                b.has_metric = bool(METRIC_REGEX.search(new_text))

        for proj in payload.projects:
            original_texts = [b.text for b in proj.bullets]
            rewritten = self._rewrite_bullets_with_openai(
                original_texts,
                job_text,
                context=f"Project: {proj.name}, Stack: {proj.stack}",
            )
            for b, new_text in zip(proj.bullets, rewritten):
                b.text = new_text
                b.has_metric = bool(METRIC_REGEX.search(new_text))

        ats_score = score_ats(payload, job_text)
        return RewriteResult(payload=payload, ats_score=ats_score)

    def _rewrite_bullets_with_openai(self, bullets: list[str], job_text: str, context: str) -> list[str]:
        if not bullets:
            return bullets

        system_prompt = (
            "You rewrite resume bullet points for ATS optimization.\n"
            "Rules:\n"
            "1) You MUST keep the same underlying facts, systems, and metrics from the input bullets.\n"
            "2) For EACH input bullet, output ONE rewritten bullet in the SAME ORDER; length of output list\n"
            "   MUST equal length of input list.\n"
            "3) Format for every bullet:\n"
            '   \"Solved [problem or challenge] by [action + tools/skills], resulting in [quantifiable or\n'
            "   clearly observable outcome]\".\n"
            "4) 50–65% of bullets should include REAL metrics present in the input bullets (%, $, counts, time, etc.).\n"
            "   Do NOT invent numbers; if none are present, use qualitative outcomes instead.\n"
            "5) Use simple American English (Flesch Reading Ease > 60).\n"
            "6) Do NOT add new employers, projects, or products; only rephrase.\n"
            "7) Output STRICT JSON: {\"bullets\": [\"...\"]} with the same number of items as input.\n"
        )

        user_payload = {
            "job_description": job_text,
            "context": context,
            "bullets": bullets,
        }

        completion = self._client.chat.completions.create(
            model=self._model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": (
                        "Rewrite the following bullets according to the rules.\n"
                        f"INPUT_JSON:\n{json.dumps(user_payload, ensure_ascii=False)}"
                    ),
                },
            ],
        )

        content = completion.choices[0].message.content or "{}"
        try:
            data = json.loads(content)
            out = data.get("bullets") or []
            if isinstance(out, list) and len(out) == len(bullets):
                return [str(x) for x in out]
        except Exception:
            pass

        # Fallback to original bullets if parsing or length check fails.
        return bullets


class PdfGenerationAgent:
    """Agent responsible for LaTeX rendering and PDF generation."""

    def generate(self, payload: ResumePayload) -> Tuple[str, str]:
        """
        Returns (tex_source, pdf_b64).
        - tex_source: final LaTeX used for compilation
        - pdf_b64: base64-encoded compiled PDF
        """
        tex_source, pdf_b64 = generate_resume_files(payload)
        return tex_source, pdf_b64


