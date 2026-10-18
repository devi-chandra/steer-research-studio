import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  CheckCircle2,
  Edit3,
  XCircle,
  AlertCircle,
  Clock,
  UserCheck,
  Sparkles,
  BookOpen,
  Filter,
  Check,
  Quote,
  Info
} from 'lucide-react';
import { api } from '../services/api';
import { Project, Claim, ReviewRecord, ReviewRule } from '../types';
import { EvidenceBadge } from '../components/EvidenceBadge';
import { NavItem } from '../components/Sidebar';

interface ReviewGatePageProps {
  currentProject: Project | null;
  onNavigate: (tab: NavItem) => void;
}

const REASONS = [
  'Unsupported claim',
  'Incorrect statistic',
  'Missing limitation',
  'Misleading headline',
  'Incorrect translation',
  'Unclear language',
  'Unsubstantiated recommendation',
  'Other'
];

export const ReviewGatePage: React.FC<ReviewGatePageProps> = ({ currentProject, onNavigate }) => {
  const [claims, setClaims] = useState<Claim[]>([]);
  const [reviews, setReviews] = useState<ReviewRecord[]>([]);
  const [rules, setRules] = useState<ReviewRule[]>([]);
  const [selectedClaim, setSelectedClaim] = useState<Claim | null>(null);

  // Review Action Form State
  const [decision, setDecision] = useState<'Approve' | 'Edit' | 'Request Changes' | 'Reject'>('Approve');
  const [reasonCategory, setReasonCategory] = useState<string>('Other');
  const [revisedContent, setRevisedContent] = useState<string>('');
  const [comments, setComments] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<false | true>(false);
  const [feedbackSuccess, setFeedbackSuccess] = useState<string | null>(null);

  const loadReviewData = async () => {
    if (!currentProject) return;
    try {
      const [claimsRes, revsRes, rulesRes] = await Promise.all([
        api.getClaims(currentProject.id),
        api.getReviews(currentProject.id),
        api.getReviewRules()
      ]);
      setClaims(claimsRes.claims);
      setReviews(revsRes.reviews);
      setRules(rulesRes.rules);
      if (claimsRes.claims.length > 0 && !selectedClaim) {
        setSelectedClaim(claimsRes.claims[0]);
        setRevisedContent(claimsRes.claims[0].claim_text);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadReviewData();
  }, [currentProject?.id]);

  const handleSelectClaim = (c: Claim) => {
    setSelectedClaim(c);
    setRevisedContent(c.claim_text);
    setDecision('Approve');
    setComments('');
    setFeedbackSuccess(null);
  };

  const handleSubmitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentProject || !selectedClaim) return;

    setIsSubmitting(true);
    setFeedbackSuccess(null);

    try {
      const res = await api.submitReview({
        project_id: currentProject.id,
        target_type: 'claim',
        target_id: selectedClaim.claim_id,
        decision: decision,
        reason_category: reasonCategory,
        original_content: selectedClaim.claim_text,
        revised_content: decision === 'Edit' ? revisedContent : '',
        comments: comments,
        reviewer_name: 'Dr. Medical Reviewer (Demo Lead)'
      });

      if (res.success) {
        setFeedbackSuccess(`Decision '${decision}' recorded. ${res.rule_update || ''}`);
        await loadReviewData();
      }
    } catch (err: any) {
      alert('Review submission failed: ' + err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!currentProject) {
    return (
      <div className="p-12 text-center max-w-xl mx-auto space-y-4">
        <h2 className="font-serif text-2xl font-bold text-[#661414]">No Project Selected</h2>
        <p className="text-sm text-[#351D1D]/70">
          Select a project to review clinical claims and enforce medical publication policies.
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

  const pendingCount = claims.filter(c => c.review_status === 'Pending Review').length;
  const approvedCount = claims.filter(c => c.review_status.includes('Approved')).length;

  return (
    <div className="workspace-page max-w-7xl mx-auto space-y-6">
      {/* Simulation / Demo Notice Banner */}
      <div className="bg-sky-50 border border-sky-300 rounded-2xl p-4 flex items-start gap-3 shadow-xs">
        <Info className="w-5 h-5 text-sky-700 shrink-0 mt-0.5" />
        <div className="space-y-1 text-xs text-sky-950">
          <div className="font-bold text-sky-900 uppercase tracking-wider text-[11px]">
            Demo Simulation Mode — Simulated Clinician Review
          </div>
          <p className="text-sky-900/90 leading-relaxed font-sans">
            This workspace demonstrates the clinician audit workflow and feedback rule engine. <strong>All review decisions and reviewer profiles in this environment are simulated for demonstration purposes.</strong> They do not represent real clinician approval, medical evaluation, or clinical advice. Real-world deployment requires authenticated, credentialed clinical reviewers.
          </p>
        </div>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-bold text-[#C04E2A] uppercase tracking-wider mb-1">
            <ShieldCheck className="w-3.5 h-3.5" />
            Differentiator Feature 5
          </div>
          <h1 className="font-serif text-3xl font-bold text-[#661414]">
            Medical Review Gate & Feedback Loop (Simulated Demo)
          </h1>
          <p className="text-xs text-[#351D1D]/75">
            Simulated clinician review workflow: Every health claim must have traceable evidence and an explicit review decision before publication approval.
          </p>
        </div>

        <div className="flex items-center gap-4 bg-[#FFFFFF] border border-[#E6CBBD] px-4 py-2 rounded-xl text-xs shadow-xs">
          <div>
            <span className="text-[#B58777]">Pending:</span>{' '}
            <strong className="text-[#C04E2A] font-mono text-sm">{pendingCount}</strong>
          </div>
          <div>
            <span className="text-emerald-700">Approved:</span>{' '}
            <strong className="text-emerald-800 font-mono text-sm">{approvedCount}</strong>
          </div>
        </div>
      </div>

      {feedbackSuccess && (
        <div className="p-4 bg-emerald-50 border border-emerald-300 rounded-xl text-xs font-semibold text-emerald-900 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{feedbackSuccess}</span>
        </div>
      )}

      {/* Main Review Workplace */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-start">
        {/* Left: Claims Queue */}
        <div className="md:col-span-5 bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-5 shadow-xs space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-[#661414] uppercase tracking-wider">
              Claims for Clinical Audit ({claims.length})
            </span>
          </div>

          <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
            {claims.map((c) => {
              const isSelected = selectedClaim?.id === c.id;
              return (
                <div
                  key={c.id}
                  onClick={() => handleSelectClaim(c)}
                  className={`p-3.5 rounded-xl border text-xs transition cursor-pointer space-y-1.5 ${
                    isSelected
                      ? 'bg-[#F5EBDF] border-[#661414] shadow-xs'
                      : 'bg-[#F8F2EB] border-[#E6CBBD] hover:bg-white'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono font-bold text-[#661414]">{c.claim_id}</span>
                    <EvidenceBadge status={c.review_status} type="review" />
                  </div>
                  <div className="font-medium text-[#351D1D] line-clamp-2">
                    {c.claim_text}
                  </div>
                  <div className="text-[11px] text-[#B58777]">
                    Page {c.page_number} • {c.numerical_result || 'Qualitative'}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: Decision Panel & Revision Editor */}
        <div className="md:col-span-7 space-y-6">
          {selectedClaim ? (
            <form onSubmit={handleSubmitReview} className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-6 shadow-xs space-y-5">
              <div className="flex items-center justify-between border-b border-[#E6CBBD] pb-4">
                <div>
                  <span className="font-mono font-bold text-sm bg-[#661414] text-[#F5EBDF] px-2.5 py-1 rounded">
                    Auditing: {selectedClaim.claim_id}
                  </span>
                  <div className="text-xs text-[#B58777] mt-1">
                    Page {selectedClaim.page_number} • Section: {selectedClaim.section_heading}
                  </div>
                </div>
                <EvidenceBadge status={selectedClaim.evidence_status} type="evidence" />
              </div>

              {/* Verbatim Supporting Quote Card */}
              <div className="bg-[#F8F2EB] border border-[#E6CBBD] rounded-xl p-3.5 space-y-1.5">
                <div className="text-[11px] font-bold text-[#661414] flex items-center gap-1.5">
                  <Quote className="w-3.5 h-3.5 text-[#C04E2A]" />
                  Original Supporting Source Quotation
                </div>
                <p className="text-xs font-serif italic text-[#351D1D] bg-white p-2.5 rounded border border-[#E6CBBD] leading-relaxed">
                  "{selectedClaim.exact_quote}"
                </p>
              </div>

              {/* Decision Options */}
              <div className="space-y-2">
                <label className="block text-xs font-bold text-[#661414] uppercase tracking-wider">
                  Simulated Review Decision
                </label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {[
                    { val: 'Approve', label: 'Approve', color: 'hover:border-emerald-600', active: 'bg-emerald-600 text-white' },
                    { val: 'Edit', label: 'Edit & Approve', color: 'hover:border-blue-600', active: 'bg-blue-600 text-white' },
                    { val: 'Request Changes', label: 'Request Changes', color: 'hover:border-amber-600', active: 'bg-amber-600 text-white' },
                    { val: 'Reject', label: 'Reject Claim', color: 'hover:border-rose-600', active: 'bg-rose-600 text-white' },
                  ].map((btn) => (
                    <button
                      key={btn.val}
                      type="button"
                      onClick={() => setDecision(btn.val as any)}
                      className={`py-2 px-3 rounded-xl text-xs font-bold border transition ${
                        decision === btn.val
                          ? btn.active
                          : 'bg-[#F8F2EB] border-[#E6CBBD] text-[#351D1D] ' + btn.color
                      }`}
                    >
                      {btn.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Reason Category if not simple approve */}
              {decision !== 'Approve' && (
                <div className="space-y-1.5">
                  <label className="block text-xs font-bold text-[#661414] uppercase tracking-wider">
                    Reason Category (Generates Reusable Review Rule)
                  </label>
                  <select
                    value={reasonCategory}
                    onChange={(e) => setReasonCategory(e.target.value)}
                    className="w-full text-xs p-2.5 bg-[#F8F2EB] border border-[#B58777] rounded-xl outline-none"
                  >
                    {REASONS.map((r) => (
                      <option key={r} value={r}>
                        {r}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Revised text if Edit is selected */}
              {decision === 'Edit' && (
                <div className="space-y-1.5">
                  <label className="block text-xs font-bold text-[#661414] uppercase tracking-wider">
                    Revised Claim Wording
                  </label>
                  <textarea
                    value={revisedContent}
                    onChange={(e) => setRevisedContent(e.target.value)}
                    rows={3}
                    className="w-full text-xs p-3 bg-[#FFFFFF] border border-[#B58777] rounded-xl outline-none focus:ring-1 focus:ring-[#C04E2A]"
                  />
                </div>
              )}

              {/* Simulated Review Notes */}
              <div className="space-y-1.5">
                <label className="block text-xs font-bold text-[#661414] uppercase tracking-wider">
                  Simulated Reviewer Notes & Justification
                </label>
                <textarea
                  value={comments}
                  onChange={(e) => setComments(e.target.value)}
                  placeholder="Record justification, clinical nuances, or missing cohort boundaries..."
                  rows={2}
                  className="w-full text-xs p-2.5 bg-[#F8F2EB] border border-[#B58777] rounded-xl outline-none"
                />
              </div>

              <div className="flex justify-end pt-2">
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-6 py-2.5 rounded-xl bg-[#661414] text-[#F5EBDF] text-xs font-bold hover:bg-[#351D1D] shadow transition"
                >
                  {isSubmitting ? 'Recording Decision...' : 'Submit Simulated Decision'}
                </button>
              </div>
            </form>
          ) : (
            <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-10 text-center text-xs text-[#B58777]">
              Select a claim on the left to perform simulated clinician review.
            </div>
          )}

          {/* Persisted Review Rules Section */}
          <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-serif text-base font-bold text-[#661414]">
                  Active Review Rules (Learned From Clinical Feedback)
                </h3>
                <p className="text-xs text-[#351D1D]/70 mt-0.5">
                  Rules persisted from prior doctor revisions to automatically flag overclaims in future content.
                </p>
              </div>
              <span className="font-mono text-xs bg-[#E6CBBD]/40 text-[#661414] px-2.5 py-1 rounded font-bold">
                {rules.length} Rules Active
              </span>
            </div>

            <div className="space-y-2">
              {rules.slice(0, 4).map((r) => (
                <div
                  key={r.id}
                  className="p-3 bg-[#F8F2EB] border border-[#E6CBBD] rounded-xl text-xs space-y-1"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono font-bold text-[#C04E2A]">{r.rule_type}</span>
                    <span className="text-[10px] text-[#B58777]">Trigger Count: {r.trigger_count}</span>
                  </div>
                  <div className="text-[#351D1D] font-medium">{r.description}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
