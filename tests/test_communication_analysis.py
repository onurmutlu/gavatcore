"""
Smoke tests for the communication_analysis application orchestrator.
"""
import pytest

from pipelines.communication_analysis import analyze_transcript


@pytest.mark.asyncio
async def test_analyze_transcript_empty():
    # With no messages, classifier should still return a result list
    result = await analyze_transcript("user1", "char1", [])
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_analyze_transcript_sample(monkeypatch):
    # Monkeypatch classifier to return a dummy BaitClassification
    class DummyClassification:
        pass

    async def dummy_classify(*args, **kwargs):
        return DummyClassification()

    monkeypatch.setattr(
        "domain.deep_bait_classifier.DeepBaitClassifier.classify_interaction",
        dummy_classify,
    )
    result = await analyze_transcript("u", "c", ["hi", "hello"])
    assert len(result) == 1
    assert isinstance(result[0], DummyClassification)
