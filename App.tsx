import React, { useState } from 'react';
import InputSection from './components/InputSection';
import ResumePreview from './components/ResumePreview';
import AboutPage from './components/AboutPage';
import { AnalysisResult, AppStep } from './types';
import { parseResumeAndJob } from './services/gemini';

const App: React.FC = () => {
  const [step, setStep] = useState<AppStep>(AppStep.INPUT);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async (resumeFile: File | null, resume: string, jobDesc: string) => {
    setIsProcessing(true);
    setError(null);
    try {
      const data = await parseResumeAndJob(resumeFile, resume, jobDesc);
      setResult(data);
      setStep(AppStep.RESULT);
    } catch (err: any) {
      console.error(err);
      setError("Failed to process resume. Please ensure you have a valid API Key and try again. " + (err.message || ''));
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReset = () => {
    setStep(AppStep.INPUT);
    setResult(null);
    setError(null);
  };

  const handleGoHome = () => {
     setStep(AppStep.INPUT);
  }

  const handleGoAbout = () => {
    setStep(AppStep.ABOUT);
  }

  return (
    <div className="min-h-screen flex flex-col overflow-x-hidden selection:bg-black selection:text-white">
      {/* Decorative Circle Element (Top Right) */}
      <div className="fixed -top-20 -right-20 w-64 h-64 border border-gray-400 rounded-full opacity-20 pointer-events-none no-print animate-pulse-slow"></div>

      {/* Navbar: Minimalist Editorial Style */}
      <nav className="no-print pt-8 px-8 md:px-16 flex justify-between items-center z-10">
        <div onClick={handleGoHome} className="group cursor-pointer">
          <div className="text-4xl md:text-5xl font-serif font-bold tracking-tighter hover:italic transition-all duration-300">
            klip
          </div>
          <div className="h-[1px] w-0 group-hover:w-full bg-black transition-all duration-500"></div>
        </div>
        
        {/* 'About' styled as the circular menu trigger in reference */}
        <div onClick={handleGoAbout} className="relative group cursor-pointer">
          <div className="w-12 h-12 border border-black rounded-full flex items-center justify-center transition-all duration-500 group-hover:scale-110">
             <div className="space-y-1">
               <div className="w-4 h-[1px] bg-black"></div>
               <div className="w-4 h-[1px] bg-black"></div>
             </div>
          </div>
          <span className="absolute right-16 top-1/2 -translate-y-1/2 text-sm font-serif italic opacity-0 group-hover:opacity-100 transition-opacity duration-300 whitespace-nowrap">
            About klip
          </span>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-grow flex flex-col items-center pt-12 md:pt-20 px-6 relative">
        
        {/* Error Banner */}
        {error && (
          <div className="max-w-xl w-full mb-8 bg-transparent border border-red-500 text-red-600 px-6 py-4 text-center font-serif italic no-print">
            {error}
          </div>
        )}

        {/* Steps */}
        {step === AppStep.INPUT && (
          <div className="w-full max-w-4xl animate-fade-in-up z-10">
            <InputSection onAnalyze={handleAnalyze} isProcessing={isProcessing} />
          </div>
        )}

        {step === AppStep.RESULT && result && (
          <div className="w-full animate-fade-in z-10">
             <div className="text-center mb-12 no-print">
               <button 
                 onClick={handleReset}
                 className="font-serif italic text-xl hover:tracking-widest transition-all duration-300 border-b border-transparent hover:border-black"
               >
                 start over
               </button>
            </div>
            <ResumePreview data={result} onReset={handleReset} />
          </div>
        )}

        {step === AppStep.ABOUT && (
           <div className="w-full animate-fade-in z-10">
              <AboutPage />
           </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-auto py-8 text-center no-print">
        <p className="font-serif text-xs italic opacity-50">"Your career, refined to its essence" — klip engine v1.0</p>
      </footer>
    </div>
  );
};

export default App;