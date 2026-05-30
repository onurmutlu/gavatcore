"""
Communication analysis endpoint.

Exposes an API to analyze transcripts via the DeepBaitClassifier orchestrator.
"""
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from pipelines.communication_analysis import analyze_transcript
from dataclasses import asdict

router = APIRouter()


class CommunicationAnalysisRequest(BaseModel):
    user_id: str = Field(..., description="Identifier for the user or caller")
    character_id: str = Field(..., description="Identifier for the character/session")
    transcript: List[str] = Field(..., description="Chronological list of message texts")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional context payload")


class CommunicationAnalysisResponse(BaseModel):
    analysis: List[Dict[str, Any]]


def _serialize_classification(result) -> Dict[str, Any]:
    data = asdict(result)
    # Convert enums and datetime
    if hasattr(result, 'interaction_type'):
        data['interaction_type'] = result.interaction_type.value
    if hasattr(result, 'authenticity_level'):
        data['authenticity_level'] = result.authenticity_level.value
    if hasattr(result, 'timestamp') and hasattr(result.timestamp, 'isoformat'):
        data['timestamp'] = result.timestamp.isoformat()
    return data


@router.post(
    "/communication",
    response_model=CommunicationAnalysisResponse,
    summary="Analyze transcript for bait vs genuine interaction",
)
async def post_communication_analysis(
    body: CommunicationAnalysisRequest,
) -> CommunicationAnalysisResponse:
    try:
        raw_results = await analyze_transcript(
            user_id=body.user_id,
            character_id=body.character_id,
            transcript=body.transcript,
            context=body.context,
        )
        serialized = [_serialize_classification(r) for r in raw_results]
        return CommunicationAnalysisResponse(analysis=serialized)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
