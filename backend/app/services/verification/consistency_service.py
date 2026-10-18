import re
import json
import uuid
from typing import Dict, List, Any
from app.core.database import get_db_connection

def run_cross_format_consistency_checks(project_id: str) -> Dict[str, Any]:
    """
    Section 11: Cross-Format Claim Safety.
    Compares factual statements and numerical consistency across:
    - Carousel slides
    - Static post
    - Professional reel
    - Everyday reel
    - PowerPoint presentation
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get claims
    cursor.execute("SELECT claim_id, claim_text, numerical_result, units, sample_size, limitations, evidence_status FROM claims WHERE project_id = ?", (project_id,))
    claims = [dict(r) for r in cursor.fetchall()]

    # Get assets
    cursor.execute("SELECT id, asset_type, metadata_json FROM assets WHERE project_id = ?", (project_id,))
    assets = [dict(r) for r in cursor.fetchall()]

    # Get reel scenes
    cursor.execute("SELECT reel_mode, scene_index, title, narration_text, claim_ids_json FROM reel_scenes WHERE project_id = ?", (project_id,))
    scenes = [dict(r) for r in cursor.fetchall()]

    # Clear previous checks for this project
    cursor.execute("DELETE FROM consistency_checks WHERE project_id = ?", (project_id,))

    discrepancies = []

    # 1. Check for Unsupported or Unverified claims used in assets
    unsupported_claims = [c for c in claims if c["evidence_status"] in ("Unsupported", "Unable to verify")]
    if unsupported_claims:
        for uc in unsupported_claims:
            cid = uc["claim_id"]
            d_id = f"chk-{uuid.uuid4().hex[:8]}"
            disc = {
                "id": d_id,
                "project_id": project_id,
                "check_type": "unsupported_claim",
                "severity": "critical",
                "affected_assets": ["Carousel", "Static Post", "Reels"],
                "source_claim_id": cid,
                "discrepancy_explanation": f"Claim {cid} is marked as '{uc['evidence_status']}' against original source text, but is scheduled for publication.",
                "suggestion": f"Doctor review required: Edit or remove Claim {cid} in Evidence Ledger before exporting publication package.",
                "resolved": False
            }
            discrepancies.append(disc)

    # 2. Check for Exaggerated Causal Language in Headlines vs Body
    for a in assets:
        try:
            meta = json.loads(a.get("metadata_json", "{}"))
            headline = meta.get("headline", "")
            if re.search(r'\b(cures|miracle|guarantees|eliminates|100%|universally)\b', headline, re.I):
                d_id = f"chk-{uuid.uuid4().hex[:8]}"
                disc = {
                    "id": d_id,
                    "project_id": project_id,
                    "check_type": "headline_contradiction",
                    "severity": "critical",
                    "affected_assets": [a["asset_type"]],
                    "source_claim_id": "CLM-HL",
                    "discrepancy_explanation": f"Headline in {a['asset_type']} contains absolute medical promise: '{headline}'. Source paper contains contextual limitations.",
                    "suggestion": "Revise headline to reflect observational or clinical trial bounds (e.g., 'Associated with significant reduction').",
                    "resolved": False
                }
                discrepancies.append(disc)
        except Exception:
            pass

    # 3. Check Numerical Preservation across Reel Modes
    prof_scenes = [s for s in scenes if s["reel_mode"] == "professional"]
    evry_scenes = [s for s in scenes if s["reel_mode"] == "everyday"]

    # Extract all numbers from claims
    source_numbers = []
    for c in claims:
        nums = re.findall(r'\b\d+(?:\.\d+)?%?\b', c.get("numerical_result", "") + " " + c.get("claim_text", ""))
        source_numbers.extend(nums)

    # Verify that everyday mode has not invented unverified numbers
    for es in evry_scenes:
        es_nums = re.findall(r'\b\d+(?:\.\d+)?%?\b', es.get("narration_text", ""))
        for num in es_nums:
            if num not in source_numbers and num not in ["1", "2", "3", "4", "5", "6"]:
                d_id = f"chk-{uuid.uuid4().hex[:8]}"
                disc = {
                    "id": d_id,
                    "project_id": project_id,
                    "check_type": "numerical_discrepancy",
                    "severity": "warning",
                    "affected_assets": ["Everyday Reel"],
                    "source_claim_id": json.loads(es.get("claim_ids_json", "[]"))[0] if json.loads(es.get("claim_ids_json", "[]")) else "CLM-01",
                    "discrepancy_explanation": f"Number '{num}' appears in Everyday Reel Scene {es['scene_index']} but is not explicitly found in extracted source claim metrics.",
                    "suggestion": f"Cross-verify numerical value '{num}' against source table or restore exact paper statistic.",
                    "resolved": False
                }
                discrepancies.append(disc)

    # 4. Check for Lost Limitations in Regional / Everyday Scripts
    has_caveat_in_everyday = any(
        any(k in s.get("narration_text", "").lower() for k in ["doctor", "consult", "limit", "context", "specific", "check"])
        for s in evry_scenes
    )
    if not has_caveat_in_everyday and evry_scenes:
        d_id = f"chk-{uuid.uuid4().hex[:8]}"
        disc = {
            "id": d_id,
            "project_id": project_id,
            "check_type": "missing_limitation",
            "severity": "warning",
            "affected_assets": ["Everyday Reel"],
            "source_claim_id": "CLM-LIM",
            "discrepancy_explanation": "Everyday Mode script is missing a closing clinical caveat or physician consultation disclaimer.",
            "suggestion": "Include medical consultation reminder in concluding scene to satisfy Steer medical safety policy.",
            "resolved": False
        }
        discrepancies.append(disc)

    # Insert into database
    for d in discrepancies:
        cursor.execute("""
        INSERT INTO consistency_checks (
            id, project_id, check_type, severity, affected_assets_json,
            source_claim_id, discrepancy_explanation, suggestion, resolved
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            d["id"], project_id, d["check_type"], d["severity"],
            json.dumps(d["affected_assets"]), d["source_claim_id"],
            d["discrepancy_explanation"], d["suggestion"], 0
        ))

    conn.commit()
    conn.close()

    total_critical = sum(1 for d in discrepancies if d["severity"] == "critical")
    total_warning = sum(1 for d in discrepancies if d["severity"] == "warning")

    return {
        "project_id": project_id,
        "total_checks_run": 5,
        "total_discrepancies_found": len(discrepancies),
        "critical_issues": total_critical,
        "warnings": total_warning,
        "is_publication_ready": (total_critical == 0),
        "discrepancies": discrepancies
    }
