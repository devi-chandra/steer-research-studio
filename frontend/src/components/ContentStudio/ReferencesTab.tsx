import React from 'react';
import { BookOpen, ExternalLink, Quote, ShieldCheck } from 'lucide-react';
import { Project } from '../../types';

interface ReferencesTabProps {
  project: Project;
}

export const ReferencesTab: React.FC<ReferencesTabProps> = ({ project }) => {
  const meta = project.paper_metadata || {};
  const claims = project.claims || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '13px', fontWeight: 700, color: 'var(--color-rust)', textTransform: 'uppercase' }}>
            ACADEMIC INTEGRITY
          </span>
          <span className="badge-tag badge-blush">SOURCE REFERENCES</span>
        </div>
        <h3 style={{ fontSize: '22px', color: 'var(--color-ink)', marginTop: '4px' }}>
          Citation & Claim Verification Ledger
        </h3>
      </div>

      {/* Primary Reference Citation Box */}
      <div className="steer-card" style={{ padding: '28px 32px' }}>
        <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--color-clay)', textTransform: 'uppercase', marginBottom: '8px' }}>
          Primary Scientific Source
        </div>

        <h4 style={{ fontSize: '20px', color: 'var(--color-ink)', lineHeight: 1.35, marginBottom: '8px' }}>
          {meta.title || project.title}
        </h4>

        <div style={{ fontSize: '14px', color: 'var(--color-ink-muted)', marginBottom: '14px' }}>
          {meta.authors && meta.authors.join(', ')} • {meta.year || '2024'} •{' '}
          <em>{meta.journal || 'Clinical Metabolic Research'}</em>
        </div>

        {meta.doi && (
          <div style={{ fontSize: '13px', color: 'var(--color-rust)', fontWeight: 600 }}>
            DOI: https://doi.org/{meta.doi}
          </div>
        )}
      </div>

      {/* Claims Grounding Table */}
      <div className="steer-card" style={{ padding: '24px 28px' }}>
        <h4 style={{ fontSize: '16px', color: 'var(--color-ink)', marginBottom: '16px' }}>
          Claim-by-Claim Citation Grounding
        </h4>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {claims.map((claim) => (
            <div
              key={claim.id}
              style={{
                border: '1px solid var(--color-card-border)',
                borderRadius: 'var(--radius-md)',
                padding: '18px 20px',
                background: 'var(--color-cream)'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ fontFamily: 'monospace', fontWeight: 700, fontSize: '13px', color: 'var(--color-rust)' }}>
                    {claim.claim_id}
                  </span>
                  <span className={`badge-tag ${
                    claim.verification_status === 'approved' ? 'badge-approved' : 'badge-pending'
                  }`}>
                    {claim.verification_status.toUpperCase()}
                  </span>
                </div>
                <div style={{ fontSize: '12px', color: 'var(--color-clay)', fontWeight: 600 }}>
                  Page {claim.page_number || 'N/A'} • {claim.section || 'Results'}
                </div>
              </div>

              <div style={{ fontSize: '15px', fontWeight: 600, color: 'var(--color-ink)', marginBottom: '10px' }}>
                {claim.claim_text}
              </div>

              <div style={{
                background: 'var(--color-soft-paper)',
                padding: '12px 16px',
                borderRadius: '8px',
                fontSize: '13px',
                fontStyle: 'italic',
                color: 'var(--color-ink-muted)',
                lineHeight: 1.5
              }}>
                "{claim.evidence_quote}"
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
