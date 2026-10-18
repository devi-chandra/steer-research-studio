import React, { useState, useEffect } from 'react';
import {
  Settings,
  Cpu,
  Volume2,
  Video,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  Play,
  Languages,
  Palette,
  HardDrive
} from 'lucide-react';
import { api } from '../services/api';
import { SystemStatus } from '../types';

export const SettingsPage: React.FC = () => {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [testingLang, setTestingLang] = useState<string | null>(null);
  const [audioResult, setAudioResult] = useState<any | null>(null);

  const fetchStatus = async () => {
    try {
      const res = await api.getStatus();
      setStatus(res);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleTestVoice = async (langCode: string) => {
    setTestingLang(langCode);
    setAudioResult(null);
    try {
      const res = await api.testTtsVoice(langCode);
      setAudioResult(res);
    } catch (err: any) {
      alert('Voice test error: ' + err.message);
    } finally {
      setTestingLang(null);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-1.5 text-xs font-bold text-[#C04E2A] uppercase tracking-wider mb-1">
          <Settings className="w-3.5 h-3.5" />
          System Health & Provider Architecture
        </div>
        <h1 className="font-serif text-3xl font-bold text-[#661414]">
          Settings & Provider Status
        </h1>
        <p className="text-xs text-[#351D1D]/75">
          Inspect configured LLM providers, TTS speech engines, FFmpeg video encoders, and storage directories.
        </p>
      </div>

      {/* AI Provider Status Card */}
      <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#661414]/10 text-[#661414] flex items-center justify-center">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <h2 className="font-serif font-bold text-lg text-[#661414]">
                AI Provider Abstraction
              </h2>
              <div className="text-xs text-[#351D1D]/70">
                Grounding & Schema Enforcement Layer
              </div>
            </div>
          </div>

          <span className="bg-emerald-50 text-emerald-800 border border-emerald-300 text-xs font-bold px-3 py-1 rounded-full">
            Active: {status?.ai_provider?.active_provider.toUpperCase()}
          </span>
        </div>

        <div className="p-4 bg-[#F8F2EB] rounded-xl border border-[#E6CBBD] space-y-2 text-xs text-[#351D1D]">
          <div className="font-bold text-[#661414]">Status & Disclosure:</div>
          <p className="leading-relaxed">
            {status?.ai_provider?.status_label}. The application enforces strict structured JSON schemas and never fabricates research findings. When no external LLM API key is detected, the verified deterministic text extraction engine guarantees zero hallucination.
          </p>
          <div className="pt-2 flex items-center gap-6 font-mono text-[11px] text-[#B58777]">
            <span>Google Gemini Key: <strong>{status?.ai_provider?.has_gemini_key ? 'Configured' : 'Not configured (using fallback)'}</strong></span>
            <span>OpenAI Key: <strong>{status?.ai_provider?.has_openai_key ? 'Configured' : 'Not configured (using fallback)'}</strong></span>
          </div>
        </div>
      </div>

      {/* Video & FFmpeg Engine Status */}
      <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#C04E2A]/10 text-[#C04E2A] flex items-center justify-center">
              <Video className="w-5 h-5" />
            </div>
            <div>
              <h2 className="font-serif font-bold text-lg text-[#661414]">
                FFmpeg Video Encoding Engine
              </h2>
              <div className="text-xs text-[#351D1D]/70">
                Hardware & Software H.264 / AAC Video Pipeline
              </div>
            </div>
          </div>

          <span className={`text-xs font-bold px-3 py-1 rounded-full border ${
            status?.ffmpeg_available
              ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
              : 'bg-rose-50 text-rose-800 border-rose-300'
          }`}>
            {status?.ffmpeg_available ? 'OPERATIONAL' : 'NOT DETECTED'}
          </span>
        </div>

        <div className="p-4 bg-[#F8F2EB] rounded-xl border border-[#E6CBBD] text-xs space-y-1 font-mono text-[#351D1D]">
          <div><strong>Engine Path:</strong> {status?.ffmpeg_path}</div>
          <div><strong>Capabilities:</strong> 1080 × 1920 vertical reel encoding, multi-scene concatenation, audio multiplexing.</div>
        </div>
      </div>

      {/* LocalVoice TTS Engine & Live Voice Tester */}
      <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#661414]/10 text-[#661414] flex items-center justify-center">
              <Languages className="w-5 h-5" />
            </div>
            <div>
              <h2 className="font-serif font-bold text-lg text-[#661414]">
                LocalVoice Speech Synthesis Matrix (6 Languages)
              </h2>
              <div className="text-xs text-[#351D1D]/70">
                Neural Voice Generation for Regional Health Reels
              </div>
            </div>
          </div>

          <span className="bg-[#F5EBDF] text-[#661414] border border-[#B58777] text-xs font-bold px-3 py-1 rounded-full">
            TTS Provider: {status?.tts_provider?.toUpperCase()}
          </span>
        </div>

        <div className="p-3 bg-amber-50/80 border border-amber-300 rounded-xl text-xs text-amber-950">
          <strong>Translation Provider Status:</strong> Regional neural voice synthesis (TTS) is active for accents/intonation, but no text translation provider is configured. Narration and subtitles remain in verified source English.
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {status?.supported_languages?.map((lang) => (
            <div
              key={lang.code}
              className="p-3 bg-[#F8F2EB] border border-[#E6CBBD] rounded-xl flex items-center justify-between text-xs"
            >
              <div>
                <div className="font-bold text-[#351D1D]">{lang.label}</div>
                <div className="text-[11px] font-mono text-[#B58777]">{lang.tts_voice}</div>
              </div>

              <button
                onClick={() => handleTestVoice(lang.code)}
                disabled={testingLang === lang.code}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#661414] text-[#F5EBDF] text-xs font-bold hover:bg-[#351D1D] transition"
              >
                <Volume2 className="w-3.5 h-3.5" />
                {testingLang === lang.code ? 'Testing...' : 'Test Voice'}
              </button>
            </div>
          ))}
        </div>

        {audioResult && (
          <div className="p-4 bg-emerald-50 border border-emerald-300 rounded-xl text-xs space-y-2 text-emerald-950">
            <div className="font-bold flex items-center gap-2 text-emerald-900">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              Verified Audio for {audioResult.language_code.toUpperCase()} ({audioResult.provider_used})
            </div>
            <div className="italic text-emerald-800">"{audioResult.test_phrase}"</div>
            {audioResult.audio_url && (
              <audio controls autoPlay src={audioResult.audio_url} className="h-8 max-w-sm mt-2" />
            )}
          </div>
        )}
      </div>

      {/* Steer Brand Identity Tokens */}
      <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-6 shadow-xs space-y-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#661414]/10 text-[#661414] flex items-center justify-center">
            <Palette className="w-5 h-5" />
          </div>
          <div>
            <h2 className="font-serif font-bold text-lg text-[#661414]">
              Steer Brand Identity Palette
            </h2>
            <div className="text-xs text-[#351D1D]/70">
              Curated Medical Editorial Aesthetic Colors
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-7 gap-3 text-center text-xs">
          {[
            { name: 'Cream', hex: '#F5EBDF', text: 'text-[#351D1D]' },
            { name: 'Rust', hex: '#C04E2A', text: 'text-white' },
            { name: 'Deep Maroon', hex: '#661414', text: 'text-white' },
            { name: 'Ink', hex: '#351D1D', text: 'text-white' },
            { name: 'Clay', hex: '#B58777', text: 'text-white' },
            { name: 'Blush', hex: '#E6CBBD', text: 'text-[#351D1D]' },
            { name: 'Soft Paper', hex: '#F8F2EB', text: 'text-[#351D1D]' },
          ].map((c) => (
            <div key={c.name} className="space-y-1">
              <div
                style={{ backgroundColor: c.hex }}
                className={`h-14 rounded-xl flex items-center justify-center font-mono font-bold text-[11px] border border-[#E6CBBD] shadow-xs ${c.text}`}
              >
                {c.hex}
              </div>
              <div className="font-medium text-[#351D1D] text-[11px]">{c.name}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
