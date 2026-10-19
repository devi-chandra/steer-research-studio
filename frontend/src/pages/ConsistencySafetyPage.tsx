import React, { useState, useEffect } from 'react';
import {
  AlertTriangle,
  ShieldCheck,
  CheckCircle2,
  RefreshCw,
  Layers,
  ArrowRight,
  Info,
  XCircle,
  FileCheck2
} from 'lucide-react';
import { api } from '../services/api';
import { Project, ConsistencyCheck } from '../types';
import { NavItem } from '../components/Sidebar';

interface ConsistencySafetyPageProps {
  currentProject: Project | null;
  onNavigate: (tab: NavItem) => void;
}

export const ConsistencySafetyPage: React.FC<ConsistencySafetyPageProps> = ({ currentProject, onNavigate }) => {
  const [checks, setChecks] = useState<ConsistencyCheck[]>([]);
  const [criticalCount, setCriticalCount] = useState(0);
  const [isReady, setIsReady] = useState<boolean | null>(null);
  const [hasScanned, setHasScanned] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [scanMessage, setScanMessage] = useState<string | null>(null);

  const fetchChecks = async () => {
    if (!currentProject) return;
    try {
      const res = await api.getConsistencyChecks(currentProject.id);
      setChecks(res.checks);
      setCriticalCount(res.critical_count);
      setIsReady(res.is_publication_ready);
      setHasScanned(res.total > 0);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchChecks();
  }, [currentProject?.id]);

  const handleRunScan = async () => {
    if (!currentProject) return;
    setIsLoading(true);
    setScanMessage(null);
    try {
      const res = await api.checkConsistency(currentProject.id);
      setChecks(res.results.discrepancies);
      setCriticalCount(res.results.critical_issues);
      setIsReady(res.results.is_publication_ready);
      setHasScanned(true);
      setScanMessage(`Scan complete: ${res.results.total_discrepancies_found} potential flags assessed across 5 formats.`);
    } catch (err: any) {
      setScanMessage('Consistency scan failed: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  if (!currentProject) {
    return (
      <div className="p-12 text-center max-w-xl mx-auto space-y-4">
        <h2 className="font-serif text-2xl font-bold text-[#661414]">No Project Selected</h2>
        <p className="text-sm text-[#351D1D]/70">
          Select a project to verify factual consistency across Carousel, Post, Reels, and PowerPoint.
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

  return (
    <div className="workspace-page max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-bold text-[#C04E2A] uppercase tracking-wider mb-1">
            <ShieldCheck className="w-3.5 h-3.5" />
            Automated quality check
          </div>
          <h1 className="font-serif text-3xl font-bold text-[#661414]">
            Check content consistency
          </h1>
          <p className="text-xs text-[#351D1D]/75">
            Compare numbers, units and limitations across generated formats. This checks consistency—not scientific truth or clinician approval.
          </p>
        </div>

        <button
          onClick={handleRunScan}
          disabled={isLoading}
          className="flex items-center gap-1.5 px-5 py-2.5 rounded-xl bg-[#661414] text-[#F5EBDF] text-xs font-bold hover:bg-[#351D1D] shadow transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          {isLoading ? 'Checking your content…' : 'Run consistency check'}
        </button>
      </div>

      {scanMessage && (
        <div role="status" className={`${scanMessage.startsWith('Consistency scan failed') ? 'bg-rose-50 border-rose-300 text-rose-900' : 'bg-emerald-50 border-emerald-300 text-emerald-900'} border p-4 rounded-xl text-xs flex items-center gap-2`}>
          {scanMessage.startsWith('Consistency scan failed')
            ? <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
            : <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />}
          <span>{scanMessage}</span>
        </div>
      )}

      {/* Safety Gate Status Banner */}
      <div className={`p-6 rounded-2xl border shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4 ${
        !hasScanned ? 'bg-sky-50/70 border-sky-200' : isReady ? 'bg-emerald-50/70 border-emerald-200' : 'bg-rose-50/70 border-rose-300'
      }`}>
        <div className="flex items-center gap-4">
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
            !hasScanned ? 'bg-sky-100 text-sky-800' : isReady ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
          }`}>
            {!hasScanned ? <Info className="w-7 h-7" /> : isReady ? <ShieldCheck className="w-7 h-7" /> : <AlertTriangle className="w-7 h-7" />}
          </div>
          <div>
            <h3 className={`font-serif text-lg font-bold ${!hasScanned ? 'text-sky-950' : isReady ? 'text-emerald-950' : 'text-rose-950'}`}>
              {!hasScanned ? 'Consistency check not run yet' : isReady ? 'No critical inconsistencies found' : 'Critical inconsistencies need review'}
            </h3>
            <p className="text-xs text-[#351D1D]/80 mt-0.5">
              {!hasScanned
                ? 'Run the check to compare generated outputs. A clear scan is not medical approval.'
                : isReady
                  ? 'Review any warnings and get qualified human approval before publication.'
                  : `${criticalCount} critical ${criticalCount === 1 ? 'issue needs' : 'issues need'} review before relying on these outputs.`}
            </p>
          </div>
        </div>

        <button
          onClick={() => {
            if (!hasScanned) handleRunScan();
            else if (isReady) onNavigate('export_center');
            else document.getElementById('integrity-checks')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }}
          disabled={isLoading}
          className="px-5 py-2.5 rounded-xl text-xs font-bold shadow transition flex items-center gap-1.5 bg-[#661414] text-[#F5EBDF] hover:bg-[#351D1D] disabled:opacity-60"
        >
          {!hasScanned ? 'Run check now' : isReady ? 'Continue to exports' : 'Review flagged issues'}
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Discrepancies List */}
      <div id="integrity-checks" className="space-y-4">
        <h3 className="font-serif text-lg font-bold text-[#661414]">
          Check results ({checks.length})
        </h3>

        {checks.length === 0 ? (
          <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-10 text-center space-y-2">
            {hasScanned ? <CheckCircle2 className="w-8 h-8 text-emerald-600 mx-auto" /> : <Info className="w-8 h-8 text-sky-600 mx-auto" />}
            <h4 className="font-serif font-bold text-base text-[#351D1D]">{hasScanned ? 'No inconsistencies flagged' : 'Run the check to see results'}</h4>
            <p className="text-xs text-[#B58777]">
              {hasScanned
                ? 'The scan found no stored discrepancies in the generated outputs. This does not confirm the claims are true or clinically approved.'
                : 'The scan compares available numbers, units and limitations across the generated formats.'}
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {checks.map((chk, idx) => (
              <div
                key={chk.id || idx}
                className={`p-5 rounded-2xl border bg-white shadow-xs space-y-2.5 ${
                  chk.severity === 'critical'
                    ? 'border-rose-300 bg-rose-50/20'
                    : 'border-amber-300 bg-amber-50/20'
                }`}
              >
                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <span className={`font-bold uppercase tracking-wider px-2 py-0.5 rounded text-[10px] ${
                      chk.severity === 'critical' ? 'bg-rose-100 text-rose-800' : 'bg-amber-100 text-amber-800'
                    }`}>
                      {chk.severity.toUpperCase()} ALERT
                    </span>
                    <span className="font-mono font-bold text-[#661414]">{chk.check_type}</span>
                  </div>
                  <span className="text-[#B58777] font-mono text-[11px]">
                    Grounding: {chk.source_claim_id}
                  </span>
                </div>

                <div className="font-semibold text-sm text-[#351D1D]">
                  {chk.discrepancy_explanation}
                </div>

                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[#B58777]">Affected Deliverables:</span>
                  <div className="flex gap-1.5">
                    {chk.affected_assets?.map((a, i) => (
                      <span key={i} className="bg-[#F5EBDF] text-[#661414] font-medium px-2 py-0.5 rounded">
                        {a}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="p-3 bg-[#F8F2EB] rounded-xl border border-[#E6CBBD] text-xs text-[#351D1D] space-y-1">
                  <div className="font-bold text-[#C04E2A] flex items-center gap-1.5">
                    <Info className="w-3.5 h-3.5" />
                    Recommended Remediation
                  </div>
                  <p>{chk.suggestion}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
