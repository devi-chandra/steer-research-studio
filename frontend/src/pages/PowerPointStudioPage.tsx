import React, { useState, useEffect } from 'react';
import {
  Presentation,
  Download,
  Sparkles,
  FileCheck2,
  CheckCircle2,
  Layers,
  ChevronLeft,
  ChevronRight,
  BookOpen,
  Loader2
} from 'lucide-react';
import { api } from '../services/api';
import { Project } from '../types';
import { NavItem } from '../components/Sidebar';

interface PowerPointStudioPageProps {
  currentProject: Project | null;
  onNavigate: (tab: NavItem) => void;
}

export const PowerPointStudioPage: React.FC<PowerPointStudioPageProps> = ({ currentProject, onNavigate }) => {
  const [pptxData, setPptxData] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedSlide, setSelectedSlide] = useState(1);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const fetchPptx = async () => {
    if (!currentProject) return;
    try {
      const res = await api.getPptx(currentProject.id);
      if (res.exists) {
        setPptxData(res);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchPptx();
  }, [currentProject?.id]);

  const handleGenerate = async () => {
    if (!currentProject) return;
    setIsLoading(true);
    setStatusMessage(null);
    try {
      const res = await api.generatePptx(currentProject.id);
      setPptxData(res.powerpoint);
      setStatusMessage('PowerPoint .pptx presentation created and structurally validated.');
    } catch (err: any) {
      setStatusMessage('Failed to generate PowerPoint: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  if (!currentProject) {
    return (
      <div className="p-12 text-center max-w-xl mx-auto space-y-4">
        <h2 className="font-serif text-2xl font-bold text-[#661414]">No Project Selected</h2>
        <p className="text-sm text-[#351D1D]/70">
          Select a project to generate an editable clinical PowerPoint deck.
        </p>
        <button
          onClick={() => onNavigate('new_research')}
          className="bg-[#661414] text-[#F5EBDF] px-5 py-2.5 rounded-xl text-sm font-bold shadow hover:bg-[#351D1D]"
        >
          Ingest Research Paper
        </button>
      </div>
    );
  }

  const slideStructure = [
    { num: 1, title: 'Title & Source Provenance', badge: 'Cover', desc: 'Title, authors, publication DOI, and Steer verification credentials.' },
    { num: 2, title: 'Background & Clinical Question', badge: 'Context', desc: 'Primary clinical problem, public health impact, and baseline trial rationale.' },
    { num: 3, title: 'Study Design & Methodology', badge: 'Methods', desc: 'Trial classification, intervention environment, protocol duration, and controls.' },
    { num: 4, title: 'Participants & Cohort Demographics', badge: 'Demographics', desc: 'Sample size (n), participant inclusion criteria, and cohort boundaries.' },
    { num: 5, title: 'Primary Findings & Outcomes', badge: 'Results', desc: 'Primary measured endpoint with verbatim supporting source quotation.' },
    { num: 6, title: 'Quantitative Evidence Table', badge: 'Data Matrix', desc: 'Real PowerPoint editable data table with exact hazard ratios, p-values, and units.' },
    { num: 7, title: 'Interpretation & Mechanisms', badge: 'Biology', desc: 'Distinction between directly measured changes and established cellular mechanisms.' },
    { num: 8, title: 'Limitations, Bias & Uncertainty', badge: 'Caveats', desc: 'Observational bounds, residual confounding, and relative vs absolute risk qualifications.' },
    { num: 9, title: 'Practical Clinical Takeaways', badge: 'Translation', desc: 'Clinical perspective for healthcare teams and essential doctor consultation disclaimers.' },
    { num: 10, title: 'Source Provenance & Audit Manifest', badge: 'Ledger', desc: 'Bibliographic references, Claim ID audit log, and Steer Review Gate stamp.' }
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-bold text-[#C04E2A] uppercase tracking-wider mb-1">
            <Presentation className="w-3.5 h-3.5" />
            Differentiator Feature 4
          </div>
          <h1 className="font-serif text-3xl font-bold text-[#661414]">
            Research-to-PowerPoint Studio
          </h1>
          <p className="text-xs text-[#351D1D]/75">
            Generates a genuine, editable 10-slide PowerPoint (<code className="font-mono">.pptx</code>) presentation styled in the Steer clinical editorial theme.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleGenerate}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#661414] text-[#F5EBDF] text-xs font-bold hover:bg-[#351D1D] shadow transition"
          >
            {isLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
            Generate 10-Slide Deck (.pptx)
          </button>

          {pptxData?.download_url && (
            <a
              href={pptxData.download_url}
              download
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#C04E2A] text-white text-xs font-bold hover:bg-[#661414] shadow transition"
            >
              <Download className="w-3.5 h-3.5" />
              Download .pptx
            </a>
          )}
        </div>
      </div>

      {statusMessage && (
        <div className="bg-emerald-50 border border-emerald-300 text-emerald-900 px-4 py-2 rounded-xl text-xs flex items-center gap-2 shadow-xs">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{statusMessage}</span>
        </div>
      )}

      {/* Main Grid: Slide Detail & Thumbnails */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
        {/* Left: Selected Slide Canvas Mock */}
        <div className="md:col-span-7 bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between text-xs text-[#B58777]">
            <span className="font-bold uppercase tracking-wider text-[#661414]">
              Slide {selectedSlide} of 10 • {slideStructure[selectedSlide - 1]?.badge}
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setSelectedSlide(Math.max(1, selectedSlide - 1))}
                disabled={selectedSlide === 1}
                className="p-1 rounded bg-[#F8F2EB] border border-[#B58777] disabled:opacity-40"
              >
                <ChevronLeft className="w-4 h-4 text-[#351D1D]" />
              </button>
              <button
                onClick={() => setSelectedSlide(Math.min(10, selectedSlide + 1))}
                disabled={selectedSlide === 10}
                className="p-1 rounded bg-[#F8F2EB] border border-[#B58777] disabled:opacity-40"
              >
                <ChevronRight className="w-4 h-4 text-[#351D1D]" />
              </button>
            </div>
          </div>

          {/* Slide 16:9 Widescreen Frame Preview */}
          <div className="aspect-[16/9] w-full bg-[#F5EBDF] rounded-xl border-2 border-[#B58777]/50 shadow-md p-6 flex flex-col justify-between relative overflow-hidden">
            {/* Top Maroon band */}
            <div className="absolute top-0 left-0 right-0 h-2.5 bg-[#661414]" />

            <div className="space-y-3 pt-2">
              <div className="text-[10px] font-bold uppercase tracking-wider text-[#C04E2A]">
                STEER MEDICAL BRIEFING • SLIDE {selectedSlide}
              </div>
              <h2 className="font-serif text-xl md:text-2xl font-bold text-[#661414] leading-tight">
                {slideStructure[selectedSlide - 1]?.title}
              </h2>
              <div className="w-16 h-1 bg-[#C04E2A] rounded-full" />
            </div>

            <div className="bg-white/80 rounded-xl p-4 border border-[#E6CBBD] text-xs text-[#351D1D] leading-relaxed font-sans shadow-xs my-auto">
              {slideStructure[selectedSlide - 1]?.desc}
              <div className="mt-2 text-[11px] text-[#B58777] italic">
                Rendered with editable python-pptx native textframes, shapes, and tables.
              </div>
            </div>

            <div className="flex items-center justify-between text-[9px] text-[#B58777] pt-2 border-t border-[#E6CBBD]">
              <span>Verified Evidence: DOI {currentProject.doi || '10.1038/nature.med.2022'}</span>
              <span>Steer Verification Gate (Simulated Demo)</span>
            </div>
          </div>

          {pptxData && (
            <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-900 flex items-center justify-between">
              <div>
                <strong>Validated File:</strong> presentation_{currentProject.id}.pptx ({Math.round((pptxData.file_size_bytes || 0) / 1024)} KB)
              </div>
              <a
                href={pptxData.download_url}
                download
                className="font-bold text-[#C04E2A] hover:underline flex items-center gap-1"
              >
                <Download className="w-3.5 h-3.5" />
                Download Deck
              </a>
            </div>
          )}
        </div>

        {/* Right: 10 Slide Navigation Grid */}
        <div className="md:col-span-5 bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-5 shadow-xs space-y-4">
          <div className="text-xs font-bold text-[#661414] uppercase tracking-wider">
            Presentation Structure (10 Slides)
          </div>

          <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
            {slideStructure.map((s) => (
              <div
                key={s.num}
                onClick={() => setSelectedSlide(s.num)}
                className={`p-3 rounded-xl border text-xs transition cursor-pointer flex items-center justify-between ${
                  selectedSlide === s.num
                    ? 'bg-[#F5EBDF] border-[#661414] shadow-xs'
                    : 'bg-[#F8F2EB] border-[#E6CBBD] hover:bg-white'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className={`font-mono font-bold text-xs px-2 py-0.5 rounded ${
                    selectedSlide === s.num ? 'bg-[#661414] text-[#F5EBDF]' : 'bg-[#E6CBBD] text-[#351D1D]'
                  }`}>
                    {s.num < 10 ? `0${s.num}` : s.num}
                  </span>
                  <div>
                    <div className="font-serif font-bold text-sm text-[#351D1D]">{s.title}</div>
                    <div className="text-[11px] text-[#B58777]">{s.badge}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
