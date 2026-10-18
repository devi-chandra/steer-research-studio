# Steer Studio Architecture & Data Model

## 1. Directory Structure

```
d:/steer_hackathon/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI application entrypoint & static mounts
│   │   ├── core/
│   │   │   ├── config.py               # Settings, directories, palette tokens, port 8005
│   │   │   ├── database.py             # SQLite WAL connection, foreign keys, schema migrations
│   │   │   ├── security.py             # SSRF validation, safe filenames, path containment
│   │   │   └── ai_provider.py          # Gemini / OpenAI / Deterministic scientific engine
│   │   ├── models/ & schemas/
│   │   │   ├── project.py              # Ingestion & Project schemas
│   │   │   ├── claim.py                # Evidence claim schemas
│   │   │   └── review.py               # Review decisions & induced rules
│   │   ├── services/
│   │   │   ├── ingestion/
│   │   │   │   ├── pdf_extractor.py    # PyMuPDF page boundary & OCR detection
│   │   │   │   └── url_extractor.py    # SSRF-protected web article parser
│   │   │   ├── extraction/
│   │   │   │   └── claim_extractor.py  # Structured claim extraction
│   │   │   ├── verification/
│   │   │   │   ├── evidence_verifier.py# Verbatim text substring verification
│   │   │   │   └── consistency_service.py # Cross-format discrepancy scanner
│   │   │   ├── content_generation/
│   │   │   │   ├── carousel_generator.py # 1080×1350 PNG slides & ZIP
│   │   │   │   └── post_generator.py   # 1080×1350 static Instagram post
│   │   │   ├── reel_generation/
│   │   │   │   ├── two_stories_generator.py # Mode A & Mode B derivation
│   │   │   │   ├── inside_body_generator.py # Mechanism animation storyboard
│   │   │   │   └── video_renderer.py   # FFmpeg 1080×1920 MP4 & TTS stitching
│   │   │   ├── localization/
│   │   │   │   ├── local_voice_service.py # 6 Indian regional language options
│   │   │   │   └── tts_adapter.py      # Edge-TTS neural voice adapter
│   │   │   ├── powerpoint/
│   │   │   │   └── pptx_generator.py   # python-pptx 10-slide deck generator
│   │   │   ├── review/
│   │   │   │   └── feedback_service.py # Doctor review gate & rule induction
│   │   │   └── export/
│   │   │       └── export_service.py   # Master export ZIP & audit manifest
│   │   └── api/
│   │       ├── routes_projects.py
│   │       ├── routes_evidence.py
│   │       ├── routes_content.py
│   │       ├── routes_reel.py
│   │       ├── routes_pptx.py
│   │       ├── routes_review.py
│   │       ├── routes_export.py
│   │       └── routes_settings.py
│   ├── tests/
│   │   ├── test_full_suite.py          # 8 core pipeline integration tests
│   │   └── test_video_audio.py         # TTS voice matrix & FFmpeg MP4 rendering tests
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.tsx              # Top bar, project selector, AI status pill
│   │   │   ├── Sidebar.tsx             # Medical editorial navigation
│   │   │   ├── EvidenceBadge.tsx       # Standardized status badges
│   │   │   └── ClaimModal.tsx          # Verbatim quote & limitation inspection modal
│   │   ├── pages/
│   │   │   ├── DashboardPage.tsx       # Live metrics & project hub
│   │   │   ├── NewResearchPage.tsx     # PDF upload & URL ingestion
│   │   │   ├── EvidenceLedgerPage.tsx  # Verifiable claims ledger & filters
│   │   │   ├── ContentStudioPage.tsx   # Carousel, Post, Two Stories, Inside Body, LocalVoice, Reel
│   │   │   ├── PowerPointStudioPage.tsx# 10-slide PowerPoint deck viewer
│   │   │   ├── ReviewGatePage.tsx      # Doctor audit actions & rule induction
│   │   │   ├── ConsistencySafetyPage.tsx # Cross-format discrepancy scanner
│   │   │   ├── ExportCenterPage.tsx    # Master ZIP & individual downloads
│   │   │   └── SettingsPage.tsx        # System health & voice testing
│   │   ├── services/
│   │   │   └── api.ts                  # Typed client for backend API
│   │   ├── types/
│   │   │   └── index.ts                # Data models manifest
│   │   ├── App.tsx                     # Main layout & router
│   │   ├── index.css                   # Tailwind CSS v4 design tokens
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts                  # Vite + Tailwind v4 + proxy to port 8005
├── sample_papers/
│   ├── generate_paper.py               # Nature Med 2022 landmark trial PDF generator
│   └── stamatakis_vilpa_nature_med_2022.pdf # Verifiable 3-page clinical PDF
├── storage/
│   ├── steer_studio.db                 # Persistent SQLite database
│   ├── uploads/                        # Original source papers
│   ├── generated/                      # Rendered PNGs, MP4s, PPTX, audio
│   └── exports/                        # Publication packages & audit manifests
├── .env.example
├── .gitignore
├── ARCHITECTURE.md
└── README.md
```

