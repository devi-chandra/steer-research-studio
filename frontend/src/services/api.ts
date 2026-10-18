import {
  Project,
  Claim,
  TwoStoriesData,
  InsideBodyData,
  ReviewRecord,
  ReviewRule,
  ConsistencyCheck,
  SystemStatus,
  ReelScene
} from '../types';

const BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');

function resolveMediaUrls(value: any): any {
  if (Array.isArray(value)) return value.map(resolveMediaUrls);
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [
      key,
      typeof item === 'string' && key.endsWith('_url') && item.startsWith('/storage/')
        ? `${BASE_URL}${item}`
        : resolveMediaUrls(item),
    ]));
  }
  return value;
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Accept': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    let errorDetail = 'Request failed';
    try {
      const errorJson = await response.json();
      errorDetail = errorJson.detail || errorJson.error || errorDetail;
    } catch {
      errorDetail = `HTTP ${response.status}: ${response.statusText}`;
    }
    throw new Error(errorDetail);
  }

  return resolveMediaUrls(await response.json());
}

export const api = {
  // System Status
  getStatus: () => request<SystemStatus>('/api/settings/status'),
  downloadSamplePdf: async () => {
    const response = await fetch(`${BASE_URL}/api/settings/sample-pdf`, {
      headers: { 'Accept': 'application/pdf' },
    });
    if (!response.ok) {
      throw new Error(`Sample PDF request failed: HTTP ${response.status}`);
    }
    return response.blob();
  },

  // Projects
  getProjects: () => request<{ projects: Project[] }>('/api/projects'),
  getProject: (id: string) => request<Project>(`/api/projects/${id}`),
  deleteProject: (id: string) => request<{ success: boolean }>(`/api/projects/${id}`, { method: 'DELETE' }),

  uploadPdf: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return request<{ success: boolean; project_id: string; message: string; extraction: any }>('/api/projects/upload-pdf', {
      method: 'POST',
      body: formData,
    });
  },

  ingestUrl: (url: string) =>
    request<{ success: boolean; project_id: string; message: string; extraction: any }>('/api/projects/ingest-url', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    }),

  // Evidence Ledger
  extractClaims: (projectId: string) =>
    request<{ success: boolean; extraction: any; verification: any }>(`/api/projects/${projectId}/extract-claims`, {
      method: 'POST',
    }),

  getClaims: (projectId: string, evidenceStatus?: string, reviewStatus?: string) => {
    const params = new URLSearchParams();
    if (evidenceStatus) params.append('evidence_status', evidenceStatus);
    if (reviewStatus) params.append('review_status', reviewStatus);
    const qs = params.toString() ? `?${params.toString()}` : '';
    return request<{ project_id: string; total: number; claims: Claim[] }>(`/api/projects/${projectId}/claims${qs}`);
  },

  verifyEvidence: (projectId: string) =>
    request<{ success: boolean; verification: any }>(`/api/projects/${projectId}/verify-evidence`, {
      method: 'POST',
    }),

  updateClaim: (claimId: string, data: Partial<Claim>) =>
    request<{ success: boolean; claim: Claim }>(`/api/projects/claims/${claimId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }),

  // Content Studio
  generateCarousel: (projectId: string, slideCount: number = 6) =>
    request<any>(`/api/projects/${projectId}/generate/carousel`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ slide_count: slideCount }),
    }),

  getCarousel: (projectId: string) => request<any>(`/api/projects/${projectId}/carousel`),

  generatePost: (projectId: string, customHeadline: string = '', customBody: string = '') =>
    request<any>(`/api/projects/${projectId}/generate/post`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ custom_headline: customHeadline, custom_body: customBody }),
    }),

  getPost: (projectId: string) => request<any>(`/api/projects/${projectId}/post`),

  // Feature 1: Two Stories
  generateTwoStories: (projectId: string) =>
    request<{ success: boolean; stories: TwoStoriesData }>(`/api/projects/${projectId}/generate/two-stories`, {
      method: 'POST',
    }),

  getTwoStories: (projectId: string) => request<any>(`/api/projects/${projectId}/two-stories`),

  // Feature 2: Inside Your Body
  generateInsideBody: (projectId: string) =>
    request<{ success: boolean; inside_body: InsideBodyData }>(`/api/projects/${projectId}/generate/inside-body`, {
      method: 'POST',
    }),

  getInsideBody: (projectId: string) => request<any>(`/api/projects/${projectId}/inside-body`),

  // Feature 3: LocalVoice
  generateLocalVoice: (projectId: string, languageCode: string) =>
    request<{ success: boolean; localvoice: any }>(`/api/projects/${projectId}/generate/localvoice`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ language_code: languageCode }),
    }),

  getLocalVoice: (projectId: string, languageCode: string) =>
    request<any>(`/api/projects/${projectId}/localvoice?language_code=${languageCode}`),

  getReelConfig: (projectId: string) => request<{ project_id: string; style: string; theme: string }>(`/api/projects/${projectId}/reel-config`),

  updateReelConfig: (projectId: string, style: string, theme: string) =>
    request<{ project_id: string; style: string; theme: string }>(`/api/projects/${projectId}/reel-config`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ style, theme }),
    }),

  renderVideoReel: (projectId: string, reelMode: string, languageCode: string = 'en', style: string = 'auto_select', theme: string = 'steer') =>
    request<any>(`/api/projects/${projectId}/render/video-reel`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reel_mode: reelMode, language_code: languageCode, style, theme }),
    }),

  testTtsVoice: (languageCode: string) =>
    request<{
      language_code: string;
      success: boolean;
      provider_used: string;
      details: string;
      test_phrase: string;
      audio_url: string;
      file_size_bytes: number;
    }>(`/api/projects/tts/test-voice?language_code=${languageCode}`),

  // Feature 4: PowerPoint Studio
  generatePptx: (projectId: string) =>
    request<any>(`/api/projects/${projectId}/generate/pptx`, {
      method: 'POST',
    }),

  getPptx: (projectId: string) => request<any>(`/api/projects/${projectId}/pptx`),

  // Feature 5: Doctor Review Gate
  submitReview: (data: {
    project_id: string;
    target_type: string;
    target_id: string;
    decision: string;
    reason_category?: string;
    original_content?: string;
    revised_content?: string;
    comments?: string;
    reviewer_name?: string;
  }) =>
    request<any>('/api/reviews/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }),

  getReviews: (projectId: string) =>
    request<{ project_id: string; reviews: ReviewRecord[] }>(`/api/projects/${projectId}/reviews`),

  getReviewRules: () => request<{ rules: ReviewRule[] }>('/api/reviews/rules'),

  // Cross-Format Claim Safety
  checkConsistency: (projectId: string) =>
    request<{ success: boolean; results: any }>(`/api/projects/${projectId}/check-consistency`, {
      method: 'POST',
    }),

  getConsistencyChecks: (projectId: string) =>
    request<{
      project_id: string;
      total: number;
      critical_count: number;
      is_publication_ready: boolean;
      checks: ConsistencyCheck[];
    }>(`/api/projects/${projectId}/consistency-checks`),

  // Export Center
  exportProject: (projectId: string) => request<any>(`/api/projects/${projectId}/export`, { method: 'POST' }),
  getExport: (projectId: string) => request<any>(`/api/projects/${projectId}/export`),
};
