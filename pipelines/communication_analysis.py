"""
Application layer orchestrator for communication analysis.

This module adapts raw transcript data into domain-level classification
using the DeepBaitClassifier, producing bait vs genuine analysis results.
"""
import asyncio
from typing import List, Dict, Any

from domain.deep_bait_classifier import DeepBaitClassifier, BaitClassification

# Singleton classifier instance reused across calls
_classifier = DeepBaitClassifier()

async def analyze_transcript(
    user_id: str,
    character_id: str,
    transcript: List[str],
    context: Dict[str, Any] = None,
) -> List[BaitClassification]:
    """
    Analyze a sequence of transcript messages for bait vs authentic interaction.

    Args:
        user_id: Identifier for the user or caller.
        character_id: Identifier for the character/session.
        transcript: List of message texts in chronological order.
        context: Optional additional context for the classifier.

    Returns:
        List of BaitClassification results, one per transcript segment.
    """
    results: List[BaitClassification] = []
    # Convert raw strings into minimal message dicts
    messages = [{"text": msg} for msg in transcript]
    # Classify the full interaction in batch
    classification = await _classifier.classify_interaction(
        user_id=user_id,
        character_id=character_id,
        messages=messages,
        context=context,
    )
    results.append(classification)
    return results
