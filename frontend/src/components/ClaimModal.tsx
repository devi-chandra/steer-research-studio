import React, { useState } from 'react';
import { X, Check, FileText, AlertCircle, Quote, Sparkles } from 'lucide-react';
import { Claim } from '../types';
import { EvidenceBadge } from './EvidenceBadge';

interface ClaimModalProps {
  claim: Claim;
  onClose: () => void;
  onSave: (updatedClaim: Partial<Claim>) => void;
}

export const ClaimModal: React.FC<ClaimModalProps> = ({ claim, onClose, onSave }) => {
  const [claimText, setClaimText] = useState(claim.claim_text);
  const [numericalResult, setNumericalResult] = useState(claim.numerical_result);
  const [limitations, setLimitations] = useState(claim.limitations);
  const [isEditing, setIsEditing] = useState(false);

  const handleSave = () => {
    onSave({
      claim_text: claimText,
      numerical_result: numericalResult,
      limitations: limitations,
    });
    setIsEditing(false);
  };

  return (
    <div className="fixed inset-0 z-50 bg-[#351D1D]/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-[#F8F2EB] border border-[#B58777] rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-[#E6CBBD]">
          <div className="flex items-center gap-3">
            <span className="font-mono font-bold text-sm bg-[#661414] text-[#F5EBDF] px-2.5 py-1 rounded">
              {claim.claim_id}
            </span>
            <div className="flex items-center gap-2">
              <EvidenceBadge status={claim.evidence_status} type="evidence" />
              <EvidenceBadge status={claim.review_status} type="review" />
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-[#B58777] hover:text-[#661414] p-1 rounded-lg hover:bg-[#F5EBDF]"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Verbatim Supporting Quote Card */}
        <div className="bg-[#F5EBDF] border border-[#B58777]/50 rounded-xl p-4 space-y-2">
          <div className="flex items-center gap-2 text-xs font-bold text-[#661414] uppercase tracking-wider">
            <Quote className="w-3.5 h-3.5 text-[#C04E2A]" />
            Verbatim Supporting Source Quotation (Page {claim.page_number} • {claim.section_heading})
          </div>
          <p className="text-sm font-serif italic text-[#351D1D] leading-relaxed bg-white/70 p-3 rounded-lg border border-[#E6CBBD]">
            "{claim.exact_quote}"
          </p>
        </div>

        {/* Claim Statement & Metrics */}
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-[#661414] uppercase tracking-wider mb-1.5">
              Extracted Factual Statement
            </label>
            {isEditing ? (
              <textarea
                value={claimText}
                onChange={(e) => setClaimText(e.target.value)}
                className="w-full text-sm p-3 border border-[#B58777] rounded-lg bg-white focus:ring-1 focus:ring-[#C04E2A] outline-none"
                rows={3}
              />
            ) : (
              <p className="text-sm text-[#351D1D] font-medium p-3 bg-white rounded-lg border border-[#E6CBBD]">
                {claimText}
              </p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-[#661414] uppercase tracking-wider mb-1.5">
                Numerical Finding & Units
              </label>
              {isEditing ? (
                <input
                  type="text"
                  value={numericalResult}
                  onChange={(e) => setNumericalResult(e.target.value)}
                  className="w-full text-sm p-2.5 border border-[#B58777] rounded-lg bg-white focus:ring-1 focus:ring-[#C04E2A] outline-none"
                />
              ) : (
                <div className="text-sm font-mono font-semibold text-[#661414] p-2.5 bg-white rounded-lg border border-[#E6CBBD]">
                  {numericalResult || 'Qualitative finding'}
                </div>
              )}
            </div>

            <div>
              <label className="block text-xs font-bold text-[#661414] uppercase tracking-wider mb-1.5">
                Cohort & Sample Size
              </label>
              <div className="text-sm font-mono text-[#351D1D] p-2.5 bg-white rounded-lg border border-[#E6CBBD]">
                {claim.sample_size || 'Referenced in trial cohort'}
              </div>
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-[#661414] uppercase tracking-wider mb-1.5">
              Scientific Limitations & Bounds
            </label>
            {isEditing ? (
              <textarea
                value={limitations}
                onChange={(e) => setLimitations(e.target.value)}
                className="w-full text-sm p-3 border border-[#B58777] rounded-lg bg-white focus:ring-1 focus:ring-[#C04E2A] outline-none"
                rows={2}
              />
            ) : (
              <p className="text-xs text-[#351D1D]/90 p-3 bg-white rounded-lg border border-[#E6CBBD] leading-relaxed">
                {limitations || 'Standard clinical trial parameters apply.'}
              </p>
            )}
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center justify-between pt-4 border-t border-[#E6CBBD]">
          <div className="text-xs text-[#B58777]">
            Reviewer: {claim.reviewer_name || 'Dr. Medical Reviewer (Pending)'}
          </div>
          <div className="flex items-center gap-2">
            {isEditing ? (
              <>
                <button
                  onClick={() => setIsEditing(false)}
                  className="px-3.5 py-1.5 rounded-lg border border-[#B58777] text-xs font-medium text-[#351D1D] hover:bg-[#F5EBDF]"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSave}
                  className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-[#661414] text-[#F5EBDF] text-xs font-bold hover:bg-[#351D1D]"
                >
                  <Check className="w-3.5 h-3.5" />
                  Save Edits
                </button>
              </>
            ) : (
              <button
                onClick={() => setIsEditing(true)}
                className="px-4 py-1.5 rounded-lg border border-[#C04E2A] text-[#C04E2A] text-xs font-bold hover:bg-[#C04E2A]/10"
              >
                Edit Claim
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
