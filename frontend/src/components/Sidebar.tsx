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
  PanelLeftClose,
  PanelLeftOpen,
  BookOpenCheck
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

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

type SidebarItem = {
  id: NavItem;
  label: string;
  icon: LucideIcon;
  highlight?: boolean;
  badge?: number;
  badgeType?: 'alert';
};

type SidebarGroup = { label: string; items: SidebarItem[] };

interface SidebarProps {
  currentTab: NavItem;
  onSelectTab: (tab: NavItem) => void;
  pendingReviewsCount?: number;
  criticalIssuesCount?: number;
  collapsed?: boolean;
  onToggle?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  pendingReviewsCount = 0,
  criticalIssuesCount = 0,
  collapsed = false,
  onToggle,
}) => {
  const groups: SidebarGroup[] = [
    { label: 'Studio', items: [
      { id: 'dashboard', label: 'Overview', icon: LayoutDashboard },
      { id: 'new_research', label: 'New research', icon: PlusCircle, highlight: true },
      { id: 'evidence_ledger', label: 'Evidence ledger', icon: FileCheck2 },
      { id: 'content_studio', label: 'Content studio', icon: Sparkles },
      { id: 'powerpoint_studio', label: 'Presentation', icon: Presentation },
    ] },
    { label: 'Quality & delivery', items: [
      { id: 'review_gate', label: 'Medical review', icon: ShieldCheck, badge: pendingReviewsCount },
      { id: 'claim_safety', label: 'Claim safety', icon: AlertTriangle, badge: criticalIssuesCount, badgeType: 'alert' },
      { id: 'export_center', label: 'Exports', icon: Download },
    ] },
    { label: 'System', items: [
      { id: 'settings', label: 'Settings', icon: SettingsIcon },
    ] },
  ];

  return (
    <aside className={`app-sidebar ${collapsed ? 'is-collapsed' : ''}`}>
      <div className="sidebar-scroll">
        <div className="sidebar-topline">
          {!collapsed && <span>Navigate</span>}
          <button className="sidebar-toggle" onClick={onToggle} aria-label={collapsed ? 'Expand navigation' : 'Collapse navigation'} title={collapsed ? 'Expand navigation' : 'Collapse navigation'}>
            {collapsed ? <PanelLeftOpen size={17} /> : <PanelLeftClose size={17} />}
          </button>
        </div>
        {groups.map((group) => <div className="sidebar-group" key={group.label}>
          {!collapsed && <div className="sidebar-group-label">{group.label}</div>}
          {group.items.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id as NavItem)}
              title={collapsed ? item.label : undefined}
              aria-label={item.label}
              className={`sidebar-nav-item ${isActive ? 'is-active' : ''} ${item.highlight ? 'is-highlight' : ''}`}
            >
              <div className="sidebar-item-label">
                <Icon size={18} strokeWidth={1.8} />
                {!collapsed && <span>{item.label}</span>}
              </div>
              {item.badge !== undefined && item.badge > 0 && (
                <span className={`sidebar-badge ${item.badgeType === 'alert' ? 'is-alert' : ''}`}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
        </div>)}
      </div>

      <div className="sidebar-footnote" title="Evidence first · human review always">
        <BookOpenCheck size={17} />
        {!collapsed && <span>Evidence first · human review always</span>}
      </div>
    </aside>
  );
};
