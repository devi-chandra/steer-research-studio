import React, { useState, useEffect } from 'react';
import {
  Download,
  ShieldCheck,
  FileText,
  Layers,
  Image as ImageIcon,
  Video,
  Presentation,
  CheckCircle2,
  AlertTriangle,
  Archive,
  ExternalLink,
  BookOpen,
  Loader2
} from 'lucide-react';
import { api } from '../services/api';
import { Project } from '../types';
import { NavItem } from '../components/Sidebar';

interface ExportCenterPageProps {
  currentProject: Project | null;
  onNavigate: (tab: NavItem) => void;
}

export const ExportCenterPage: React.FC<ExportCenterPageProps> = ({ currentProject, onNavigate }) => {
  const [exportData, setExportData] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const fetchExport = async () => {
    if (!currentProject) return;
    try {
      const res = await api.getExport(currentProject.id);
      setExportData(res.export);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchExport();
  }, [currentProject?.id]);

  const handleGenerateExport = async () => {
    if (!currentProject) return;
    setIsLoading(true);
    setStatusMessage(null);
    try {
      const res = await api.exportProject(currentProject.id);
      setExportData(res.export);
      setStatusMessage('Export bundle assembled. Medical review status is separate—check it before sharing.');
    } catch (err: any) {
      setStatusMessage('Export packaging failed: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  if (!currentProject) {
    return (
      <div className="p-12 text-center max-w-xl mx-auto space-y-4">
        <h2 className="font-serif text-2xl font-bold text-[#661414]">No Project Selected</h2>
        <p className="text-sm text-[#351D1D]/70">
          Select a project to download publication-ready deliverables and audit manifests.
        </p>
        <button
          onClick={() => onNavigate('new_research')}
          className="bg-[#661414] text-[#F5EBDF] px-5 py-2.5 rounded-xl text-sm font-bold shadow hover:bg-[#351D1D]"
        >
          Ingest Research Paper
        </button>
      </div>
    );
  }

  return (
    <div className="workspace-page max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-bold text-[#C04E2A] uppercase tracking-wider mb-1">
            <Archive className="w-3.5 h-3.5" />
            Last step · downloads
          </div>
          <h1 className="font-serif text-3xl font-bold text-[#661414]">
            Download your work
          </h1>
          <p className="text-xs text-[#351D1D]/75">
            Download individual files or bundle the outputs generated for <span className="font-semibold">{currentProject.title}</span>. Creating a bundle does not mean the content has medical approval.
          </p>
        </div>

        <button
          onClick={handleGenerateExport}
          disabled={isLoading}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#661414] text-[#F5EBDF] text-xs font-bold hover:bg-[#351D1D] shadow transition"
        >
          {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Archive className="w-4 h-4" />}
          {isLoading ? 'Preparing bundle…' : 'Prepare download bundle'}
        </button>
      </div>

      <div className="export-howto" role="note">
        <strong>Before you download</strong>
        <span>Generate any missing files in Content Studio or Presentation, review claims, then run the consistency check. The ZIP contains generated files; it is not a medical sign-off.</span>
      </div>

      {statusMessage && (
        <div role="status" className={`${statusMessage.startsWith('Export packaging failed') ? 'bg-rose-50 border-rose-300 text-rose-900' : 'bg-emerald-50 border-emerald-300 text-emerald-900'} border p-4 rounded-xl text-xs flex items-center gap-2`}>
          {statusMessage.startsWith('Export packaging failed')
            ? <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
            : <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />}
          <span>{statusMessage}</span>
        </div>
      )}

      {/* Master Package Card */}
      {exportData?.master_zip_url && (
        <div className="bg-[#661414] text-[#F5EBDF] rounded-2xl p-6 shadow-md border border-[#B58777]/40 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="space-y-1.5 max-w-2xl">
            <div className="flex items-center gap-2">
              <span className="font-mono text-[10px] font-bold bg-[#C04E2A] text-white px-2 py-0.5 rounded">
                PACKAGE AVAILABLE
              </span>
              <span className="text-xs text-[#E6CBBD]">
                Size: {Math.round((exportData.file_size_bytes || 0) / 1024)} KB
              </span>
            </div>
            <h2 className="font-serif text-xl font-bold text-white">
              Download bundle
            </h2>
            <p className="text-xs text-[#E6CBBD] leading-relaxed">
              Includes the outputs generated so far, plus captions and an evidence audit manifest. Review each file before sharing.
            </p>
          </div>

          <a
            href={exportData.master_zip_url}
            download={`steer_export_${currentProject.id}.zip`}
            className="flex items-center gap-2 bg-[#F5EBDF] text-[#661414] hover:bg-white px-6 py-3 rounded-xl text-sm font-bold shadow transition shrink-0"
          >
            <Download className="w-4 h-4 text-[#C04E2A]" />
            Download Master ZIP
          </a>
        </div>
      )}

      {/* Individual Deliverables Grid */}
      <div className="space-y-4">
        <h3 className="font-serif text-lg font-bold text-[#661414]">
          Individual files
        </h3>
        <p className="text-xs text-[#351D1D]/70">The labels show file format, not evidence verification or clinical approval.</p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {/* Deliverable 1: Carousel */}
          <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-5 space-y-3 shadow-xs">
            <div className="flex items-center justify-between">
              <Layers className="w-6 h-6 text-[#661414]" />
              <span className="text-[10px] font-bold bg-emerald-50 text-emerald-800 border border-emerald-200 px-2 py-0.5 rounded">
                PNG slides
              </span>
            </div>
            <div>
              <h4 className="font-serif font-bold text-base text-[#351D1D]">Instagram Carousel</h4>
              <p className="text-xs text-[#351D1D]/70 mt-0.5">1080 × 1350 portrait format PNG slides packed in a ZIP.</p>
            </div>
            <a
              href={`/storage/generated/carousels/${currentProject.id}/carousel_${currentProject.id}.zip`}
              download
              className="flex items-center justify-center gap-1.5 w-full py-2 bg-[#F5EBDF] border border-[#B58777] rounded-xl text-xs font-bold text-[#661414] hover:bg-[#661414] hover:text-[#F5EBDF] transition"
            >
              <Download className="w-3.5 h-3.5" />
              Download Carousel ZIP
            </a>
          </div>

          {/* Deliverable 2: Static Post */}
          <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-5 space-y-3 shadow-xs">
            <div className="flex items-center justify-between">
              <ImageIcon className="w-6 h-6 text-[#C04E2A]" />
              <span className="text-[10px] font-bold bg-emerald-50 text-emerald-800 border border-emerald-200 px-2 py-0.5 rounded">
                PNG image
              </span>
            </div>
            <div>
              <h4 className="font-serif font-bold text-base text-[#351D1D]">Static Instagram Post</h4>
              <p className="text-xs text-[#351D1D]/70 mt-0.5">Single-image editorial briefing with key outcome and citations.</p>
            </div>
            <a
              href={`/storage/generated/posts/post_${currentProject.id}.png`}
              download
              className="flex items-center justify-center gap-1.5 w-full py-2 bg-[#F5EBDF] border border-[#B58777] rounded-xl text-xs font-bold text-[#661414] hover:bg-[#661414] hover:text-[#F5EBDF] transition"
            >
              <Download className="w-3.5 h-3.5" />
              Download Post PNG
            </a>
          </div>

          {/* Deliverable 3: PowerPoint PPTX */}
          <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-5 space-y-3 shadow-xs">
            <div className="flex items-center justify-between">
              <Presentation className="w-6 h-6 text-[#661414]" />
              <span className="text-[10px] font-bold bg-emerald-50 text-emerald-800 border border-emerald-200 px-2 py-0.5 rounded">
                PPTX deck
              </span>
            </div>
            <div>
              <h4 className="font-serif font-bold text-base text-[#351D1D]">PowerPoint Presentation</h4>
              <p className="text-xs text-[#351D1D]/70 mt-0.5">Native editable .pptx deck with tables, design, and citations.</p>
            </div>
            <a
              href={`/storage/generated/pptx/presentation_${currentProject.id}.pptx`}
              download
              className="flex items-center justify-center gap-1.5 w-full py-2 bg-[#F5EBDF] border border-[#B58777] rounded-xl text-xs font-bold text-[#661414] hover:bg-[#661414] hover:text-[#F5EBDF] transition"
            >
              <Download className="w-3.5 h-3.5" />
              Download Deck (.pptx)
            </a>
          </div>

          {/* Deliverable 4: Vertical Video Reel */}
          <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-5 space-y-3 shadow-xs">
            <div className="flex items-center justify-between">
              <Video className="w-6 h-6 text-[#C04E2A]" />
              <span className="text-[10px] font-bold bg-emerald-50 text-emerald-800 border border-emerald-200 px-2 py-0.5 rounded">
                1080 × 1920
              </span>
            </div>
            <div>
              <h4 className="font-serif font-bold text-base text-[#351D1D]">Playable Video Reel</h4>
              <p className="text-xs text-[#351D1D]/70 mt-0.5">MP4 video reel rendered with FFmpeg, motion frames, and voice narration.</p>
            </div>
            <a
              href={`/storage/generated/reels/reel_${currentProject.id}_professional_en.mp4`}
              download
              className="flex items-center justify-center gap-1.5 w-full py-2 bg-[#F5EBDF] border border-[#B58777] rounded-xl text-xs font-bold text-[#661414] hover:bg-[#661414] hover:text-[#F5EBDF] transition"
            >
              <Download className="w-3.5 h-3.5" />
              Download MP4 Reel
            </a>
          </div>

          {/* Deliverable 5: Captions */}
          <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-5 space-y-3 shadow-xs">
            <div className="flex items-center justify-between">
              <FileText className="w-6 h-6 text-[#661414]" />
              <span className="text-[10px] font-bold bg-[#E6CBBD] text-[#661414] px-2 py-0.5 rounded">
                TEXT file
              </span>
            </div>
            <div>
              <h4 className="font-serif font-bold text-base text-[#351D1D]">Captions & Hashtags</h4>
              <p className="text-xs text-[#351D1D]/70 mt-0.5">Ready-to-post clinical summaries and educational medical hashtags.</p>
            </div>
            <a
              href={exportData?.captions_url || '#'}
              download
              className="flex items-center justify-center gap-1.5 w-full py-2 bg-[#F5EBDF] border border-[#B58777] rounded-xl text-xs font-bold text-[#661414] hover:bg-[#661414] hover:text-[#F5EBDF] transition"
            >
              <Download className="w-3.5 h-3.5" />
              Download Captions (.txt)
            </a>
          </div>

          {/* Deliverable 6: Audit Manifest */}
          <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-5 space-y-3 shadow-xs">
            <div className="flex items-center justify-between">
              <ShieldCheck className="w-6 h-6 text-emerald-700" />
              <span className="text-[10px] font-bold bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded">
                SOURCE LOG
              </span>
            </div>
            <div>
              <h4 className="font-serif font-bold text-base text-[#351D1D]">Evidence Audit Manifest</h4>
              <p className="text-xs text-[#351D1D]/70 mt-0.5">Traceability log linking each claim to its verbatim page quote and reviewer decision.</p>
            </div>
            <a
              href={exportData?.audit_manifest_url || '#'}
              download
              className="flex items-center justify-center gap-1.5 w-full py-2 bg-[#F5EBDF] border border-[#B58777] rounded-xl text-xs font-bold text-[#661414] hover:bg-[#661414] hover:text-[#F5EBDF] transition"
            >
              <Download className="w-3.5 h-3.5" />
              Download Manifest (.md)
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};
