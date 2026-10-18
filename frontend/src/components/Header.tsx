import React from 'react';
import { Cpu, UserRoundCheck, BookOpen, Moon, Sun } from 'lucide-react';
import { Project, SystemStatus } from '../types';

interface HeaderProps {
  currentProject: Project | null;
  projects: Project[];
  onSelectProject: (proj: Project) => void;
  systemStatus: SystemStatus | null;
  darkMode: boolean;
  onToggleTheme: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  currentProject,
  projects,
  onSelectProject,
  systemStatus,
  darkMode,
  onToggleTheme
}) => {
  return (
    <header className="app-header">
      <div className="header-brand-row">
        <div className="brand-lockup">
          <div className="brand-mark">S</div>
          <div>
            <span className="brand-name">STEER</span>
            <span className="brand-caption">Research studio</span>
          </div>
        </div>

        {/* Project Selector */}
        {projects.length > 0 && (
          <div className="project-picker">
            <BookOpen size={16} />
            <select
              value={currentProject?.id || ''}
              onChange={(e) => {
                const found = projects.find(p => p.id === e.target.value);
                if (found) onSelectProject(found);
              }}
              className="project-picker-select"
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

      <div className="header-status-row">
        <button className="theme-toggle" type="button" onClick={onToggleTheme} aria-label={`Switch to ${darkMode ? 'light' : 'dark'} mode`} title={`Switch to ${darkMode ? 'light' : 'dark'} mode`}>
          {darkMode ? <Sun size={16} /> : <Moon size={16} />}
        </button>
        {/* AI Provider Status Pill */}
        <div className="provider-chip" title={systemStatus?.ai_provider?.status_label || 'Deterministic scientific engine'}>
          <Cpu size={15} />
          <span>{systemStatus?.ai_provider?.active_provider || 'Local'} <span className="provider-detail">engine</span></span>
        </div>

        {/* Simulated Reviewer Demo Profile */}
        <div className="reviewer-chip" title="Reviewer actions are simulated in this demo">
          <UserRoundCheck size={15} />
          <span>Demo reviewer</span>
          <span className="demo-dot" aria-label="Simulation" />
        </div>
      </div>
    </header>
  );
};
