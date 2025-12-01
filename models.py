from typing import List, Optional

from pydantic import BaseModel, Field


class Bullet(BaseModel):
    text: str = Field(..., description="ATS-compliant bullet sentence")
    has_metric: bool = Field(False, description="Flag indicating bullet includes quantifiable metric")


class Experience(BaseModel):
    role: str
    company: str
    location: str
    start: str
    end: str
    bullets: List[Bullet]


class Project(BaseModel):
    name: str
    stack: str
    timeline: str
    bullets: List[Bullet]


class Heading(BaseModel):
    name: str
    title: str
    phone: str
    email: str
    linkedin: str
    github: str


class ResumePayload(BaseModel):
    heading: Heading
    experiences: List[Experience]
    skills: List[str]
    projects: List[Project]
    education: str
    certifications: List[str]


class UploadResponse(BaseModel):
    session_id: str
    ats_score: int
    status: str = Field("processing", description="Status of the rewrite flow")


class ResultResponse(BaseModel):
    session_id: str
    ats_score: int
    resume_data: ResumePayload
    final_resume_tex: str
    final_resume_pdf_b64: str

