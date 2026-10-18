import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { Sidebar, NavItem } from './components/Sidebar';
import { DashboardPage } from './pages/DashboardPage';
import { NewResearchPage } from './pages/NewResearchPage';
import { EvidenceLedgerPage } from './pages/EvidenceLedgerPage';
import { ContentStudioPage } from './pages/ContentStudioPage';
import { PowerPointStudioPage } from './pages/PowerPointStudioPage';
import { ReviewGatePage } from './pages/ReviewGatePage';
import { ConsistencySafetyPage } from './pages/ConsistencySafetyPage';
import { ExportCenterPage } from './pages/ExportCenterPage';
import { SettingsPage } from './pages/SettingsPage';
import { api } from './services/api';
import { Project, SystemStatus } from './types';

export function App() {
  const [currentTab, setCurrentTab] = useState<NavItem>('dashboard');
  const [projects, setProjects] = useState<Project[]>([]);
  const [currentProject, setCurrentProject] = useState<Project | null>(null);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [criticalIssuesCount, setCriticalIssuesCount] = useState<number>(0);

  const loadProjects = async () => {
    try {
      const res = await api.getProjects();
      setProjects(res.projects);
      if (res.projects.length > 0 && !currentProject) {
        setCurrentProject(res.projects[0]);
      }
    } catch (err) {
      console.error('Failed to load projects:', err);
    }
  };

  const loadSystemStatus = async () => {
    try {
      const res = await api.getStatus();
      setSystemStatus(res);
    } catch (err) {
      console.error('Failed to load system status:', err);
    }
  };

  const loadConsistency = async (projectId: string) => {
    try {
      const res = await api.getConsistencyChecks(projectId);
      setCriticalIssuesCount(res.critical_count);
    } catch (err) {
      console.error('Failed to load consistency:', err);
    }
  };

  useEffect(() => {
    loadProjects();
    loadSystemStatus();
  }, []);

  useEffect(() => {
    if (currentProject) {
      loadConsistency(currentProject.id);
    }
  }, [currentProject?.id]);

  const handleProjectCreated = (newProj: Project) => {
    setProjects([newProj, ...projects]);
    setCurrentProject(newProj);
    setCurrentTab('evidence_ledger');
  };

  return (
    <div className="min-h-screen bg-[#F8F2EB] text-[#351D1D] flex flex-col font-sans selection:bg-[#E6CBBD] selection:text-[#661414]">
      {/* Top Header */}
      <Header
        currentProject={currentProject}
        projects={projects}
        onSelectProject={(proj) => setCurrentProject(proj)}
        systemStatus={systemStatus}
      />

      {/* Main Body */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <Sidebar
          currentTab={currentTab}
          onSelectTab={(tab) => setCurrentTab(tab)}
          pendingReviewsCount={currentProject?.pending_reviews_count || 0}
          criticalIssuesCount={criticalIssuesCount}
        />

        {/* Dynamic Main Workspace */}
        <main className="flex-1 overflow-y-auto">
          {currentTab === 'dashboard' && (
            <DashboardPage
              projects={projects}
              currentProject={currentProject}
              onSelectProject={(p) => setCurrentProject(p)}
              onNavigate={(tab) => setCurrentTab(tab)}
            />
          )}

          {currentTab === 'new_research' && (
            <NewResearchPage
              onProjectCreated={handleProjectCreated}
              onNavigate={(tab) => setCurrentTab(tab)}
            />
          )}

          {currentTab === 'evidence_ledger' && (
            <EvidenceLedgerPage
              currentProject={currentProject}
              onNavigate={(tab) => setCurrentTab(tab)}
            />
          )}

          {currentTab === 'content_studio' && (
            <ContentStudioPage
              currentProject={currentProject}
              onNavigate={(tab) => setCurrentTab(tab)}
            />
          )}

          {currentTab === 'powerpoint_studio' && (
            <PowerPointStudioPage
              currentProject={currentProject}
              onNavigate={(tab) => setCurrentTab(tab)}
            />
          )}

          {currentTab === 'review_gate' && (
            <ReviewGatePage
              currentProject={currentProject}
              onNavigate={(tab) => setCurrentTab(tab)}
            />
          )}

          {currentTab === 'claim_safety' && (
            <ConsistencySafetyPage
              currentProject={currentProject}
              onNavigate={(tab) => setCurrentTab(tab)}
            />
          )}

          {currentTab === 'export_center' && (
            <ExportCenterPage
              currentProject={currentProject}
              onNavigate={(tab) => setCurrentTab(tab)}
            />
          )}

          {currentTab === 'settings' && <SettingsPage />}
        </main>
      </div>
    </div>
  );
}

export default App;
