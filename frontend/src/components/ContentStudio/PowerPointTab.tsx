import React, { useState } from 'react';
import { 
  Presentation, 
  Download, 
  RotateCw, 
  CheckCircle2, 
  AlertCircle, 
  Layers, 
  FileSpreadsheet, 
  ShieldCheck, 
  Footprints,
  Info
} from 'lucide-react';
import { Project, ContentDraft } from '../../types';
import { api } from '../../services/api';

interface PowerPointTabProps {
  project: Project;
  draft: ContentDraft | null;
  onRefresh: () => void;
}

export const PowerPointTab: React.FC<PowerPointTabProps> = ({
  project,
  draft,
  onRefresh,
}) => {
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [statusMessage, setStatusMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const meta = project.paper_metadata || {};
  const claims = project.claims || [];
  const pptArtifact = project.artifacts?.find((a) => a.artifact_type === 'powerpoint_pptx');

  const handleDownloadPptx = async () => {
    setIsGenerating(true);
    setStatusMessage(null);
    try {
      await api.downloadPowerPointFile(project.id, `Steer_Presentation_${project.id.slice(0, 8)}.pptx`);
      setIsGenerating(false);
      setStatusMessage({
        type: 'success',
        text: 'PowerPoint presentation (.pptx) successfully compiled and downloaded!',
      });
      onRefresh();
      setTimeout(() => setStatusMessage(null), 6000);
    } catch (err: any) {
      setIsGenerating(false);
      setStatusMessage({
        type: 'error',
        text: `PowerPoint generation failed: ${err.message || 'Unknown error'}`,
      });
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Studio Header Card */}
      <div className="steer-card" style={{ padding: '28px 32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span className="badge-tag badge-rust">
                POWERPOINT STUDIO
              </span>
              <span className="badge-tag badge-blush">
                16:9 WIDESCREEN CLINICAL DECK
              </span>
            </div>
            <h3 style={{ fontSize: '24px', color: 'var(--color-ink)', marginTop: '8px' }}>
              Executive Clinical Briefing & Research Deck
            </h3>
            <p style={{ fontSize: '14px', color: 'var(--color-ink-muted)', marginTop: '4px' }}>
              Automated 6-slide PowerPoint presentation formatted with Steer's clinical research-to-media branding.
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
            <button
              onClick={handleDownloadPptx}
              disabled={isGenerating}
              className="btn-primary"
              style={{ fontSize: '14px', padding: '12px 24px' }}
            >
              {isGenerating ? (
                <>
                  <RotateCw size={17} className="pulse-glow" />
                  <span>Compiling PPTX Deck...</span>
                </>
              ) : (
                <>
                  <Download size={17} />
                  <span>Download Presentation (.pptx)</span>
                </>
              )}
            </button>

            {pptArtifact && (
              <a
                href={api.getPowerPointDownloadUrl(project.id)}
                download={`Steer_Presentation_${project.id.slice(0, 8)}.pptx`}
                className="btn-secondary"
                style={{ fontSize: '14px', padding: '12px 20px', textDecoration: 'none' }}
                title="Download previously compiled .pptx file"
              >
                <Download size={16} />
                <span>Download Saved Build ({(pptArtifact.file_size_bytes / 1024).toFixed(0)} KB)</span>
              </a>
            )}
          </div>
        </div>

        {/* Feedback Alert */}
        {statusMessage && (
          <div style={{
            background: statusMessage.type === 'success' ? '#E8F5E9' : '#FFEBEE',
            border: `1px solid ${statusMessage.type === 'success' ? '#A5D6A7' : '#EF9A9A'}`,
            color: statusMessage.type === 'success' ? '#1B5E20' : '#C62828',
            borderRadius: 'var(--radius-md)',
            padding: '12px 18px',
            marginTop: '18px',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            fontSize: '14px'
          }}>
            {statusMessage.type === 'success' ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
            <span>{statusMessage.text}</span>
          </div>
        )}

        {pptArtifact && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '16px', fontSize: '13px', color: 'var(--color-clay)' }}>
            <Info size={15} />
            <span>Latest build: {pptArtifact.filename} ({(pptArtifact.file_size_bytes / 1024).toFixed(1)} KB)</span>
          </div>
        )}
      </div>

      {/* Slide Deck Outline / Preview Grid */}
      <div>
        <h4 style={{ fontSize: '18px', color: 'var(--color-ink)', marginBottom: '14px' }}>
          Slide Deck Architecture (6 Slides)
        </h4>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
          gap: '18px'
        }}>
          {/* Slide 1 */}
          <div className="steer-card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span className="badge-tag badge-blush">SLIDE 1</span>
              <span style={{ fontSize: '12px', color: 'var(--color-clay)' }}>Title & Provenance</span>
            </div>
            <h5 style={{ fontSize: '16px', color: 'var(--color-ink)' }}>Steer Research-to-Media Briefing</h5>
            <p style={{ fontSize: '13px', color: 'var(--color-ink-muted)', lineHeight: 1.5 }}>
              Paper title, primary clinical investigators, journal DOI, year of publication, and Medical Review Gate status.
            </p>
          </div>

          {/* Slide 2 */}
          <div className="steer-card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span className="badge-tag badge-blush">SLIDE 2</span>
              <span style={{ fontSize: '12px', color: 'var(--color-clay)' }}>Executive Briefing</span>
            </div>
            <h5 style={{ fontSize: '16px', color: 'var(--color-ink)' }}>Core Scientific Finding & Editorial Translation</h5>
            <p style={{ fontSize: '13px', color: 'var(--color-ink-muted)', lineHeight: 1.5 }}>
              Main clinical takeaway, target patient cohort, and underlying metabolic physiology (GLUT4 non-insulin pathway).
            </p>
          </div>

          {/* Slide 3 */}
          <div className="steer-card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span className="badge-tag badge-blush">SLIDE 3</span>
              <span style={{ fontSize: '12px', color: 'var(--color-clay)' }}>Evidence Ledger</span>
            </div>
            <h5 style={{ fontSize: '16px', color: 'var(--color-ink)' }}>Source-Grounding & Claim Verification Table</h5>
            <p style={{ fontSize: '13px', color: 'var(--color-ink-muted)', lineHeight: 1.5 }}>
              Tabular breakdown of extracted numerical findings with verbatim quotes, confidence ratings, and review status.
            </p>
          </div>

          {/* Slide 4 */}
          <div className="steer-card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span className="badge-tag badge-blush">SLIDE 4</span>
              <span style={{ fontSize: '12px', color: 'var(--color-clay)' }}>Study Methodology</span>
            </div>
            <h5 style={{ fontSize: '16px', color: 'var(--color-ink)' }}>Clinical Protocol & Demographics</h5>
            <p style={{ fontSize: '13px', color: 'var(--color-ink-muted)', lineHeight: 1.5 }}>
              Cohort criteria (South Asian adults), crossover intervention arms, and continuous metabolic outcome measures.
            </p>
          </div>

          {/* Slide 5 */}
          <div className="steer-card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span className="badge-tag badge-blush">SLIDE 5</span>
              <span style={{ fontSize: '12px', color: 'var(--color-clay)' }}>Safety & Limitations</span>
            </div>
            <h5 style={{ fontSize: '16px', color: 'var(--color-ink)' }}>Evidence Boundaries & Compliance</h5>
            <p style={{ fontSize: '13px', color: 'var(--color-ink-muted)', lineHeight: 1.5 }}>
              Explicit study limitations, non-substitutability warnings, zero miracle claim rules, and Doctor Gate requirements.
            </p>
          </div>

          {/* Slide 6 */}
          <div className="steer-card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span className="badge-tag badge-blush">SLIDE 6</span>
              <span style={{ fontSize: '12px', color: 'var(--color-clay)' }}>Actionable Protocol</span>
            </div>
            <h5 style={{ fontSize: '16px', color: 'var(--color-ink)' }}>Clinical Translation: The Shatapadi Protocol</h5>
            <p style={{ fontSize: '13px', color: 'var(--color-ink-muted)', lineHeight: 1.5 }}>
              10-minute post-meal habit guidance, timing rules, pacing instructions, and multi-format media asset index.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
