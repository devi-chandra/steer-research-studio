import uuid
from typing import Dict, List, Any, Optional
from app.core.database import get_db_connection

VALID_REASONS = [
    "Unsupported claim",
    "Incorrect statistic",
    "Missing limitation",
    "Misleading headline",
    "Incorrect translation",
    "Unclear language",
    "Unsubstantiated recommendation",
    "Other"
]

def submit_doctor_review(
    project_id: str,
    target_type: str, # 'claim', 'asset', 'scene', 'slide'
    target_id: str,
    decision: str, # 'Approve', 'Edit', 'Request Changes', 'Reject'
    reason_category: str = "Other",
    original_content: str = "",
    revised_content: str = "",
    comments: str = "",
    reviewer_name: str = "Dr. Medical Reviewer (Demo Lead)"
) -> Dict[str, Any]:
    """
    Feature 5: Doctor Feedback Loop.
    Records clinical editorial decisions, persists revision history, and induces reusable review rules.
    """
    if decision not in ("Approve", "Edit", "Request Changes", "Reject"):
        raise ValueError(f"Invalid review decision: {decision}")

    if reason_category not in VALID_REASONS:
        reason_category = "Other"

    review_id = f"rev-{uuid.uuid4().hex[:8]}"

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Insert review record
    cursor.execute("""
    INSERT INTO reviews (
        id, project_id, target_type, target_id, decision, reason_category,
        original_content, revised_content, comments, reviewer_name
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        review_id, project_id, target_type, target_id, decision, reason_category,
        original_content, revised_content, comments, reviewer_name
    ))

    # 2. Update target status
    if target_type == "claim":
        status_map = {
            "Approve": "Approved",
            "Edit": "Approved (Edited by Doctor)",
            "Request Changes": "Changes Requested",
            "Reject": "Rejected"
        }
        new_status = status_map.get(decision, "Pending Review")
        rev_text = revised_content if decision == "Edit" and revised_content else None
        if rev_text:
            cursor.execute("""
            UPDATE claims
            SET claim_text = ?, review_status = ?, review_notes = ?, reviewer_name = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? OR claim_id = ?
            """, (rev_text, new_status, f"Reason: {reason_category}. {comments}", reviewer_name, target_id, target_id))
        else:
            cursor.execute("""
            UPDATE claims
            SET review_status = ?, review_notes = ?, reviewer_name = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? OR claim_id = ?
            """, (new_status, f"Reason: {reason_category}. {comments}", reviewer_name, target_id, target_id))

    elif target_type == "asset":
        asset_status = "approved" if decision in ("Approve", "Edit") else ("rejected" if decision == "Reject" else "draft")
        cursor.execute("UPDATE assets SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (asset_status, target_id))

    # 3. Rule Induction: If rejection or edit for statistic/overclaim, generate or update a Review Rule
    rule_generated = None
    if decision in ("Edit", "Request Changes", "Reject"):
        rule_type = reason_category.lower().replace(" ", "_")
        pattern = comments[:50] if comments else f"Flagged {reason_category}"
        desc = f"Doctor review alert: Content flagged for '{reason_category}'. Ensure future drafts verify exact source citations."

        # Check if rule exists
        cursor.execute("SELECT id, trigger_count FROM review_rules WHERE rule_type = ?", (rule_type,))
        existing_rule = cursor.fetchone()
        if existing_rule:
            cursor.execute("UPDATE review_rules SET trigger_count = trigger_count + 1 WHERE id = ?", (existing_rule["id"],))
            rule_generated = f"Updated rule {existing_rule['id']} (Triggers: {existing_rule['trigger_count'] + 1})"
        else:
            new_rule_id = f"rule-{uuid.uuid4().hex[:6]}"
            cursor.execute("""
            INSERT INTO review_rules (id, rule_type, pattern_or_keyword, description, trigger_count, is_active)
            VALUES (?, ?, ?, ?, 1, 1)
            """, (new_rule_id, rule_type, pattern, desc))
            rule_generated = f"Created new active rule {new_rule_id}"

    conn.commit()
    conn.close()

    return {
        "success": True,
        "review_id": review_id,
        "project_id": project_id,
        "target_type": target_type,
        "target_id": target_id,
        "decision": decision,
        "reason_category": reason_category,
        "reviewer_name": reviewer_name,
        "rule_update": rule_generated
    }

def get_project_reviews(project_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reviews WHERE project_id = ? ORDER BY created_at DESC", (project_id,))
    reviews = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return reviews

def get_active_review_rules() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM review_rules WHERE is_active = 1 ORDER BY trigger_count DESC", ())
    rules = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rules
