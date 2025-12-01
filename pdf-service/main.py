from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import base64
import io
import os
import sys

# Set library paths for WeasyPrint on macOS
if sys.platform == "darwin":
    homebrew_lib = "/opt/homebrew/lib"
    if os.path.exists(homebrew_lib):
        os.environ.setdefault("DYLD_LIBRARY_PATH", homebrew_lib)
        # Also try to set it via ctypes if needed
        try:
            import ctypes
            ctypes.CDLL(f"{homebrew_lib}/libgobject-2.0.dylib", mode=ctypes.RTLD_GLOBAL)
        except:
            pass

app = FastAPI(title="PDF Generation Service")

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError) as e:
    WEASYPRINT_AVAILABLE = False
    print(f"WeasyPrint not available: {e}")


class PdfRequest(BaseModel):
    html_content: str


@app.post("/generate")
async def generate_pdf(req: PdfRequest):
    if not WEASYPRINT_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="PDF generation unavailable. WeasyPrint system dependencies not installed. See: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation"
        )
    try:
        import re
        import logging
        logger = logging.getLogger(__name__)
        
        # Ensure HTML has proper structure for WeasyPrint
        html_content = req.html_content.strip()
        logger.info(f"Received HTML content, length: {len(html_content)}")
        
        # If HTML doesn't start with <!DOCTYPE or <html, wrap it properly
        if not html_content.startswith("<!DOCTYPE") and not html_content.startswith("<html"):
            # Extract style if present
            style_match = re.search(r'<style>(.*?)</style>', html_content, re.DOTALL)
            style_content = style_match.group(1) if style_match else ""
            
            # Extract body content - find the opening <div class="resume"> and match to its closing tag
            # We need to handle nested divs properly
            resume_start = html_content.find('<div class="resume">')
            if resume_start == -1:
                # Try alternative pattern
                resume_start = html_content.find("<div class='resume'>")
            if resume_start == -1:
                # Try with any attributes
                resume_match = re.search(r'<div[^>]*class=["\']resume["\'][^>]*>', html_content)
                if resume_match:
                    resume_start = resume_match.start()
            
            if resume_start != -1:
                # Find the matching closing tag by counting divs
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
                    # Fallback: use from start to end
                    body_content = html_content[resume_start:]
                    logger.warning("Could not find matching closing div, using partial content")
            else:
                # Fallback: use the entire content
                body_content = html_content
                logger.warning("Could not find resume div, using entire HTML content")
            
            # Wrap in proper HTML structure with better CSS for PDF
            # Override padding for PDF to reduce side margins
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
            logger.info(f"Wrapped HTML, final length: {len(html_content)}")
        else:
            logger.info("HTML already has proper structure")
        
        # Generate PDF
        html_doc = HTML(string=html_content)
        pdf_bytes = html_doc.write_pdf()
        logger.info(f"Generated PDF, size: {len(pdf_bytes)} bytes")
        
        if len(pdf_bytes) == 0:
            raise ValueError("Generated PDF is empty")

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=resume.pdf"},
        )
    except Exception as e:
        import traceback
        error_detail = f"PDF generation error: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)


@app.get("/health")
async def health():
    return {"status": "ok"}

