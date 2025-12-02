from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import os
import uuid
import time
import base64
import json
import re
import logging
from typing import Optional, Dict, Any
from threading import Lock
from collections import Counter

from models import UploadResponse
from utils.parser import parse_resume, parse_job_description

# Try to import OpenAI and WeasyPrint for integrated mode
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError):
    WEASYPRINT_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import redis
except Exception:
    redis = None

SESSION_TTL_SECONDS = 60 * 30
REWRITER_URL = os.getenv("REWRITER_URL", None)  # None means use integrated mode
PDF_URL = os.getenv("PDF_URL", None)  # None means use integrated mode
USE_MICROSERVICES = os.getenv("USE_MICROSERVICES", "false").lower() == "true"

# If URLs are not set and microservices not explicitly enabled, use integrated mode
if not USE_MICROSERVICES:
    REWRITER_URL = None
    PDF_URL = None


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


# Integrated rewriter function (used when REWRITER_URL is not set)
def _get_openai_client():
    """Get OpenAI client, raising clear error if API key is missing."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set. Please configure it.")
    import httpx
    http_client = httpx.Client(timeout=120.0)
    return OpenAI(api_key=api_key, http_client=http_client)


def _rewrite_resume_integrated(resume_text: str, job_description: str) -> Dict[str, Any]:
    """Rewrite resume using OpenAI directly (integrated mode)."""
    if not OPENAI_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="OpenAI library not available. Install with: pip install openai"
        )
    
    system_prompt = """You are a recruiter-proof resume editor. Output ONLY valid HTML with embedded CSS—no markdown, no explanations.

CRITICAL: The HTML structure MUST match EXACTLY. Use the exact class names and structure shown below.

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
.resume {
  width: 100%;
  max-width: 850px;
  margin: 0 auto;
  padding: 40px 50px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
  font-size: 11pt;
  line-height: 1.4;
  color: #000;
  background: white;
}
.header {
  text-align: center;
  margin-bottom: 20px;
  border-bottom: 1px solid #000;
  padding-bottom: 10px;
}
.header h1 {
  font-size: 24pt;
  font-weight: bold;
  margin: 0 0 5px 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.header .title {
  font-size: 11pt;
  margin: 5px 0;
  font-style: italic;
}
.header .contact {
  font-size: 10pt;
  margin: 5px 0;
}
section {
  margin-bottom: 15px;
}
h2 {
  font-size: 11pt;
  font-weight: bold;
  text-transform: uppercase;
  margin: 15px 0 8px 0;
  border-bottom: 1px solid #000;
  padding-bottom: 2px;
  letter-spacing: 0.5px;
}
.job, .project {
  margin-bottom: 12px;
}
.job-header, .project-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 2px;
  width: 100%;
}
.role {
  font-weight: bold;
  font-size: 11pt;
  flex: 1;
}
.project-name {
  font-weight: bold;
  font-size: 11pt;
  flex: 1;
}
.dates {
  font-size: 10pt;
  text-align: right;
  white-space: nowrap;
  margin-left: 10px;
}
.job-meta {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 5px;
  width: 100%;
}
.company {
  font-style: italic;
  font-size: 10pt;
  flex: 1;
}
.job-meta .location {
  font-size: 10pt;
  text-align: right;
  font-style: italic;
  white-space: nowrap;
  margin-left: 10px;
}
.bullets {
  margin: 5px 0 0 15px;
  padding-left: 0;
  list-style-type: disc;
  list-style-position: outside;
}
.bullets li {
  margin-bottom: 3px;
  font-size: 10pt;
  text-align: left;
  padding-left: 5px;
}
.skills p {
  margin: 3px 0;
  font-size: 10pt;
}
.edu-entry {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 2px;
  width: 100%;
}
.school {
  font-weight: bold;
  font-size: 11pt;
  flex: 1;
}
.degree {
  font-style: italic;
  font-size: 10pt;
  margin: 2px 0 0 0;
}
.education .location {
  font-size: 10pt;
  margin: 0;
  text-align: right;
}
</style>

