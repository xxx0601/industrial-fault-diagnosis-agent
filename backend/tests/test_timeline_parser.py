"""Tests for timeline log parsing and fault code collection."""

from app.parsers.timeline_parser import TimelineParser, collect_fault_codes


def test_json_logs_array():
    text = """{
      "logs": [
        {"time": "08:00", "status": "NORMAL"},
        {"time": "09:00", "fault_code": "E101"},
        {"time": "10:10", "fault_code": "E410", "temperature": 92, "vibration": 8.2}
      ]
    }"""
    entries = TimelineParser().parse(text)
    codes = collect_fault_codes(entries)
    assert len(entries) == 3
    assert codes == ["E101", "E410"]
    assert entries[-1].temperature == 92.0
    assert entries[-1].vibration == 8.2


def test_text_timeline_lines():
    text = """08:00 NORMAL
09:00 E101
09:30 E305
10:00 E204
10:10 E410"""
    entries = TimelineParser().parse(text)
    codes = collect_fault_codes(entries)
    assert len(entries) == 5
    assert codes == ["E101", "E305", "E204", "E410"]
    assert entries[0].status == "NORMAL"
