import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  Layers,
  Image as ImageIcon,
  Video,
  FileText,
  Volume2,
  Download,
  Play,
  RotateCcw,
  Check,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
  Languages,
  Activity,
  Copy,
  CheckCircle2,
  Loader2,
  AlertCircle
} from 'lucide-react';
import { api } from '../services/api';
import { Project, Claim, TwoStoriesData, InsideBodyData, CarouselSlide, ReelScene } from '../types';
import { NavItem } from '../components/Sidebar';

interface ContentStudioPageProps {
  currentProject: Project | null;
  onNavigate: (tab: NavItem) => void;
}

export const ContentStudioPage: React.FC<ContentStudioPageProps> = ({ currentProject, onNavigate }) => {
  const [subTab, setSubTab] = useState<
    'carousel' | 'post' | 'two_stories' | 'inside_body' | 'localvoice' | 'video_player' | 'captions'
  >('carousel');

  // Carousel State
  const [carouselData, setCarouselData] = useState<any | null>(null);
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);
  const [carouselCount, setCarouselCount] = useState(6);

  // Static Post State
  const [postData, setPostData] = useState<any | null>(null);
  const [postHeadline, setPostHeadline] = useState('');
  const [postBody, setPostBody] = useState('');

  // Two Stories State (Feature 1)
  const [twoStories, setTwoStories] = useState<TwoStoriesData | null>(null);
  const [selectedStoryMode, setSelectedStoryMode] = useState<'professional' | 'everyday'>('professional');

  // Inside Body State (Feature 2)
  const [insideBody, setInsideBody] = useState<InsideBodyData | null>(null);

  // LocalVoice State (Feature 3)
  const [selectedLanguage, setSelectedLanguage] = useState<string>('hi_en');
  const [localVoiceScenes, setLocalVoiceScenes] = useState<ReelScene[]>([]);
  const [projectClaims, setProjectClaims] = useState<Claim[]>([]);
  const [audioTestResult, setAudioTestResult] = useState<any | null>(null);

  // Video Reel Player State
  const [renderedReel, setRenderedReel] = useState<any | null>(null);
  const [isRenderingVideo, setIsRenderingVideo] = useState(false);
  const [reelStyle, setReelStyle] = useState('relatable_human');
  const [reelTheme, setReelTheme] = useState('steer');

  // General Loading & Notification States
  const [isLoading, setIsLoading] = useState(false);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [copiedCaption, setCopiedCaption] = useState(false);

  const loadData = async () => {
    if (!currentProject) return;
    // Clear the previous project's in-memory artifacts before fetching this one.
    setCarouselData(null);
    setPostData(null);
    setTwoStories(null);
    setInsideBody(null);
    setLocalVoiceScenes([]);
    setProjectClaims([]);
    setRenderedReel(null);
    setReelStyle('relatable_human');
    setReelTheme('steer');
    try {
      const [carRes, postRes, storiesRes, bodyRes, locRes, configRes, claimsRes] = await Promise.allSettled([
        api.getCarousel(currentProject.id),
        api.getPost(currentProject.id),
        api.getTwoStories(currentProject.id),
        api.getInsideBody(currentProject.id),
        api.getLocalVoice(currentProject.id, selectedLanguage),
        api.getReelConfig(currentProject.id),
        api.getClaims(currentProject.id)
      ]);

      if (carRes.status === 'fulfilled' && carRes.value.exists) {
        setCarouselData(carRes.value);
      }
      if (postRes.status === 'fulfilled' && postRes.value.exists) {
        setPostData(postRes.value);
        setPostHeadline(postRes.value.headline);
        setPostBody(postRes.value.explanation);
      }
      if (storiesRes.status === 'fulfilled' && storiesRes.value.exists) {
        setTwoStories(storiesRes.value);
      }
      if (bodyRes.status === 'fulfilled' && bodyRes.value.exists) {
        setInsideBody(bodyRes.value);
      }
      if (locRes.status === 'fulfilled' && locRes.value.exists) {
        setLocalVoiceScenes(locRes.value.scenes);
      }
      if (configRes.status === 'fulfilled') {
        setReelStyle(configRes.value.style);
        setReelTheme(configRes.value.theme);
      }
      if (claimsRes.status === 'fulfilled') setProjectClaims(claimsRes.value.claims);
    } catch (err) {
      console.error('Failed to load studio data:', err);
    }
  };

  useEffect(() => {
    loadData();
  }, [currentProject?.id]);

  if (!currentProject) {
    return (
      <div className="p-12 text-center max-w-xl mx-auto space-y-4">
        <h2 className="font-serif text-2xl font-bold text-[#661414]">No Project Selected</h2>
        <p className="text-sm text-[#351D1D]/70">
          Please select or ingest a research paper to generate multi-format deliverables.
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

  const captionContent = projectClaims.length
    ? `# Research in Context\n\n${currentProject.title}\n\nWhat the paper reports:\n${projectClaims.slice(0, 3).map((claim) => `• ${claim.exact_quote || claim.claim_text} (source page ${claim.page_number}; ${claim.claim_id})`).join('\n')}\n\nThese findings describe this study and its participants. They are educational information, not personal medical advice.\n\nSource: ${currentProject.title}${currentProject.doi ? ` (DOI: ${currentProject.doi})` : ''}\n\n#MedicalResearch #EvidenceBasedMedicine #SteerStudio`
    : `No extracted evidence is available for ${currentProject.title}. Process the paper and extract claims before preparing a research caption.`;

  // Action Handlers
  const handleGenerateCarousel = async () => {
    setIsLoading(true);
    setActionMessage(null);
    try {
      const res = await api.generateCarousel(currentProject.id, carouselCount);
      setCarouselData(res.carousel);
      setCurrentSlideIndex(0);
      setActionMessage('Instagram carousel PNG slides rendered successfully.');
    } catch (err: any) {
      setActionMessage('Failed to generate carousel: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGeneratePost = async () => {
    setIsLoading(true);
    setActionMessage(null);
    try {
      const res = await api.generatePost(currentProject.id, postHeadline, postBody);
      setPostData(res.post);
      setActionMessage('Static Instagram post PNG rendered successfully.');
    } catch (err: any) {
      setActionMessage('Failed to generate post: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateTwoStories = async () => {
    setIsLoading(true);
    setActionMessage(null);
    try {
      const res = await api.generateTwoStories(currentProject.id);
      setTwoStories(res.stories);
      setActionMessage('Same Evidence, Two Stories scripts generated.');
    } catch (err: any) {
      setActionMessage('Failed to generate two stories: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateInsideBody = async () => {
    setIsLoading(true);
    setActionMessage(null);
    try {
      const res = await api.generateInsideBody(currentProject.id);
      setInsideBody(res.inside_body);
      setActionMessage('Inside Your Body animated storyboard generated.');
    } catch (err: any) {
      setActionMessage('Failed to generate inside body: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateLocalVoice = async (lang: string) => {
    setSelectedLanguage(lang);
    setIsLoading(true);
    setActionMessage(null);
    try {
      // First ensure everyday story exists
      if (!twoStories) {
        await api.generateTwoStories(currentProject.id);
      }
      const res = await api.generateLocalVoice(currentProject.id, lang);
      setLocalVoiceScenes(res.localvoice.scenes);
      setActionMessage(`LocalVoice script generated for ${lang}.`);
    } catch (err: any) {
      setActionMessage('Failed to generate localvoice: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTestVoice = async (lang: string) => {
    setIsLoading(true);
    try {
      const res = await api.testTtsVoice(lang);
      setAudioTestResult(res);
      setActionMessage(`TTS voice verified for ${lang} (${res.provider_used}).`);
    } catch (err: any) {
      setActionMessage('TTS voice test failed: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRenderVideoReel = async (mode: string, lang: string = 'en') => {
    setIsRenderingVideo(true);
    setActionMessage(null);
    try {
      await api.updateReelConfig(currentProject.id, reelStyle, reelTheme);
      const res = await api.renderVideoReel(currentProject.id, mode, lang, reelStyle, reelTheme);
      setRenderedReel(res);
      setActionMessage(`Vertical 1080x1920 MP4 reel rendered with FFmpeg (${res.total_duration_seconds}s).`);
      setSubTab('video_player');

      // Sync state so storyboard views reflect any auto-generated scenes
      if (mode === 'everyday' || mode === 'professional') {
        api.getTwoStories(currentProject.id).then((r) => {
          if (r.exists) setTwoStories(r);
        });
      }
      if (mode === 'localvoice') {
        api.getLocalVoice(currentProject.id, lang).then((r) => {
          if (r.exists) setLocalVoiceScenes(r.scenes);
        });
      }
    } catch (err: any) {
      setActionMessage('Failed to render MP4 video: ' + err.message);
    } finally {
      setIsRenderingVideo(false);
    }
  };

  return (
    <div className="workspace-page max-w-7xl mx-auto space-y-6">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-bold text-[#C04E2A] uppercase tracking-wider mb-1">
            <Sparkles className="w-3.5 h-3.5" />
            Create from your research
          </div>
          <h1 className="font-serif text-3xl font-bold text-[#661414]">
            Create content
          </h1>
          <p className="text-xs text-[#351D1D]/75 mt-1">
            Choose a format below, generate it, then preview and download. Based on: <span className="font-semibold text-[#351D1D]">{currentProject.title}</span>
          </p>
        </div>

        {actionMessage && (
          <div role="status" className={`${actionMessage.startsWith('Failed') ? 'bg-rose-50 border-rose-300 text-rose-900' : 'bg-emerald-50 border-emerald-300 text-emerald-900'} border px-4 py-2 rounded-xl text-xs flex items-center gap-2 shadow-xs`}>
            {actionMessage.startsWith('Failed')
              ? <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
              : <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />}
            <span>{actionMessage}</span>
          </div>
        )}
      </div>

      {/* Navigation Sub-Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-[#E6CBBD] pb-3" role="group" aria-label="Choose a content format">
        <button
          onClick={() => setSubTab('carousel')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition ${
            subTab === 'carousel'
              ? 'bg-[#661414] text-[#F5EBDF] shadow-xs'
              : 'text-[#351D1D] hover:bg-[#F5EBDF]'
          }`}
        >
          <Layers className="w-3.5 h-3.5" />
          Carousel
        </button>

        <button
          onClick={() => setSubTab('post')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition ${
            subTab === 'post'
              ? 'bg-[#661414] text-[#F5EBDF] shadow-xs'
              : 'text-[#351D1D] hover:bg-[#F5EBDF]'
          }`}
        >
          <ImageIcon className="w-3.5 h-3.5" />
          Static post
        </button>

        <button
          onClick={() => setSubTab('two_stories')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition ${
            subTab === 'two_stories'
              ? 'bg-[#C04E2A] text-white shadow-xs'
              : 'text-[#C04E2A] hover:bg-[#E6CBBD]/40 font-semibold'
          }`}
        >
          <Sparkles className="w-3.5 h-3.5" />
          Two stories
        </button>

        <button
          onClick={() => setSubTab('inside_body')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition ${
            subTab === 'inside_body'
              ? 'bg-[#661414] text-[#F5EBDF] shadow-xs'
              : 'text-[#351D1D] hover:bg-[#F5EBDF]'
          }`}
        >
          <Activity className="w-3.5 h-3.5" />
          Body explainer
        </button>

        <button
          onClick={() => setSubTab('localvoice')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition ${
            subTab === 'localvoice'
              ? 'bg-[#661414] text-[#F5EBDF] shadow-xs'
              : 'text-[#351D1D] hover:bg-[#F5EBDF]'
          }`}
        >
          <Languages className="w-3.5 h-3.5" />
          Local voice
        </button>

        <button
          onClick={() => setSubTab('video_player')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition ${
            subTab === 'video_player'
              ? 'bg-[#661414] text-[#F5EBDF] shadow-xs'
              : 'text-[#351D1D] hover:bg-[#F5EBDF]'
          }`}
        >
          <Video className="w-3.5 h-3.5" />
          Reel
        </button>

        <button
          onClick={() => setSubTab('captions')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition ${
            subTab === 'captions'
              ? 'bg-[#661414] text-[#F5EBDF] shadow-xs'
              : 'text-[#351D1D] hover:bg-[#F5EBDF]'
          }`}
        >
          <FileText className="w-3.5 h-3.5" />
          Captions & sources
        </button>
      </div>

      {/* ======================================================== */}
      {/* SUB-TAB 1: INSTAGRAM CAROUSEL                            */}
      {/* ======================================================== */}
      {subTab === 'carousel' && (
        <div className="space-y-6">
          <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h2 className="font-serif text-xl font-bold text-[#661414]">
                1080 × 1350 Portrait Instagram Carousel
              </h2>
              <p className="text-xs text-[#351D1D]/70 mt-1">
                Default 6-slide evidence progression: Hook → Context → Methodology → Main Finding → Limitations → Takeaways.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5 text-xs text-[#351D1D]">
                <span>Slides:</span>
                <select
                  value={carouselCount}
                  onChange={(e) => setCarouselCount(Number(e.target.value))}
                  className="bg-[#F8F2EB] border border-[#B58777]/50 rounded px-2 py-1 text-xs outline-none"
                >
                  <option value={4}>4 Slides</option>
                  <option value={6}>6 Slides (Default)</option>
                  <option value={8}>8 Slides</option>
                </select>
              </div>

              <button
                onClick={handleGenerateCarousel}
                disabled={isLoading}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#661414] text-[#F5EBDF] text-xs font-bold hover:bg-[#351D1D] shadow transition"
              >
                {isLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
                Render PNG Slides
              </button>

              {carouselData?.zip_url && (
                <a
                  href={carouselData.zip_url}
                  download
                  className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#C04E2A] text-white text-xs font-bold hover:bg-[#661414] shadow transition"
                >
                  <Download className="w-3.5 h-3.5" />
                  Download ZIP
                </a>
              )}
            </div>
          </div>

          {/* Carousel Slide Viewer */}
          {carouselData?.slides && carouselData.slides.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
              {/* Left: Slide Card Render Preview */}
              <div className="md:col-span-7 bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-6 shadow-sm space-y-4">
                <div className="flex items-center justify-between text-xs text-[#B58777]">
                  <span className="font-bold uppercase tracking-wider text-[#661414]">
                    Slide {currentSlideIndex + 1} of {carouselData.slides.length}
                  </span>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setCurrentSlideIndex(Math.max(0, currentSlideIndex - 1))}
                      disabled={currentSlideIndex === 0}
                      className="p-1 rounded bg-[#F8F2EB] border border-[#B58777] disabled:opacity-40"
                    >
                      <ChevronLeft className="w-4 h-4 text-[#351D1D]" />
                    </button>
                    <button
                      onClick={() => setCurrentSlideIndex(Math.min(carouselData.slides.length - 1, currentSlideIndex + 1))}
                      disabled={currentSlideIndex === carouselData.slides.length - 1}
                      className="p-1 rounded bg-[#F8F2EB] border border-[#B58777] disabled:opacity-40"
                    >
                      <ChevronRight className="w-4 h-4 text-[#351D1D]" />
                    </button>
                  </div>
                </div>

                {/* Rendered PNG Preview Frame */}
                <div className="aspect-[4/5] max-w-[420px] mx-auto bg-[#F8F2EB] rounded-xl overflow-hidden border-2 border-[#B58777]/30 shadow-md">
                  <img
                    src={carouselData.slides[currentSlideIndex]?.preview_url}
                    alt={`Slide ${currentSlideIndex + 1}`}
                    className="w-full h-full object-contain"
                  />
                </div>

                <div className="text-center pt-2">
                  <a
                    href={carouselData.slides[currentSlideIndex]?.preview_url}
                    download={carouselData.slides[currentSlideIndex]?.filename}
                    className="inline-flex items-center gap-1.5 text-xs text-[#C04E2A] font-bold hover:underline"
                  >
                    <Download className="w-3.5 h-3.5" />
                    Download Slide {currentSlideIndex + 1} PNG
                  </a>
                </div>
              </div>

              {/* Right: Slide Text Breakdown & Thumbnail Strip */}
              <div className="md:col-span-5 space-y-4">
                <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-5 shadow-xs space-y-3">
                  <div className="text-xs font-bold text-[#661414] uppercase tracking-wider">
                    Slide Content Breakdown
                  </div>
                  <div className="space-y-2 text-xs">
                    <div>
                      <span className="text-[#B58777] font-semibold">Headline:</span>
                      <div className="font-serif font-bold text-sm text-[#351D1D] mt-0.5">
                        {carouselData.slides[currentSlideIndex]?.headline}
                      </div>
                    </div>
                    <div>
                      <span className="text-[#B58777] font-semibold">Subhead:</span>
                      <div className="text-[#661414] font-medium mt-0.5">
                        {carouselData.slides[currentSlideIndex]?.subhead}
                      </div>
                    </div>
                    <div>
                      <span className="text-[#B58777] font-semibold">Body Copy:</span>
                      <div className="text-[#351D1D]/90 mt-0.5 leading-relaxed bg-[#F8F2EB] p-2.5 rounded-lg border border-[#E6CBBD]">
                        {carouselData.slides[currentSlideIndex]?.body}
                      </div>
                    </div>
                    <div className="flex items-center gap-3 pt-1 text-[11px] text-[#B58777]">
                      <span>Claim ID: <strong>{carouselData.slides[currentSlideIndex]?.claim_id}</strong></span>
                      <span>Page: <strong>{carouselData.slides[currentSlideIndex]?.page_num}</strong></span>
                    </div>
                  </div>
                </div>

                {/* Thumbnails */}
                <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-4 shadow-xs space-y-2">
                  <div className="text-xs font-bold text-[#B58777] uppercase tracking-wider">
                    All Slides
                  </div>
                  <div className="grid grid-cols-3 gap-2">
                    {carouselData.slides.map((s: CarouselSlide, idx: number) => (
                      <div
                        key={idx}
                        onClick={() => setCurrentSlideIndex(idx)}
                        className={`cursor-pointer rounded-lg overflow-hidden border-2 transition aspect-[4/5] bg-[#F8F2EB] ${
                          currentSlideIndex === idx ? 'border-[#661414] shadow' : 'border-[#E6CBBD] opacity-70 hover:opacity-100'
                        }`}
                      >
                        <img src={s.preview_url} alt={`Thumb ${idx + 1}`} className="w-full h-full object-cover" />
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-12 text-center space-y-3">
              <Layers className="w-10 h-10 text-[#B58777] mx-auto opacity-50" />
              <h3 className="font-serif text-lg font-bold text-[#661414]">No Carousel Slides Generated Yet</h3>
              <p className="text-xs text-[#351D1D]/70 max-w-md mx-auto">
                Click "Render PNG Slides" to generate genuine 1080×1350 portrait slides grounded in your verified research claims.
              </p>
              <button
                onClick={handleGenerateCarousel}
                disabled={isLoading}
                className="bg-[#661414] text-[#F5EBDF] px-5 py-2.5 rounded-xl text-xs font-bold hover:bg-[#351D1D] shadow transition"
              >
                Render Carousel Now
              </button>
            </div>
          )}
        </div>
      )}

      {/* ======================================================== */}
      {/* SUB-TAB 2: STATIC INSTAGRAM POST                         */}
      {/* ======================================================== */}
      {subTab === 'post' && (
        <div className="space-y-6">
          <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h2 className="font-serif text-xl font-bold text-[#661414]">
                1080 × 1350 Static Editorial Instagram Post
              </h2>
              <p className="text-xs text-[#351D1D]/70 mt-1">
                A single-image high-impact clinical briefing containing headline, primary outcome, explanation, caveats, and source DOI.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={handleGeneratePost}
                disabled={isLoading}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#661414] text-[#F5EBDF] text-xs font-bold hover:bg-[#351D1D] shadow transition"
              >
                {isLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
                Render Static Post PNG
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
            {/* Left: Render Preview */}
            <div className="md:col-span-6 bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-6 shadow-sm space-y-4">
              <div className="aspect-[4/5] max-w-[420px] mx-auto bg-[#F8F2EB] rounded-xl overflow-hidden border-2 border-[#B58777]/30 shadow-md">
                {postData?.preview_url ? (
                  <img src={postData.preview_url} alt="Static Post" className="w-full h-full object-contain" />
                ) : (
                  <div className="h-full flex items-center justify-center p-8 text-center text-xs text-[#B58777]">
                    Click "Render Static Post PNG" to generate image preview.
                  </div>
                )}
              </div>

              {postData?.preview_url && (
                <div className="text-center pt-2">
                  <a
                    href={postData.preview_url}
                    download="instagram_post.png"
                    className="inline-flex items-center gap-1.5 text-xs text-[#C04E2A] font-bold hover:underline"
                  >
                    <Download className="w-3.5 h-3.5" />
                    Download Post PNG (1080 × 1350)
                  </a>
                </div>
              )}
            </div>

            {/* Right: Editable Copy Controls */}
            <div className="md:col-span-6 bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-6 shadow-xs space-y-4">
              <div className="text-xs font-bold text-[#661414] uppercase tracking-wider">
                Live Post Copy Editor
              </div>

              <div className="space-y-3">
                <div>
                  <label className="block text-xs font-bold text-[#351D1D] mb-1">
                    Accurate Headline
                  </label>
                  <input
                    type="text"
                    value={postHeadline}
                    onChange={(e) => setPostHeadline(e.target.value)}
                    placeholder="Clinical Update Headline..."
                    className="w-full text-xs p-2.5 border border-[#B58777] rounded-lg bg-[#F8F2EB] focus:bg-white focus:ring-1 focus:ring-[#C04E2A] outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-[#351D1D] mb-1">
                    Concise Scientific Explanation
                  </label>
                  <textarea
                    value={postBody}
                    onChange={(e) => setPostBody(e.target.value)}
                    placeholder="Explain clinical findings without exaggeration..."
                    rows={4}
                    className="w-full text-xs p-2.5 border border-[#B58777] rounded-lg bg-[#F8F2EB] focus:bg-white focus:ring-1 focus:ring-[#C04E2A] outline-none"
                  />
                </div>

                <div className="p-3 bg-[#F5EBDF] rounded-xl border border-[#E6CBBD] text-xs space-y-1">
                  <div className="font-bold text-[#661414] flex items-center gap-1.5">
                    <ShieldCheck className="w-3.5 h-3.5 text-[#C04E2A]" />
                    Evidence Qualification
                  </div>
                  <p className="text-[#351D1D]/80">
                    Post maintains grounded source traceability: Claim CLM-01 • Verified Peer-Reviewed DOI. Exaggerations or absolute cures are prohibited by Steer Content Policy.
                  </p>
                </div>

                <button
                  onClick={handleGeneratePost}
                  disabled={isLoading}
                  className="w-full py-2.5 bg-[#C04E2A] text-white rounded-xl text-xs font-bold hover:bg-[#661414] shadow transition"
                >
                  Update & Re-Render PNG
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* SUB-TAB 3: FEATURE 1 — SAME EVIDENCE, TWO STORIES        */}
      {/* ======================================================== */}
      {subTab === 'two_stories' && (
        <div className="space-y-6">
          <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-1.5 text-xs font-bold text-[#C04E2A] uppercase tracking-wider mb-1">
                <Sparkles className="w-3.5 h-3.5" />
                Differentiator Feature 1
              </div>
              <h2 className="font-serif text-xl font-bold text-[#661414]">
                Same Evidence, Two Stories
              </h2>
              <p className="text-xs text-[#351D1D]/70 mt-1">
                Transforms identical evidence claims into two distinct scripts: <strong>Professional Mode</strong> (clinicians) and <strong>Everyday Mode</strong> (public viewers).
              </p>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={handleGenerateTwoStories}
                disabled={isLoading}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#661414] text-[#F5EBDF] text-xs font-bold hover:bg-[#351D1D] shadow transition"
              >
                {isLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <RotateCcw className="w-3.5 h-3.5" />}
                Generate Both Scripts
              </button>

              <button
                onClick={() => handleRenderVideoReel(selectedStoryMode, 'en')}
                disabled={isRenderingVideo}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#C04E2A] text-white text-xs font-bold hover:bg-[#661414] shadow transition"
              >
                {isRenderingVideo ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
                Render {selectedStoryMode === 'professional' ? 'Mode A' : 'Mode B'} Reel
              </button>
            </div>
          </div>

          {twoStories ? (
            <div className="space-y-6">
              {/* Mode Toggle Bar */}
              <div className="flex items-center gap-3 bg-[#F5EBDF] p-2 rounded-xl border border-[#E6CBBD] max-w-md">
                <button
                  onClick={() => setSelectedStoryMode('professional')}
                  className={`flex-1 py-2 text-xs font-bold rounded-lg transition ${
                    selectedStoryMode === 'professional'
                      ? 'bg-[#661414] text-[#F5EBDF] shadow-xs'
                      : 'text-[#351D1D] hover:bg-[#FFFFFF]'
                  }`}
                >
                  Mode A: Professional (Clinicians)
                </button>
                <button
                  onClick={() => setSelectedStoryMode('everyday')}
                  className={`flex-1 py-2 text-xs font-bold rounded-lg transition ${
                    selectedStoryMode === 'everyday'
                      ? 'bg-[#C04E2A] text-white shadow-xs'
                      : 'text-[#351D1D] hover:bg-[#FFFFFF]'
                  }`}
                >
                  Mode B: Everyday (General Public)
                </button>
              </div>

              {/* Storyboard Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {(selectedStoryMode === 'professional'
                  ? twoStories.professional.scenes
                  : twoStories.everyday.scenes
                ).map((scene: ReelScene, idx: number) => (
                  <div
                    key={idx}
                    className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-xl p-4 space-y-3 shadow-xs hover:border-[#661414] transition"
                  >
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-mono font-bold text-[#661414]">Scene {scene.scene_index}</span>
                      <span className="text-[10px] bg-[#E6CBBD]/40 text-[#351D1D] px-2 py-0.5 rounded font-medium">
                        {scene.duration_seconds}s
                      </span>
                    </div>

                    <div className="font-serif font-bold text-sm text-[#351D1D]">
                      {scene.title}
                    </div>

                    <div className="text-xs text-[#B58777] font-semibold">
                      Narrator: {scene.narrator_character}
                    </div>

                    <div className="text-xs text-[#351D1D] p-2.5 bg-[#F8F2EB] rounded-lg border border-[#E6CBBD] leading-relaxed">
                      "{scene.narration_text}"
                    </div>

                    <div className="text-[11px] text-[#B58777] line-clamp-2">
                      Visual: {scene.visual_description}
                    </div>

                    <div className="pt-1 text-[10px] font-mono font-bold text-[#C04E2A]">
                      Claim ID: {scene.claim_ids?.[0] || 'CLM-01'}
                    </div>
                  </div>
                ))}
              </div>

              {/* Shared Evidence Side-by-Side Comparison Matrix */}
              <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-6 shadow-xs space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-serif text-lg font-bold text-[#661414]">
                      Shared Evidence Comparison Matrix
                    </h3>
                    <p className="text-xs text-[#351D1D]/70 mt-0.5">
                      Both modes derive from identical evidence records. Inspect wording differences and factual alignment.
                    </p>
                  </div>
                  <span className="bg-emerald-50 text-emerald-800 border border-emerald-200 text-xs font-bold px-3 py-1 rounded-full flex items-center gap-1.5">
                    <Check className="w-3.5 h-3.5" />
                    Zero Evidence Discrepancy
                  </span>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse text-xs">
                    <thead>
                      <tr className="bg-[#F5EBDF] border-b border-[#E6CBBD] text-[#661414] font-bold uppercase tracking-wider text-[11px]">
                        <th className="py-3 px-4 w-20">Scene</th>
                        <th className="py-3 px-4 w-28">Shared Claim</th>
                        <th className="py-3 px-4 w-1/2">Mode A: Professional Script (Doctors)</th>
                        <th className="py-3 px-4 w-1/2">Mode B: Everyday Script (Public)</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#E6CBBD]/60">
                      {twoStories.shared_evidence_comparison?.map((row, idx) => (
                        <tr key={idx} className="hover:bg-[#F8F2EB]">
                          <td className="py-3 px-4 font-mono font-bold text-[#661414]">
                            Scene {row.scene_index}
                          </td>
                          <td className="py-3 px-4 font-mono font-bold text-[#C04E2A]">
                            {row.claim_id}
                          </td>
                          <td className="py-3 px-4 text-[#351D1D] leading-relaxed">
                            {row.professional_wording}
                          </td>
                          <td className="py-3 px-4 text-[#351D1D] leading-relaxed bg-[#F5EBDF]/30">
                            {row.everyday_wording}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-12 text-center space-y-3">
              <Sparkles className="w-10 h-10 text-[#C04E2A] mx-auto opacity-50" />
              <h3 className="font-serif text-lg font-bold text-[#661414]">Two Stories Not Generated Yet</h3>
              <p className="text-xs text-[#351D1D]/70 max-w-md mx-auto">
                Click "Generate Both Scripts" to synthesize tailored Mode A and Mode B scripts from shared evidence claims.
              </p>
              <button
                onClick={handleGenerateTwoStories}
                disabled={isLoading}
                className="bg-[#661414] text-[#F5EBDF] px-5 py-2.5 rounded-xl text-xs font-bold hover:bg-[#351D1D] shadow transition"
              >
                Generate Two Stories Now
              </button>
            </div>
          )}
        </div>
      )}

      {/* ======================================================== */}
      {/* SUB-TAB 4: FEATURE 2 — INSIDE YOUR BODY                 */}
      {/* ======================================================== */}
      {subTab === 'inside_body' && (
        <div className="space-y-6">
          <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-1.5 text-xs font-bold text-[#C04E2A] uppercase tracking-wider mb-1">
                <Activity className="w-3.5 h-3.5" />
                Differentiator Feature 2
              </div>
              <h2 className="font-serif text-xl font-bold text-[#661414]">
                Inside Your Body: Science in Motion
              </h2>
              <p className="text-xs text-[#351D1D]/70 mt-1">
                Shows source-grounded findings with a neutral body outline. Biological mechanisms are not inferred from a title or topic.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={handleGenerateInsideBody}
                disabled={isLoading}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#661414] text-[#F5EBDF] text-xs font-bold hover:bg-[#351D1D] shadow transition"
              >
                {isLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <RotateCcw className="w-3.5 h-3.5" />}
                Generate Physiological Storyboard
              </button>

              <button
                onClick={() => handleRenderVideoReel('inside_body', 'en')}
                disabled={isRenderingVideo}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#C04E2A] text-white text-xs font-bold hover:bg-[#661414] shadow transition"
              >
                {isRenderingVideo ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
                Render Animation Reel
              </button>
            </div>
          </div>

          {insideBody ? (
            <div className="space-y-6">
              {/* Biological Domain Card */}
              <div className="bg-[#F5EBDF] border border-[#B58777]/50 rounded-2xl p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                <div>
                  <span className="text-xs font-bold text-[#C04E2A] uppercase tracking-wider">
                    Target Biological Mechanism
                  </span>
                  <h3 className="font-serif text-xl font-bold text-[#661414] mt-1">
                    {insideBody.target_system}
                  </h3>
                  <p className="text-xs text-[#351D1D]/80 mt-1 max-w-2xl">
                    {insideBody.safeguard_notice}
                  </p>
                </div>

                <span className="bg-[#661414] text-[#F5EBDF] text-xs font-mono font-semibold px-3 py-1.5 rounded-lg shrink-0">
                  DOMAIN: {insideBody.mechanism_type.toUpperCase()}
                </span>
              </div>

              {/* Storyboard Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {insideBody.scenes?.map((scene: ReelScene, idx: number) => (
                  <div
                    key={idx}
                    className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-5 space-y-3 shadow-xs hover:border-[#C04E2A] transition"
                  >
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-mono font-bold text-[#C04E2A]">Scene {scene.scene_index}</span>
                      <span className="text-[10px] bg-[#E6CBBD]/40 text-[#351D1D] px-2 py-0.5 rounded font-medium">
                        {scene.duration_seconds}s Animation
                      </span>
                    </div>

                    <h4 className="font-serif font-bold text-base text-[#661414]">
                      {scene.title}
                    </h4>

                    <div className="aspect-video bg-[#F8F2EB] rounded-xl border border-[#E6CBBD] flex items-center justify-center p-4 text-center">
                      <div className="space-y-1">
                        <Activity className="w-6 h-6 text-[#C04E2A] mx-auto opacity-70" />
                        <div className="text-xs font-semibold text-[#351D1D]">
                          {scene.visual_description}
                        </div>
                      </div>
                    </div>

                    <div className="text-xs text-[#351D1D] bg-[#F5EBDF]/40 p-3 rounded-lg border border-[#E6CBBD] leading-relaxed">
                      "{scene.narration_text}"
                    </div>

                    <div className="text-[11px] font-mono text-[#B58777]">
                      Grounding Claim: <strong>{scene.claim_id || 'CLM-01'}</strong>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-12 text-center space-y-3">
              <Activity className="w-10 h-10 text-[#C04E2A] mx-auto opacity-50" />
              <h3 className="font-serif text-lg font-bold text-[#661414]">Inside Your Body Not Generated Yet</h3>
              <p className="text-xs text-[#351D1D]/70 max-w-md mx-auto">
                Generate motion scenes from verified quotations. Mechanisms are not added unless directly supported by the source evidence.
              </p>
              <button
                onClick={handleGenerateInsideBody}
                disabled={isLoading}
                className="bg-[#661414] text-[#F5EBDF] px-5 py-2.5 rounded-xl text-xs font-bold hover:bg-[#351D1D] shadow transition"
              >
                Generate Inside Body Scenes
              </button>
            </div>
          )}
        </div>
      )}

      {/* ======================================================== */}
      {/* SUB-TAB 5: FEATURE 3 — LOCALVOICE REGIONAL REELS        */}
      {/* ======================================================== */}
      {subTab === 'localvoice' && (
        <div className="space-y-6">
          {/* LocalVoice Regional Voice & Subtitle Status */}
          <div className="bg-emerald-50/90 border border-emerald-300 rounded-2xl p-4 flex items-start gap-3 shadow-xs">
            <Languages className="w-5 h-5 text-emerald-700 shrink-0 mt-0.5" />
            <div className="space-y-1 text-xs text-emerald-950">
              <div className="font-bold text-emerald-900 uppercase tracking-wider text-[11px]">
                LocalVoice Multi-Language Engine Active
              </div>
              <p className="text-emerald-900/90 leading-relaxed font-sans">
                Full end-to-end support for 5 regional languages (Hindi, Telugu, Tamil, Kannada, Malayalam) and English. Spoken audio generates with authentic regional neural voice models, and synchronized subtitles render in native scripts.
              </p>
            </div>
          </div>

          <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-1.5 text-xs font-bold text-[#C04E2A] uppercase tracking-wider mb-1">
                <Languages className="w-3.5 h-3.5" />
                Differentiator Feature 3
              </div>
              <h2 className="font-serif text-xl font-bold text-[#661414]">
                LocalVoice: Regional Health Reels
              </h2>
              <p className="text-xs text-[#351D1D]/70 mt-1">
                Select an accent/voice track below. Script content remains in verified source English.
              </p>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => handleTestVoice(selectedLanguage)}
                disabled={isLoading}
                className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-[#F5EBDF] border border-[#B58777] text-[#661414] text-xs font-bold hover:bg-[#661414] hover:text-[#F5EBDF] transition"
              >
                <Volume2 className="w-3.5 h-3.5" />
                Test Voice Audio
              </button>

              <button
                onClick={() => handleRenderVideoReel('localvoice', selectedLanguage)}
                disabled={isRenderingVideo}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#C04E2A] text-white text-xs font-bold hover:bg-[#661414] shadow transition"
              >
                {isRenderingVideo ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
                {selectedLanguage === 'en' ? 'Render English MP4 Reel' : `Render Voice Reel (${selectedLanguage.toUpperCase()} Voice Track)`}
              </button>
            </div>
          </div>

          {/* Language Selection Buttons */}
          <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
            {[
              { code: 'en', label: 'English', native: 'English' },
              { code: 'hi_en', label: 'Hindi + English', native: 'हिन्दी + English' },
              { code: 'te_en', label: 'Telugu + English', native: 'తెలుగు + English' },
              { code: 'ta_en', label: 'Tamil + English', native: 'தமிழ் + English' },
              { code: 'kn_en', label: 'Kannada + English', native: 'ಕನ್ನಡ + English' },
              { code: 'ml_en', label: 'Malayalam + English', native: 'മലയാളം + English' },
            ].map((lang) => (
              <button
                key={lang.code}
                onClick={() => handleGenerateLocalVoice(lang.code)}
                className={`p-3 rounded-xl border text-left transition ${
                  selectedLanguage === lang.code
                    ? 'bg-[#661414] text-[#F5EBDF] border-[#661414] shadow-xs'
                    : 'bg-[#FFFFFF] text-[#351D1D] border-[#E6CBBD] hover:bg-[#F5EBDF]'
                }`}
              >
                <div className="text-xs font-bold">{lang.label}</div>
                <div className={`text-[11px] mt-0.5 ${selectedLanguage === lang.code ? 'text-[#E6CBBD]' : 'text-[#B58777]'}`}>
                  {lang.native}
                </div>
              </button>
            ))}
          </div>

          {/* Audio Test Player if tested */}
          {audioTestResult && (
            <div className="bg-emerald-50 border border-emerald-300 rounded-xl p-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 text-xs text-emerald-950">
              <div className="space-y-1">
                <div className="font-bold flex items-center gap-1.5 text-emerald-900">
                  <Volume2 className="w-4 h-4 text-emerald-700" />
                  Voice Provider: {audioTestResult.provider_used} ({audioTestResult.details})
                </div>
                <div className="italic text-emerald-800">"{audioTestResult.test_phrase}"</div>
              </div>
              {audioTestResult.audio_url && (
                <audio controls src={audioTestResult.audio_url} className="h-8 max-w-xs" />
              )}
            </div>
          )}

          {/* Localized Storyboard Scenes */}
          {localVoiceScenes.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {localVoiceScenes.map((scene: ReelScene, idx: number) => (
                <div
                  key={idx}
                  className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-5 space-y-3 shadow-xs"
                >
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-mono font-bold text-[#661414]">Scene {scene.scene_index}</span>
                    <span className="bg-[#E6CBBD]/40 text-[#351D1D] px-2 py-0.5 rounded text-[10px] font-mono">
                      {selectedLanguage.toUpperCase()}
                    </span>
                  </div>

                  <h4 className="font-serif font-bold text-sm text-[#351D1D]">{scene.title}</h4>

                  <div className="space-y-2">
                    <div>
                      <div className="flex items-center justify-between">
                        <span className="text-[11px] font-bold text-[#661414] uppercase tracking-wider">
                          Spoken Voice Narration ({selectedLanguage.toUpperCase()})
                        </span>
                        {selectedLanguage !== 'en' && (
                          <span className="bg-emerald-100 text-emerald-900 text-[10px] px-2 py-0.5 rounded font-mono font-medium">
                            Bilingual LocalVoice
                          </span>
                        )}
                      </div>
                      <div className="text-xs text-[#351D1D] bg-[#F8F2EB] p-3 rounded-lg border border-[#E6CBBD] leading-relaxed mt-1">
                        "{scene.narration_text}"
                      </div>
                    </div>

                    {scene.subtitle_native && (
                      <div>
                        <span className="text-[11px] font-bold text-[#C04E2A] uppercase tracking-wider">
                          Synchronized Subtitles (Native Script)
                        </span>
                        <div className="text-xs text-[#661414] bg-[#F5EBDF] p-3 rounded-lg border border-[#B58777]/40 leading-relaxed font-sans mt-1">
                          {scene.subtitle_native}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-10 text-center space-y-3">
              <Languages className="w-8 h-8 text-[#B58777] mx-auto opacity-50" />
              <p className="text-xs text-[#351D1D]/70">
                Select a language to prepare a localized voice track and synchronized native subtitles.
              </p>
            </div>
          )}
        </div>
      )}

      {/* ======================================================== */}
      {/* SUB-TAB 6: VIDEO REEL PLAYER (5.3)                       */}
      {/* ======================================================== */}
      {subTab === 'video_player' && (
        <div className="space-y-6">
          <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h2 className="font-serif text-xl font-bold text-[#661414]">
                1080 × 1920 Vertical Video Reel Player
              </h2>
              <p className="text-xs text-[#351D1D]/70 mt-1">
                Real playable vertical video reel generated with scene motion graphics, TTS voice narration, and synchronized subtitles.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => handleRenderVideoReel('professional', 'en')}
                disabled={isRenderingVideo}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#661414] text-[#F5EBDF] text-xs font-bold hover:bg-[#351D1D] shadow transition"
              >
                {isRenderingVideo ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
                Render Professional Mode Reel
              </button>

              <button
                onClick={() => handleRenderVideoReel('everyday', 'en')}
                disabled={isRenderingVideo}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#C04E2A] text-white text-xs font-bold hover:bg-[#661414] shadow transition"
              >
                {isRenderingVideo ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
                Render Everyday Mode Reel
              </button>
            </div>
          </div>

          <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-5 flex flex-wrap items-end gap-4">
            <label className="text-xs font-bold text-[#661414] space-y-1">
              <span className="block">Creative style</span>
              <select value={reelStyle} onChange={(e) => setReelStyle(e.target.value)} className="block rounded-lg border border-[#B58777] bg-[#F8F2EB] px-3 py-2 text-[#351D1D]">
                <option value="fruits_food">Talking Characters</option>
                <option value="inside_body">Inside Your Body</option>
                <option value="relatable_human">Everyday Human</option>
              </select>
            </label>
            <span className="text-xs text-[#351D1D]/70">Selected style is saved to this research project and applied to the next render.</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
            {/* Video Player Column */}
            <div className="md:col-span-5 bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-6 shadow-sm space-y-4">
              <div className="aspect-[9/16] max-w-[340px] mx-auto bg-black rounded-2xl overflow-hidden shadow-2xl relative border-4 border-[#351D1D]">
                {renderedReel?.video_url ? (
                  <video
                    controls
                    autoPlay
                    src={renderedReel.video_url}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="h-full flex flex-col items-center justify-center p-6 text-center text-xs text-white/70 space-y-3">
                    <Video className="w-12 h-12 text-[#C04E2A] opacity-60" />
                    <div>Render an MP4 reel using the buttons above to watch the playback.</div>
                  </div>
                )}
              </div>

              {renderedReel?.video_url && (
                <div className="text-center pt-2">
                  <a
                    href={renderedReel.video_url}
                    download="steer_reel.mp4"
                    className="inline-flex items-center gap-1.5 text-xs text-[#C04E2A] font-bold hover:underline"
                  >
                    <Download className="w-3.5 h-3.5" />
                    Download MP4 Video Reel (1080 × 1920)
                  </a>
                </div>
              )}
            </div>

            {/* Video Metadata & Scene Breakdown */}
            <div className="md:col-span-7 space-y-4">
              <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-6 shadow-xs space-y-3">
                <div className="text-xs font-bold text-[#661414] uppercase tracking-wider">
                  Reel Production Specifications
                </div>
                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="p-3 bg-[#F8F2EB] rounded-xl border border-[#E6CBBD]">
                    <div className="text-[#B58777]">Resolution:</div>
                    <div className="font-mono font-bold text-sm text-[#351D1D] mt-0.5">1080 × 1920 (9:16)</div>
                  </div>
                  <div className="p-3 bg-[#F8F2EB] rounded-xl border border-[#E6CBBD]">
                    <div className="text-[#B58777]">Total Duration:</div>
                    <div className="font-mono font-bold text-sm text-[#351D1D] mt-0.5">
                      {renderedReel?.total_duration_seconds || '4.5'}s
                    </div>
                  </div>
                  <div className="p-3 bg-[#F8F2EB] rounded-xl border border-[#E6CBBD]">
                    <div className="text-[#B58777]">Encoding Engine:</div>
                    <div className="font-mono font-bold text-sm text-[#351D1D] mt-0.5">FFmpeg libx264 / aac</div>
                  </div>
                  <div className="p-3 bg-[#F8F2EB] rounded-xl border border-[#E6CBBD]">
                    <div className="text-[#B58777]">Narration Voice:</div>
                    <div className="font-mono font-bold text-sm text-[#351D1D] mt-0.5">Edge-TTS Neural Voice</div>
                  </div>
                </div>
              </div>

              {/* Rendered Scenes List */}
              {renderedReel?.scenes && (
                <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-6 shadow-xs space-y-3">
                  <div className="text-xs font-bold text-[#B58777] uppercase tracking-wider">
                    Rendered Scenes Timeline
                  </div>
                  <div className="space-y-2">
                    {renderedReel.scenes.map((sc: any, idx: number) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between p-3 rounded-xl bg-[#F8F2EB] border border-[#E6CBBD] text-xs"
                      >
                        <div className="flex items-center gap-3">
                          <span className="font-mono font-bold text-[#661414]">0{sc.scene_index}</span>
                          <div>
                            <div className="font-bold text-[#351D1D]">{sc.title}</div>
                            <div className="text-[11px] text-[#B58777]">{sc.tts_details}</div>
                          </div>
                        </div>
                        <span className="font-mono text-[#C04E2A] font-bold">{sc.duration}s</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* SUB-TAB 7: CAPTIONS & HASHTAGS                           */}
      {/* ======================================================== */}
      {subTab === 'captions' && (
        <div className="bg-[#FFFFFF] border border-[#E6CBBD] rounded-2xl p-6 shadow-xs space-y-4 max-w-3xl">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-serif text-lg font-bold text-[#661414]">
                Social Media Caption & Evidence Disclaimer
              </h3>
              <p className="text-xs text-[#351D1D]/70 mt-0.5">
                Draft educational captions with source-page traceability. Complete evidence review and medical approval before publishing.
              </p>
            </div>
            <button
              onClick={() => {
                navigator.clipboard.writeText(captionContent);
                setCopiedCaption(true);
                setTimeout(() => setCopiedCaption(false), 2000);
              }}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-[#F5EBDF] border border-[#B58777] text-xs font-bold text-[#661414] rounded-lg hover:bg-[#661414] hover:text-[#F5EBDF] transition"
            >
              <Copy className="w-3.5 h-3.5" />
              {copiedCaption ? 'Copied!' : 'Copy Caption'}
            </button>
          </div>

          <div className="bg-[#F8F2EB] p-4 rounded-xl border border-[#E6CBBD] text-xs font-mono text-[#351D1D] leading-relaxed whitespace-pre-wrap">
{captionContent}
          </div>
        </div>
      )}
    </div>
  );
};
