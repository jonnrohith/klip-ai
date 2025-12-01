import { jsPDF } from "jspdf";
import { RewrittenResume } from "../types";

export const generateResumePDF = (data: RewrittenResume) => {
  // Initialize document - Letter size, points unit for easier calculation
  const doc = new jsPDF({
    orientation: 'portrait',
    unit: 'pt',
    format: 'letter'
  });

  // --- Constants & Config ---
  const margin = 36; // 0.5 inch = 36 points
  const pageWidth = 612; // Letter width in points
  const contentWidth = pageWidth - (margin * 2);
  const lineHeight = 1.2;
  
  // Colors
  const black = '#000000';
  
  // Fonts - jsPDF default fonts mimic standard Serif/Sans
  const fontMain = 'times'; // Mimics LaTeX default Computer Modern Serif roughly
  
  let y = margin;

  // --- Helpers ---
  
  const checkPageBreak = (heightNeeded: number) => {
    if (y + heightNeeded > 792 - margin) {
      doc.addPage();
      y = margin;
    }
  };

  const drawLine = (yPos: number) => {
    doc.setDrawColor(0, 0, 0);
    doc.setLineWidth(0.5);
    doc.line(margin, yPos, pageWidth - margin, yPos);
  };

  const drawBullet = (text: string, indent: number = 10) => {
    doc.setFont(fontMain, 'normal');
    doc.setFontSize(11);
    
    const bullet = "•";
    const textX = margin + indent + 10;
    const bulletX = margin + indent;
    const maxWidth = contentWidth - indent - 10;
    
    const lines = doc.splitTextToSize(text, maxWidth);
    
    checkPageBreak(lines.length * 13);
    
    doc.text(bullet, bulletX, y);
    doc.text(lines, textX, y);
    
    y += lines.length * 13; // Line height approx 13pt for 11pt font
  };

  // --- Header ---
  
  // Name
  doc.setFont(fontMain, 'bold');
  doc.setFontSize(24);
  doc.setTextColor(black);
  const nameWidth = doc.getTextWidth(data.fullName.toUpperCase());
  doc.text(data.fullName.toUpperCase(), (pageWidth - nameWidth) / 2, y);
  y += 16;

  // Title (Optional from Summary or static)
  // For this template, we often skip a dedicated title line unless it's in data, 
  // but let's assume standard "Name" header.
  
  // Contact Info
  doc.setFont(fontMain, 'normal');
  doc.setFontSize(11);
  const contactText = data.contactInfo; // e.g., "123-456-7890 | email@gmail.com | linkedin..."
  const contactWidth = doc.getTextWidth(contactText);
  doc.text(contactText, (pageWidth - contactWidth) / 2, y + 10);
  y += 30;


  // --- Experience Section ---
  if (data.experience.length > 0) {
    checkPageBreak(40);
    doc.setFont(fontMain, 'bold');
    doc.setFontSize(12);
    doc.text('EXPERIENCE', margin, y);
    y += 4;
    drawLine(y);
    y += 14;

    data.experience.forEach(exp => {
      checkPageBreak(50);
      
      // Role & Date
      doc.setFont(fontMain, 'bold');
      doc.setFontSize(11);
      doc.text(exp.role, margin, y);
      
      doc.setFont(fontMain, 'normal');
      const dateWidth = doc.getTextWidth(exp.duration);
      doc.text(exp.duration, pageWidth - margin - dateWidth, y);
      y += 12;

      // Company & Location
      doc.setFont(fontMain, 'italic');
      doc.setFontSize(11);
      const companyText = `${exp.company}`;
      doc.text(companyText, margin, y);
      
      if (exp.location) {
        doc.setFont(fontMain, 'italic');
        const locWidth = doc.getTextWidth(exp.location);
        doc.text(exp.location, pageWidth - margin - locWidth, y);
      }
      y += 14;

      // Bullets
      exp.points.forEach(point => {
        drawBullet(point);
      });
      y += 6; // Spacing between jobs
    });
    y += 6; // Section spacing
  }

  // --- Technical Skills ---
  if (data.skills.length > 0) {
    checkPageBreak(40);
    doc.setFont(fontMain, 'bold');
    doc.setFontSize(12);
    doc.text('TECHNICAL SKILLS', margin, y);
    y += 4;
    drawLine(y);
    y += 14;

    data.skills.forEach(skillGroup => {
      checkPageBreak(15);
      const category = skillGroup.category ? `${skillGroup.category}: ` : '';
      const items = skillGroup.items;
      
      doc.setFont(fontMain, 'bold');
      doc.setFontSize(11);
      const catWidth = doc.getTextWidth(category);
      doc.text(category, margin + 10, y); // Indented slightly per template
      
      doc.setFont(fontMain, 'normal');
      // Wrap the items if they are too long
      const maxWidth = contentWidth - 10 - catWidth;
      const itemLines = doc.splitTextToSize(items, maxWidth);
      
      doc.text(itemLines, margin + 10 + catWidth, y);
      y += itemLines.length * 13;
    });
    y += 10;
  }

  // --- Projects ---
  if (data.projects && data.projects.length > 0) {
    checkPageBreak(40);
    doc.setFont(fontMain, 'bold');
    doc.setFontSize(12);
    doc.text('PROJECTS', margin, y);
    y += 4;
    drawLine(y);
    y += 14;

    data.projects.forEach(proj => {
      checkPageBreak(40);
      
      // Name | Tech Stack & Date
      // The template does: "Name | Tech Stack" ...... Date
      
      const titleStart = proj.name;
      const techStack = proj.technologies ? ` | ${proj.technologies}` : '';
      
      doc.setFont(fontMain, 'bold');
      doc.setFontSize(11);
      doc.text(titleStart, margin, y);
      const titleWidth = doc.getTextWidth(titleStart);
      
      doc.setFont(fontMain, 'italic');
      doc.text(techStack, margin + titleWidth, y);
      
      doc.setFont(fontMain, 'normal');
      const durWidth = doc.getTextWidth(proj.duration);
      doc.text(proj.duration, pageWidth - margin - durWidth, y);
      y += 14;

      // Bullets
      proj.points.forEach(point => {
        drawBullet(point);
      });
      y += 6;
    });
    y += 6;
  }

  // --- Education ---
  if (data.education.length > 0) {
    checkPageBreak(40);
    doc.setFont(fontMain, 'bold');
    doc.setFontSize(12);
    doc.text('EDUCATION', margin, y);
    y += 4;
    drawLine(y);
    y += 14;

    data.education.forEach(edu => {
      checkPageBreak(30);
      
      // School & Location
      doc.setFont(fontMain, 'bold');
      doc.setFontSize(11);
      doc.text(edu.school, margin, y);
      
      if (edu.location) {
        doc.setFont(fontMain, 'normal');
        const locWidth = doc.getTextWidth(edu.location);
        doc.text(edu.location, pageWidth - margin - locWidth, y);
      }
      y += 12;
      
      // Degree & Year
      doc.setFont(fontMain, 'italic');
      doc.text(edu.degree, margin, y);
      
      doc.setFont(fontMain, 'normal');
      const yearWidth = doc.getTextWidth(edu.year);
      doc.text(edu.year, pageWidth - margin - yearWidth, y);
      y += 18;
    });
    y += 6;
  }

  // --- Certifications ---
  if (data.certifications && data.certifications.length > 0) {
    checkPageBreak(40);
    doc.setFont(fontMain, 'bold');
    doc.setFontSize(12);
    doc.text('CERTIFICATIONS', margin, y);
    y += 4;
    drawLine(y);
    y += 14;

    data.certifications.forEach(cert => {
      checkPageBreak(20);
      doc.setFont(fontMain, 'bold');
      doc.setFontSize(11);
      const line = `${cert.name}${cert.issuer ? ' - ' + cert.issuer : ''}`;
      doc.text(line, margin + 10, y);
      
      // Optional date on right? Template shows italics below or inline
      if (cert.date) {
        doc.setFont(fontMain, 'italic');
        doc.setFontSize(10);
        // doc.text(cert.date, ... ) // skipping for simplicity as template varies
      }
      y += 14;
    });
  }

  // Save
  doc.save(`${data.fullName.replace(/\s+/g, '_')}_Resume.pdf`);
};
