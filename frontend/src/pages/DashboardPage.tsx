import React from 'react';
import {
  ArrowRight,
  BookOpenCheck,
  FileCheck2,
  Files,
  ImagePlus,
  Layers3,
  Plus,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';
import { Project } from '../types';
import { NavItem } from '../components/Sidebar';

interface DashboardPageProps {
  projects: Project[];
  currentProject: Project | null;
  onSelectProject: (proj: Project) => void;
  onNavigate: (tab: NavItem) => void;
}

const metrics = [
  { label: 'Papers', key: 'papers', icon: Files, color: 'clay' },
  { label: 'Evidence claims', key: 'claims', icon: FileCheck2, color: 'sage' },
  { label: 'Deliverables', key: 'assets', icon: Layers3, color: 'apricot' },
  { label: 'To review', key: 'reviews', icon: ShieldCheck, color: 'plum' },
] as const;

export const DashboardPage: React.FC<DashboardPageProps> = ({
  projects,
  currentProject,
  onSelectProject,
  onNavigate,
}) => {
  const totalClaims = projects.reduce((sum, project) => sum + (project.claims_count || 0), 0);
  const totalAssets = projects.reduce((sum, project) => sum + (project.assets_count || 0), 0);
  const pendingReviews = projects.reduce((sum, project) => sum + (project.pending_reviews_count || 0), 0);
  const values = { papers: projects.length, claims: totalClaims, assets: totalAssets, reviews: pendingReviews };

  return (
    <div className="workspace-page dashboard-page">
      <section className="dashboard-hero">
        <div className="hero-copy">
          <div className="eyebrow"><Sparkles size={14} /> Research, with evidence attached</div>
          <h1>Good science deserves<br className="hero-break" /> clear stories.</h1>
          <p>Turn one research paper into careful, reviewable content for different audiences.</p>
          <div className="hero-actions">
            <button className="button-primary" onClick={() => onNavigate('new_research')}>
              <Plus size={17} /> Start with a paper
            </button>
            {currentProject && <button className="button-quiet hero-secondary" onClick={() => onNavigate('evidence_ledger')}>
              Open evidence <ArrowRight size={16} />
            </button>}
          </div>
        </div>
        <div className="hero-art" aria-hidden="true">
          <div className="hero-art-orbit orbit-one" />
          <div className="hero-art-orbit orbit-two" />
          <div className="hero-art-paper"><BookOpenCheck size={26} /><span>Research</span><i /><i /><i /></div>
          <div className="hero-art-link"><span /><span /><span /></div>
          <div className="hero-art-cards"><div><FileCheck2 size={17} /></div><div><Sparkles size={17} /></div><div><ImagePlus size={17} /></div></div>
          <div className="hero-art-caption">Source → evidence → story</div>
        </div>
      </section>

      <section className="metric-grid" aria-label="Studio overview">
        {metrics.map(({ label, key, icon: Icon, color }) => (
          <div className="metric-card" key={key}>
            <span className={`metric-icon ${color}`}><Icon size={17} /></span>
            <span className="metric-label">{label}</span>
            <strong>{values[key]}</strong>
          </div>
        ))}
      </section>

      <section className="project-panel">
        <div className="section-heading">
          <div>
            <span className="section-kicker">Your workspace</span>
            <h2>Research papers</h2>
          </div>
          <button className="button-quiet add-paper" onClick={() => onNavigate('new_research')}>
            <Plus size={16} /> Add paper
          </button>
        </div>

        {projects.length === 0 ? (
          <div className="empty-projects">
            <div className="empty-icon"><BookOpenCheck size={22} /></div>
            <h3>Your studio is ready</h3>
            <p>Add a paper to begin building an evidence-linked story.</p>
            <button className="button-primary" onClick={() => onNavigate('new_research')}>
              Choose a research paper <ArrowRight size={16} />
            </button>
          </div>
        ) : (
          <div className="project-list">
            {projects.map((project) => {
              const selected = currentProject?.id === project.id;
              return (
                <article className={`project-row ${selected ? 'is-selected' : ''}`} key={project.id}>
                  <button className="project-main" onClick={() => onSelectProject(project)}>
                    <span className="project-file-icon"><BookOpenCheck size={19} /></span>
                    <span className="project-copy">
                      <span className="project-title">{project.title}</span>
                      <span className="project-meta">
                        <span>{project.source_type.toUpperCase()}</span>
                        <span>{project.claims_count || 0} claims</span>
                        <span>{project.assets_count || 0} outputs</span>
                        {(project.pending_reviews_count || 0) > 0 && <span className="pending-meta">{project.pending_reviews_count} to review</span>}
                      </span>
                    </span>
                  </button>
                  <button className="project-open" onClick={() => { onSelectProject(project); onNavigate('content_studio'); }} aria-label={`Open ${project.title}`} title="Open content studio">
                    <ArrowRight size={17} />
                  </button>
                </article>
              );
            })}
          </div>
        )}
      </section>

      <div className="workflow-strip" aria-label="Workflow overview">
        <div className="workflow-heading"><span className="section-kicker">A simple path through the studio</span></div>
        <div className="workflow-steps">
          <div><span className="workflow-icon"><Files size={16} /></span><span><b>01</b> Add research</span></div>
          <span className="workflow-connector" />
          <div><span className="workflow-icon"><FileCheck2 size={16} /></span><span><b>02</b> Ground in evidence</span></div>
          <span className="workflow-connector" />
          <div><span className="workflow-icon"><Sparkles size={16} /></span><span><b>03</b> Create & review</span></div>
        </div>
      </div>
    </div>
  );
};
