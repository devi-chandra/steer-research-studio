import React, { useState } from 'react';
import { UploadCloud, Globe, FileText, CheckCircle2, AlertTriangle, ArrowRight, Sparkles, Loader2, ShieldCheck } from 'lucide-react';
import { api } from '../services/api';
import { Project } from '../types';
import { NavItem } from '../components/Sidebar';

interface NewResearchPageProps {
  onProjectCreated: (proj: Project) => void;
  onNavigate: (tab: NavItem) => void;
}

export const NewResearchPage: React.FC<NewResearchPageProps> = ({ onProjectCreated, onNavigate }) => {
  const [activeTab, setActiveTab] = useState<'pdf' | 'url'>('pdf');
  const [file, setFile] = useState<File | null>(null);
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successData, setSuccessData] = useState<any | null>(null);

  const handlePdfUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setIsLoading(true);
    setError(null);
    setSuccessData(null);

    try {
      const res = await api.uploadPdf(file);
      if (res.success) {
        // Automatically extract claims as required in step 2 of pipeline
        await api.extractClaims(res.project_id);
        const freshProj = await api.getProject(res.project_id);
        setSuccessData(res);
        onProjectCreated(freshProj);
      } else {
        setError((res as any).error || res.message || 'PDF extraction encountered an issue.');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to upload and extract PDF.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUrlIngestion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    setIsLoading(true);
    setError(null);
    setSuccessData(null);

    try {
      const res = await api.ingestUrl(url.trim());
      if (res.success) {
        // Automatically extract claims
        await api.extractClaims(res.project_id);
        const freshProj = await api.getProject(res.project_id);
        setSuccessData(res);
        onProjectCreated(freshProj);
      } else {
        setError((res as any).error || 'URL extraction failed.');
      }
    } catch (err: any) {
      setError(err.message || 'URL ingestion failed.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoadSamplePaper = async () => {
    setIsLoading(true);
    setError(null);
    setSuccessData(null);

    try {
      const blob = await api.downloadSamplePdf();
      const sampleFile = new File([blob], 'stamatakis_vilpa_nature_med_2022.pdf', { type: 'application/pdf' });
      setFile(sampleFile);

      const uploadRes = await api.uploadPdf(sampleFile);
      if (uploadRes.success) {
        await api.extractClaims(uploadRes.project_id);
        const freshProj = await api.getProject(uploadRes.project_id);
        setSuccessData(uploadRes);
        onProjectCreated(freshProj);
      } else {
        setError((uploadRes as any).error || 'Sample PDF extraction failed.');
      }
    } catch (err: any) {
      setError('Could not load sample paper automatically: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="workspace-page max-w-4xl mx-auto space-y-8">
      {/* Title */}
      <div>
        <div className="inline-flex items-center gap-1.5 text-xs font-bold text-[#C04E2A] uppercase tracking-wider mb-1.5">
          <ShieldCheck className="w-3.5 h-3.5" />
          Step 1 • Document Ingestion & Provenance
        </div>
        <h1 className="font-serif text-3xl font-bold text-[#661414]">
          Ingest Scientific Paper
        </h1>
        <p className="text-sm text-[#351D1D]/80 mt-1">
          Upload an original research PDF or enter a public peer-reviewed article URL. Every factual claim will be linked directly to its page and section.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-[#E6CBBD]">
        <button
          onClick={() => { setActiveTab('pdf'); setError(null); }}
          className={`flex items-center gap-2 pb-3 px-6 text-sm font-bold border-b-2 transition ${
            activeTab === 'pdf'
              ? 'border-[#661414] text-[#661414]'
              : 'border-transparent text-[#B58777] hover:text-[#351D1D]'
          }`}
        >
          <UploadCloud className="w-4 h-4" />
          Upload Research PDF
        </button>
        <button
          onClick={() => { setActiveTab('url'); setError(null); }}
          className={`flex items-center gap-2 pb-3 px-6 text-sm font-bold border-b-2 transition ${
            activeTab === 'url'
              ? 'border-[#661414] text-[#661414]'
              : 'border-transparent text-[#B58777] hover:text-[#351D1D]'
          }`}
        >
          <Globe className="w-4 h-4" />
          Public Research URL
        </button>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="p-4 bg-rose-50 border border-rose-300 rounded-xl flex items-start gap-3 text-rose-900 text-sm">
          <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
          <div>
            <div className="font-bold">Ingestion Warning</div>
            <div className="mt-0.5">{error}</div>
          </div>
        </div>
      )}

      {/* Success Banner */}
      {successData && (
        <div className="p-6 bg-emerald-50 border border-emerald-300 rounded-2xl space-y-4">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="w-6 h-6 text-emerald-600" />
            <div>
              <h3 className="font-serif font-bold text-lg text-emerald-900">
                Document Ingestion & Claim Extraction Completed
              </h3>
              <p className="text-xs text-emerald-800">
                Extracted {successData.extraction?.total_pages ?? 'unknown'} pages.
              </p>
            </div>
          </div>

          <div className="bg-white/80 p-4 rounded-xl border border-emerald-200 text-xs space-y-2 text-[#351D1D]">
            {successData.extraction?.detected_title && <div><strong>Detected Title:</strong> {successData.extraction.detected_title}</div>}
            {successData.extraction?.detected_doi && (
              <div><strong>DOI:</strong> {successData.extraction?.detected_doi}</div>
            )}
            <div><strong>Pages Preserved:</strong> {successData.extraction?.total_pages ?? 'Unknown'} pages ({successData.extraction?.total_characters ?? 'Unknown'} characters)</div>
          </div>

          <div className="flex items-center gap-3 pt-2">
            <button
              onClick={() => onNavigate('evidence_ledger')}
              className="flex items-center gap-2 px-5 py-2.5 bg-[#661414] text-[#F5EBDF] rounded-xl text-sm font-bold hover:bg-[#351D1D] shadow transition"
            >
              Inspect Evidence Ledger
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => onNavigate('content_studio')}
              className="px-5 py-2.5 bg-[#C04E2A] text-white rounded-xl text-sm font-bold hover:bg-[#C04E2A]/90 transition"
            >
              Open Content Studio
            </button>
          </div>
        </div>
      )}

      {/* PDF Upload Tab Form */}
      {activeTab === 'pdf' && !successData && (
        <form onSubmit={handlePdfUpload} className="space-y-6">
          <div className="border-2 border-dashed border-[#B58777] rounded-2xl p-10 bg-[#FFFFFF] text-center hover:bg-[#F5EBDF]/40 transition relative">
            <input
              type="file"
              accept=".pdf"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
            />
            <div className="space-y-3 pointer-events-none">
              <div className="w-14 h-14 bg-[#E6CBBD]/50 text-[#661414] rounded-full flex items-center justify-center mx-auto">
                <FileText className="w-7 h-7 text-[#661414]" />
              </div>
              <div className="text-base font-bold text-[#351D1D]">
                {file ? file.name : 'Drag and drop your scientific paper PDF here'}
              </div>
              <p className="text-xs text-[#B58777]">
                Supported: Peer-reviewed manuscripts, clinical trial publications, preprint PDFs up to 50MB.
              </p>
            </div>
          </div>

          <div className="flex items-center justify-between pt-2">
            {/* Quick Demo Preload Button */}
            <button
              type="button"
              onClick={handleLoadSamplePaper}
              disabled={isLoading}
              className="flex items-center gap-2 text-xs font-bold text-[#C04E2A] hover:text-[#661414] border border-[#C04E2A]/40 px-3.5 py-2 rounded-xl transition"
            >
              <Sparkles className="w-3.5 h-3.5" />
              Load Verified Sample Paper (Nature Medicine 2022 VILPA Trial)
            </button>

            <button
              type="submit"
              disabled={!file || isLoading}
              className="flex items-center gap-2 bg-[#661414] hover:bg-[#351D1D] disabled:opacity-50 text-[#F5EBDF] px-6 py-2.5 rounded-xl text-sm font-bold shadow transition"
            >
              {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
              {isLoading ? 'Extracting Text & Claims...' : 'Process PDF Document'}
            </button>
          </div>
        </form>
      )}

      {/* URL Ingestion Tab Form */}
      {activeTab === 'url' && !successData && (
        <form onSubmit={handleUrlIngestion} className="space-y-6">
          <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-6 space-y-4 shadow-xs">
            <label className="block text-xs font-bold text-[#661414] uppercase tracking-wider">
              Public Research Paper URL
            </label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://www.nature.com/articles/s41591-022-02100-x or PubMed / PMC link"
              className="w-full p-3.5 text-sm border border-[#B58777] rounded-xl bg-[#F8F2EB] focus:bg-white focus:ring-1 focus:ring-[#C04E2A] outline-none"
              required
            />
            <div className="p-3 bg-[#F5EBDF] border border-[#B58777]/30 rounded-xl text-xs text-[#351D1D]/80 leading-relaxed space-y-1">
              <div className="font-bold text-[#661414] flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5" />
                SSRF Security Enforced
              </div>
              <p>
                Private IP addresses, cloud metadata endpoints, and non-HTTP protocols are automatically blocked. Paywalled pages without full text will be reported honestly.
              </p>
            </div>
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={!url || isLoading}
              className="flex items-center gap-2 bg-[#661414] hover:bg-[#351D1D] disabled:opacity-50 text-[#F5EBDF] px-6 py-2.5 rounded-xl text-sm font-bold shadow transition"
            >
              {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
              {isLoading ? 'Fetching & Extracting...' : 'Ingest Research URL'}
            </button>
          </div>
        </form>
      )}
    </div>
  );
};
