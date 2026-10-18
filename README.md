# Steer — Doctor-Led Research-to-Content Studio
### Hackathon PS2 (Scheme 2) | Automated Multi-Format Clinical Editorial Engine

> **Core Principle:** One verified scientific source. Multiple formats. Different audiences. Consistent evidence. Human approval.

Steer transforms complex scientific research papers into accurate, audience-tailored medical communications—including Instagram carousels, static posts, vertical video reels, and PowerPoint presentations—with end-to-end evidence traceability and human clinical review gates.

---

## 1. System Architecture

```
                    ┌───────────────────────────────────────────────┐
                    │            Scientific Paper Source            │
                    │      (Original PDF Upload or Public URL)      │
                    └───────────────────────┬───────────────────────┘
                                            │
                                            ▼
                    ┌───────────────────────────────────────────────┐
                    │               Ingestion Service               │
                    │   • PyMuPDF (Page boundaries, OCR detection)  │
                    │   • SSRF-Safe Web Fetcher (Private IP defense)│
                    └───────────────────────┬───────────────────────┘
                                            │
                                            ▼
                    ┌───────────────────────────────────────────────┐
                    │           Structured Evidence Engine          │
                    │   • Claim ID, Verbatim Quote, Page Number     │
                    │   • Numerical Result, Units, Sample Size (n)  │
                    │   • Study Type, Caveats, p-value / Uncertainty│
                    └───────────────────────┬───────────────────────┘
                                            │
                                            ▼
                    ┌───────────────────────────────────────────────┐
                    │         Automated Verification Service        │
                    │   • Verbatim substring matching against text  │
                    │   • Directly / Partially / Unsupported flags  │
                    └───────────────────────┬───────────────────────┘
                                            │
                    ┌───────────────────────┴───────────────────────┐
                    ▼                                               ▼
    ┌───────────────────────────────┐               ┌───────────────────────────────┐
    │     Mode A: Professional      │               │       Mode B: Everyday        │
    │  • Healthcare professionals   │               │  • General public & social    │
    │  • Clinical, quantitative     │               │  • Conversational & engaging  │
    │  • Exact methodology bounds   │               │  • No cures / shaming         │
    └───────────────┬───────────────┘               └───────────────┬───────────────┘
                    └───────────────────────┬───────────────────────┘
                                            │
                 ┌──────────────────────────┼──────────────────────────┐
                 ▼                          ▼                          ▼
    ┌─────────────────────────┐┌─────────────────────────┐┌─────────────────────────┐
    │  Instagram Studio (5.1) ││ Inside Your Body (Feat 2)││  LocalVoice (Feature 3) │
    │ • 1080×1350 PNG slides  ││ • Physiological animation││ • 6 Indian language pairs│
    │ • Structured 6 slides   ││ • Cellular mechanism     ││ • Synchronized subtitles│
    │ • Downloadable ZIP      ││ • Tailored to paper topic││ • Edge-TTS Neural voices│
    └─────────────────────────┘└─────────────────────────┘└─────────────────────────┘
                 │                          │                          │
                 └──────────────────────────┼──────────────────────────┘
                                            ▼
                    ┌───────────────────────────────────────────────┐
                    │        Research-to-PowerPoint (Feat 4)        │
                    │   • python-pptx native 10-slide presentation  │
                    │   • Editable tables, text, speaker notes      │
                    │   • Steer Clinical Editorial theme            │
                    └───────────────────────┬───────────────────────┘
                                            │
                                            ▼
                    ┌───────────────────────────────────────────────┐
                    │          Doctor Feedback Loop (Feat 5)        │
                    │   • Approve / Edit / Changes / Reject         │
                    │   • Revision history & Induced review rules   │
                    └───────────────────────┬───────────────────────┘
                                            │
                                            ▼
                    ┌───────────────────────────────────────────────┐
                    │          Cross-Format Claim Safety            │
                    │   • Scans numbers, units, denominators       │
                    │   • Flags headline vs body contradictions     │
                    │   • Enforces publication readiness gate       │
                    └───────────────────────┬───────────────────────┘
                                            │
                                            ▼
                    ┌───────────────────────────────────────────────┐
                    │                 Export Center                 │
                    │   • Master ZIP archive                        │
                    │   • PNGs, MP4 reels, PPTX, Captions, Manifest │
                    └───────────────────────────────────────────────┘
```