<div class="resume">
  <div class="header">
    <h1>Name Surname</h1>
    <p class="title">Job Title</p>
    <p class="contact">Phone | Email | LinkedIn | GitHub</p>
  </div>

  <section class="experience">
    <h2>EXPERIENCE</h2>
    <div class="job">
      <div class="job-header">
        <span class="role">Role Title</span>
        <span class="dates">Start Date - End Date</span>
      </div>
      <div class="job-meta">
        <span class="company">Company Name</span>
        <span class="location">City, Country</span>
      </div>
      <ul class="bullets">
        <li>Solved [problem] by [action + tools], resulting in [metric/outcome]</li>
        <li>Solved [problem] by [action + tools], resulting in [metric/outcome]</li>
      </ul>
    </div>
  </section>

  <section class="skills">
    <h2>TECHNICAL SKILLS</h2>
    <p><strong>Languages:</strong> Skill1, Skill2, Skill3</p>
    <p><strong>Frameworks:</strong> Framework1, Framework2</p>
    <p><strong>Developer Tools:</strong> Tool1, Tool2</p>
    <p><strong>Libraries:</strong> Lib1, Lib2</p>
  </section>

  <section class="projects">
    <h2>PROJECTS</h2>
    <div class="project">
      <div class="project-header">
        <span class="project-name"><strong>Project Name</strong> | <em>Tech Stack</em></span>
        <span class="dates">Jan 2023 - Dec 2023</span>
      </div>
      <ul class="bullets">
        <li>Solved [problem] by [action + tools], resulting in [metric/outcome]</li>
      </ul>
    </div>
  </section>

  <section class="education">
    <h2>EDUCATION</h2>
    <div class="edu-entry">
      <span class="school">University Name</span>
      <span class="dates">Start - End</span>
    </div>
    <p class="degree">Degree, Major</p>
    <p class="location">City, Country</p>
  </section>

  <section class="certifications">
    <h2>CERTIFICATIONS</h2>
    <p><strong>Certification Name</strong></p>
    <p><em>Issued Date - Expires Date</em></p>
  </section>
</div>

CRITICAL RULES - FOLLOW STRICTLY:

1. CONTENT TRANSFORMATION (MANDATORY):
   - You MUST completely rewrite every bullet point. Do NOT copy-paste original text.
   - Transform generic descriptions into specific, impactful achievements.
   - Use different words, phrases, and sentence structures than the original.
   - Each bullet must be substantially different from the original while preserving the core achievement.

2. ZERO REPETITION (MANDATORY):
   - NEVER repeat the same word, phrase, or pattern across multiple bullets.
   - Use synonyms and varied vocabulary throughout the resume.
   - Each bullet must use unique action verbs and descriptive terms.
   - If you see "Solved X by Y" appearing multiple times, vary the phrasing: "Addressed X through Y", "Resolved X using Y", "Tackled X by implementing Y", etc.

3. BULLET FORMAT (MANDATORY):
   - Every bullet MUST follow: "Solved [problem] by [action + tools], resulting in [metric/outcome]"
   - Vary the opening: "Solved", "Addressed", "Resolved", "Tackled", "Overcame", "Eliminated", "Reduced", "Improved"
   - Vary the connector: "by", "through", "using", "via", "with", "by implementing", "by deploying"
   - Vary the result phrase: "resulting in", "leading to", "achieving", "delivering", "yielding", "producing"

4. METRICS (MANDATORY):
   - 50-65% of bullets must contain real numbers from the original (%, $, time, team size, volume).
   - Extract numbers conservatively from the original resume. Never invent metrics.
   - If no numbers exist, infer reasonable ones based on context (e.g., "team of 5" if mentioned, "30% improvement" if "significant" is mentioned).

5. INDUSTRY AWARENESS:
   - Analyze the job description to understand the industry and role requirements.
   - Tailor technical terms, tools, and achievements to match the job description.
   - Use industry-appropriate language and terminology.
   - Ensure all achievements are realistic and achievable for the role level.

