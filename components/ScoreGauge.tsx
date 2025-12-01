import React from 'react';

interface ScoreGaugeProps {
  score: number;
  label: string;
  color: 'blue' | 'green' | 'red'; // Kept for prop compatibility, but we will override with monochrome theme
}

const ScoreGauge: React.FC<ScoreGaugeProps> = ({ score, label }) => {
  const radius = 36;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="relative w-24 h-24 group">
        {/* Background Circle - Thin Gray */}
        <svg className="w-full h-full transform -rotate-90">
          <circle
            className="text-gray-300 opacity-30"
            strokeWidth="1"
            stroke="currentColor"
            fill="transparent"
            r={radius}
            cx="48"
            cy="48"
          />
          {/* Progress Circle - Thin Black */}
          <circle
            className="text-black transition-all duration-1000 ease-out"
            strokeWidth="1.5"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="butt"
            stroke="currentColor"
            fill="transparent"
            r={radius}
            cx="48"
            cy="48"
          />
        </svg>
        
        {/* Inner Text */}
        <div className="absolute top-0 left-0 w-full h-full flex flex-col items-center justify-center text-black">
          <span className="text-3xl font-serif">{score}</span>
        </div>
        
        {/* Hover decorative ring */}
        <div className="absolute inset-0 border border-gray-200 rounded-full scale-110 opacity-0 group-hover:opacity-100 transition-all duration-500"></div>
      </div>
      <p className="mt-3 text-xs uppercase tracking-widest font-sans font-medium">{label}</p>
    </div>
  );
};

export default ScoreGauge;