---

## 2. Technology Stack

- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS v4, Lucide React icons.
- **Backend**: Python 3.10+, FastAPI, Pydantic v2, SQLite (WAL mode & foreign keys enabled).
- **Document Processing**: PyMuPDF (fitz) for page boundary text extraction, heading detection, and scanned document detection.
- **Presentation Generation**: `python-pptx` generating native editable 10-slide decks.
- **Graphics & Imaging**: Pillow (`PIL`) for 1080×1350 Instagram carousel slides and static posts.
- **Video & Audio Pipeline**: FFmpeg (H.264 video, AAC audio, 1080×1920 vertical format), `edge-tts` with high-quality Indian regional neural voices, and `gTTS` fallback.
- **AI Abstraction**: Provider abstraction supporting Google Gemini API (`gemini-2.5-flash`), OpenAI (`gpt-4o-mini`), and high-fidelity Deterministic Scientific Engine with explicit fallback disclosure.

---

## 3. Brand Identity & Design System

The studio uses the Steer clinical editorial palette:

| Brand Token | Hex Code | Purpose |
| :--- | :--- | :--- |
| **Cream** | `#F5EBDF` | Warm background surface & content cards |
| **Rust** | `#C04E2A` | Accent callouts, dividers, primary buttons |
| **Deep Maroon** | `#661414` | Editorial serif headlines, primary brand badges |
| **Ink** | `#351D1D` | High-contrast readable body text, captions |
| **Clay** | `#B58777` | Subtle borders, meta tags, provenance indicators |
| **Blush** | `#E6CBBD` | Pill badges, table borders, dividers |
| **Soft Paper** | `#F8F2EB` | Application workspace background |

**Typography:**
- Editorial Headlines: *Newsreader* (Serif).
- Controls, Tables, Body: *Plus Jakarta Sans* / system sans.
- Provenance & Identifiers: *JetBrains Mono*.

---

## 4. Key Differentiator Features

### Feature 1: Same Evidence, Two Stories
- **Mode A (Professional Mode)**: Tailored for healthcare professionals and researchers. Clinical, precise, quantitative tone covering study design, sample size ($n$), primary endpoints, p-values, clinical bounds, and citations.
- **Mode B (Everyday Mode)**: Tailored for social media and general audiences. Conversational, engaging, friendly characters/scenarios, with strictly no personalized diagnosis, no cure promises, and zero body shaming.
- **Shared Evidence Comparison Matrix**: A side-by-side audit view demonstrating how each sentence in both modes maps directly to the identical source Claim ID.

### Feature 2: Inside Your Body — Science in Motion
- Explains biological mechanisms tailored specifically to the paper's subject (cardiovascular arterial compliance, cellular glucose transport via GLUT4, mitochondrial respiration, or circadian neurochemistry).
- Visual scene storyboards rendered with motion graphics and source citations.

### Feature 3: LocalVoice — Regional Health Reels
Supports 6 language combinations for narration and synchronized subtitles:
1. English (`en`)
2. Hindi + English / Hinglish (`hi_en`)
3. Telugu + English (`te_en`)
4. Tamil + English (`ta_en`)
5. Kannada + English (`kn_en`)
6. Malayalam + English (`ml_en`)
- Preserves all clinical metrics, numbers, units, and limitations in translation.
- Provides native script subtitles and Roman script transliterations.
- Real-time voice testing capability via `edge-tts` neural voices.

