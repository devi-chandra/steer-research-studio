import React from 'react';
import { ShieldCheck, Cpu, UserCheck, BookOpen, Layers } from 'lucide-react';
import { Project, SystemStatus } from '../types';

interface HeaderProps {
  currentProject: Project | null;
  projects: Project[];
  onSelectProject: (proj: Project) => void;
  systemStatus: SystemStatus | null;
}

export const Header: React.FC<HeaderProps> = ({
  currentProject,
  projects,
  onSelectProject,
  systemStatus
}) => {
  return (
    <header className="h-16 border-b border-[#E6CBBD] bg-[#F8F2EB] px-6 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-[#661414] flex items-center justify-center text-[#F5EBDF] font-serif font-bold text-lg shadow-sm">
            S
          </div>
          <div>
            <span className="font-serif font-bold text-[#661414] text-lg tracking-tight">STEER</span>
            <span className="ml-2 text-xs font-semibold uppercase tracking-wider text-[#C04E2A] bg-[#E6CBBD]/40 px-2 py-0.5 rounded">
              Scheme 2 Studio
            </span>
          </div>
        </div>

        {/* Project Selector */}
        {projects.length > 0 && (
          <div className="flex items-center gap-2 ml-4 pl-4 border-l border-[#E6CBBD]">
            <BookOpen className="w-4 h-4 text-[#B58777]" />
            <select
              value={currentProject?.id || ''}
              onChange={(e) => {
                const found = projects.find(p => p.id === e.target.value);
                if (found) onSelectProject(found);
              }}
              className="bg-[#F5EBDF] border border-[#B58777]/50 rounded-md text-xs font-medium text-[#351D1D] px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-[#C04E2A] max-w-[280px] truncate"
            >
              {projects.map(p => (
                <option key={p.id} value={p.id}>
                  {p.title.length > 38 ? p.title.slice(0, 38) + '...' : p.title}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      <div className="flex items-center gap-3">
        {/* AI Provider Status Pill */}
        <div className="hidden md:flex items-center gap-1.5 bg-[#F5EBDF] border border-[#B58777]/40 px-3 py-1 rounded-full text-xs text-[#351D1D]">
          <Cpu className="w-3.5 h-3.5 text-[#C04E2A]" />
          <span className="font-medium">
            {systemStatus?.ai_provider?.status_label || 'Deterministic Scientific Engine'}
          </span>
        </div>

        {/* Simulated Reviewer Demo Profile */}
        <div className="flex items-center gap-2 bg-[#661414]/10 border border-[#661414]/20 px-3 py-1 rounded-full text-xs text-[#661414]">
          <UserCheck className="w-3.5 h-3.5 text-[#661414]" />
          <span className="font-semibold">Simulated Reviewer</span>
          <span className="bg-[#661414] text-[#F5EBDF] text-[10px] px-1.5 py-0.2 rounded font-mono">
            DEMO SIMULATION
          </span>
        </div>
      </div>
    </header>
  );
};