6. CONTENT PRESERVATION:
   - Extract ALL roles, companies, dates, locations from the original resume. Never drop or invent.
   - CRITICAL: Projects MUST include dates in the format "MMM YYYY - MMM YYYY" (e.g., "Jan 2023 - Dec 2023"). 
   - If the original resume has project dates, extract them exactly. If only a year is given, use "Jan YYYY - Dec YYYY". 
   - If no dates are provided, estimate reasonable dates based on the project context (e.g., if it's a recent project, use dates from the past 1-2 years).
   - NEVER leave project dates blank or use placeholder text like "Start - End".
   - Keep all original experience—don't compress or merge roles.
   - Preserve the factual accuracy of all information.

7. LANGUAGE QUALITY:
   - Use simple American English (Flesch readability > 60).
   - Write in active voice.
   - Use concise, powerful language.

8. OUTPUT FORMAT:
   - Use EXACTLY the HTML structure shown above with the <style> tag and <div class="resume"> wrapper.
   - Output ONLY the complete HTML starting with <style> and ending with </div>, no markdown, no explanations, no code blocks.

EXAMPLE OF GOOD TRANSFORMATION:
Original: "Developed web applications using React and Node.js"
Rewritten: "Solved frontend performance bottlenecks by implementing React with code splitting and Node.js microservices, resulting in 40% faster page load times"

EXAMPLE OF BAD TRANSFORMATION (REJECTED):
Original: "Developed web applications using React and Node.js"
Bad: "Solved web application development by using React and Node.js, resulting in successful deployment"
(Too similar to original, lacks specificity, no real metric)"""

    try:
        client = _get_openai_client()
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"""You are rewriting a resume to match a job description. 

CRITICAL: You must COMPLETELY TRANSFORM every bullet point. Do not copy the original text. Use different words, phrases, and structures. Ensure ZERO repetition across bullets.

ORIGINAL RESUME TEXT:
{resume_text}

TARGET JOB DESCRIPTION:
{job_description}

INSTRUCTIONS:
1. Completely rewrite every bullet point using the "Solved X by Y, resulting in Z" format
2. Use ZERO repeated words or phrases across all bullets
3. Vary your vocabulary, action verbs, and sentence structures
4. Extract and include real metrics from the original (50-65% of bullets should have numbers)
5. Tailor content to match the job description's industry and requirements
6. CRITICAL: Extract dates for ALL projects. If dates are missing, estimate reasonable dates (e.g., "Jan 2023 - Dec 2023"). Never use placeholder text.
7. Output the complete HTML resume following the exact structure provided in the system prompt

Rewrite the resume now:""",
                },
            ],
            temperature=0.7,
        )

        html_resume = completion.choices[0].message.content.strip()
        
        # Clean up any markdown code blocks if OpenAI wrapped it
        if html_resume.startswith("```"):
            lines = html_resume.split("\n")
            html_resume = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
        
        # Analyze transformations and keywords
        resume_lower = resume_text.lower()
        jd_lower = job_description.lower()
        html_lower = html_resume.lower()
        
        # Extract keywords from job description (meaningful words only)
        jd_words = set(re.findall(r'\b\w{4,}\b', jd_lower))
        html_words = set(re.findall(r'\b\w{4,}\b', html_lower))
        original_words = set(re.findall(r'\b\w{4,}\b', resume_lower))
        
        # Keywords matched in rewritten resume
        keywords_matched = sorted(list(jd_words & html_words), key=lambda x: (-html_lower.count(x), x))[:30]
        
        # Keywords missing from rewritten resume
        keywords_missing = sorted(list(jd_words - html_words), key=lambda x: (-jd_lower.count(x), x))[:30]
        
        # Generate real transformations based on analysis
        transformations = []
        
        html_bullets = len(re.findall(r'<li>', html_resume))
        if html_bullets > 0:
            transformations.append(f"Rewrote {html_bullets} bullet points into ATS-friendly 'Solved X by Y, resulting in Z' structure")
        
        new_keywords = html_words - original_words
        if len(new_keywords & jd_words) > 0:
            transformations.append(f"Added {len(new_keywords & jd_words)} job-relevant keywords to align with job description")
        
        metrics_found = len(re.findall(r'\d+%|\$\d+|\d+\s*(?:hours?|days?|months?|years?|people|users|team)', html_resume, re.IGNORECASE))
        if metrics_found > 0:
            transformations.append(f"Included {metrics_found} quantifiable metrics to demonstrate impact")
        
        if '<section class="experience">' in html_resume:
            transformations.append("Structured resume with proper HTML formatting for ATS parsing")
        
        if not transformations:
            transformations = [
                "Rewrote bullets into ATS-friendly 'Solved X by Y, resulting in Z' structure",
                "Aligned skills and experience with job description keywords",
                "Generated HTML resume matching the target format"
            ]
        
        # Calculate ATS score based on keyword overlap
        overlap = len(jd_words & html_words)
        ats_score = min(95, max(80, int(80 + (overlap / max(len(jd_words), 1)) * 15)))

        return {
            "html_resume": html_resume,
            "ats_score": ats_score,
            "transformations": transformations,
            "keywords_matched": keywords_matched,
            "keywords_missing": keywords_missing
        }
    except RuntimeError as e:
        if "OPENAI_API_KEY" in str(e):
            raise HTTPException(
                status_code=503,
                detail="OPENAI_API_KEY environment variable is not set. Please configure it."
            )
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")
    except Exception as e:
        error_msg = str(e)
        if "API key" in error_msg or "authentication" in error_msg.lower():
            raise HTTPException(
                status_code=401,
                detail=f"OpenAI API authentication failed: {error_msg}. Please check your OPENAI_API_KEY."
            )
        raise HTTPException(status_code=500, detail=f"OpenAI error: {error_msg}")


def _generate_pdf_integrated(html_content: str) -> bytes:
    """Generate PDF from HTML using WeasyPrint directly (integrated mode)."""
    if not WEASYPRINT_AVAILABLE:
        raise ValueError("WeasyPrint not available")
    
    # Ensure HTML has proper structure for WeasyPrint
    html_content = html_content.strip()
    
    # If HTML doesn't start with <!DOCTYPE or <html, wrap it properly
    if not html_content.startswith("<!DOCTYPE") and not html_content.startswith("<html"):
        style_match = re.search(r'<style>(.*?)</style>', html_content, re.DOTALL)
        style_content = style_match.group(1) if style_match else ""
        
        resume_start = html_content.find('<div class="resume">')
        if resume_start == -1:
            resume_match = re.search(r'<div[^>]*class=["\']resume["\'][^>]*>', html_content)
            if resume_match:
                resume_start = resume_match.start()
        
        if resume_start != -1:
            depth = 0
            i = resume_start
            resume_end = -1
            while i < len(html_content):
                if html_content[i:i+5] == '<div ' or html_content[i:i+6] == '<div>':
                    depth += 1
                    i = html_content.find('>', i) + 1
                elif html_content[i:i+6] == '</div>':
                    depth -= 1
                    if depth == 0:
                        resume_end = i + 6
                        break
                    i += 6
                else:
                    i += 1
            
            if resume_end > 0:
                body_content = html_content[resume_start:resume_end]
            else:
                body_content = html_content[resume_start:]
        else:
            body_content = html_content
        
        pdf_style_override = """
        .resume {
            padding: 30px 15px !important;
            max-width: 100% !important;
            margin: 0 !important;
        }
        """
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: letter;
            margin: 0.25in 0.15in;
        }}
        body {{
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
        }}
        {style_content}
        {pdf_style_override}
    </style>
</head>
<body>
    {body_content}
</body>
</html>"""
    
    html_doc = HTML(string=html_content)
    pdf_bytes = html_doc.write_pdf()
    
    if len(pdf_bytes) == 0:
        raise ValueError("Generated PDF is empty")
    
    return pdf_bytes


@app.post("/upload", response_model=UploadResponse)
async def upload_resume(
    original_resume: UploadFile = File(...),
    job_description: Optional[str] = Form(None),
    job_description_file: Optional[UploadFile] = File(None),
) -> JSONResponse:
    resume_text = parse_resume(original_resume)
    jd_text, _ = parse_job_description(job_description, job_description_file)

    # Use integrated mode if microservice URLs are not set
    if REWRITER_URL:
        # Microservice mode: call external rewriter service
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                rewriter_resp = await client.post(
                    REWRITER_URL,
                    json={"resume_text": resume_text, "job_description": jd_text},
                )
                if rewriter_resp.status_code != 200:
                    error_detail = rewriter_resp.text
                    try:
                        error_json = rewriter_resp.json()
                        error_detail = error_json.get("detail", error_detail)
                    except:
                        pass
                    raise HTTPException(
                        status_code=502, 
                        detail=f"Rewriter service failed: {error_detail}"
                    )
                rewriter_data = rewriter_resp.json()
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=503,
                    detail=f"Cannot connect to rewriter service at {REWRITER_URL}. Please ensure the service is running and OPENAI_API_KEY is configured."
                )
            html_resume = rewriter_data["html_resume"]
            ats_score = rewriter_data["ats_score"]
            transformations = rewriter_data.get("transformations", [])
            keywords_matched = rewriter_data.get("keywords_matched", [])
            keywords_missing = rewriter_data.get("keywords_missing", [])
    else:
        # Integrated mode: use internal rewriter function
        rewriter_data = _rewrite_resume_integrated(resume_text, jd_text)
        html_resume = rewriter_data["html_resume"]
        ats_score = rewriter_data["ats_score"]
        transformations = rewriter_data.get("transformations", [])
        keywords_matched = rewriter_data.get("keywords_matched", [])
        keywords_missing = rewriter_data.get("keywords_missing", [])

    # Generate PDF (optional - gracefully handle failures)
    pdf_b64 = ""
    if PDF_URL:
        # Microservice mode: call external PDF service
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                pdf_resp = await client.post(
                    PDF_URL,
                    json={"html_content": html_resume},
                )
                if pdf_resp.status_code == 200:
                    pdf_b64 = base64.b64encode(pdf_resp.content).decode("utf-8")
            except Exception as e:
                logger.warning(f"PDF service failed: {e}")
    else:
        # Integrated mode: use internal PDF function
        try:
            pdf_bytes = _generate_pdf_integrated(html_resume)
            pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")
        except Exception as e:
            logger.warning(f"PDF generation failed: {e}")

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