---

## 2. SQLite Database Schema

### `projects`
- `id` (TEXT PRIMARY KEY)
- `title` (TEXT NOT NULL)
- `authors` (TEXT)
- `publication` (TEXT)
- `year` (TEXT)
- `doi` (TEXT)
- `source_type` (TEXT: 'pdf' | 'url' | 'text')
- `source_path` (TEXT)
- `source_url` (TEXT)
- `extraction_status` (TEXT: 'pending' | 'extracted' | 'failed' | 'scanned_needs_ocr')
- `metadata_verified` (BOOLEAN)
- `limitation_notes` (TEXT)
- `created_at`, `updated_at` (TIMESTAMP)

### `document_pages`
- `id` (INTEGER PRIMARY KEY)
- `project_id` (TEXT REFERENCES projects(id))
- `page_number` (INTEGER)
- `text_content` (TEXT)
- `char_count` (INTEGER)
- `section_headings` (TEXT)

### `claims`
- `id` (TEXT PRIMARY KEY)
- `project_id` (TEXT REFERENCES projects(id))
- `claim_id` (TEXT, e.g. 'CLM-01')
- `claim_text` (TEXT NOT NULL)
- `exact_quote` (TEXT NOT NULL)
- `page_number` (INTEGER NOT NULL)
- `section_heading` (TEXT)
- `study_type` (TEXT)
- `population` (TEXT)
- `sample_size` (TEXT)
- `outcome_measured` (TEXT)
- `numerical_result` (TEXT)
- `units` (TEXT)
- `study_conditions` (TEXT)
- `limitations` (TEXT)
- `uncertainty` (TEXT)
- `evidence_status` (TEXT: 'Directly supported' | 'Partially supported' | 'Unsupported' | 'Unable to verify')
- `review_status` (TEXT: 'Pending Review' | 'Approved' | 'Approved (Edited by Doctor)' | 'Changes Requested' | 'Rejected')
- `review_notes` (TEXT)
- `reviewer_name` (TEXT)

### `assets`
- `id` (TEXT PRIMARY KEY)
- `project_id` (TEXT REFERENCES projects(id))
- `asset_type` (TEXT: 'carousel' | 'post' | 'reel_professional' | 'reel_everyday' | 'reel_inside_body' | 'reel_localvoice' | 'pptx')
- `title` (TEXT NOT NULL)
- `status` (TEXT: 'draft' | 'rendered' | 'approved' | 'rejected')
- `file_path` (TEXT)
- `preview_url` (TEXT)
- `metadata_json` (TEXT)

### `reel_scenes`
- `id` (TEXT PRIMARY KEY)
- `project_id` (TEXT REFERENCES projects(id))
- `reel_mode` (TEXT: 'professional' | 'everyday' | 'inside_body' | 'localvoice')
- `scene_index` (INTEGER)
- `title` (TEXT NOT NULL)
- `narrator_character` (TEXT)
- `visual_description` (TEXT NOT NULL)
- `narration_text` (TEXT NOT NULL)
- `visual_type` (TEXT: 'graphic' | 'character' | 'animation' | 'chart')
- `duration_seconds` (REAL)
- `claim_ids_json` (TEXT)
- `language_code` (TEXT)
- `render_status` (TEXT)

### `reviews` & `review_rules`
- `reviews`: Stores every decision, timestamp, reason category, original and revised content.
- `review_rules`: Stores induced rules (e.g. `headline_overclaim`, `causation_assumption`, `missing_sample_size`) to prevent recurrence of flagged issues in future generated drafts.
