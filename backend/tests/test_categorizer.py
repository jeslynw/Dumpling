import pytest
from app.agents.agent_categorizer import categorize_note
from app.schemas.folder import CategorizationRequest

def test_categorize_note_finance():
    req = CategorizationRequest(content="This is a finance report.")
    res = categorize_note(req)
    assert res.suggested_folder == "Finance"
    assert res.confidence >= 0.9

def test_categorize_note_health():
    req = CategorizationRequest(content="This is about health and wellness.")
    res = categorize_note(req)
    assert res.suggested_folder == "Health"
    assert res.confidence >= 0.85

def test_categorize_note_general():
    req = CategorizationRequest(content="Random unrelated text.")
    res = categorize_note(req)
    assert res.suggested_folder == "General"
    assert res.confidence == 0.5
