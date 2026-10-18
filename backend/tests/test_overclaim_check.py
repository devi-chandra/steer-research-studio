from types import SimpleNamespace

from app.services.overclaim_check import OverclaimCheckService, build_editorial_brief


def _claim(text, claim_id="CLM-001", evidence_type="Randomized Controlled Trial"):
    return SimpleNamespace(
        claim_id=claim_id,
        claim_text=text,
        limitations=["Short follow-up and a defined study population"],
        evidence_type=evidence_type,
    )


def _draft(text, claim_ids=None):
    return SimpleNamespace(
        main_message=text,
        hook="",
        caption=text,
        slide_data=[],
        static_data=None,
        reel_data={"scenes": []},
        claim_ids=claim_ids or ["CLM-001"],
    )


def test_overclaim_checker_flags_guarantees_and_missing_limitations():
    report = OverclaimCheckService().audit(
        _draft("This treatment prevents regain for everyone."),
        [_claim("The study observed a change.")],
    )
    assert report["overall_status"] == "review_required"
    assert any(check["check_id"] == "OC-002" for check in report["checks"])
    assert any(check["check_id"] == "OC-003" for check in report["checks"])
    assert any(check["check_id"] == "OC-005" for check in report["checks"])


def test_editorial_brief_is_concern_led():
    brief = build_editorial_brief([_claim("The study observed lean mass changes.")], None)
    assert brief["audience_concern"] == "What happens to muscle during weight loss?"
    assert "CLM-001" in brief["supported_claim_ids"]
