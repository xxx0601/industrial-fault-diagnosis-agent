"""Tests for shared timeline workflow (mock + offline)."""

from pathlib import Path

from app.agent.workflows.timeline import analyze_timeline

SAMPLE_JSON = Path(__file__).resolve().parents[1] / "data" / "samples" / "timeline_fault_chain.json"


def test_analyze_timeline_sample():
    text = SAMPLE_JSON.read_text(encoding="utf-8")
    out = analyze_timeline(text, request_fault_code=None)

    assert out.fault_codes == ["E101", "E305", "E204", "E410"]
    assert out.primary_fault is not None
    assert out.primary_fault["code"] == "E410"
    assert len(out.related_faults) == 3
    assert out.temperature_trend["direction"] == "rising"
    assert out.vibration_trend["direction"] == "rising"
    assert "轴承磨损" in out.fault_evolution[0]
    assert out.risk_level == "HIGH"

    result = out.to_diagnosis_result()
    assert result.fault_codes == out.fault_codes
    assert result.primary_fault is not None
    assert result.primary_fault.code == "E410"


def test_request_fault_code_overrides_primary():
    text = SAMPLE_JSON.read_text(encoding="utf-8")
    out = analyze_timeline(text, request_fault_code="E204")
    assert out.primary_fault is not None
    assert out.primary_fault["code"] == "E204"
