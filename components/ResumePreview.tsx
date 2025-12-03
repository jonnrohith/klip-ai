import React from 'react';
import { AnalysisResult } from '../types';
import ScoreGauge from './ScoreGauge';
import html2pdf from 'html2pdf.js';

interface ResumePreviewProps {
  data: AnalysisResult;
  onReset: () => void;
}

const ResumePreview: React.FC<ResumePreviewProps> = ({ data }) => {
  const { rewrittenResume, keywordsFound, keywordsMissing, improvementsMade, originalScore, optimizedScore, pdfB64 } = data;

  const handleDownload = async () => {
    if (pdfB64 && pdfB64.length > 0) {
      // Use the PDF from backend
      const byteCharacters = atob(pdfB64);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${rewrittenResume.fullName.replace(/\s+/g, '_')}_Resume.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } else if (data.htmlResume) {
      // Fallback: Generate PDF from HTML using html2pdf.js
      try {
        // Find the resume container element
        const resumeContainer = document.querySelector('.resume-container') || 
                                document.getElementById('resume-preview')?.querySelector('.resume-container');
        
        let elementToConvert;
        
        if (resumeContainer) {
          elementToConvert = resumeContainer;
          // Ensure white background
          (elementToConvert as HTMLElement).style.backgroundColor = 'white';
        } else {
          // Create a temporary element with the HTML resume
          const tempDiv = document.createElement('div');
          tempDiv.innerHTML = data.htmlResume;
          tempDiv.style.width = '8.5in';
          tempDiv.style.padding = '0';
          tempDiv.style.margin = '0';
          tempDiv.style.backgroundColor = 'white';
          tempDiv.style.background = 'white';
          // Ensure proper spacing for PDF
          tempDiv.style.lineHeight = '1.4';
          document.body.appendChild(tempDiv);
          elementToConvert = tempDiv;
        }
        
        // Add additional CSS to prevent overlapping and ensure white background
        const style = document.createElement('style');
        style.textContent = `
          body {
            background-color: white !important;
          }
          .resume {
            background-color: white !important;
            background: white !important;
          }
          .resume section {
            margin-bottom: 20px !important;
            page-break-inside: avoid !important;
            background-color: white !important;
          }
          .resume h2 {
            margin-top: 20px !important;
            margin-bottom: 10px !important;
            padding-top: 5px !important;
            page-break-after: avoid !important;
          }
          .resume .job, .resume .project {
            margin-bottom: 15px !important;
            page-break-inside: avoid !important;
          }
        `;
        document.head.appendChild(style);
        
        const opt = {
          margin: [0.25, 0.15],
          filename: `${rewrittenResume.fullName.replace(/\s+/g, '_')}_Resume.pdf`,
          image: { type: 'jpeg', quality: 0.98 },
          html2canvas: { 
            scale: 2, 
            useCORS: true,
            logging: false,
            backgroundColor: '#ffffff',
            letterRendering: true,
            allowTaint: false
          },
          jsPDF: { 
            unit: 'in', 
            format: 'letter', 
            orientation: 'portrait',
            compress: true
          },
          pagebreak: { 
            mode: ['avoid-all', 'css', 'legacy'],
            before: '.page-break-before',
            after: '.page-break-after',
            avoid: ['h2', 'section']
          }
        };
        
        await html2pdf().set(opt).from(elementToConvert).save();
        
        // Clean up
        document.head.removeChild(style);
        if (!resumeContainer && elementToConvert.parentNode) {
          document.body.removeChild(elementToConvert);
        }
      } catch (error) {
        console.error('PDF generation error:', error);
        alert('Failed to generate PDF. Please try again.');
      }
    } else {
      alert('PDF not available. Please try again or contact support.');
    }
  };

  return (
    <div className="flex flex-col lg:flex-row gap-12 max-w-7xl mx-auto px-4 md:px-8">
      
      {/* Sidebar - Analysis & Metrics (Hidden on Print) */}
      <div className="lg:w-1/3 space-y-8 no-print pt-8">
        
        {/* Analysis Card */}
        <div className="border-t border-b border-black py-8">
          <h3 className="text-3xl font-serif italic mb-8 text-center">Analysis</h3>
          
          <div className="flex justify-around mb-10">
            <ScoreGauge score={originalScore} label="Original" color="red" />
            <ScoreGauge score={optimizedScore} label="Optimized" color="green" />
          </div>

          <div className="space-y-8">
            <div>
              <h4 className="font-sans text-xs font-bold uppercase tracking-widest mb-4 border-l-2 border-black pl-3">
                Transformations
              </h4>
              <ul className="text-sm font-serif italic text-gray-800 space-y-2 pl-4">
                {improvementsMade.map((imp, idx) => (
                  <li key={idx} className="relative before:content-['—'] before:absolute before:-left-4 before:text-gray-400">
                    {imp}
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h4 className="font-sans text-xs font-bold uppercase tracking-widest mb-4 border-l-2 border-black pl-3">
                Keywords Matched
              </h4>
              <div className="flex flex-wrap gap-x-4 gap-y-2">
                {keywordsFound.map((kw, idx) => (
                  <span key={idx} className="text-sm font-serif text-black border-b border-gray-300 pb-0.5">{kw}</span>
                ))}
              </div>
            </div>

            <div>
              <h4 className="font-sans text-xs font-bold uppercase tracking-widest mb-4 border-l-2 border-black pl-3 text-gray-500">
                Missing Keywords
              </h4>
              <div className="flex flex-wrap gap-x-4 gap-y-2 opacity-60">
                {keywordsMissing.map((kw, idx) => (
                  <span key={idx} className="text-sm font-serif text-gray-600 italic line-through decoration-gray-400">{kw}</span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Action Card */}
        <div className="text-center space-y-4">
          <p className="font-serif italic text-lg">Ready for export?</p>
          <button 
            onClick={handleDownload}
            className="w-full bg-black text-[#EAE8E3] font-serif text-lg py-3 rounded-none border border-black hover:bg-transparent hover:text-black transition-all duration-300"
          >
            Download PDF
          </button>
        </div>
      </div>

      {/* Resume Document Preview - HTML Representation for Screen */}
      <div className="lg:w-2/3 bg-white shadow-2xl min-h-[1100px] print-only relative transform hover:-translate-y-1 transition-transform duration-500" id="resume-preview">
        {/* Paper texture overlay effect */}
        <div className="absolute inset-0 pointer-events-none opacity-[0.03] bg-[url('https://www.transparenttextures.com/patterns/cream-paper.png')]"></div>

        {data.htmlResume ? (
          <div 
            className="resume-container"
            dangerouslySetInnerHTML={{ __html: data.htmlResume }}
            style={{
              width: '100%',
              height: '100%',
              backgroundColor: 'white',
              background: 'white',
            }}
          />
        ) : (
        <div className="p-12 md:p-16 max-w-[850px] mx-auto text-gray-900 font-sans">
          
          {/* Header */}
          <header className="border-b border-gray-900 pb-6 mb-8 text-center">
            <h1 className="text-4xl md:text-5xl font-serif font-bold text-gray-900 uppercase tracking-tight mb-3">{rewrittenResume.fullName}</h1>
            <p className="text-gray-600 text-sm tracking-wide font-medium">{rewrittenResume.contactInfo}</p>
          </header>

          {/* Experience */}
          {rewrittenResume.experience.length > 0 && (
            <section className="mb-8">
              <h2 className="text-sm font-bold uppercase tracking-widest text-gray-900 border-b border-gray-200 mb-4 pb-1">Experience</h2>
              <div className="space-y-6">
                {rewrittenResume.experience.map((exp, i) => (
                  <div key={i}>
                    <div className="flex justify-between items-baseline mb-1">
                      <h3 className="font-bold text-gray-900 text-base">{exp.role}</h3>
                      <span className="text-xs font-mono text-gray-500">{exp.duration}</span>
                    </div>
                    <div className="flex justify-between items-baseline mb-2">
                       <p className="text-sm text-gray-800 italic font-serif">{exp.company}</p>
                       <p className="text-xs text-gray-600 italic">{exp.location}</p>
                    </div>
                    <ul className="list-disc list-outside ml-4 space-y-1.5">
                      {exp.points.map((point, j) => (
                        <li key={j} className="text-sm text-gray-700 leading-normal pl-1">
                          {point}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Technical Skills - Grouped */}
          {rewrittenResume.skills.length > 0 && (
            <section className="mb-8">
              <h2 className="text-sm font-bold uppercase tracking-widest text-gray-900 border-b border-gray-200 mb-4 pb-1">Technical Skills</h2>
              <div className="space-y-2">
                 {rewrittenResume.skills.map((skillGroup, i) => (
                   <div key={i} className="text-sm">
                      <span className="font-bold text-gray-900">{skillGroup.category}: </span>
                      <span className="text-gray-700">{skillGroup.items}</span>
                   </div>
                 ))}
              </div>
            </section>
          )}

           {/* Projects */}
           {rewrittenResume.projects && rewrittenResume.projects.length > 0 && (
            <section className="mb-8">
              <h2 className="text-sm font-bold uppercase tracking-widest text-gray-900 border-b border-gray-200 mb-4 pb-1">Projects</h2>
              <div className="space-y-6">
                {rewrittenResume.projects.map((proj, i) => (
                  <div key={i}>
                    <div className="flex justify-between items-baseline mb-1">
                      <div className="flex items-baseline gap-2">
                         <h3 className="font-bold text-gray-900 text-base">{proj.name}</h3>
                         {proj.technologies && <span className="text-sm font-serif italic text-gray-600">| {proj.technologies}</span>}
                      </div>
                      <span className="text-xs font-mono text-gray-500">{proj.duration}</span>
                    </div>
                    <ul className="list-disc list-outside ml-4 space-y-1.5">
                      {proj.points.map((point, j) => (
                        <li key={j} className="text-sm text-gray-700 leading-normal pl-1">
                          {point}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Education */}
          {rewrittenResume.education.length > 0 && (
            <section className="mb-8">
              <h2 className="text-sm font-bold uppercase tracking-widest text-gray-900 border-b border-gray-200 mb-4 pb-1">Education</h2>
               <div className="space-y-3">
                {rewrittenResume.education.map((edu, i) => (
                  <div key={i} className="flex justify-between items-end border-b border-dashed border-gray-200 pb-2 last:border-0">
                    <div>
                      <h3 className="font-bold text-gray-900 text-sm">{edu.school}</h3>
                      <p className="text-sm text-gray-700 font-serif italic">{edu.degree}</p>
                    </div>
                    <div className="text-right">
                       <p className="text-xs font-mono text-gray-500">{edu.year}</p>
                       <p className="text-xs text-gray-400 italic">{edu.location}</p>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}
          
           {/* Certifications */}
           {rewrittenResume.certifications && rewrittenResume.certifications.length > 0 && (
            <section className="mb-8">
              <h2 className="text-sm font-bold uppercase tracking-widest text-gray-900 border-b border-gray-200 mb-4 pb-1">Certifications</h2>
               <div className="space-y-2">
                {rewrittenResume.certifications.map((cert, i) => (
                   <div key={i} className="text-sm">
                      <span className="font-bold text-gray-900">{cert.name}</span>
                      {cert.issuer && <span className="text-gray-700"> - {cert.issuer}</span>}
                   </div>
                ))}
              </div>
            </section>
          )}
        </div>
        )}
      </div>
    </div>
  );
};

export default ResumePreview;