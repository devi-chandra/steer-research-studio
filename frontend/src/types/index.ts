export interface Project {
  id: string;
  title: string;
  authors: string;
  publication: string;
  year: string;
  doi: string;
  source_type: 'pdf' | 'url' | 'text';
  source_url: string;
  source_path: string;
  extraction_status: 'pending' | 'extracted' | 'failed' | 'scanned_needs_ocr';
  metadata_verified: boolean;
  limitation_notes: string;
  created_at: string;
  updated_at: string;
  claims_count?: number;
  assets_count?: number;
  pending_reviews_count?: number;
  pages?: {
    page_number: number;
    char_count: number;
    section_headings: string;
  }[];
}

export interface Claim {
  id: string;
  project_id: string;
  claim_id: string;
  claim_text: string;
  exact_quote: string;
  page_number: number;
  section_heading: string;
  study_type: string;
  population: string;
  sample_size: string;
  outcome_measured: string;
  numerical_result: string;
  units: string;
  study_conditions: string;
  limitations: string;
  uncertainty: string;
  evidence_status: 'Directly supported' | 'Partially supported' | 'Unsupported' | 'Unable to verify';
  review_status: 'Pending Review' | 'Approved' | 'Approved (Edited by Doctor)' | 'Changes Requested' | 'Rejected';
  review_notes: string;
  reviewer_name: string;
  created_at: string;
  updated_at: string;
}

export interface CarouselSlide {
  slide_index: number;
  filename: string;
  file_path: string;
  preview_url: string;
  headline: string;
  subhead: string;
  body: string;
  claim_id: string;
  page_num: number;
}

export interface ReelScene {
  id?: string;
  scene_index: number;
  title: string;
  narrator_character: string;
  visual_description: string;
  narration_text: string;
  subtitle_native?: string;
  subtitle_roman?: string;
  visual_type: string;
  duration_seconds: number;
  claim_ids: string[];
  claim_id?: string;
  language_code?: string;
  frame_preview?: string;
  audio_url?: string;
  tts_provider?: string;
}

export interface TwoStoriesData {
  professional: {
    audience: string;
    tone: string;
    scenes: ReelScene[];
  };
  everyday: {
    audience: string;
    tone: string;
    scenes: ReelScene[];
  };
  shared_evidence_comparison: {
    scene_index: number;
    claim_id: string;
    professional_wording: string;
    everyday_wording: string;
    shared_facts: string;
  }[];
}

export interface InsideBodyData {
  mechanism_type: string;
  target_system: string;
  safeguard_notice: string;
  scenes: ReelScene[];
}

export interface ReviewRecord {
  id: string;
  project_id: string;
  target_type: string;
  target_id: string;
  decision: 'Approve' | 'Edit' | 'Request Changes' | 'Reject';
  reason_category: string;
  original_content: string;
  revised_content: string;
  comments: string;
  reviewer_name: string;
  created_at: string;
}

export interface ReviewRule {
  id: string;
  rule_type: string;
  pattern_or_keyword: string;
  description: string;
  trigger_count: number;
  is_active: boolean;
  created_at: string;
}

export interface ConsistencyCheck {
  id: string;
  project_id: string;
  check_type: string;
  severity: 'critical' | 'warning' | 'info';
  affected_assets: string[];
  source_claim_id: string;
  discrepancy_explanation: string;
  suggestion: string;
  resolved: boolean;
  created_at: string;
}

export interface SystemStatus {
  project_name: string;
  version: string;
  ai_provider: {
    active_provider: string;
    has_gemini_key: boolean;
    has_openai_key: boolean;
    status_label: string;
  };
  tts_provider: string;
  supported_languages: {
    code: string;
    label: string;
    tts_voice: string;
    native_name: string;
  }[];
  ffmpeg_available: boolean;
  ffmpeg_path: string;
}
