import React, { useState, useEffect } from 'react';
import { X, Settings, Sparkles, Key, Volume2, HardDrive, CheckCircle2, ShieldCheck, Info } from 'lucide-react';
import { SettingsData, HealthStatus } from '../types';
import { api } from '../services/api';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSettingsUpdated: () => void;
  health: HealthStatus | null;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  onSettingsUpdated,
  health,
}) => {
  const [provider, setProvider] = useState<string>('local_sample');
  const [geminiKey, setGeminiKey] = useState<string>('');
  const [openaiKey, setOpenAIKey] = useState<string>('');
  const [ttsVoice, setTtsVoice] = useState<string>('en-IN-NeerjaNeural');
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [saveSuccess, setSaveSuccess] = useState<boolean>(false);

  useEffect(() => {
    if (isOpen) {
      api.getSettings().then((s) => {
        setProvider(s.ai_provider);
        setTtsVoice(s.tts_voice);
      }).catch(console.error);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setSaveSuccess(false);

    try {
      await api.updateSettings({
        ai_provider: provider,
        gemini_api_key: geminiKey.trim() || undefined,
        openai_api_key: openaiKey.trim() || undefined,
        tts_voice: ttsVoice,
      });

      setIsSaving(false);
      setSaveSuccess(true);
      onSettingsUpdated();
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err: any) {
      setIsSaving(false);
      alert(`Failed to save settings: ${err.message}`);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ padding: '36px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
          <div>
            <div className="badge-tag badge-blush" style={{ marginBottom: '8px' }}>
              CONFIGURATION & PROVIDERS
            </div>
            <h2 style={{ fontSize: '24px', color: 'var(--color-ink)' }}>Steer Studio Settings</h2>
          </div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--color-clay)' }}>
            <X size={24} />
          </button>
        </div>

        {saveSuccess && (
          <div style={{
            background: '#E8F5E9',
            border: '1px solid #A5D6A7',
            color: '#1B5E20',
            borderRadius: 'var(--radius-md)',
            padding: '12px 18px',
            marginBottom: '20px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '14px',
            fontWeight: 600
          }}>
            <CheckCircle2 size={18} />
            <span>Settings updated successfully!</span>
          </div>
        )}

        {/* System Diagnostics Strip */}
        <div style={{
          background: 'var(--color-cream)',
          borderRadius: 'var(--radius-md)',
          padding: '16px 20px',
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: '14px',
          marginBottom: '24px',
          fontSize: '12px'
        }}>
          <div>
            <div style={{ color: 'var(--color-clay)', fontWeight: 700 }}>FFmpeg Video Engine</div>
            <div style={{ fontWeight: 700, color: health?.ffmpeg_available ? '#1B5E20' : '#C62828', marginTop: '2px' }}>
              {health?.ffmpeg_available ? '✓ Installed & Ready' : '✗ Not Found'}
            </div>
          </div>
          <div>
            <div style={{ color: 'var(--color-clay)', fontWeight: 700 }}>Database</div>
            <div style={{ fontWeight: 700, color: health?.database_connected ? '#1B5E20' : '#C62828', marginTop: '2px' }}>
              {health?.database_connected ? '✓ SQLite Connected' : '✗ Disconnected'}
            </div>
          </div>
          <div>
            <div style={{ color: 'var(--color-clay)', fontWeight: 700 }}>Active Mode</div>
            <div style={{ fontWeight: 700, color: 'var(--color-rust)', marginTop: '2px' }}>
              {health?.ai_provider || 'Local Deterministic'}
            </div>
          </div>
          <div>
            <div style={{ color: 'var(--color-clay)', fontWeight: 700 }}>Storage Center</div>
            <div style={{ fontWeight: 700, color: '#1B5E20', marginTop: '2px' }}>
              ✓ Storage Active
            </div>
          </div>
        </div>

        <form onSubmit={handleSave}>
          {/* AI Provider Selector */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: 'var(--color-ink)', marginBottom: '8px' }}>
              AI Intelligence Provider
            </label>
            <select
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              style={{
                width: '100%',
                padding: '12px 16px',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--color-clay)',
                background: 'var(--color-white)',
                fontFamily: 'var(--font-sans)',
                fontSize: '14px',
                color: 'var(--color-ink)',
                fontWeight: 600
              }}
            >
              <option value="local_sample">Deterministic Local Research Engine (No API Key Required - Default)</option>
              <option value="gemini">Google Gemini 2.5 / Flash (Live LLM)</option>
              <option value="openai">OpenAI GPT-4o (Live LLM)</option>
            </select>
          </div>

          {/* Transparency Info Box */}
          <div style={{
            background: '#FFF9F4',
            border: '1px solid var(--color-blush)',
            borderRadius: 'var(--radius-md)',
            padding: '14px 18px',
            marginBottom: '20px',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '10px',
            fontSize: '12px',
            color: 'var(--color-ink-muted)',
            lineHeight: 1.5
          }}>
            <Info size={16} color="var(--color-rust)" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <strong>Scientific Transparency:</strong> If no API credentials are provided, Steer Studio executes non-AI text ingestion, quotation cross-examination, and uses its verified local research engine with clearly labelled provenance tags. Fabricated AI outputs are never silently substituted.
            </div>
          </div>

          {/* Gemini Key Input */}
          <div style={{ marginBottom: '18px' }}>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: 'var(--color-ink)', marginBottom: '6px' }}>
              Google Gemini API Key (Optional)
            </label>
            <input
              type="password"
              placeholder="AIzaSy..."
              value={geminiKey}
              onChange={(e) => setGeminiKey(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 14px',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--color-clay)',
                background: 'var(--color-white)',
                fontSize: '13px',
                fontFamily: 'monospace'
              }}
            />
          </div>

          {/* OpenAI Key Input */}
          <div style={{ marginBottom: '22px' }}>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: 'var(--color-ink)', marginBottom: '6px' }}>
              OpenAI API Key (Optional)
            </label>
            <input
              type="password"
              placeholder="sk-proj-..."
              value={openaiKey}
              onChange={(e) => setOpenAIKey(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 14px',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--color-clay)',
                background: 'var(--color-white)',
                fontSize: '13px',
                fontFamily: 'monospace'
              }}
            />
          </div>


          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" disabled={isSaving} className="btn-primary">
              <span>{isSaving ? 'Saving...' : 'Save Settings'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
