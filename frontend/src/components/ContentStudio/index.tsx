import React, { useState } from 'react';
import { Layers, Image as ImageIcon, Video, MessageSquare, BookOpen, Presentation } from 'lucide-react';
import { Project, ContentDraft } from '../../types';
import { CarouselTab } from './CarouselTab';
import { StaticPostTab } from './StaticPostTab';
import { VideoReelTab } from './VideoReelTab';
import { CaptionsTab } from './CaptionsTab';
import { ReferencesTab } from './ReferencesTab';
import { PowerPointTab } from './PowerPointTab';

interface ContentStudioProps {
  project: Project;
  draft: ContentDraft | null;
  onRefresh: () => void;
}

export const ContentStudio: React.FC<ContentStudioProps> = ({
  project,
  draft,
  onRefresh,
}) => {
  const [activeTab, setActiveTab] = useState<'carousel' | 'static' | 'reel' | 'powerpoint' | 'captions' | 'references'>('carousel');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      {/* Studio Tab Bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        background: 'var(--color-cream)',
        padding: '6px',
        borderRadius: 'var(--radius-lg)',
        border: '1px solid var(--color-card-border)',
        overflowX: 'auto'
      }}>
        <button
          onClick={() => setActiveTab('carousel')}
          className={`steer-tab-btn ${activeTab === 'carousel' ? 'active' : ''}`}
        >
          <Layers size={17} />
          <span>Instagram Carousel</span>
        </button>

        <button
          onClick={() => setActiveTab('static')}
          className={`steer-tab-btn ${activeTab === 'static' ? 'active' : ''}`}
        >
          <ImageIcon size={17} />
          <span>Static Image Post</span>
        </button>

        <button
          onClick={() => setActiveTab('reel')}
          className={`steer-tab-btn ${activeTab === 'reel' ? 'active' : ''}`}
        >
          <Video size={17} />
          <span>AI-Assisted Video Reel</span>
        </button>

        <button
          onClick={() => setActiveTab('powerpoint')}
          className={`steer-tab-btn ${activeTab === 'powerpoint' ? 'active' : ''}`}
        >
          <Presentation size={17} />
          <span>PowerPoint Studio</span>
          <span className="badge-tag badge-rust" style={{ fontSize: '9px', padding: '2px 5px', marginLeft: '4px' }}>PPTX</span>
        </button>

        <button
          onClick={() => setActiveTab('captions')}
          className={`steer-tab-btn ${activeTab === 'captions' ? 'active' : ''}`}
        >
          <MessageSquare size={17} />
          <span>Caption & Hashtags</span>
        </button>

        <button
          onClick={() => setActiveTab('references')}
          className={`steer-tab-btn ${activeTab === 'references' ? 'active' : ''}`}
        >
          <BookOpen size={17} />
          <span>Source References</span>
        </button>
      </div>

      {/* Tab Content Display */}
      <div>
        {activeTab === 'carousel' && (
          <CarouselTab project={project} draft={draft} onRefresh={onRefresh} />
        )}
        {activeTab === 'static' && (
          <StaticPostTab project={project} draft={draft} onRefresh={onRefresh} />
        )}
        {activeTab === 'reel' && (
          <VideoReelTab project={project} draft={draft} onRefresh={onRefresh} />
        )}
        {activeTab === 'powerpoint' && (
          <PowerPointTab project={project} draft={draft} onRefresh={onRefresh} />
        )}
        {activeTab === 'captions' && (
          <CaptionsTab draft={draft} />
        )}
        {activeTab === 'references' && (
          <ReferencesTab project={project} />
        )}
      </div>
    </div>
  );
};
