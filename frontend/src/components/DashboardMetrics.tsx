import React from 'react';
import { 
  FileText, 
  CheckCircle2, 
  Clock, 
  Layers, 
  TrendingUp, 
  ArrowRight, 
  Sparkles,
  AlertTriangle,
  Play
} from 'lucide-react';
import { DashboardMetrics as MetricsType, Project } from '../types';

interface DashboardMetricsProps {
  metrics: MetricsType | null;
  onSelectProject: (projectId: string) => void;
  onOpenNewProject: () => void;
  onQuickStartDemo: () => void;
  isQuickStarting?: boolean;
}

export const DashboardMetrics: React.FC<DashboardMetricsProps> = ({
  metrics,
  onSelectProject,
  onOpenNewProject,
  onQuickStartDemo,
  isQuickStarting = false,
}) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
      {/* Hero Welcome & Quick Demo Banner */}
      <div className="steer-card" style={{
        padding: '36px 40px',
        background: 'linear-gradient(135deg, #F8F2EB 0%, #F5EBDF 100%)',
        border: '1px solid var(--color-blush)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{ maxWidth: '780px' }}>
          <div className="badge-tag badge-rust" style={{ marginBottom: '14px' }}>
            STEER METABOLIC INTELLIGENCE • HACKATHON PS2
          </div>
          <h1 style={{
            fontSize: '38px',
            lineHeight: 1.2,
            color: 'var(--color-ink)',
            marginBottom: '12px'
          }}>
            Turn credible research into content people understand.
          </h1>
          <p style={{
            fontSize: '17px',
            color: 'var(--color-ink-muted)',
            lineHeight: 1.6,
            marginBottom: '26px'
          }}>
            An end-to-end AI workflow that digests complex metabolic science papers, extracts source-traceable claims with exact page citations, enforces a human medical-review gate, and generates finished Instagram carousels, static posts, and vertical video reels.
          </p>

          <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
            <button
              onClick={onQuickStartDemo}
              disabled={isQuickStarting}
              className="btn-primary"
              style={{ padding: '13px 26px', fontSize: '15px' }}
            >
              <Play size={18} fill="currentColor" />
              <span>{isQuickStarting ? 'Processing Sample Paper...' : 'Run One-Click Sample Paper Demo'}</span>
            </button>
            <button
              onClick={onOpenNewProject}
              className="btn-secondary"
              style={{ padding: '12px 24px', fontSize: '15px' }}
            >
              <FileText size={18} />
              <span>Upload Custom Research PDF</span>
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))',
        gap: '20px'
      }}>
        {/* Metric 1: Papers */}
        <div className="steer-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--color-ink-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Papers Processed
            </span>
            <div style={{ background: 'var(--color-cream)', padding: '8px', borderRadius: '10px' }}>
              <FileText size={18} color="var(--color-rust)" />
            </div>
          </div>
          <div style={{ fontFamily: 'var(--font-serif)', fontSize: '36px', fontWeight: 700, color: 'var(--color-ink)' }}>
            {metrics?.total_projects || 0}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--color-ink-muted)', marginTop: '4px' }}>
            Academic clinical papers ingested
          </div>
        </div>

        {/* Metric 2: Claims Extracted */}
        <div className="steer-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--color-ink-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Claims Extracted
            </span>
            <div style={{ background: 'var(--color-cream)', padding: '8px', borderRadius: '10px' }}>
              <Layers size={18} color="var(--color-maroon)" />
            </div>
          </div>
          <div style={{ fontFamily: 'var(--font-serif)', fontSize: '36px', fontWeight: 700, color: 'var(--color-maroon)' }}>
            {metrics?.total_claims || 0}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--color-ink-muted)', marginTop: '4px' }}>
            Source-traceable findings
          </div>
        </div>

        {/* Metric 3: Awaiting Review */}
        <div className="steer-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--color-ink-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Awaiting Review
            </span>
            <div style={{ background: '#FFF8E1', padding: '8px', borderRadius: '10px' }}>
              <AlertTriangle size={18} color="#E65100" />
            </div>
          </div>
          <div style={{ fontFamily: 'var(--font-serif)', fontSize: '36px', fontWeight: 700, color: '#E65100' }}>
            {metrics?.pending_claims || 0}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--color-ink-muted)', marginTop: '4px' }}>
            Pending doctor sign-off
          </div>
        </div>

        {/* Metric 4: Approved */}
        <div className="steer-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--color-ink-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Doctor Approved
            </span>
            <div style={{ background: '#E8F5E9', padding: '8px', borderRadius: '10px' }}>
              <CheckCircle2 size={18} color="#1B5E20" />
            </div>
          </div>
          <div style={{ fontFamily: 'var(--font-serif)', fontSize: '36px', fontWeight: 700, color: '#1B5E20' }}>
            {metrics?.approved_claims || 0}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--color-ink-muted)', marginTop: '4px' }}>
            Verified clinical claims
          </div>
        </div>

        {/* Metric 5: Human Hours Saved */}
        <div className="steer-card" style={{ padding: '24px', background: 'var(--color-rust-light)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--color-rust)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Hours Saved
            </span>
            <div style={{ background: 'var(--color-soft-paper)', padding: '8px', borderRadius: '10px' }}>
              <Clock size={18} color="var(--color-rust)" />
            </div>
          </div>
          <div style={{ fontFamily: 'var(--font-serif)', fontSize: '36px', fontWeight: 700, color: 'var(--color-rust)' }}>
            {metrics?.total_hours_saved || 0}h
          </div>
          <div style={{ fontSize: '12px', color: 'var(--color-ink)', marginTop: '4px' }}>
            Measured vs manual synthesis
          </div>
        </div>
      </div>

      {/* Recent Research Projects */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '18px' }}>
          <div>
            <h2 style={{ fontSize: '24px', color: 'var(--color-ink)' }}>Recent Research Projects</h2>
            <p style={{ fontSize: '14px', color: 'var(--color-ink-muted)' }}>
              Scientific papers currently in the Steer pipeline
            </p>
          </div>
          <button onClick={onOpenNewProject} className="btn-secondary" style={{ fontSize: '13px' }}>
            <span>Add New Paper</span>
          </button>
        </div>

        {!metrics?.recent_projects || metrics.recent_projects.length === 0 ? (
          <div className="steer-card" style={{ padding: '48px', textAlign: 'center' }}>
            <div style={{ width: '56px', height: '56px', borderRadius: '50%', background: 'var(--color-cream)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
              <FileText size={24} color="var(--color-clay)" />
            </div>
            <h3 style={{ fontSize: '18px', color: 'var(--color-ink)', marginBottom: '8px' }}>No research projects yet</h3>
            <p style={{ fontSize: '14px', color: 'var(--color-ink-muted)', maxWidth: '440px', margin: '0 auto 20px' }}>
              Get started by uploading a paper or click below to run the verified sample metabolic trial.
            </p>
            <button onClick={onQuickStartDemo} className="btn-primary" disabled={isQuickStarting}>
              <Sparkles size={16} />
              <span>Load Verified Sample Paper</span>
            </button>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))', gap: '20px' }}>
            {metrics.recent_projects.map((proj: Project) => (
              <div 
                key={proj.id}
                className="steer-card"
                onClick={() => onSelectProject(proj.id)}
                style={{
                  padding: '24px',
                  cursor: 'pointer',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between'
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                    <span className={`badge-tag ${
                      proj.status === 'approved' ? 'badge-approved' :
                      proj.status === 'content_ready' ? 'badge-rust' :
                      proj.status === 'error' ? 'badge-rejected' : 'badge-pending'
                    }`}>
                      {proj.status.replace('_', ' ')}
                    </span>
                    <span style={{ fontSize: '12px', color: 'var(--color-clay)' }}>
                      Stage {proj.current_stage}/7
                    </span>
                  </div>

                  <h3 style={{
                    fontSize: '18px',
                    color: 'var(--color-ink)',
                    marginBottom: '8px',
                    lineHeight: 1.3
                  }}>
                    {proj.title}
                  </h3>

                  {proj.campaign_topic && (
                    <div style={{ fontSize: '13px', color: 'var(--color-rust)', fontWeight: 600, marginBottom: '10px' }}>
                      Topic: {proj.campaign_topic}
                    </div>
                  )}

                  <p style={{
                    fontSize: '13px',
                    color: 'var(--color-ink-muted)',
                    lineHeight: 1.5,
                    marginBottom: '16px'
                  }}>
                    {proj.stage_message}
                  </p>
                </div>

                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  paddingTop: '16px',
                  borderTop: '1px solid var(--color-card-border)',
                  fontSize: '12px',
                  color: 'var(--color-ink-muted)'
                }}>
                  <span>{new Date(proj.created_at).toLocaleDateString()}</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--color-rust)', fontWeight: 600 }}>
                    <span>Open Studio</span>
                    <ArrowRight size={14} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
