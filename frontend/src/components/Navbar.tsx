import React from 'react';
import { PlusCircle, Settings, ShieldCheck, Sparkles, BookOpen } from 'lucide-react';
import { HealthStatus } from '../types';

interface NavbarProps {
  health: HealthStatus | null;
  onOpenNewProject: () => void;
  onOpenSettings: () => void;
  onGoHome: () => void;
  activeProjectTitle?: string;
}

export const Navbar: React.FC<NavbarProps> = ({
  health,
  onOpenNewProject,
  onOpenSettings,
  onGoHome,
  activeProjectTitle,
}) => {
  // Format long provider string into clean, concise badge
  const getProviderShortLabel = (label?: string) => {
    if (!label) return 'Local Engine';
    const lower = label.toLowerCase();
    if (lower.includes('deterministic') || lower.includes('local')) return 'Local Engine';
    if (lower.includes('gemini')) return 'Gemini Flash';
    if (lower.includes('openai') || lower.includes('gpt')) return 'GPT-4o';
    return label.length > 18 ? label.slice(0, 16) + '...' : label;
  };

  const rawProvider = health?.ai_provider || 'Deterministic Local Engine';
  const providerLabel = getProviderShortLabel(rawProvider);

  return (
    <header style={{
      background: 'var(--color-soft-paper)',
      borderBottom: '1px solid var(--color-card-border)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
      boxShadow: 'var(--shadow-sm)'
    }}>
      <div className="steer-container" style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: '74px',
        gap: '16px',
        flexWrap: 'nowrap'
      }}>
        {/* Brand */}
        <div 
          onClick={onGoHome}
          style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '12px', 
            cursor: 'pointer',
            flexShrink: 0
          }}
          title="Return to Steer Dashboard"
        >
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '11px',
            background: 'var(--color-rust)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--color-soft-paper)',
            fontFamily: 'var(--font-serif)',
            fontSize: '22px',
            fontWeight: 'bold',
            boxShadow: '0 2px 8px rgba(192, 78, 42, 0.3)',
            flexShrink: 0
          }}>
            S
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{
                fontFamily: 'var(--font-serif)',
                fontSize: '20px',
                fontWeight: '700',
                color: 'var(--color-ink)',
                letterSpacing: '-0.01em',
                lineHeight: 1
              }}>
                Steer
              </span>
              <span className="badge-tag badge-blush" style={{ fontSize: '10px', padding: '2px 7px', lineHeight: 1 }}>
                STUDIO
              </span>
            </div>
            <div className="navbar-subtitle">
              Doctor-Led Research-to-Content Studio
            </div>
          </div>
        </div>

        {/* Center: Active Research Identifier */}
        {activeProjectTitle ? (
          <div 
            title={`Active Project: ${activeProjectTitle}`}
            className="navbar-pill"
            style={{
              gap: '8px',
              background: 'var(--color-cream)',
              padding: '0 14px',
              borderRadius: '19px',
              border: '1px solid var(--color-clay)',
              maxWidth: 'clamp(140px, 24vw, 340px)',
              minWidth: 0,
              flexShrink: 1,
              overflow: 'hidden'
            }}
          >
            <BookOpen size={14} color="var(--color-rust)" style={{ flexShrink: 0 }} />
            <span style={{ 
              fontSize: '12px', 
              fontWeight: 600, 
              color: 'var(--color-ink)', 
              overflow: 'hidden', 
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap'
            }}>
              {activeProjectTitle}
            </span>
          </div>
        ) : (
          <div style={{ flex: '0 1 auto' }} />
        )}

        {/* Right Action Cluster */}
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '8px',
          flexShrink: 0
        }}>
          {/* Doctor Gate Status */}
          <div 
            className="navbar-pill"
            style={{
              gap: '6px',
              background: '#E8F5E9',
              border: '1px solid #A5D6A7',
              padding: '0 12px',
              borderRadius: '19px',
              fontSize: '12px',
              fontWeight: '600',
              color: '#1B5E20'
            }}
            title="Doctor Gate is enforcing claim verification before export"
          >
            <ShieldCheck size={14} style={{ flexShrink: 0 }} />
            <span className="hide-on-compact">Doctor Gate Active</span>
            <span className="show-on-compact">Doctor Gate</span>
          </div>

          {/* Research Engine Status */}
          <div 
            onClick={onOpenSettings}
            className="navbar-pill"
            style={{
              gap: '6px',
              background: 'var(--color-rust-light)',
              border: '1px solid var(--color-blush)',
              padding: '0 12px',
              borderRadius: '19px',
              fontSize: '12px',
              fontWeight: '600',
              color: 'var(--color-rust)',
              cursor: 'pointer'
            }}
            title={`Active Engine: ${rawProvider}\nClick to configure API settings`}
          >
            <Sparkles size={14} style={{ flexShrink: 0 }} />
            <span>{providerLabel}</span>
          </div>

          {/* Settings Button */}
          <button
            onClick={onOpenSettings}
            className="btn-secondary btn-navbar-icon"
            style={{ borderRadius: '19px' }}
            title="Configure AI API Keys & System Settings"
          >
            <Settings size={15} />
          </button>

          {/* New Research Button */}
          <button
            onClick={onOpenNewProject}
            className="btn-primary btn-navbar-primary"
            style={{ borderRadius: '19px', fontSize: '13px' }}
          >
            <PlusCircle size={15} style={{ flexShrink: 0 }} />
            <span className="hide-on-compact">New Research</span>
            <span className="show-on-compact">New</span>
          </button>
        </div>
      </div>
    </header>
  );
};
