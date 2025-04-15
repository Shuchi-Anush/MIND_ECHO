"""
Example Router for MIND_ECHO API
Defines an endpoint to analyze sentiment from user-provided text and return an empathetic response.
"""

from fastapi import APIRouter, HTTPException
from backend.models.schemas import SentimentRequest
from backend.services import sentiment_engine

router = APIRouter(tags=["Sentiment Analysis"])

@router.post("/analyze", summary="Analyze Sentiment and Provide Empathetic Response")
def sentiment_endpoint(request: SentimentRequest):
    try:
        result = sentiment_engine.process_sentiment(request.text)
        if result["sentiment"]["label"] == "Positive":
            empathetic_message = "It's great to see positivity! Keep nurturing your happy moments."
        elif result["sentiment"]["label"] == "Negative":
            empathetic_message = "I understand you're going through a tough time. It's okay to feel this way."
        else:
            empathetic_message = "It seems you're in a balanced state. Take care of yourself."
        return {"sentiment": result["sentiment"], "empathetic_response": empathetic_message}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))