export interface ResumeSection {
  title: string;
  content: string[];
}

export interface RewrittenResume {
  fullName: string;
  contactInfo: string; // Email | LinkedIn | Github etc
  summary: string;
  skills: {
    category: string; // e.g., "Languages", "Frameworks"
    items: string; // e.g., "Java, Python, C++"
  }[];
  experience: {
    role: string;
    company: string;
    location: string;
    duration: string;
    points: string[];
  }[];
  projects: {
    name: string;
    technologies: string;
    duration: string;
    points: string[];
  }[];
  education: {
    degree: string;
    school: string;
    location: string;
    year: string;
  }[];
  certifications: {
    name: string;
    issuer: string;
    date: string;
  }[];
}

export interface AnalysisResult {
  originalScore: number;
  optimizedScore: number;
  keywordsFound: string[];
  keywordsMissing: string[];
  improvementsMade: string[];
  rewrittenResume: RewrittenResume;
  htmlResume?: string;
  pdfB64?: string;
}

export enum AppStep {
  INPUT = 'INPUT',
  PROCESSING = 'PROCESSING',
  RESULT = 'RESULT',
  ABOUT = 'ABOUT'
}