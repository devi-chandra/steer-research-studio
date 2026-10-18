import React from 'react';
import {
  PlusCircle,
  FileText,
  ShieldCheck,
  Sparkles,
  Layers,
  ArrowRight,
  CheckCircle2,
  AlertCircle,
  Calendar,
  ExternalLink,
  Presentation
} from 'lucide-react';
import { Project } from '../types';
import { NavItem } from '../components/Sidebar';

interface DashboardPageProps {
  projects: Project[];
  currentProject: Project | null;
  onSelectProject: (proj: Project) => void;
  onNavigate: (tab: NavItem) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  projects,
  currentProject,
  onSelectProject,
  onNavigate,
}) => {
  const totalProjects = projects.length;
  const totalClaims = projects.reduce((acc, p) => acc + (p.claims_count || 0), 0);
  const totalAssets = projects.reduce((acc, p) => acc + (p.assets_count || 0), 0);
  const pendingReviews = projects.reduce((acc, p) => acc + (p.pending_reviews_count || 0), 0);

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Editorial Welcome Banner */}
      <div className="bg-[#661414] text-[#F5EBDF] rounded-2xl p-8 relative overflow-hidden shadow-lg border border-[#B58777]/30">
        <div className="relative z-10 max-w-2xl space-y-3">
          <div className="inline-flex items-center gap-2 bg-[#F5EBDF]/10 border border-[#F5EBDF]/20 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider text-[#E6CBBD]">
            <Sparkles className="w-3.5 h-3.5 text-[#C04E2A]" />
            Doctor-Led Research-to-Content Studio
          </div>
          <h1 className="font-serif text-3xl md:text-4xl font-bold tracking-tight text-[#F8F2EB]">
            From Research Paper to Instagram & PowerPoint, Automated.
          </h1>
          <p className="text-sm md:text-base text-[#E6CBBD] leading-relaxed">
            One verified scientific source. Multiple formats. Different audiences. Consistent evidence. Simulated clinical review workflow.
          </p>
          <div className="pt-2 flex flex-wrap items-center gap-3">
            <button
              onClick={() => onNavigate('new_research')}
              className="flex items-center gap-2 bg-[#C04E2A] hover:bg-[#C04E2A]/90 text-white px-5 py-2.5 rounded-xl text-sm font-bold shadow transition"
            >
              <PlusCircle className="w-4 h-4" />
              Ingest New Research
            </button>
            {currentProject && (
              <button
                onClick={() => onNavigate('evidence_ledger')}
                className="flex items-center gap-2 bg-[#F5EBDF] hover:bg-white text-[#661414] px-5 py-2.5 rounded-xl text-sm font-bold shadow transition"
              >
                Inspect Evidence Ledger
                <ArrowRight className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* Brand decorative background emblem */}
        <div className="absolute right-[-20px] bottom-[-40px] opacity-10 pointer-events-none">
          <span className="font-serif font-bold text-[240px] text-white">S</span>
        </div>
      </div>

      {/* Real Metric Highlights */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-xl p-5 shadow-xs">
          <div className="text-xs font-bold text-[#B58777] uppercase tracking-wider">
            Research Papers
          </div>
          <div className="text-3xl font-serif font-bold text-[#661414] mt-2">
            {totalProjects}
          </div>
          <div className="text-xs text-[#351D1D]/70 mt-1">Verified primary sources</div>
        </div>

        <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-xl p-5 shadow-xs">
          <div className="text-xs font-bold text-[#B58777] uppercase tracking-wider">
            Evidence Claims
          </div>
          <div className="text-3xl font-serif font-bold text-[#351D1D] mt-2">
            {totalClaims}
          </div>
          <div className="text-xs text-[#351D1D]/70 mt-1">Extracted & traceable</div>
        </div>

        <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-xl p-5 shadow-xs">
          <div className="text-xs font-bold text-[#B58777] uppercase tracking-wider">
            Generated Deliverables
          </div>
          <div className="text-3xl font-serif font-bold text-[#C04E2A] mt-2">
            {totalAssets}
          </div>
          <div className="text-xs text-[#351D1D]/70 mt-1">Carousels, posts, reels, decks</div>
        </div>

        <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-xl p-5 shadow-xs">
          <div className="text-xs font-bold text-[#B58777] uppercase tracking-wider">
            Pending Reviews
          </div>
          <div className="text-3xl font-serif font-bold text-[#661414] mt-2">
            {pendingReviews}
          </div>
          <div className="text-xs text-[#351D1D]/70 mt-1">Awaiting simulated review sign-off</div>
        </div>
      </div>

      {/* Research Projects Table */}
      <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-serif text-xl font-bold text-[#661414]">Research Projects In Studio</h2>
            <p className="text-xs text-[#351D1D]/70 mt-0.5">
              Select any project to inspect its evidence ledger, content studio, or presentation deck.
            </p>
          </div>
          <button
            onClick={() => onNavigate('new_research')}
            className="flex items-center gap-1.5 text-xs font-bold text-[#C04E2A] hover:text-[#661414] transition"
          >
            <PlusCircle className="w-4 h-4" />
            Add Another Paper
          </button>
        </div>

        {projects.length === 0 ? (
          <div className="text-center py-12 border-2 border-dashed border-[#E6CBBD] rounded-xl space-y-3">
            <FileText className="w-10 h-10 text-[#B58777] mx-auto opacity-60" />
            <h3 className="font-serif text-lg font-bold text-[#661414]">No research documents uploaded yet</h3>
            <p className="text-xs text-[#351D1D]/70 max-w-md mx-auto">
              Start by uploading a peer-reviewed PDF or public research URL to extract verifiable clinical claims.
            </p>
            <button
              onClick={() => onNavigate('new_research')}
              className="bg-[#661414] text-[#F5EBDF] px-4 py-2 rounded-xl text-xs font-bold hover:bg-[#351D1D] transition"
            >
              Upload First Research Paper
            </button>
          </div>
        ) : (
          <div className="divide-y divide-[#E6CBBD]/60">
            {projects.map((proj) => {
              const isSelected = currentProject?.id === proj.id;
              return (
                <div
                  key={proj.id}
                  onClick={() => onSelectProject(proj)}
                  className={`py-4 px-3 rounded-xl transition flex items-center justify-between cursor-pointer ${
                    isSelected ? 'bg-[#F5EBDF]/70 border border-[#B58777]/30' : 'hover:bg-[#F8F2EB]'
                  }`}
                >
                  <div className="space-y-1.5 max-w-3xl">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold px-2 py-0.5 bg-[#661414]/10 text-[#661414] rounded">
                        {proj.source_type.toUpperCase()}
                      </span>
                      {proj.doi && (
                        <span className="text-xs text-[#B58777] font-mono">
                          DOI: {proj.doi}
                        </span>
                      )}
                      {isSelected && (
                        <span className="text-[10px] font-bold bg-[#C04E2A] text-white px-2 py-0.5 rounded-full">
                          ACTIVE WORKSPACE
                        </span>
                      )}
                    </div>
                    <h3 className="font-serif font-bold text-base text-[#351D1D] hover:text-[#661414] transition">
                      {proj.title}
                    </h3>
                    <div className="flex items-center gap-4 text-xs text-[#351D1D]/70">
                      <span>Claims: <strong>{proj.claims_count || 0}</strong></span>
                      <span>Assets: <strong>{proj.assets_count || 0}</strong></span>
                      <span>Pending Review: <strong className="text-[#C04E2A]">{proj.pending_reviews_count || 0}</strong></span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectProject(proj);
                        onNavigate('evidence_ledger');
                      }}
                      className="px-3 py-1.5 text-xs font-bold rounded-lg bg-[#F5EBDF] border border-[#B58777] text-[#661414] hover:bg-[#661414] hover:text-[#F5EBDF] transition"
                    >
                      Ledger
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectProject(proj);
                        onNavigate('content_studio');
                      }}
                      className="px-3 py-1.5 text-xs font-bold rounded-lg bg-[#C04E2A] text-white hover:bg-[#661414] transition"
                    >
                      Studio
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* 5 Distinctive Pillars Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="bg-[#F8F2EB] border border-[#E6CBBD] rounded-xl p-5 space-y-2">
          <div className="flex items-center gap-2 text-[#661414] font-serif font-bold text-base">
            <Sparkles className="w-4 h-4 text-[#C04E2A]" />
            Same Evidence, Two Stories
          </div>
          <p className="text-xs text-[#351D1D]/80 leading-relaxed font-sans">
            Produces tailored briefings for Doctors (Mode A: clinical, quantitative, rigorous) and Everyday social viewers (Mode B: conversational, animated) grounded in identical Claim IDs.
          </p>
        </div>

        <div className="bg-[#F8F2EB] border border-[#E6CBBD] rounded-xl p-5 space-y-2">
          <div className="flex items-center gap-2 text-[#661414] font-serif font-bold text-base">
            <Layers className="w-4 h-4 text-[#C04E2A]" />
            LocalVoice Multilingual Reels
          </div>
          <p className="text-xs text-[#351D1D]/80 leading-relaxed font-sans">
            Neural voice synthesis in 6 regional options. Note: Text translation is unavailable without a configured provider; scripts remain in verified English to prevent clinical inaccuracies.
          </p>
        </div>

        <div className="bg-[#F8F2EB] border border-[#E6CBBD] rounded-xl p-5 space-y-2">
          <div className="flex items-center gap-2 text-[#661414] font-serif font-bold text-base">
            <ShieldCheck className="w-4 h-4 text-[#C04E2A]" />
            Clinical Review & Safety (Simulated Demo)
          </div>
          <p className="text-xs text-[#351D1D]/80 leading-relaxed font-sans">
            Demonstrates human clinical review and safety gating. In this demo, reviewer decisions are simulated to show how feedback generates active rules preventing future overclaims.
          </p>
        </div>
      </div>
    </div>
  );
};
