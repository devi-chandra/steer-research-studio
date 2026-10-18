import React, { useState } from 'react';
import { 
  Download, 
  FileArchive, 
  Film, 
  Image as ImageIcon, 
  FileText, 
  FileSpreadsheet, 
  CheckCircle2, 
  AlertTriangle,
  RotateCw,
  Layers,
  Sparkles,
  Presentation,
  ScanEye,
  CircleHelp
} from 'lucide-react';
import { Project, Artifact } from '../types';
import { api } from '../services/api';

interface ExportCenterProps {
  project: Project;
  onRefresh: () => void;
}

export const ExportCenter: React.FC<ExportCenterProps> = ({
  project,
  onRefresh,
}) => {
  const [isBuilding, setIsBuilding] = useState<boolean>(false);
  const [buildSuccess, setBuildSuccess] = useState<string | null>(null);
  const [isDownloadingPptx, setIsDownloadingPptx] = useState<boolean>(false);
  const [isCheckingAssets, setIsCheckingAssets] = useState(false);
  const [assetReport, setAssetReport] = useState<any | null>(null);
  const [fitReport, setFitReport] = useState<any | null>(null);
  const [isCheckingFit, setIsCheckingFit] = useState(false);

  const artifacts = project.artifacts || [];
  const claims = project.claims || [];
  const pendingCount = claims.filter((c) => c.verification_status === 'pending').length;

  const handleBuildAllExports = async () => {
    setIsBuilding(true);
    setBuildSuccess(null);
    try {
      const res = await api.buildAllExports(project.id);
      setIsBuilding(false);
      setBuildSuccess(`Successfully compiled ${res.exported_count} export packages including PowerPoint (.pptx).`);
      onRefresh();
      setTimeout(() => setBuildSuccess(null), 4000);
    } catch (err: any) {
      setIsBuilding(false);
      alert(`Export compile failed: ${err.message}`);
    }
  };

  const handleDownloadPowerPoint = async () => {
    setIsDownloadingPptx(true);
    try {
      await api.downloadPowerPointFile(project.id, `Steer_Presentation_${project.id.slice(0, 8)}.pptx`);
      setIsDownloadingPptx(false);
      onRefresh();
    } catch (err: any) {
      setIsDownloadingPptx(false);
      alert(`PowerPoint download failed: ${err.message}`);
    }
  };

  const handleAssetCheck = async () => {
    setIsCheckingAssets(true);
    try {
      setAssetReport(await api.checkAssetQuality(project.id));
    } catch (err: any) {
      alert(`Asset check failed: ${err.message}`);
    } finally {
      setIsCheckingAssets(false);
    }
  };

  const handleUnsupportedQuestionDemo = async () => {
    setIsCheckingFit(true);
    try {
      setFitReport(await api.checkEditorialFit(project.id, 'Does tapering semaglutide prevent weight regain?'));
    } catch (err: any) {
      alert(`Source fit check failed: ${err.message}`);
    } finally {
      setIsCheckingFit(false);
    }
  };

  const getArtifact = (type: string) => artifacts.find((a) => a.artifact_type === type);

  const carouselZip = getArtifact('carousel_zip');
  const staticPost = getArtifact('static_post');
  const reelVideo = getArtifact('reel_video');
  const captionsTxt = getArtifact('captions_txt');
  const claimsJson = getArtifact('claims_export_json');
  const claimsCsv = getArtifact('claims_export_csv');
  const summaryJson = getArtifact('project_summary');
  const powerpointPptx = getArtifact('powerpoint_pptx');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      {/* Top Banner */}
      <div className="steer-card" style={{ padding: '28px 32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '13px', fontWeight: 700, color: 'var(--color-rust)', textTransform: 'uppercase' }}>
                EXPORT CENTER & AUDIT VAULT
              </span>
              <span className={`badge-tag ${pendingCount > 0 ? 'badge-pending' : 'badge-approved'}`}>
                {pendingCount > 0 ? `${pendingCount} UNAPPROVED CLAIMS PRESENT` : 'DOCTOR SIGNED OFF'}
              </span>
            </div>
            <h3 style={{ fontSize: '24px', color: 'var(--color-ink)', marginTop: '4px' }}>
              Publish-Ready Media Assets & Provenance Reports
            </h3>
            <p style={{ fontSize: '14px', color: 'var(--color-ink-muted)', marginTop: '4px' }}>
              Export high-resolution images, video reels, PowerPoint decks (.pptx), captions, and structured claim records.
            </p>
          </div>

          <button
            onClick={handleBuildAllExports}
            disabled={isBuilding}
            className="btn-primary"
            style={{ fontSize: '14px', padding: '11px 22px' }}
          >
            <RotateCw size={16} className={isBuilding ? 'pulse-glow' : ''} />
            <span>{isBuilding ? 'Compiling Export Packages...' : 'Compile All Export Packages'}</span>
          </button>
        </div>

        <div style={{ marginTop: '18px', paddingTop: '16px', borderTop: '1px solid var(--color-blush)' }}>
          <button type="button" onClick={handleAssetCheck} disabled={isCheckingAssets} className="btn-secondary">
            <ScanEye size={16} />
            <span>{isCheckingAssets ? 'Checking files…' : 'Run rendered asset checks'}</span>
          </button>
          {assetReport && (
            <div style={{ marginTop: '12px', padding: '14px', borderRadius: 'var(--radius-md)', background: '#FFF9F4', border: '1px solid var(--color-blush)' }}>
              <strong style={{ color: 'var(--color-ink)' }}>
                Automated file checks: {assetReport.overall_status === 'passed' ? 'passed' : `${assetReport.flagged_assets} item(s) need review`}
              </strong>
              <p style={{ fontSize: '12px', lineHeight: 1.5, color: 'var(--color-ink-muted)', margin: '6px 0 10px' }}>{assetReport.limits}</p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {assetReport.reports?.map((item: any, index: number) => (
                  <span key={`${item.asset_type}-${index}`} className={`badge-tag ${item.status === 'passed' ? 'badge-approved' : 'badge-pending'}`}>
                    {item.asset_type} · {item.status}{item.size ? ` · ${item.size.join('×')}` : ''}
                  </span>
                ))}
              </div>
              <p style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-rust)', marginTop: '10px' }}>
                Please inspect every slide and subtitle visually before submission.
              </p>
            </div>
          )}
        </div>

        <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid var(--color-blush)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', color: 'var(--color-ink)' }}>
            <CircleHelp size={16} color="var(--color-rust)" />
            <strong style={{ fontSize: '13px' }}>Demo the source boundary</strong>
          </div>
          <button type="button" onClick={handleUnsupportedQuestionDemo} disabled={isCheckingFit} className="btn-secondary">
            {isCheckingFit ? 'Checking source…' : 'Ask a question this paper may not answer'}
          </button>
          {fitReport && (
            <div role="status" style={{ marginTop: '10px', padding: '12px 14px', background: fitReport.answerability === 'supported' ? '#FBFDFB' : '#FFF8E1', border: `1px solid ${fitReport.answerability === 'supported' ? '#C8E6C9' : '#FFE082'}`, borderRadius: 'var(--radius-md)' }}>
              <div style={{ fontSize: '12px', fontWeight: 700, color: fitReport.answerability === 'supported' ? '#1B5E20' : '#9A5B00' }}>
                {fitReport.answerability === 'supported' ? 'Related evidence found' : 'This source does not answer that question'}
              </div>
              <p style={{ fontSize: '12px', color: 'var(--color-ink)', margin: '5px 0' }}>{fitReport.refusal_message || 'Review the matched claims and their limitations before using this source.'}</p>
              <small style={{ color: 'var(--color-clay)' }}>Topic overlap is a routing signal only; clinician review is still needed.</small>
            </div>
          )}
        </div>

        {buildSuccess && (
          <div style={{
            background: '#E8F5E9',
            border: '1px solid #A5D6A7',
            color: '#1B5E20',
            borderRadius: 'var(--radius-md)',
            padding: '12px 18px',
            marginTop: '18px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '14px'
          }}>
            <CheckCircle2 size={18} />
            <span>{buildSuccess}</span>
          </div>
        )}

        {pendingCount > 0 && (
          <div style={{
            background: '#FFF8E1',
            border: '1px solid #FFE082',
            color: '#E65100',
            borderRadius: 'var(--radius-md)',
            padding: '12px 18px',
            marginTop: '18px',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            fontSize: '13px'
          }}>
            <AlertTriangle size={18} style={{ flexShrink: 0 }} />
            <div>
              <strong>Compliance Notice:</strong> This project contains {pendingCount} claims awaiting human medical review. Exported drafts will be labelled as provisional drafts until verified by a physician.
            </div>
          </div>
        )}
      </div>

      {/* Export Cards Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))',
        gap: '20px'
      }}>
        {/* Export 1: PowerPoint Studio Deck (.pptx) */}
        <div className="steer-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
              <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'var(--color-cream)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Presentation size={20} color="var(--color-rust)" />
              </div>
              <span className="badge-tag badge-rust">POWERPOINT (.PPTX)</span>
            </div>
            <h4 style={{ fontSize: '18px', color: 'var(--color-ink)', marginBottom: '6px' }}>
              PowerPoint Presentation (.pptx)
            </h4>
            <p style={{ fontSize: '13px', color: 'var(--color-ink-muted)', lineHeight: 1.5, marginBottom: '16px' }}>
              Widescreen 16:9 clinical slide deck with Executive Briefing, Evidence Ledger table, Methodology, Limitations, and Shatapadi Protocol.
            </p>
          </div>
          <div>
            <button
              onClick={handleDownloadPowerPoint}
              disabled={isDownloadingPptx}
              className="btn-primary"
              style={{ width: '100%', justifyContent: 'center' }}
            >
              {isDownloadingPptx ? (
                <>
                  <RotateCw size={15} className="pulse-glow" />
                  <span>Compiling Deck...</span>
                </>
              ) : (
                <>
                  <Download size={15} />
                  <span>
                    {powerpointPptx 
                      ? `Download Presentation (.pptx, ${(powerpointPptx.file_size_bytes / 1024).toFixed(0)} KB)` 
                      : 'Generate & Download PPTX'}
                  </span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Export 2: Carousel ZIP */}
        <div className="steer-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
              <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'var(--color-cream)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Layers size={20} color="var(--color-rust)" />
              </div>
              <span className="badge-tag badge-blush">CAROUSEL (ZIP)</span>
            </div>
            <h4 style={{ fontSize: '18px', color: 'var(--color-ink)', marginBottom: '6px' }}>
              Instagram Carousel Slides
            </h4>
            <p style={{ fontSize: '13px', color: 'var(--color-ink-muted)', lineHeight: 1.5, marginBottom: '16px' }}>
              ZIP archive containing all rendered 1080x1350 portrait PNG slides with Steer editorial branding.
            </p>
          </div>
          <div>
            {carouselZip ? (
              <a
                href={api.getArtifactFileUrl(carouselZip.id, true)}
                className="btn-primary"
                style={{ width: '100%', justifyContent: 'center' }}
                download
              >
                <Download size={15} />
                <span>Download Slides ZIP ({(carouselZip.file_size_bytes / 1024).toFixed(0)} KB)</span>
              </a>
            ) : (
              <div style={{ fontSize: '12px', color: 'var(--color-clay)', textAlign: 'center' }}>
                Render carousel in Content Studio to generate ZIP
              </div>
            )}
          </div>
        </div>

        {/* Export 3: Static Post */}
        <div className="steer-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
              <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'var(--color-cream)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <ImageIcon size={20} color="var(--color-rust)" />
              </div>
              <span className="badge-tag badge-blush">STATIC IMAGE</span>
            </div>
            <h4 style={{ fontSize: '18px', color: 'var(--color-ink)', marginBottom: '6px' }}>
              Static Post Image (PNG)
            </h4>
            <p style={{ fontSize: '13px', color: 'var(--color-ink-muted)', lineHeight: 1.5, marginBottom: '16px' }}>
              Single high-impact 1080x1350 PNG with Steer typography, clinical finding, and actionable rule.
            </p>
          </div>
          <div>
            {staticPost ? (
              <a
                href={api.getArtifactFileUrl(staticPost.id, true)}
                className="btn-primary"
                style={{ width: '100%', justifyContent: 'center' }}
                download
              >
                <Download size={15} />
                <span>Download PNG ({(staticPost.file_size_bytes / 1024).toFixed(0)} KB)</span>
              </a>
            ) : (
              <div style={{ fontSize: '12px', color: 'var(--color-clay)', textAlign: 'center' }}>
                Render static post in Content Studio to generate PNG
              </div>
            )}
          </div>
        </div>

        {/* Export 4: Reel MP4 */}
        <div className="steer-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
              <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'var(--color-cream)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Film size={20} color="var(--color-rust)" />
              </div>
              <span className="badge-tag badge-approved">9:16 VERTICAL MP4</span>
            </div>
            <h4 style={{ fontSize: '18px', color: 'var(--color-ink)', marginBottom: '6px' }}>
              Finished Instagram Reel (MP4)
            </h4>
            <p style={{ fontSize: '13px', color: 'var(--color-ink-muted)', lineHeight: 1.5, marginBottom: '16px' }}>
              Completed vertical video with H.264 video, AAC audio, neural Indian English voiceover, and motion visuals.
            </p>
          </div>
          <div>
            {reelVideo ? (
              <a
                href={api.getArtifactFileUrl(reelVideo.id, true)}
                className="btn-primary"
                style={{ width: '100%', justifyContent: 'center' }}
                download
              >
                <Download size={15} />
                <span>Download Reel MP4 ({(reelVideo.file_size_bytes / (1024 * 1024)).toFixed(1)} MB)</span>
              </a>
            ) : (
              <div style={{ fontSize: '12px', color: 'var(--color-clay)', textAlign: 'center' }}>
                Render reel in Content Studio to generate MP4
              </div>
            )}
          </div>
        </div>

        {/* Export 5: Captions TXT */}
        <div className="steer-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
              <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'var(--color-cream)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <FileText size={20} color="var(--color-ink)" />
              </div>
              <span className="badge-tag badge-blush">COPYWRITING</span>
            </div>
            <h4 style={{ fontSize: '18px', color: 'var(--color-ink)', marginBottom: '6px' }}>
              Captions & Hashtags (TXT)
            </h4>
            <p style={{ fontSize: '13px', color: 'var(--color-ink-muted)', lineHeight: 1.5, marginBottom: '16px' }}>
              Formatted social media copy, curated hashtags, and medical reasoning behind post structure.
            </p>
          </div>
          <div>
            {captionsTxt ? (
              <a
                href={api.getArtifactFileUrl(captionsTxt.id, true)}
                className="btn-secondary"
                style={{ width: '100%', justifyContent: 'center' }}
                download
              >
                <Download size={15} />
                <span>Download Captions.txt</span>
              </a>
            ) : (
              <button onClick={handleBuildAllExports} className="btn-secondary" style={{ width: '100%', justifyContent: 'center' }}>
                Compile Captions TXT
              </button>
            )}
          </div>
        </div>

        {/* Export 6: Claims Ledger JSON & CSV */}
        <div className="steer-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
              <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'var(--color-cream)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <FileSpreadsheet size={20} color="var(--color-maroon)" />
              </div>
              <span className="badge-tag badge-blush">PROVENANCE DATA</span>
            </div>
            <h4 style={{ fontSize: '18px', color: 'var(--color-ink)', marginBottom: '6px' }}>
              Claims Evidence Ledger
            </h4>
            <p style={{ fontSize: '13px', color: 'var(--color-ink-muted)', lineHeight: 1.5, marginBottom: '16px' }}>
              Complete audit ledger connecting every claim to verbatim quotes, page numbers, and review sign-offs.
            </p>
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            {claimsJson && (
              <a
                href={api.getArtifactFileUrl(claimsJson.id, true)}
                className="btn-secondary"
                style={{ flex: 1, justifyContent: 'center', fontSize: '12px' }}
                download
              >
                <Download size={14} />
                <span>JSON</span>
              </a>
            )}
            {claimsCsv && (
              <a
                href={api.getArtifactFileUrl(claimsCsv.id, true)}
                className="btn-secondary"
                style={{ flex: 1, justifyContent: 'center', fontSize: '12px' }}
                download
              >
                <Download size={14} />
                <span>CSV</span>
              </a>
            )}
          </div>
        </div>

        {/* Export 7: Project Summary & ROI Audit */}
        <div className="steer-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
              <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'var(--color-cream)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <CheckCircle2 size={20} color="#1B5E20" />
              </div>
              <span className="badge-tag badge-approved">EXECUTIVE SUMMARY</span>
            </div>
            <h4 style={{ fontSize: '18px', color: 'var(--color-ink)', marginBottom: '6px' }}>
              Project Summary & Effort Audit
            </h4>
            <p style={{ fontSize: '13px', color: 'var(--color-ink-muted)', lineHeight: 1.5, marginBottom: '16px' }}>
              Comprehensive JSON record of tools used, outputs produced, human effort tracking, and time saved.
            </p>
          </div>
          <div>
            {summaryJson ? (
              <a
                href={api.getArtifactFileUrl(summaryJson.id, true)}
                className="btn-primary"
                style={{ width: '100%', justifyContent: 'center', background: 'var(--color-maroon)' }}
                download
              >
                <Download size={15} />
                <span>Download Audit Report</span>
              </a>
            ) : (
              <button onClick={handleBuildAllExports} className="btn-secondary" style={{ width: '100%', justifyContent: 'center' }}>
                Compile Audit Report
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
