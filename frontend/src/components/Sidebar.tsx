import React from 'react';
import {
  LayoutDashboard,
  PlusCircle,
  FileCheck2,
  Sparkles,
  Presentation,
  ShieldCheck,
  AlertTriangle,
  Download,
  Settings as SettingsIcon,
  HelpCircle
} from 'lucide-react';

export type NavItem =
  | 'dashboard'
  | 'new_research'
  | 'evidence_ledger'
  | 'content_studio'
  | 'powerpoint_studio'
  | 'review_gate'
  | 'claim_safety'
  | 'export_center'
  | 'settings';

interface SidebarProps {
  currentTab: NavItem;
  onSelectTab: (tab: NavItem) => void;
  pendingReviewsCount?: number;
  criticalIssuesCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  pendingReviewsCount = 0,
  criticalIssuesCount = 0,
}) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'new_research', label: 'New Research', icon: PlusCircle, highlight: true },
    { id: 'evidence_ledger', label: 'Evidence Ledger', icon: FileCheck2 },
    { id: 'content_studio', label: 'Content Studio', icon: Sparkles },
    { id: 'powerpoint_studio', label: 'PowerPoint Studio', icon: Presentation },
    { id: 'review_gate', label: 'Medical Review Gate', icon: ShieldCheck, badge: pendingReviewsCount },
    { id: 'claim_safety', label: 'Claim Safety Checks', icon: AlertTriangle, badge: criticalIssuesCount, badgeType: 'alert' },
    { id: 'export_center', label: 'Export Center', icon: Download },
    { id: 'settings', label: 'Settings & Status', icon: SettingsIcon },
  ];

  return (
    <aside className="w-64 border-r border-[#E6CBBD] bg-[#F8F2EB] flex flex-col justify-between p-4 shrink-0 h-[calc(100vh-4rem)]">
      <div className="space-y-1">
        <div className="px-3 py-2 text-[11px] font-bold uppercase tracking-wider text-[#B58777]">
          Medical Editorial Workflow
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id as NavItem)}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-[#661414] text-[#F5EBDF] shadow-sm font-semibold'
                  : item.highlight
                  ? 'text-[#C04E2A] hover:bg-[#E6CBBD]/30 font-semibold'
                  : 'text-[#351D1D] hover:bg-[#F5EBDF] hover:text-[#661414]'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-[#F5EBDF]' : item.highlight ? 'text-[#C04E2A]' : 'text-[#B58777]'}`} />
                <span>{item.label}</span>
              </div>

              {item.badge !== undefined && item.badge > 0 && (
                <span
                  className={`text-[11px] font-bold px-2 py-0.5 rounded-full ${
                    item.badgeType === 'alert'
                      ? 'bg-rose-100 text-rose-800'
                      : isActive
                      ? 'bg-[#F5EBDF] text-[#661414]'
                      : 'bg-[#C04E2A] text-white'
                  }`}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Steer Editorial Principle Card */}
      <div className="bg-[#F5EBDF] border border-[#E6CBBD] rounded-xl p-3.5 text-xs text-[#351D1D] space-y-1.5 shadow-sm">
        <div className="flex items-center gap-1.5 text-[#661414] font-serif font-bold text-sm">
          <span>Editorial Oath</span>
        </div>
        <p className="text-[#351D1D]/80 leading-relaxed font-sans text-[11px]">
          One verified scientific source. Multiple formats. Different audiences. Consistent evidence. Human approval.
        </p>
      </div>
    </aside>
  );
};
