from __future__ import annotations

import random
from typing import Sequence

from models import ResumePayload


def score_ats(payload: ResumePayload, job_text: str) -> int:
    """Return a bounded ATS score between 80 and 95."""
    base = 80
    bonus = min(15, len(payload.skills))
    overlap = _keyword_overlap(payload.skills, job_text)
    noise = random.randint(0, 4)
    score = base + int(bonus * overlap) + noise
    return max(80, min(95, score))


def _keyword_overlap(skills: Sequence[str], job_text: str) -> float:
    if not job_text:
        return 0.5
    job_lower = job_text.lower()
    matches = sum(1 for skill in skills if skill.lower() in job_lower)
    return matches / max(1, len(skills))

