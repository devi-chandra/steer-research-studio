"""Deterministic editorial safety checks for research-to-social content.

These checks are intentionally conservative. They surface possible distortions for
review; they do not claim to replace a clinician or prove that wording is wrong.
"""
import re
from typing import Any, Dict, Iterable, List


class OverclaimCheckService:
    _CAUSE_WORDS = re.compile(r"\b(causes?|prevents?|protects?|proves?|guarantees?|leads to|turns into|will)\b", re.I)
    _UNIVERSAL_WORDS = re.compile(r"\b(everyone|all people|anyone|for everyone|your body|will happen to you)\b", re.I)
    _GUARANTEE_WORDS = re.compile(r"\b(always|never|cure|miracle|guaranteed|permanent|beat|outsmarts|proves?)\b", re.I)
    _DRUG_WORDS = re.compile(r"\b(semaglutide|tirzepatide|ozempic|wegovy|mounjaro)\b", re.I)

    @staticmethod
    def _content_text(draft: Any) -> str:
        bits: List[str] = [draft.main_message or "", draft.hook or "", draft.caption or ""]
        for slide in draft.slide_data or []:
            bits.extend(str(slide.get(k, "")) for k in ("headline", "body_text", "practical_tip"))
        if draft.static_data:
            bits.extend(str(draft.static_data.get(k, "")) for k in ("headline", "body_copy", "practical_takeaway"))
        for scene in (draft.reel_data or {}).get("scenes", []):
            bits.extend(str(scene.get(k, "")) for k in ("narration", "on_screen_text", "subtitle_text"))
        return " ".join(bits)

    @staticmethod
    def _check(label: str, status: str, details: str, severity: str = "warning", **extra: Any) -> Dict[str, Any]:
        return {"check_id": extra.pop("check_id", label.lower().replace(" ", "-")), "label": label,
                "status": status, "severity": severity, "details": details, **extra}

    def audit(self, draft: Any, claims: Iterable[Any], paper_metadata: Dict[str, Any] | None = None) -> Dict[str, Any]:
        paper_metadata = paper_metadata or {}
        claims = list(claims)
        text = self._content_text(draft)
        lower = text.lower()
        checks: List[Dict[str, Any]] = []

        study_type = " ".join(str(c.evidence_type or "") for c in claims).lower()
        study_type += " " + str(paper_metadata.get("study_type", "")).lower()
        is_protocol = "protocol" in study_type or "protocol" in str(paper_metadata).lower()
        if is_protocol:
            checks.append(self._check("Protocol/result boundary", "flagged",
                "This source appears to be a protocol. Treat hypotheses and planned outcomes as non-results.",
                "high", check_id="OC-001", suggested_revision="Label this as a planned study; do not describe findings."))
        else:
            checks.append(self._check("Protocol/result boundary", "passed",
                "No protocol-only source signal detected in the available metadata.", "info", check_id="OC-001"))

        if self._CAUSE_WORDS.search(text) or self._GUARANTEE_WORDS.search(text):
            checks.append(self._check("Causal or guaranteed language", "flagged",
                "The draft contains causal, guarantee, or victory language that may exceed the study design.",
                "high", check_id="OC-002", suggested_revision="Use measured wording such as ‘was associated with’, ‘observed’, or ‘may’."))
        else:
            checks.append(self._check("Causal or guaranteed language", "passed",
                "No high-risk causal or guarantee wording detected.", "info", check_id="OC-002"))

        if self._UNIVERSAL_WORDS.search(text):
            checks.append(self._check("Population scope", "flagged",
                "The draft may generalize a study population or result to everyone.", "high", check_id="OC-003",
                suggested_revision="Name the studied population and add the study limitation."))
        else:
            checks.append(self._check("Population scope", "passed", "No obvious universal-population language detected.", "info", check_id="OC-003"))

        if self._DRUG_WORDS.search(text):
            checks.append(self._check("Prescription-drug promotion", "flagged",
                "A prescription drug name appears in public-facing copy. Keep it in the evidence ledger unless the educational context is essential and reviewed.",
                "high", check_id="OC-004", suggested_revision="Use a treatment-class or evidence description and avoid eligibility or outcome promises."))
        else:
            checks.append(self._check("Prescription-drug promotion", "passed", "No prescription drug name detected in public copy.", "info", check_id="OC-004"))

        missing_limitations = [c.claim_id for c in claims if c.limitations and not any(str(x).lower() in lower for x in c.limitations)]
        if missing_limitations:
            checks.append(self._check("Limitations carried into content", "flagged",
                f"Limitations for {', '.join(missing_limitations)} are present in the ledger but not visibly represented in the draft.",
                "medium", check_id="OC-005", affected_claim_ids=missing_limitations,
                suggested_revision="Add a short ‘what this study cannot tell us’ line to the caption or final slide."))
        else:
            checks.append(self._check("Limitations carried into content", "passed", "No omitted claim limitations detected by the conservative text check.", "info", check_id="OC-005"))

        referenced = set(draft.claim_ids or [])
        valid = {c.claim_id for c in claims}
        orphaned = sorted(referenced - valid)
        if orphaned:
            checks.append(self._check("Claim ID integrity", "flagged", f"Draft references missing claim IDs: {', '.join(orphaned)}.", "high", check_id="OC-006"))
        else:
            checks.append(self._check("Claim ID integrity", "passed", "All master-draft claim IDs exist in the evidence ledger.", "info", check_id="OC-006"))

        flagged = sum(c["status"] == "flagged" for c in checks)
        return {"overall_status": "review_required" if flagged else "passed", "total_checks": len(checks),
                "flagged_checks": flagged, "passed_checks": len(checks) - flagged, "checks": checks,
                "disclaimer": "Potential issues are heuristic flags for human clinical review, not definitive error findings."}


