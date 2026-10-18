import React from 'react';
import { 
  Check, 
  RotateCw, 
  AlertCircle, 
  FileSearch, 
  Layers, 
  ShieldCheck, 
  MessageSquare, 
  Sparkles, 
  Stethoscope, 
  Download 
} from 'lucide-react';
import { Project } from '../types';

interface ProcessingProgressProps {
  project: Project;
  onRetry: () => void;
  isProcessing?: boolean;
}

const STAGES = [
  { id: 1, name: 'Ingest', desc: 'PDF / URL text extraction', icon: FileSearch },
  { id: 2, name: 'Extract', desc: 'Structured scientific claims', icon: Layers },
  { id: 3, name: 'Verify Evidence', desc: 'Quote cross-examination', icon: ShieldCheck },
  { id: 4, name: 'Translate', desc: 'Steer clinical voice', icon: MessageSquare },
  { id: 5, name: 'Generate Content', desc: 'Carousel, static & reel', icon: Sparkles },
  { id: 6, name: 'Medical Review', desc: 'Doctor gate validation', icon: Stethoscope },
  { id: 7, name: 'Export', desc: 'Media assets & audit ledger', icon: Download },
];

export const ProcessingProgress: React.FC<ProcessingProgressProps> = ({
  project,
  onRetry,
  isProcessing = false,
}) => {
  const currentStage = project.current_stage || 1;
  const isError = project.status === 'error';

  return (
    <div className="steer-card" style={{ padding: '28px 32px', marginBottom: '28px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '13px', fontWeight: 700, color: 'var(--color-rust)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              PIPELINE PROGRESS
            </span>
            <span className={`badge-tag ${
              project.status === 'approved' ? 'badge-approved' :
              project.status === 'error' ? 'badge-rejected' : 'badge-rust'
            }`}>
              {project.status.toUpperCase()}
            </span>
          </div>
          <h2 style={{ fontSize: '20px', color: 'var(--color-ink)', marginTop: '4px' }}>
            {project.stage_message || 'Processing scientific research paper...'}
          </h2>
        </div>

        {isError && (
          <button onClick={onRetry} disabled={isProcessing} className="btn-primary" style={{ padding: '8px 16px', fontSize: '13px' }}>
            <RotateCw size={14} className={isProcessing ? 'pulse-glow' : ''} />
            <span>Retry Stage</span>
          </button>
        )}
      </div>

      {isError && project.error_message && (
        <div style={{
          background: '#FFEBEE',
          border: '1px solid #EF9A9A',
          color: '#C62828',
          borderRadius: 'var(--radius-md)',
          padding: '12px 16px',
          marginBottom: '20px',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          fontSize: '13px'
        }}>
          <AlertCircle size={18} />
          <div>{project.error_message}</div>
        </div>
      )}

      {/* 7 Stages Stepper */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(7, 1fr)',
        gap: '12px',
        position: 'relative'
      }}>
        {STAGES.map((stg) => {
          const isDone = currentStage > stg.id || project.status === 'approved';
          const isCurrent = currentStage === stg.id && project.status !== 'approved';
          const IconComponent = stg.icon;

          return (
            <div 
              key={stg.id}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                textAlign: 'center',
                opacity: (isDone || isCurrent) ? 1 : 0.45,
                transition: 'all 0.2s ease'
              }}
            >
              <div style={{
                width: '42px',
                height: '42px',
                borderRadius: '50%',
                background: isDone ? '#E8F5E9' : isCurrent ? 'var(--color-rust)' : 'var(--color-cream)',
                border: `2px solid ${isDone ? '#4CAF50' : isCurrent ? 'var(--color-rust)' : 'var(--color-clay)'}`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: isDone ? '#1B5E20' : isCurrent ? '#FFFFFF' : 'var(--color-ink-muted)',
                marginBottom: '8px',
                boxShadow: isCurrent ? '0 0 0 4px var(--color-rust-light)' : 'none'
              }}>
                {isDone ? (
                  <Check size={18} strokeWidth={3} />
                ) : (
                  <IconComponent size={18} />
                )}
              </div>

              <div style={{
                fontSize: '13px',
                fontWeight: isCurrent ? 700 : 600,
                color: isCurrent ? 'var(--color-rust)' : 'var(--color-ink)',
                marginBottom: '2px'
              }}>
                {stg.id}. {stg.name}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--color-ink-muted)', lineHeight: 1.2 }}>
                {stg.desc}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
