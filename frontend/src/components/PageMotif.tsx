import React from 'react';
import {
  BookOpenCheck,
  ClipboardCheck,
  FileCheck2,
  Files,
  Presentation,
  SearchCheck,
  Settings2,
  ShieldCheck,
  Sparkles,
  Upload,
} from 'lucide-react';
import { NavItem } from './Sidebar';

const motifs: Record<NavItem, { icon: typeof Files; label: string }> = {
  dashboard: { icon: Sparkles, label: 'Studio overview' },
  new_research: { icon: Files, label: 'Research intake' },
  evidence_ledger: { icon: BookOpenCheck, label: 'Evidence ledger' },
  content_studio: { icon: Sparkles, label: 'Content studio' },
  powerpoint_studio: { icon: Presentation, label: 'Presentation studio' },
  review_gate: { icon: ClipboardCheck, label: 'Medical review' },
  claim_safety: { icon: ShieldCheck, label: 'Claim safety' },
  export_center: { icon: Upload, label: 'Export center' },
  settings: { icon: Settings2, label: 'Settings' },
};

export const PageMotif: React.FC<{ tab: NavItem }> = ({ tab }) => {
  const { icon: Icon, label } = motifs[tab];

  return (
    <div className="page-motif" aria-hidden="true" title={label}>
      <span className="motif-orbit motif-orbit-one" />
      <span className="motif-orbit motif-orbit-two" />
      <span className="motif-bubble motif-bubble-main"><Icon size={23} /></span>
      <span className="motif-bubble motif-bubble-small"><FileCheck2 size={14} /></span>
      <span className="motif-sparkle"><SearchCheck size={13} /></span>
    </div>
  );
};
