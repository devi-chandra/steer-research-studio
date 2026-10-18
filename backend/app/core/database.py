import sqlite3
import json
from pathlib import Path
from typing import Any, List, Optional, Dict
from app.core.config import settings

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(settings.DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Projects
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        authors TEXT DEFAULT '',
        publication TEXT DEFAULT '',
        year TEXT DEFAULT '',
        doi TEXT DEFAULT '',
        source_type TEXT NOT NULL, -- 'pdf' or 'url' or 'text'
        source_path TEXT DEFAULT '',
        source_url TEXT DEFAULT '',
        reel_style TEXT DEFAULT 'relatable_human',
        reel_theme TEXT DEFAULT 'steer',
        extraction_status TEXT DEFAULT 'pending', -- pending, extracted, failed
        metadata_verified BOOLEAN DEFAULT 0,
        limitation_notes TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    for column, definition in (("reel_style", "TEXT DEFAULT 'relatable_human'"), ("reel_theme", "TEXT DEFAULT 'steer'")):
        try:
            cursor.execute(f"ALTER TABLE projects ADD COLUMN {column} {definition};")
        except Exception:
            pass

    # Document Pages (Page boundary preservation)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS document_pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id TEXT NOT NULL,
        page_number INTEGER NOT NULL,
        text_content TEXT NOT NULL,
        char_count INTEGER NOT NULL,
        section_headings TEXT DEFAULT '',
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    );
    """)

    # Claims & Evidence Ledger
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS claims (
        id TEXT PRIMARY KEY, -- e.g. CLM-PROJID-01
        project_id TEXT NOT NULL,
        claim_id TEXT NOT NULL, -- Short readable code: e.g. CLM-01
        claim_text TEXT NOT NULL,
        exact_quote TEXT NOT NULL,
        page_number INTEGER NOT NULL,
        section_heading TEXT DEFAULT '',
        study_type TEXT DEFAULT 'Observational',
        population TEXT DEFAULT '',
        sample_size TEXT DEFAULT '',
        outcome_measured TEXT DEFAULT '',
        numerical_result TEXT DEFAULT '',
        units TEXT DEFAULT '',
        study_conditions TEXT DEFAULT '',
        limitations TEXT DEFAULT '',
        uncertainty TEXT DEFAULT '',
        evidence_status TEXT DEFAULT 'Directly supported', -- 'Directly supported', 'Partially supported', 'Unsupported', 'Unable to verify'
        review_status TEXT DEFAULT 'Pending Review', -- 'Pending Review', 'Approved', 'Edited', 'Rejected'
        review_notes TEXT DEFAULT '',
        reviewer_name TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    );
    """)

    # Generated Assets (Carousel, Static Post, Video Reels, PowerPoint, etc.)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assets (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        asset_type TEXT NOT NULL, -- 'carousel', 'post', 'reel_professional', 'reel_everyday', 'reel_localvoice', 'reel_inside_body', 'pptx'
        title TEXT NOT NULL,
        status TEXT DEFAULT 'draft', -- 'draft', 'rendered', 'approved', 'rejected'
        file_path TEXT DEFAULT '',
        preview_url TEXT DEFAULT '',
        metadata_json TEXT DEFAULT '{}',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    );
    """)

    # Reel Scenes (Professional, Everyday, Inside Body, LocalVoice)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reel_scenes (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        reel_mode TEXT NOT NULL, -- 'professional', 'everyday', 'inside_body', 'localvoice'
        scene_index INTEGER NOT NULL,
        title TEXT NOT NULL,
        narrator_character TEXT DEFAULT '',
        visual_description TEXT NOT NULL,
        narration_text TEXT NOT NULL,
        visual_type TEXT DEFAULT 'graphic', -- 'graphic', 'character', 'animation', 'chart'
        duration_seconds REAL DEFAULT 4.0,
        claim_ids_json TEXT DEFAULT '[]',
        language_code TEXT DEFAULT 'en',
        subtitle_native TEXT DEFAULT '',
        style_type TEXT DEFAULT 'relatable_human', -- 'fruits_food', 'inside_body', 'relatable_human', 'funny_science_convo'
        character_type TEXT DEFAULT '',
        character_action TEXT DEFAULT '',
        render_status TEXT DEFAULT 'pending',
        frame_image_path TEXT DEFAULT '',
        audio_path TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    );
    """)

    try:
        cursor.execute("ALTER TABLE reel_scenes ADD COLUMN subtitle_native TEXT DEFAULT '';")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE reel_scenes ADD COLUMN style_type TEXT DEFAULT 'relatable_human';")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE reel_scenes ADD COLUMN character_type TEXT DEFAULT '';")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE reel_scenes ADD COLUMN character_action TEXT DEFAULT '';")
    except Exception:
        pass

    # Doctor Review Records
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        target_type TEXT NOT NULL, -- 'claim', 'asset', 'scene', 'slide'
        target_id TEXT NOT NULL,
        decision TEXT NOT NULL, -- 'Approve', 'Edit', 'Request Changes', 'Reject'
        reason_category TEXT DEFAULT 'Other', -- 'Unsupported claim', 'Incorrect statistic', 'Missing limitation', 'Misleading headline', 'Incorrect translation', 'Unclear language', 'Unsubstantiated recommendation', 'Other'
        original_content TEXT DEFAULT '',
        revised_content TEXT DEFAULT '',
        comments TEXT DEFAULT '',
        reviewer_name TEXT DEFAULT 'Dr. Medical Reviewer (Demo)',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    );
    """)

    # Review Rules (Learned / Persisted from Doctor Feedback)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS review_rules (
        id TEXT PRIMARY KEY,
        rule_type TEXT NOT NULL,
        pattern_or_keyword TEXT NOT NULL,
        description TEXT NOT NULL,
        trigger_count INTEGER DEFAULT 1,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Cross-Format Consistency Checks
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS consistency_checks (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        check_type TEXT NOT NULL, -- 'numerical', 'unit', 'unsupported_claim', 'missing_limitation', 'headline_contradiction'
        severity TEXT DEFAULT 'warning', -- 'warning', 'critical', 'info'
        affected_assets_json TEXT DEFAULT '[]',
        source_claim_id TEXT DEFAULT '',
        discrepancy_explanation TEXT NOT NULL,
        suggestion TEXT DEFAULT '',
        resolved BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    );
    """)

    # Seed default review rules if empty
    cursor.execute("SELECT COUNT(*) FROM review_rules;")
    if cursor.fetchone()[0] == 0:
        default_rules = [
            ("rule-1", "headline_overclaim", "Relative risk presented as absolute cure", "Never convert relative improvements into universal cure statements.", 1, 1),
            ("rule-2", "causation_assumption", "Associational study presented as causal mechanism", "Observational cohorts show correlation; do not state causation without randomized trial evidence.", 1, 1),
            ("rule-3", "missing_sample_size", "Numerical findings presented without sample size context", "Always preserve participant count (n) and confidence intervals where available in the original paper.", 1, 1),
            ("rule-4", "unsupported_extrapolation", "Results generalized beyond study population", "Preserve demographic or clinical criteria (e.g. healthy adults, post-menopausal women, diabetic cohort).", 1, 1),
            ("rule-5", "medical_advice_prohibition", "Educational synthesis turned into personalized prescriptive advice", "Always maintain educational framing with explicit disclaimer: 'Consult your physician before altering medical regimen'.", 1, 1)
        ]
        cursor.executemany("""
        INSERT INTO review_rules (id, rule_type, pattern_or_keyword, description, trigger_count, is_active)
        VALUES (?, ?, ?, ?, ?, ?);
        """, default_rules)

    conn.commit()
    conn.close()

# Initialize DB on load
init_db()