### Feature 4: Research-to-PowerPoint Studio
- Generates genuine, editable `.pptx` presentations (10 slides) using `python-pptx`.
- Complete slide progression: Title/Provenance, Background, Methodology, Cohort Demographics, Key Findings, Quantitative Data Table, Biological Mechanisms, Limitations & Bias, Clinical Takeaways, References Audit.
- Slides are validated by reopening the presentation file structurally.

### Feature 5: Doctor Feedback Loop & Claim Safety
- Clinical review gate with `Approve`, `Edit`, `Request Changes`, `Reject` actions.
- Standardized reason taxonomy: *Unsupported claim*, *Incorrect statistic*, *Missing limitation*, *Misleading headline*, *Incorrect translation*, *Unclear language*, *Unsubstantiated recommendation*, *Other*.
- Induced Review Rules: Automatically learns from doctor revisions to create persistent rules flagging future overclaims.
- Cross-Format Claim Safety Engine: Compares claims across Carousel, Static Post, Professional Reel, Everyday Reel, and PowerPoint. Flags numerical discrepancies, changed units, lost caveats, or headline-body contradictions.

---

## 5. Quickstart & Installation

### Prerequisites
- Python 3.10+
- Node.js v18+ and npm
- FFmpeg installed in system PATH (for video reel rendering)

### 1. Backend Setup
```bash
cd d:/steer_hackathon/backend
python -m pip install -r requirements.txt
```

### 2. Frontend Setup
```bash
cd d:/steer_hackathon/frontend
npm install
```

### 3. Running Locally
Run the backend on port 8005 (the port used by the Vite proxy):
```bash
# From the repository root:
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8005
```

Run the frontend on port 5174. The port is configured in `frontend/vite.config.ts`; 5173 is not this project's configured port.
```bash
# From the repository root:
cd frontend
npm run dev -- --host 127.0.0.1
```

Access the studio in your browser at: **`http://127.0.0.1:5174/`**

### Environment and separate hosting

- Backend settings are read from `backend/app/core/config.py`; copy `.env.example` to the backend process working directory when you need overrides. `PORT` must stay at `8005` for the checked-in local Vite proxy. AI keys are optional; `GEMINI_API_KEY` and `OPENAI_API_KEY` are backend-only. `AI_PROVIDER` accepts `auto`, `gemini`, `openai`, or `deterministic`. `TTS_PROVIDER` selects the configured speech provider.
- Local development needs no frontend environment variable: Vite proxies `/api` and `/storage` to `http://127.0.0.1:8005`. For a separately hosted frontend, set public `VITE_API_BASE_URL` at build time to the FastAPI origin. It must contain no key or credential. API-returned `/storage/...` media URLs use the same origin.
- No Vercel routing or deployed backend configuration is present in this repository, and no deployed pair was tested. The backend stores SQLite data, uploaded PDFs, and generated PNG/MP4/PPTX files on disk. A deployment needs persistent storage and enough CPU/time for PDF extraction and FFmpeg rendering; an ephemeral serverless filesystem is not sufficient for durable projects and exports.

---

## 6. Automated Test Results

Run the backend suite from `backend/`:

### Test Command:
```bash
python -m pytest -q
```

### Results Summary:
```
============================= test session starts =============================
platform win32 -- Python 3.10.10, pytest-9.1.1, pluggy-1.6.0
collected 10 items

tests/test_full_suite.py::test_ssrf_security_rules PASSED                [ 10%]
tests/test_full_suite.py::test_pdf_ingestion_and_claim_extraction PASSED [ 20%]
tests/test_full_suite.py::test_carousel_and_post_generation PASSED       [ 30%]
tests/test_full_suite.py::test_two_stories_and_inside_body PASSED        [ 40%]
tests/test_full_suite.py::test_localvoice_script_adaptation PASSED       [ 50%]
tests/test_full_suite.py::test_powerpoint_generation_and_validation PASSED [ 60%]
tests/test_full_suite.py::test_doctor_feedback_and_consistency PASSED    [ 70%]
tests/test_full_suite.py::test_export_package PASSED                     [ 80%]
tests/test_video_audio.py::test_tts_voice_generation_multilingual PASSED [ 90%]
tests/test_video_audio.py::test_full_video_reel_rendering PASSED         [100%]

27 passed, 2 warnings in 2216.03s
```

