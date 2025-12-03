# Architecture Overview

## Current Architecture

The application supports **two deployment modes**:

### 1. Integrated Mode (Default - Current)
**Single Service Deployment**
- **Backend:** `main.py` (FastAPI)
- **Location:** Project root
- **Technologies:**
  - **Resume Rewriting:** OpenAI API (`gpt-4o-mini`)
  - **PDF Generation:** WeasyPrint (server-side) OR html2pdf.js (client-side fallback)
- **Deployment:** Single service (Render, Railway, etc.)

### 2. Microservice Mode (Optional)
**Separate Services**
- **Rewriter Service:** `rewriter-service/main.py`
  - **Technology:** OpenAI API (`gpt-4o-mini`)
  - **Port:** 8001
  - **Endpoint:** `POST /generate`
  
- **PDF Service:** `pdf-service/main.py`
  - **Technology:** WeasyPrint
  - **Port:** 8002
  - **Endpoint:** `POST /generate`

- **Gateway Service:** `main.py`
  - **Port:** 8000
  - **Endpoints:** `POST /upload`, `GET /result/{session_id}`
  - **Orchestrates:** Calls rewriter and PDF services

---

## Technologies Used

### Resume Rewriting
- **Primary:** OpenAI API (`gpt-4o-mini`)
- **Location:** 
  - Integrated: `main.py` → `_rewrite_resume_integrated()`
  - Microservice: `rewriter-service/main.py`
- **Input:** Resume text + Job description
- **Output:** HTML resume with embedded CSS

### PDF Generation
- **Primary (Server-side):** WeasyPrint
  - **Location:** 
    - Integrated: `main.py` → `_generate_pdf_integrated()`
    - Microservice: `pdf-service/main.py`
  - **Input:** HTML content
  - **Output:** PDF bytes (base64 encoded)
  
- **Fallback (Client-side):** html2pdf.js
  - **Location:** `components/ResumePreview.tsx` → `handleDownload()`
  - **Used when:** WeasyPrint unavailable (Vercel, local dev without system libs)
  - **Input:** HTML element
  - **Output:** PDF file download

### Legacy Agents (Not Currently Used)
Located in `utils/agents.py`:
- **ResumeRewritingAgent:** spaCy-based (old)
- **OpenAIResumeRewritingAgent:** OpenAI with JSON output (old)
- **OpenAIEnhancedRewritingAgent:** Hybrid spaCy + OpenAI (old)
- **PdfGenerationAgent:** LaTeX/pdflatex-based (old)

---

## Current Implementation

### What's Actually Running

**For Resume Rewriting:**
- ✅ **OpenAI API** (`gpt-4o-mini`)
- ✅ Generates complete HTML resume
- ✅ Uses system prompt with strict rules
- ❌ spaCy (removed from requirements, not used)

**For PDF Generation:**
- ✅ **WeasyPrint** (when system libraries available - Render, Railway)
- ✅ **html2pdf.js** (fallback - Vercel, local dev)
- ❌ LaTeX/pdflatex (old, not used)

---

## File Structure

```
resumate-ai/
├── main.py                    # Gateway + Integrated functions
├── rewriter-service/
│   └── main.py                # Microservice: OpenAI rewriting
├── pdf-service/
│   └── main.py                # Microservice: WeasyPrint PDF
├── utils/
│   └── agents.py              # Legacy agent classes (not used)
└── components/
    └── ResumePreview.tsx      # Client-side PDF fallback (html2pdf.js)
```

---

## Summary

**What We Use:**
1. **OpenAI API** - For AI-powered resume rewriting
2. **WeasyPrint** - For server-side PDF generation (when available)
3. **html2pdf.js** - For client-side PDF generation (fallback)

**What We Don't Use:**
- ❌ spaCy (removed, not needed)
- ❌ LaTeX/pdflatex (old approach)
- ❌ Legacy agent classes in `utils/agents.py`

**Current Mode:**
- ✅ **Integrated Mode** (default)
- ✅ Single service deployment
- ✅ Works on Render, Railway, etc.

