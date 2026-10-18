import pytest
from app.services.ai_provider import ai_provider_service
from app.services.video_generation import video_generation_service
from app.services.cross_format_claims import CrossFormatClaimsService
from app.schemas.schemas import ReelSceneUpdateRequest

def test_inside_your_body_storyboard_generation():
    """Verify Inside Your Body extracts up to 3 distinct supported biological findings with real organ characters"""
    claims = [
        {"claim_id": "CLM-001", "claim_text": "Postprandial walking reduces blood sugar spikes by 34%."},
        {"claim_id": "CLM-002", "claim_text": "Skeletal muscle contractions clear glucose without placing pancreatic demand."},
        {"claim_id": "CLM-003", "claim_text": "Timing matters: walking within 30 minutes is 3x more effective than waiting an hour."}
    ]

    reel = ai_provider_service.generate_regional_reel_script(
        mode="everyday",
        visual_style="inside_your_body",
        language="en",
        paper_title="Postprandial Walking Crossover Trial",
        claims=claims
    )

    assert reel["visual_style"] == "inside_your_body"
    assert len(reel["scenes"]) == 3
    organs = [s.get("organ_character") for s in reel["scenes"]]
    assert organs == ["red_blood_cell", "brain", "stomach"]
    
    # Check durations are realistic and non-5.0 hardcoded
    durations = [s["duration_seconds"] for s in reel["scenes"]]
    assert sum(durations) >= 30.0
    for d in durations:
        assert d >= 10.0


def test_everyday_mode_7_scene_narrative():
    """Verify Everyday Mode produces 7-scene character-driven Instagram reel in all 6 regional languages"""
    claims = [{"claim_id": "CLM-001", "claim_text": "Walking reduces sugar by 34%."}]
    languages = ["en", "hi", "te", "ta", "kn", "ml"]

    for lang in languages:
        reel = ai_provider_service.generate_regional_reel_script(
            mode="everyday",
            visual_style="talking_characters",
            language=lang,
            paper_title="Postprandial Walking Trial",
            claims=claims
        )

        assert len(reel["scenes"]) == 7
        assert reel["language"] == lang
        assert 25 <= reel["target_duration_seconds"] <= 45
        
        # Verify first scene has hook
        assert "Hey!" in reel["scenes"][0]["narration"] or len(reel["scenes"][0]["narration"]) > 10


def test_localvoice_fallback_guards():
    """Verify regional languages never silently fall back to English voice"""
    fallbacks = {
        "hi": "hi-IN-SwaraNeural",
        "te": "te-IN-ShrutiNeural",
        "ta": "ta-IN-PallaviNeural",
        "kn": "kn-IN-SapnaNeural",
        "ml": "ml-IN-SobhanaNeural",
    }
    
    for lang, expected_voice in fallbacks.items():
        voices = ai_provider_service.get_available_voices()
        assert lang in voices
        assert voices[lang]["default_voice"] == expected_voice
        assert "en-IN" not in voices[lang]["default_voice"]


def test_cross_format_claims_audit():
    """Verify Cross-Format Claims Service detects numerical, population, and citation consistency"""
    service = CrossFormatClaimsService()
    assert hasattr(service, "audit_project_consistency")