The warnings were a Pydantic settings deprecation notice and a `requests` dependency version warning. The frontend production build was also run with `npm run build` and succeeded.

---

## 7. Generated File Artifacts

All rendered deliverables are persisted in `storage/`:

| Artifact | File Path | Specs |
| :--- | :--- | :--- |
| **Master Export Archive** | `storage/exports/steer_export_test-proj-001.zip` | 1.1 MB complete deliverable suite |
| **Evidence Audit Manifest** | `storage/exports/test-proj-001/evidence_audit_manifest.md` | Markdown traceability audit |
| **Social Captions & Tags** | `storage/exports/test-proj-001/captions_and_hashtags.txt` | Educational caption + disclaimer |
| **PowerPoint Deck** | `storage/generated/pptx/presentation_test-proj-001.pptx` | 10 slides, native editable shapes & tables |
| **Instagram Carousel ZIP** | `storage/generated/carousels/test-proj-001/carousel_test-proj-001.zip` | 6 portrait PNG slides (1080 × 1350) |
| **Static Instagram Post** | `storage/generated/posts/post_test-proj-001.png` | 1080 × 1350 high-res PNG |
| **Vertical Video Reel** | `storage/generated/reels/reel_test-proj-001_professional_en.mp4` | 1080 × 1920 MP4 (H.264 / AAC) |
| **Multilingual TTS Audio** | `storage/generated/audio/test_voice_*.mp3` | Tested for EN, HI, TE, TA, KN, ML |

---

## 8. Recommended 2-Minute Hackathon Demonstration Sequence

1. **Dashboard (0:00 - 0:15)**: Open `http://127.0.0.1:5174/`. Point out the Steer brand palette, active research projects, and provider status pill (*Deterministic Scientific Engine*).
2. **New Research (0:15 - 0:35)**: Click *New Research*. Click *Load Verified Sample Paper (Nature Medicine 2022 VILPA Trial)*. Show instant PDF extraction with 3 preserved pages, DOI detection, and heading identification.
3. **Evidence Ledger (0:35 - 0:50)**: Navigate to *Evidence Ledger*. Show extracted claims, exact verbatim supporting quotations, page numbers, and evidence status badges (*Directly supported*). Click a row to open the *Claim Modal* and inspect source quotes.
4. **Content Studio & Two Stories (0:50 - 1:15)**:
   - Navigate to *Content Studio*. Preview the 6-slide *Instagram Carousel* and *Static Post*.
   - Switch to *Two Stories*: Toggle between *Mode A: Professional* and *Mode B: Everyday*. Show the *Shared Evidence Comparison Matrix* proving both derive from the same Claim IDs.
   - Switch to *Inside Your Body*: Show the cardiovascular endothelial animation storyboard.
   - Switch to *LocalVoice*: Switch to *Hindi + English* or *Telugu + English*, click *Test Voice Audio* to hear the audio playback.
5. **PowerPoint Studio (1:15 - 1:30)**: Click *PowerPoint Studio*. Show the 10-slide deck gallery and click *Download .pptx* to demonstrate the real editable presentation.
6. **Review Gate & Claim Safety (1:30 - 1:45)**: Click *Medical Review Gate*. Perform an audit decision (*Approve* or *Edit*). Navigate to *Claim Safety Checks* and show the cross-format discrepancy audit.
7. **Export Center (1:45 - 2:00)**: Navigate to *Export Center*. Click *Download Master ZIP* containing all rendered PNGs, MP4 reel, PPTX, captions, and evidence audit manifest.
