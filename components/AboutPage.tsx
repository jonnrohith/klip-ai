import React from 'react';

const AboutPage: React.FC = () => {
  return (
    <div className="w-full max-w-3xl mx-auto text-center animate-fade-in space-y-16 py-12">
      
      {/* Header */}
      <div className="space-y-6">
        <h1 className="text-5xl md:text-7xl font-serif">
          <span className="italic font-light">the</span> <span className="font-bold tracking-tight">PHILOSOPHY</span>
        </h1>
        <div className="w-24 h-[1px] bg-black mx-auto"></div>
      </div>

      {/* Content */}
      <div className="space-y-12 text-lg md:text-xl font-serif leading-relaxed text-gray-800">
        <p>
          <span className="font-bold">klip</span> is not just a resume rewriter. It is an instrument of clarity.
          In a world saturated with noise, we believe your professional story deserves to be heard with 
          <span className="italic"> absolute precision</span>.
        </p>

        <p>
          Currently powered by <span className="font-bold border-b border-black pb-0.5">CrewAI agent framework</span>, 
          our engine deconstructs your career history and reconstructs it through the lens of algorithmic perfection.
          We strip away the redundant, the vague, and the unseen—leaving only the essential.
        </p>

        <p className="text-sm opacity-70 italic">
          Version 2 will be powered by an open-source SLM, bringing the same precision with enhanced privacy and control.
        </p>

        <div className="grid md:grid-cols-3 gap-8 text-base pt-8">
            <div className="space-y-3">
                <div className="w-12 h-12 border border-black rounded-full flex items-center justify-center mx-auto text-2xl font-light italic">1</div>
                <h3 className="font-bold uppercase tracking-widest text-xs">Analysis</h3>
                <p className="opacity-70 text-sm">Parsing your history against modern Applicant Tracking Systems (ATS).</p>
            </div>
            <div className="space-y-3">
                <div className="w-12 h-12 border border-black rounded-full flex items-center justify-center mx-auto text-2xl font-light italic">2</div>
                <h3 className="font-bold uppercase tracking-widest text-xs">Synthesis</h3>
                <p className="opacity-70 text-sm">Matching keywords and metrics to the specific frequency of your target role.</p>
            </div>
            <div className="space-y-3">
                <div className="w-12 h-12 border border-black rounded-full flex items-center justify-center mx-auto text-2xl font-light italic">3</div>
                <h3 className="font-bold uppercase tracking-widest text-xs">Output</h3>
                <p className="opacity-70 text-sm">Generating a LaTeX-standard PDF designed to pass through digital gatekeepers.</p>
            </div>
        </div>

        <p className="text-sm opacity-50 italic pt-12">
          "Signal over noise."
        </p>
      </div>
    </div>
  );
};

export default AboutPage;