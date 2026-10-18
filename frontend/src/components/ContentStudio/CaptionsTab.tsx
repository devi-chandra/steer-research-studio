import React, { useState } from 'react';
import { Copy, Check, MessageSquare, Sparkles, Hash, ShieldAlert } from 'lucide-react';
import { ContentDraft } from '../../types';

interface CaptionsTabProps {
  draft: ContentDraft | null;
}

export const CaptionsTab: React.FC<CaptionsTabProps> = ({ draft }) => {
  const [copied, setCopied] = useState<boolean>(false);

  const caption = draft?.caption || 'Metabolic health educational post from Steer.';
  const hashtags = draft?.hashtags || ['#MetabolicHealth', '#SteerHealth', '#DoctorLed'];
  const reasoning = draft?.reasoning || {};

  const handleCopy = () => {
    const fullText = `${caption}\n\n${hashtags.join(' ')}`;
    navigator.clipboard.writeText(fullText);
    setCopied(true);
    setTimeout(() => setCopied(false), 3000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '13px', fontWeight: 700, color: 'var(--color-rust)', textTransform: 'uppercase' }}>
              SOCIAL MEDIA COPY
            </span>
            <span className="badge-tag badge-blush">INSTAGRAM CAPTION</span>
          </div>
          <h3 style={{ fontSize: '22px', color: 'var(--color-ink)', marginTop: '4px' }}>
            Editorial Caption, Hashtags & Medical Reasoning
          </h3>
        </div>

        <button onClick={handleCopy} className="btn-primary" style={{ fontSize: '13px', padding: '9px 18px' }}>
          {copied ? <Check size={16} /> : <Copy size={16} />}
          <span>{copied ? 'Copied to Clipboard!' : 'Copy Caption & Hashtags'}</span>
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '3fr 2fr', gap: '28px' }}>
        {/* Left Column: Full Caption Box */}
        <div className="steer-card" style={{ padding: '32px' }}>
          <h4 style={{ fontSize: '16px', color: 'var(--color-ink)', marginBottom: '16px' }}>
            Instagram Caption Text
          </h4>

          <div style={{
            background: 'var(--color-cream)',
            border: '1px solid var(--color-card-border)',
            borderRadius: 'var(--radius-md)',
            padding: '24px',
            fontSize: '15px',
            color: 'var(--color-ink)',
            lineHeight: 1.7,
            whiteSpace: 'pre-wrap',
            marginBottom: '24px'
          }}>
            {caption}
          </div>

          <h4 style={{ fontSize: '14px', fontWeight: 700, color: 'var(--color-clay)', textTransform: 'uppercase', marginBottom: '12px' }}>
            Curated Hashtags
          </h4>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {hashtags.map((tag) => (
              <span
                key={tag}
                style={{
                  background: 'var(--color-rust-light)',
                  color: 'var(--color-rust)',
                  fontWeight: 600,
                  fontSize: '13px',
                  padding: '6px 12px',
                  borderRadius: '20px'
                }}
              >
                {tag}
              </span>
            ))}
          </div>
        </div>

        {/* Right Column: Reasoning & Rationale Cards */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div className="steer-card" style={{ padding: '28px' }}>
            <h4 style={{ fontSize: '16px', color: 'var(--color-ink)', marginBottom: '16px' }}>
              Medical & Editorial Rationale
            </h4>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
              <div>
                <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--color-rust)', textTransform: 'uppercase', marginBottom: '4px' }}>
                  Why This Hook Attracts Attention
                </div>
                <div style={{ fontSize: '13px', color: 'var(--color-ink)', lineHeight: 1.5 }}>
                  {reasoning.hook_rationale || 'Leverages universal post-meal sluggishness and cultural familiarity with Shatapadi.'}
                </div>
              </div>

              <div>
                <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--color-rust)', textTransform: 'uppercase', marginBottom: '4px' }}>
                  Relevance to Indian Lifestyles
                </div>
                <div style={{ fontSize: '13px', color: 'var(--color-ink)', lineHeight: 1.5 }}>
                  {reasoning.audience_relevance || 'South Asian diets are carb-dense; immediate 10-minute movement fits busy desk jobs with zero gym barrier.'}
                </div>
              </div>

              <div>
                <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--color-rust)', textTransform: 'uppercase', marginBottom: '4px' }}>
                  Underlying Metabolic Principle
                </div>
                <div style={{ fontSize: '13px', color: 'var(--color-ink)', lineHeight: 1.5 }}>
                  {reasoning.metabolic_principle || 'Skeletal muscle GLUT4 glucose uptake without placing secretory burden on pancreatic beta cells.'}
                </div>
              </div>
            </div>
          </div>

          <div style={{
            background: 'var(--color-cream)',
            border: '1px solid var(--color-clay)',
            borderRadius: 'var(--radius-lg)',
            padding: '20px 24px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--color-maroon)', fontWeight: 700, fontSize: '12px', textTransform: 'uppercase', marginBottom: '6px' }}>
              <ShieldAlert size={16} />
              <span>Steer Medical Compliance Policy</span>
            </div>
            <p style={{ fontSize: '12px', color: 'var(--color-ink-muted)', lineHeight: 1.5 }}>
              All social media drafts generated by Steer Studio must refrain from promising miracle timelines, promoting specific prescription medications, or using fear or body-shaming. Factual claims remain subject to human medical review.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
