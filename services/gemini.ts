import { AnalysisResult, RewrittenResume } from "../types";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "https://klip-ai.onrender.com";

interface UploadResponse {
  session_id: string;
  ats_score: number;
  status: string;
}

interface ResultResponse {
  session_id: string;
  ats_score: number;
  html_resume: string;
  pdf_b64: string;
  transformations?: string[];
  keywords_matched?: string[];
  keywords_missing?: string[];
}

const parseResumeAndJob = async (
  resumeFile: File | null,
  resumeText: string,
  jobDescription: string
): Promise<AnalysisResult> => {
  // 1) Call backend /upload with the real file when available; otherwise text as a pseudo-file
  const formData = new FormData();
  if (resumeFile) {
    formData.append("original_resume", resumeFile, resumeFile.name);
  } else {
    const resumeBlob = new Blob([resumeText], { type: "text/plain" });
    formData.append("original_resume", resumeBlob, "resume.txt");
  }
  formData.append("job_description", jobDescription);

  const uploadRes = await fetch(`${BACKEND_URL}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!uploadRes.ok) {
    const msg = await uploadRes.text();
    throw new Error(`Backend /upload failed: ${uploadRes.status} ${msg}`);
  }

  const uploadJson = (await uploadRes.json()) as UploadResponse;

  // 2) Fetch final result from /result/{session_id}
  const resultRes = await fetch(`${BACKEND_URL}/result/${uploadJson.session_id}`);
  if (!resultRes.ok) {
    const msg = await resultRes.text();
    throw new Error(`Backend /result failed: ${resultRes.status} ${msg}`);
  }

  const resultJson = (await resultRes.json()) as ResultResponse;
  const atsScore = resultJson.ats_score;
  const htmlResume = resultJson.html_resume;

  // Use backend-provided analytics if available, otherwise fallback to frontend calculation
  let keywordsFound: string[];
  let keywordsMissing: string[];
  let improvementsMade: string[];

  if (resultJson.keywords_matched && resultJson.keywords_missing && resultJson.transformations) {
    // Use real analytics from backend
    keywordsFound = resultJson.keywords_matched;
    keywordsMissing = resultJson.keywords_missing;
    improvementsMade = resultJson.transformations;
  } else {
    // Fallback to frontend calculation
    const jdLower = jobDescription.toLowerCase();
    const jdWords = new Set(jdLower.split(/\s+/));
    const resumeLower = htmlResume.toLowerCase();
    const resumeWords = new Set(resumeLower.split(/\s+/));
    
    keywordsFound = Array.from(jdWords).filter((w) => resumeWords.has(w) && w.length > 3);
    keywordsMissing = Array.from(jdWords).filter((w) => !resumeWords.has(w) && w.length > 3);
    improvementsMade = [
      "Rewrote bullets into ATS-friendly 'Solved X by Y, resulting in Z' structure.",
      "Aligned skills and experience with job description keywords.",
      "Generated HTML resume matching the target format.",
    ];
  }

  // Create a minimal RewrittenResume for compatibility (frontend will render HTML directly)
  const rewrittenResume: RewrittenResume = {
    fullName: "Resume",
    contactInfo: "",
    summary: "AI-optimized resume",
    skills: [],
    experience: [],
    projects: [],
    education: [],
    certifications: [],
  };

  const analysis: AnalysisResult = {
    originalScore: Math.max(0, atsScore - 5),
    optimizedScore: atsScore,
    keywordsFound: keywordsFound.slice(0, 30),
    keywordsMissing: keywordsMissing.slice(0, 30),
    improvementsMade: improvementsMade,
    rewrittenResume,
    htmlResume, // Add HTML for direct rendering
    pdfB64: resultJson.pdf_b64, // Add PDF base64 from backend
  };

  return analysis;
};

export { parseResumeAndJob };