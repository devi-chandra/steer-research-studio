import React, { useState } from 'react';
import { 
  Download, 
  RotateCw, 
  ChevronLeft, 
  ChevronRight, 
  Layers, 
  Sparkles, 
  FileArchive, 
  Edit3,
  Save,
  Check
} from 'lucide-react';
import { Project, ContentDraft, Artifact, CarouselSlide } from '../../types';
import { api } from '../../services/api';

interface CarouselTabProps {
  project: Project;
  draft: ContentDraft | null;
  onRefresh: () => void;
}

export const CarouselTab: React.FC<CarouselTabProps> = ({
  project,
  draft,
  onRefresh,
}) => {
  const [activeSlideIdx, setActiveSlideIdx] = useState<number>(0);
  const [isRendering, setIsRendering] = useState<boolean>(false);
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [editedSlide, setEditedSlide] = useState<CarouselSlide | null>(null);

  const slides: CarouselSlide[] = draft?.slide_data || [];
  const activeSlide = slides[activeSlideIdx] || slides[0];

  // Find slide artifacts
  const slideArtifacts = project.artifacts.filter(
    (a) => a.artifact_type === 'carousel_slide'
  ).sort((a, b) => (a.metadata_json?.slide_number || 0) - (b.metadata_json?.slide_number || 0));

  const zipArtifact = project.artifacts.find((a) => a.artifact_type === 'carousel_zip');

  const activeArtifact = slideArtifacts[activeSlideIdx];

  const handleRenderCarousel = async () => {
    setIsRendering(true);
    try {
      await api.generateCarousel(project.id);
      setIsRendering(false);
      onRefresh();
    } catch (err: any) {
      setIsRendering(false);
      alert(`Carousel rendering failed: ${err.message}`);
    }
  };

  const startEdit = () => {
    if (activeSlide) {
      setEditedSlide({ ...activeSlide });
      setIsEditing(true);
    }
  };

  const saveSlideEdit = async () => {
    if (!draft || !editedSlide) return;
    const updatedSlides = [...slides];
    updatedSlides[activeSlideIdx] = editedSlide;

    try {
      await api.updateDraft(project.id, { slide_data: updatedSlides });
      setIsEditing(false);
      onRefresh();
    } catch (err: any) {
      alert(`Failed to save slide changes: ${err.message}`);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      {/* Top action bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '13px', fontWeight: 700, color: 'var(--color-rust)', textTransform: 'uppercase' }}>
              INSTAGRAM CAROUSEL
            </span>
            <span className="badge-tag badge-blush">
              1080 × 1350 PORTRAIT
            </span>
            <span className="badge-tag badge-rust">
              {slides.length} SLIDES
            </span>
          </div>
          <h3 style={{ fontSize: '22px', color: 'var(--color-ink)', marginTop: '4px' }}>
            Multi-Slide Narrative Deck
          </h3>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <button
            onClick={handleRenderCarousel}
            disabled={isRendering || slides.length === 0}
            className="btn-primary"
            style={{ fontSize: '13px', padding: '9px 18px' }}
          >
            <RotateCw size={15} className={isRendering ? 'pulse-glow' : ''} />
            <span>{isRendering ? 'Rendering 1080x1350 PNGs...' : 'Render Carousel PNGs'}</span>
          </button>

          {zipArtifact && (
            <a
              href={api.getArtifactFileUrl(zipArtifact.id, true)}
              className="btn-secondary"
              style={{ fontSize: '13px', padding: '8px 16px' }}
              download
            >
              <FileArchive size={16} />
              <span>Download All (ZIP)</span>
            </a>
          )}
        </div>
      </div>

      {/* Main Studio Workspace: Side-by-Side Visual Preview & Content Editor */}
      <div style={{ display: 'grid', gridTemplateColumns: '460px 1fr', gap: '32px' }}>
        {/* Left Column: Phone Frame Preview */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <div style={{
            width: '380px',
            background: 'var(--color-ink)',
            borderRadius: '36px',
            padding: '12px',
            boxShadow: '0 24px 60px rgba(53, 29, 29, 0.22)',
            border: '4px solid var(--color-ink)'
          }}>
            {/* Top Phone speaker bar */}
            <div style={{ width: '80px', height: '4px', background: 'rgba(255,255,255,0.3)', borderRadius: '2px', margin: '4px auto 10px' }} />

            {/* Slide Render Screen (4:5 Aspect Ratio) */}
            <div style={{
              width: '100%',
              aspectRatio: '4 / 5',
              borderRadius: '24px',
              overflow: 'hidden',
              background: 'var(--color-soft-paper)',
              position: 'relative'
            }}>
              {activeArtifact ? (
                <img
                  src={api.getArtifactFileUrl(activeArtifact.id)}
                  alt={`Slide ${activeSlideIdx + 1}`}
                  style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                />
              ) : (
                /* Dynamic HTML Fallback Preview if not yet rendered */
                <div style={{
                  padding: '28px 24px',
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  background: 'var(--color-cream)',
                  border: '1px solid var(--color-blush)'
                }}>
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '14px' }}>
                      <span className="badge-tag badge-blush" style={{ fontSize: '10px' }}>STEER CLINICAL</span>
                      <span style={{ fontSize: '11px', color: 'var(--color-clay)', fontWeight: 700 }}>
                        {activeSlide?.slide_number || 1} / {slides.length}
                      </span>
                    </div>

                    <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-rust)', textTransform: 'uppercase', marginBottom: '4px' }}>
                      {activeSlide?.eyebrow || 'METABOLIC SCIENCE'}
                    </div>

                    <div style={{ fontFamily: 'var(--font-serif)', fontSize: '20px', fontWeight: 700, color: 'var(--color-ink)', lineHeight: 1.25, marginBottom: '14px' }}>
                      {activeSlide?.headline}
                    </div>

                    {activeSlide?.key_stat && (
                      <div style={{
                        background: 'var(--color-soft-paper)',
                        border: '1px solid var(--color-clay)',
                        borderRadius: '12px',
                        padding: '10px 14px',
                        marginBottom: '14px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px'
                      }}>
                        <span style={{ fontFamily: 'var(--font-serif)', fontSize: '24px', fontWeight: 700, color: 'var(--color-rust)' }}>
                          {activeSlide.key_stat}
                        </span>
                        <span style={{ fontSize: '11px', color: 'var(--color-ink)', fontWeight: 600 }}>
                          {activeSlide.stat_label}
                        </span>
                      </div>
                    )}

                    <div style={{ fontSize: '12px', color: 'var(--color-ink)', lineHeight: 1.45 }}>
                      {activeSlide?.body_text}
                    </div>
                  </div>

                  <div style={{ borderTop: '1px solid var(--color-card-border)', paddingTop: '10px', fontSize: '10px', color: 'var(--color-clay)' }}>
                    {activeSlide?.source_citation || 'Steer Health Clinical Protocol'}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Slide Navigation Controls */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginTop: '18px' }}>
            <button
              onClick={() => setActiveSlideIdx(Math.max(0, activeSlideIdx - 1))}
              disabled={activeSlideIdx === 0}
              className="btn-secondary"
              style={{ padding: '6px 12px' }}
            >
              <ChevronLeft size={16} />
            </button>
            <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--color-ink)' }}>
              Slide {activeSlideIdx + 1} of {slides.length}
            </span>
            <button
              onClick={() => setActiveSlideIdx(Math.min(slides.length - 1, activeSlideIdx + 1))}
              disabled={activeSlideIdx >= slides.length - 1}
              className="btn-secondary"
              style={{ padding: '6px 12px' }}
            >
              <ChevronRight size={16} />
            </button>
          </div>

          {/* Slide thumbnails */}
          <div style={{ display: 'flex', gap: '8px', marginTop: '16px', overflowX: 'auto', maxWidth: '380px', paddingBottom: '6px' }}>
            {slides.map((_, idx) => (
              <button
                key={idx}
                onClick={() => setActiveSlideIdx(idx)}
                style={{
                  width: '36px',
                  height: '45px',
                  borderRadius: '6px',
                  border: `2px solid ${activeSlideIdx === idx ? 'var(--color-rust)' : 'var(--color-clay)'}`,
                  background: activeSlideIdx === idx ? 'var(--color-rust-light)' : 'var(--color-soft-paper)',
                  color: activeSlideIdx === idx ? 'var(--color-rust)' : 'var(--color-ink)',
                  fontSize: '12px',
                  fontWeight: 700,
                  cursor: 'pointer'
                }}
              >
                {idx + 1}
              </button>
            ))}
          </div>

          {activeArtifact && (
            <a
              href={api.getArtifactFileUrl(activeArtifact.id, true)}
              className="btn-secondary"
              style={{ marginTop: '16px', fontSize: '12px', padding: '6px 16px' }}
              download
            >
              <Download size={14} />
              <span>Download Slide {activeSlideIdx + 1} PNG</span>
            </a>
          )}
        </div>

        {/* Right Column: Slide Copy Inspector & Editable Form */}
        <div className="steer-card" style={{ padding: '32px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '22px' }}>
            <div>
              <span className="badge-tag badge-rust" style={{ marginBottom: '6px' }}>
                SLIDE {activeSlideIdx + 1} OF {slides.length}
              </span>
              <h4 style={{ fontSize: '20px', color: 'var(--color-ink)' }}>Slide Content & Scientific Evidence</h4>
            </div>

            {!isEditing ? (
              <button onClick={startEdit} className="btn-secondary" style={{ fontSize: '13px', padding: '6px 14px' }}>
                <Edit3 size={14} />
                <span>Edit Slide Copy</span>
              </button>
            ) : (
              <button onClick={saveSlideEdit} className="btn-primary" style={{ fontSize: '13px', padding: '6px 16px' }}>
                <Check size={14} />
                <span>Save Changes</span>
              </button>
            )}
          </div>

          {activeSlide ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
              {/* Eyebrow */}
              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, color: 'var(--color-clay)', textTransform: 'uppercase', marginBottom: '4px' }}>
                  Slide Eyebrow Tag
                </label>
                {isEditing ? (
                  <input
                    type="text"
                    value={editedSlide?.eyebrow || ''}
                    onChange={(e) => setEditedSlide(editedSlide ? { ...editedSlide, eyebrow: e.target.value } : null)}
                    style={{ width: '100%', padding: '8px 12px', borderRadius: '8px', border: '1px solid var(--color-clay)' }}
                  />
                ) : (
                  <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--color-rust)' }}>
                    {activeSlide.eyebrow || 'METABOLIC SCIENCE'}
                  </div>
                )}
              </div>

              {/* Headline */}
              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, color: 'var(--color-clay)', textTransform: 'uppercase', marginBottom: '4px' }}>
                  Headline
                </label>
                {isEditing ? (
                  <input
                    type="text"
                    value={editedSlide?.headline || ''}
                    onChange={(e) => setEditedSlide(editedSlide ? { ...editedSlide, headline: e.target.value } : null)}
                    style={{ width: '100%', padding: '10px 14px', borderRadius: '8px', border: '1px solid var(--color-clay)', fontSize: '15px' }}
                  />
                ) : (
                  <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--color-ink)' }}>
                    {activeSlide.headline}
                  </div>
                )}
              </div>

              {/* Key Stat & Label */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '16px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, color: 'var(--color-clay)', textTransform: 'uppercase', marginBottom: '4px' }}>
                    Key Metric / Stat
                  </label>
                  {isEditing ? (
                    <input
                      type="text"
                      value={editedSlide?.key_stat || ''}
                      onChange={(e) => setEditedSlide(editedSlide ? { ...editedSlide, key_stat: e.target.value } : null)}
                      style={{ width: '100%', padding: '8px 12px', borderRadius: '8px', border: '1px solid var(--color-clay)' }}
                    />
                  ) : (
                    <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--color-rust)' }}>
                      {activeSlide.key_stat || 'N/A'}
                    </div>
                  )}
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, color: 'var(--color-clay)', textTransform: 'uppercase', marginBottom: '4px' }}>
                    Metric Label
                  </label>
                  {isEditing ? (
                    <input
                      type="text"
                      value={editedSlide?.stat_label || ''}
                      onChange={(e) => setEditedSlide(editedSlide ? { ...editedSlide, stat_label: e.target.value } : null)}
                      style={{ width: '100%', padding: '8px 12px', borderRadius: '8px', border: '1px solid var(--color-clay)' }}
                    />
                  ) : (
                    <div style={{ fontSize: '14px', color: 'var(--color-ink)' }}>
                      {activeSlide.stat_label || 'Metric description'}
                    </div>
                  )}
                </div>
              </div>

              {/* Body Text */}
              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, color: 'var(--color-clay)', textTransform: 'uppercase', marginBottom: '4px' }}>
                  Educational Body Text
                </label>
                {isEditing ? (
                  <textarea
                    rows={4}
                    value={editedSlide?.body_text || ''}
                    onChange={(e) => setEditedSlide(editedSlide ? { ...editedSlide, body_text: e.target.value } : null)}
                    style={{ width: '100%', padding: '10px 14px', borderRadius: '8px', border: '1px solid var(--color-clay)', fontSize: '14px' }}
                  />
                ) : (
                  <div style={{ fontSize: '15px', color: 'var(--color-ink)', lineHeight: 1.55 }}>
                    {activeSlide.body_text}
                  </div>
                )}
              </div>

              {/* Practical Tip */}
              {activeSlide.practical_tip && (
                <div style={{ background: 'var(--color-cream)', padding: '14px 18px', borderRadius: 'var(--radius-md)' }}>
                  <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, color: 'var(--color-rust)', textTransform: 'uppercase', marginBottom: '2px' }}>
                    Practical Steer Takeaway
                  </label>
                  <div style={{ fontSize: '13px', color: 'var(--color-ink)', fontWeight: 500 }}>
                    {activeSlide.practical_tip}
                  </div>
                </div>
              )}

              {/* Source Note & Claim IDs */}
              <div style={{
                borderTop: '1px solid var(--color-card-border)',
                paddingTop: '14px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                fontSize: '12px',
                color: 'var(--color-clay)'
              }}>
                <div>
                  Source: <strong>{activeSlide.source_citation || 'Steer Clinical Research'}</strong>
                </div>
                <div>
                  Linked Claim IDs:{' '}
                  {activeSlide.claim_ids && activeSlide.claim_ids.length > 0 ? (
                    activeSlide.claim_ids.map((id) => (
                      <span key={id} style={{ background: 'var(--color-cream)', padding: '2px 6px', borderRadius: '4px', marginLeft: '4px', fontWeight: 700, color: 'var(--color-rust)' }}>
                        {id}
                      </span>
                    ))
                  ) : (
                    <span>CLM-001</span>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div>No slide data available. Please generate content.</div>
          )}
        </div>
      </div>
    </div>
  );
};
