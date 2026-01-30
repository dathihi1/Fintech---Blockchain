"""
NLP API endpoints
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

from nlp import get_nlp_engine, VIETNAMESE_TRADING_KEYWORDS, ENGLISH_TRADING_KEYWORDS

router = APIRouter(prefix="/nlp", tags=["NLP"])


# ============ Request/Response Schemas ============

class AnalyzeRequest(BaseModel):
    """Request schema for text analysis"""
    text: str


class EmotionResponse(BaseModel):
    """Detected emotion"""
    type: str
    confidence: float
    matched_keywords: List[str]
    weight: float


class AnalyzeResponse(BaseModel):
    """Response schema for NLP analysis"""
    text: str
    language: str
    sentiment_score: float
    sentiment_label: str
    emotions: List[EmotionResponse]
    behavioral_flags: List[str]
    quality_score: float
    warnings: List[str]


class AnalyzeBatchRequest(BaseModel):
    """Request schema for batch analysis"""
    texts: List[str]


class KeywordsResponse(BaseModel):
    """Response schema for keywords"""
    vi: dict
    en: dict


# ============ Endpoints ============

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(request: AnalyzeRequest):
    """
    Analyze trading note text using NLP.
    
    Returns:
    - Sentiment score (-1 to 1) and label
    - Detected emotions (FOMO, FEAR, GREED, REVENGE, RATIONAL, etc.)
    - Quality score (0 to 1) - how rational is the reasoning
    - Behavioral flags and warnings
    """
    nlp_engine = get_nlp_engine()
    result = nlp_engine.analyze(request.text)
    
    return AnalyzeResponse(
        text=result.text,
        language=result.language,
        sentiment_score=result.sentiment_score,
        sentiment_label=result.sentiment_label,
        emotions=[
            EmotionResponse(
                type=e.type,
                confidence=e.confidence,
                matched_keywords=e.matched_keywords,
                weight=e.weight
            )
            for e in result.emotions
        ],
        behavioral_flags=result.behavioral_flags,
        quality_score=result.quality_score,
        warnings=result.warnings
    )


@router.post("/analyze-batch", response_model=List[AnalyzeResponse])
async def analyze_batch(request: AnalyzeBatchRequest):
    """
    Analyze multiple trading notes in batch.
    Useful for analyzing historical notes.
    """
    nlp_engine = get_nlp_engine()
    results = []
    
    for text in request.texts:
        result = nlp_engine.analyze(text)
        results.append(AnalyzeResponse(
            text=result.text,
            language=result.language,
            sentiment_score=result.sentiment_score,
            sentiment_label=result.sentiment_label,
            emotions=[
                EmotionResponse(
                    type=e.type,
                    confidence=e.confidence,
                    matched_keywords=e.matched_keywords,
                    weight=e.weight
                )
                for e in result.emotions
            ],
            behavioral_flags=result.behavioral_flags,
            quality_score=result.quality_score,
            warnings=result.warnings
        ))
    
    return results


@router.get("/keywords", response_model=KeywordsResponse)
async def get_keywords():
    """
    Get the keyword dictionaries used for emotion detection.
    Useful for understanding how the system detects emotions.
    """
    return KeywordsResponse(
        vi=VIETNAMESE_TRADING_KEYWORDS,
        en=ENGLISH_TRADING_KEYWORDS
    )


@router.get("/emotions")
async def get_emotion_types():
    """
    Get list of emotion types that can be detected.
    """
    return {
        "negative_emotions": [
            {"type": "FOMO", "description": "Fear of Missing Out - Sợ bỏ lỡ cơ hội"},
            {"type": "FEAR", "description": "Fear - Sợ hãi, lo lắng"},
            {"type": "GREED", "description": "Greed - Tham lam"},
            {"type": "REVENGE", "description": "Revenge Trading - Gỡ gạc, trả thù thị trường"},
            {"type": "OVERCONFIDENCE", "description": "Overconfidence - Quá tự tin"}
        ],
        "positive_emotions": [
            {"type": "RATIONAL", "description": "Rational - Lý trí, có kế hoạch"},
            {"type": "CONFIDENT", "description": "Confident - Tự tin có căn cứ"},
            {"type": "DISCIPLINE", "description": "Discipline - Kỷ luật"}
        ]
    }
