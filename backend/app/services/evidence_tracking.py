import re
from typing import Dict, Any, List

class EvidenceTrackingService:
    @staticmethod
    def verify_claim_evidence(claim: Dict[str, Any], full_paper_text: str, pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Cross-examines an extracted claim and its verbatim quotation against the source paper text.
        Determines verification strength: 'strong', 'moderate', 'weak', or 'unsupported'.
        Flags weak or unsupported claims for human medical review.
        """
        quote = (claim.get("evidence_quote") or "").strip()
        cited_page = claim.get("page_number")
        
        if not quote:
            return {
                "support_level": "unsupported",
                "support_notes": "No supporting quotation provided in extraction.",
                "verification_status": "flagged",
                "confidence_estimate": 0.40
            }

        # Normalize strings for comparison (remove punctuation, collapse whitespace)
        def normalize(t: str) -> str:
            clean = re.sub(r"[^\w\s]", " ", t.lower())
            return re.sub(r"\s+", " ", clean).strip()

        norm_quote = normalize(quote)
        norm_full = normalize(full_paper_text)

        # 1. Check exact match in full text or normalized text
        if quote.lower() in full_paper_text.lower() or norm_quote in norm_full:
            # Check if it is on the cited page
            page_matched = False
            if cited_page and 1 <= cited_page <= len(pages):
                target_page_norm = normalize(pages[cited_page - 1].get("text", ""))
                if norm_quote in target_page_norm:
                    page_matched = True

            notes = f"Exact verbatim passage verified in paper{' on cited page ' + str(cited_page) if page_matched else ''}."
            return {
                "support_level": "strong",
                "support_notes": notes,
                "verification_status": "pending",  # Pending human medical review
                "confidence_estimate": claim.get("confidence_estimate") or 0.94
            }

        # 3. Fuzzy match: Check if substantial word sequence (>=70% words) appears in window
        words = norm_quote.split()
        if len(words) >= 5:
            matched_count = sum(1 for w in words if w in norm_full)
            ratio = matched_count / len(words)
            if ratio >= 0.80:
                return {
                    "support_level": "moderate",
                    "support_notes": f"Substantial textual overlap ({int(ratio*100)}% key terms found in source text). Passage may be slightly paraphrased.",
                    "verification_status": "pending",
                    "confidence_estimate": 0.82
                }
            elif ratio >= 0.50:
                return {
                    "support_level": "weak",
                    "support_notes": f"Only partial overlap ({int(ratio*100)}% terms found). Specific phrasing or numbers could not be fully verified.",
                    "verification_status": "flagged",
                    "confidence_estimate": 0.60
                }

        return {
            "support_level": "unsupported",
            "support_notes": "Quotation could not be located in the extracted document text. Flagged for mandatory reviewer check.",
            "verification_status": "flagged",
            "confidence_estimate": 0.35
        }
