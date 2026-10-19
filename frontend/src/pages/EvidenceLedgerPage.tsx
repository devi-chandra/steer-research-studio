import React, { useState, useEffect } from 'react';
import {
  FileCheck2,
  Filter,
  CheckCircle2,
  AlertCircle,
  Eye,
  RefreshCw,
  Search,
  BookOpen,
  ArrowRight,
  Sparkles,
  Presentation,
  ShieldCheck,
  Download,
  ClipboardCheck
} from 'lucide-react';
import { api } from '../services/api';
import { Project, Claim } from '../types';
import { EvidenceBadge } from '../components/EvidenceBadge';
import { ClaimModal } from '../components/ClaimModal';
import { NavItem } from '../components/Sidebar';

interface EvidenceLedgerPageProps {
  currentProject: Project | null;
  onNavigate: (tab: NavItem) => void;
}

export const EvidenceLedgerPage: React.FC<EvidenceLedgerPageProps> = ({ currentProject, onNavigate }) => {
  const [claims, setClaims] = useState<Claim[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [evidenceFilter, setEvidenceFilter] = useState<string>('');
  const [reviewFilter, setReviewFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedClaim, setSelectedClaim] = useState<Claim | null>(null);
  const [verificationSummary, setVerificationSummary] = useState<any | null>(null);

  const fetchClaims = async () => {
    if (!currentProject) return;
    setIsLoading(true);
    try {
      const res = await api.getClaims(currentProject.id, evidenceFilter || undefined, reviewFilter || undefined);
      setClaims(res.claims);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchClaims();
  }, [currentProject?.id, evidenceFilter, reviewFilter]);

  const handleVerify = async () => {
    if (!currentProject) return;
    setIsLoading(true);
    try {
      const res = await api.verifyEvidence(currentProject.id);
      setVerificationSummary(res.verification);
      await fetchClaims();
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveClaim = async (updatedFields: Partial<Claim>) => {
    if (!selectedClaim) return;
    try {
      const res = await api.updateClaim(selectedClaim.id, updatedFields);
      if (res.success) {
        setClaims(claims.map(c => c.id === selectedClaim.id ? { ...c, ...res.claim } : c));
        setSelectedClaim(null);
      }
    } catch (err) {
      console.error('Update claim error:', err);
    }
  };

  if (!currentProject) {
    return (
      <div className="p-12 text-center max-w-xl mx-auto space-y-4">
        <BookOpen className="w-12 h-12 text-[#B58777] mx-auto opacity-50" />
        <h2 className="font-serif text-2xl font-bold text-[#661414]">No Project Selected</h2>
        <p className="text-sm text-[#351D1D]/70">
          Please select an existing research project or upload a new paper to view its evidence ledger.
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

  const filteredClaims = claims.filter(c => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      c.claim_id.toLowerCase().includes(q) ||
      c.claim_text.toLowerCase().includes(q) ||
      c.exact_quote.toLowerCase().includes(q) ||
      c.numerical_result.toLowerCase().includes(q)
    );
  });

  const directlyCount = claims.filter(c => c.evidence_status === 'Directly supported').length;
  const partiallyCount = claims.filter(c => c.evidence_status === 'Partially supported').length;
  const unsupportedCount = claims.filter(c => c.evidence_status === 'Unsupported').length;

  return (
    <div className="workspace-page evidence-page max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-bold text-[#C04E2A] uppercase tracking-wider mb-1">
            <FileCheck2 className="w-3.5 h-3.5" />
            Paper workspace
          </div>
          <h1 className="font-serif text-3xl font-bold text-[#661414]">
            Evidence & claims
          </h1>
          <p className="text-xs text-[#351D1D]/75 mt-0.5">
            Source: <span className="font-semibold text-[#351D1D]">{currentProject.title}</span> • DOI: {currentProject.doi || 'Peer-Reviewed'}
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleVerify}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#F5EBDF] border border-[#B58777] text-xs font-bold text-[#661414] hover:bg-[#661414] hover:text-[#F5EBDF] transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            Re-Verify Evidence
          </button>
        </div>
      </div>

      <section className="paper-workflow" aria-labelledby="paper-workflow-title">
        <div className="paper-workflow-heading">
          <div>
            <span className="workflow-kicker"><ClipboardCheck size={14} /> Recommended workflow</span>
            <h2 id="paper-workflow-title">What would you like to do with this paper?</h2>
            <p>Start with the evidence, then create, review and export your work.</p>
          </div>
          <span className="workflow-claim-count">{isLoading ? 'Loading claims…' : `${claims.length} extracted ${claims.length === 1 ? 'claim' : 'claims'}`}</span>
        </div>
        <div className="paper-workflow-actions">
          <button className="workflow-action" onClick={() => document.getElementById('claims-table')?.scrollIntoView({ behavior: 'smooth', block: 'start' })}>
            <span className="workflow-action-icon"><FileCheck2 size={17} /></span>
            <span><b>1. Check evidence</b><small>Inspect claims and source quotes</small></span>
            <ArrowRight size={15} />
          </button>
          <button className="workflow-action" onClick={() => onNavigate('content_studio')}>
            <span className="workflow-action-icon"><Sparkles size={17} /></span>
            <span><b>2. Create social content</b><small>Carousel, post, captions and reel</small></span>
            <ArrowRight size={15} />
          </button>
          <button className="workflow-action" onClick={() => onNavigate('powerpoint_studio')}>
            <span className="workflow-action-icon"><Presentation size={17} /></span>
            <span><b>3. Build a presentation</b><small>Turn findings into slides</small></span>
            <ArrowRight size={15} />
          </button>
          <button className="workflow-action" onClick={() => onNavigate('review_gate')}>
            <span className="workflow-action-icon"><ShieldCheck size={17} /></span>
            <span><b>4. Review claims</b><small>Open the simulated review queue</small></span>
            <ArrowRight size={15} />
          </button>
          <button className="workflow-action" onClick={() => onNavigate('claim_safety')}>
            <span className="workflow-action-icon"><Download size={17} /></span>
            <span><b>5. Check and export</b><small>Run safety checks, then package</small></span>
            <ArrowRight size={15} />
          </button>
        </div>
        <p className="workflow-demo-note">Review decisions in this demo are simulated; real medical approval requires a qualified reviewer.</p>
      </section>

      {/* Verification Counter Bar */}
      <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-xl p-4 flex flex-wrap items-center justify-between gap-4 shadow-xs">
        <div className="flex items-center gap-6 text-xs">
          <div>
            <span className="text-[#B58777]">Total Extracted Claims:</span>{' '}
            <strong className="text-[#351D1D] font-mono text-sm">{claims.length}</strong>
          </div>
          <div>
            <span className="text-emerald-700">Directly Supported:</span>{' '}
            <strong className="text-emerald-800 font-mono text-sm">{directlyCount}</strong>
          </div>
          <div>
            <span className="text-amber-700">Partially Supported:</span>{' '}
            <strong className="text-amber-800 font-mono text-sm">{partiallyCount}</strong>
          </div>
          <div>
            <span className="text-rose-700">Unsupported:</span>{' '}
            <strong className="text-rose-800 font-mono text-sm">{unsupportedCount}</strong>
          </div>
        </div>

        {verificationSummary && (
          <div className="text-xs text-emerald-800 bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-lg">
            ✓ Verification completed: {verificationSummary.directly_supported} exact matches verified on page text.
          </div>
        )}
      </div>

      {/* Filters & Search */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-3 bg-[#FFFFFF] border border-[#E6CBBD] p-3 rounded-xl">
        <div className="flex items-center gap-2 w-full md:w-auto">
          <Search className="w-4 h-4 text-[#B58777]" />
          <input
            type="text"
            placeholder="Search claims, quotes, numbers..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="text-xs p-2 bg-transparent outline-none w-full md:w-64 text-[#351D1D]"
          />
        </div>

        <div className="flex items-center gap-3 w-full md:w-auto">
          <div className="flex items-center gap-1.5 text-xs text-[#B58777]">
            <Filter className="w-3.5 h-3.5" />
            <span>Evidence:</span>
            <select
              value={evidenceFilter}
              onChange={(e) => setEvidenceFilter(e.target.value)}
              className="bg-[#F8F2EB] border border-[#B58777]/40 rounded px-2 py-1 text-xs text-[#351D1D] outline-none"
            >
              <option value="">All Statuses</option>
              <option value="Directly supported">Directly supported</option>
              <option value="Partially supported">Partially supported</option>
              <option value="Unsupported">Unsupported</option>
              <option value="Unable to verify">Unable to verify</option>
            </select>
          </div>

          <div className="flex items-center gap-1.5 text-xs text-[#B58777]">
            <span>Review:</span>
            <select
              value={reviewFilter}
              onChange={(e) => setReviewFilter(e.target.value)}
              className="bg-[#F8F2EB] border border-[#B58777]/40 rounded px-2 py-1 text-xs text-[#351D1D] outline-none"
            >
              <option value="">All Reviews</option>
              <option value="Pending Review">Pending Review</option>
              <option value="Approved">Approved</option>
              <option value="Approved (Edited by Doctor)">Approved (Edited)</option>
              <option value="Changes Requested">Changes Requested</option>
              <option value="Rejected">Rejected</option>
            </select>
          </div>
        </div>
      </div>

      {/* Table */}
      <div id="claims-table" className="evidence-table-wrap bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-[#F5EBDF] border-b border-[#E6CBBD] text-[#661414] font-bold uppercase tracking-wider text-[11px]">
                <th className="py-3.5 px-4 w-24">Claim ID</th>
                <th className="py-3.5 px-4 w-64">Statement & Metrics</th>
                <th className="py-3.5 px-4">Verbatim Supporting Quote</th>
                <th className="py-3.5 px-4 w-32">Page & Section</th>
                <th className="py-3.5 px-4 w-36">Evidence Status</th>
                <th className="py-3.5 px-4 w-36">Review Status</th>
                <th className="py-3.5 px-4 w-20 text-right">Inspect</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E6CBBD]/60">
              {filteredClaims.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-12 text-[#B58777]">
                    No claims match the selected criteria.
                  </td>
                </tr>
              ) : (
                filteredClaims.map((c) => (
                  <tr
                    key={c.id}
                    onClick={() => setSelectedClaim(c)}
                    className="hover:bg-[#F8F2EB] transition cursor-pointer"
                  >
                    <td className="py-3.5 px-4 font-mono font-bold text-[#661414]">
                      {c.claim_id}
                    </td>

                    <td className="py-3.5 px-4 space-y-1">
                      <div className="font-semibold text-[#351D1D] line-clamp-2">
                        {c.claim_text}
                      </div>
                      {c.numerical_result && (
                        <div className="font-mono text-[11px] text-[#C04E2A] font-bold">
                          {c.numerical_result}
                        </div>
                      )}
                    </td>

                    <td className="py-3.5 px-4 text-[#351D1D]/80 italic font-serif line-clamp-2">
                      "{c.exact_quote.slice(0, 110)}..."
                    </td>

                    <td className="py-3.5 px-4 text-[#B58777] font-medium">
                      Page {c.page_number}
                      <div className="text-[10px] text-[#351D1D]/60">{c.section_heading}</div>
                    </td>

                    <td className="py-3.5 px-4">
                      <EvidenceBadge status={c.evidence_status} type="evidence" />
                    </td>

                    <td className="py-3.5 px-4">
                      <EvidenceBadge status={c.review_status} type="review" />
                    </td>

                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedClaim(c);
                        }}
                        className="p-1.5 rounded-lg text-[#B58777] hover:text-[#661414] hover:bg-[#F5EBDF]"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Claim Detail / Edit Modal */}
      {selectedClaim && (
        <ClaimModal
          claim={selectedClaim}
          onClose={() => setSelectedClaim(null)}
          onSave={handleSaveClaim}
        />
      )}
    </div>
  );
};