overclaim_check_service = OverclaimCheckService()


def build_editorial_brief(claims: Iterable[Any], campaign_topic: str | None, paper_metadata: Dict[str, Any] | None = None) -> Dict[str, Any]:
    claims = list(claims)
    concern = campaign_topic or "What does this research actually tell us?"
    if not campaign_topic:
        joined = " ".join(str(c.claim_text) for c in claims).lower()
        if "muscle" in joined or "lean mass" in joined:
            concern = "What happens to muscle during weight loss?"
        elif "regain" in joined or "withdraw" in joined:
            concern = "Will the weight come back?"
        elif "diabetes" in joined:
            concern = "Is this only for people with diabetes?"
    ids = [c.claim_id for c in claims]
    fit = assess_question_fit(concern, claims)
    return {
        "audience_concern": concern,
        **fit,
        "one_message": "Explain the strongest supported finding without turning it into a personal promise.",
        "supported_claim_ids": ids[:3],
        "important_boundary": "This source describes a study population and design; it is not a personal prescription or proof that Steer’s programme produces the same outcome.",
        "what_this_paper_cannot_answer": ["Individual eligibility", "Individual treatment response", "Whether a Steer programme prevents a future outcome"],
        "reasoning": "The concern is answered only to the extent that the selected claims and their limitations support it."
    }


def assess_question_fit(question: str, claims: Iterable[Any]) -> Dict[str, Any]:
    """Conservative topic coverage check; low overlap prompts a graceful refusal."""
    stop_words = {"what", "does", "this", "that", "the", "a", "an", "is", "are", "will", "can", "how", "for", "to", "of", "during", "happen", "about", "people", "me", "my", "we", "do"}
    words = set(re.findall(r"[a-z]{4,}", (question or "").lower())) - stop_words
    claim_text = " ".join(
        " ".join([str(getattr(c, "claim_text", "")), str(getattr(c, "evidence_type", "")), " ".join(getattr(c, "limitations", []) or [])])
        for c in claims
    ).lower()
    supported_terms = sorted(w for w in words if re.search(rf"\b{re.escape(w)}\w*\b", claim_text))
    score = len(supported_terms) / max(len(words), 1)
    answerable = score >= 0.3
    return {
        "answerability": "supported" if answerable else "not_supported_by_this_source",
        "topic_overlap_score": round(score, 2),
        "matched_terms": supported_terms,
        "refusal_message": None if answerable else "This paper does not directly answer that question. Choose a related question that matches the study findings, or use a more relevant source.",
    }
