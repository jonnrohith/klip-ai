import React, { useState, useRef } from 'react';

interface InputSectionProps {
  onAnalyze: (resumeFile: File | null, resumeText: string, jobDesc: string) => void;
  isProcessing: boolean;
}

const InputSection: React.FC<InputSectionProps> = ({ onAnalyze, isProcessing }) => {
  const [resumeText, setResumeText] = useState('');
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jobDesc, setJobDesc] = useState('');
  const [fileName, setFileName] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleResumeFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setFileName(file.name);
      setResumeFile(file);
      const reader = new FileReader();
      reader.onload = (event) => {
        setResumeText(event.target?.result as string);
      };
      reader.readAsText(file);
    }
  };

  return (
    <div className="flex flex-col items-center w-full relative">
      
      {/* Decorative Center Element behind content */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-white rounded-full blur-3xl opacity-40 -z-10 pointer-events-none"></div>

      {/* 1. Upload Resume Section */}
      <div className="mb-16 md:mb-24 flex flex-col items-center gap-6 text-center">
        <h2 className="text-5xl md:text-7xl font-serif">
          <span className="italic font-light mr-4">upload</span>
          <span className="font-bold tracking-tight">RESUME</span>
        </h2>
        
        <div 
          onClick={() => fileInputRef.current?.click()}
          className="group relative cursor-pointer mt-4"
        >
          {/* Animated Circle Button */}
          <div className="w-24 h-24 border border-black rounded-full flex items-center justify-center bg-transparent group-hover:bg-black transition-all duration-500 ease-out">
            <span className="text-3xl font-light text-black group-hover:text-[#EAE8E3] transition-colors duration-300">
              {fileName ? '✓' : '+'}
            </span>
          </div>
          
          {/* Rotating Text Ring (Simulated with CSS or keep simple) */}
          <div className="absolute -inset-2 border border-dashed border-gray-400 rounded-full opacity-0 group-hover:opacity-100 transition-all duration-700 rotate-0 group-hover:rotate-180"></div>
          
          <input 
            type="file" 
            ref={fileInputRef}
            accept=".txt,.md,.pdf" 
            onChange={handleResumeFile}
            className="hidden"
          />
        </div>

        {fileName && (
          <span className="font-mono text-xs uppercase tracking-widest mt-2 border-b border-black pb-1">
            {fileName}
          </span>
        )}
        
        {!fileName && (
          <button 
            onClick={() => {
              const text = prompt("Paste resume text:");
              if (text) {
                setResumeText(text);
                setFileName("Text pasted");
              }
            }}
            className="text-xs font-serif italic text-gray-500 hover:text-black transition-colors"
          >
            (or paste text directly)
          </button>
        )}
      </div>

      {/* 2. Job Description Section */}
      <div className="w-full mb-16 relative">
        <h2 className="text-4xl md:text-6xl font-serif text-center mb-8">
          <span className="font-bold">TARGET</span> <span className="italic font-light">job description</span>
        </h2>
        
        <div className="relative w-full max-w-2xl mx-auto group">
          <textarea
            className="w-full h-48 bg-transparent p-4 text-lg md:text-xl font-serif leading-relaxed border-l border-black focus:outline-none focus:border-l-4 transition-all resize-none placeholder:text-gray-400/50 text-center md:text-left"
            placeholder="Paste the job description here to begin the alignment process..."
            value={jobDesc}
            onChange={(e) => setJobDesc(e.target.value)}
          />
          {/* Bottom Line Animation */}
          <div className="absolute bottom-0 left-0 w-0 h-[1px] bg-black transition-all duration-700 group-hover:w-full"></div>
        </div>
      </div>

      {/* Action Button */}
      <button
        onClick={() => onAnalyze(resumeFile, resumeText, jobDesc)}
        disabled={(!resumeFile && !resumeText) || !jobDesc || isProcessing}
        className={`group relative px-12 py-4 overflow-hidden rounded-full transition-all duration-500
          ${((!resumeFile && !resumeText) || !jobDesc || isProcessing) 
            ? 'opacity-50 cursor-not-allowed' 
            : 'opacity-100 hover:scale-105'
          }`}
      >
        <div className="absolute inset-0 bg-black transition-transform duration-500 group-hover:scale-110"></div>
        <span className="relative z-10 text-[#EAE8E3] font-serif italic text-2xl px-6">
          {isProcessing ? 'processing' : 'optimize'}
        </span>
      </button>

    </div>
  );
};

export default InputSection;