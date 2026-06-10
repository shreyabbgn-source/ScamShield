from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from ..services.feedback_store import save_feedback, get_feedback_stats

router = APIRouter()

class FeedbackRequest(BaseModel):
    text: str
    predicted_category: str
    predicted_risk: str
    scam_probability: float
    is_correct: bool
    correct_category: Optional[str] = None

@router.post("/feedback")
async def submit_feedback(req: FeedbackRequest):
    save_feedback(
        text=req.text,
        predicted_category=req.predicted_category,
        predicted_risk=req.predicted_risk,
        scam_probability=req.scam_probability,
        is_correct=req.is_correct,
        correct_category=req.correct_category,
    )
    return {"status": "saved", "message": "Thank you for the feedback!"}

@router.get("/feedback/stats")
async def feedback_stats():
    return get_feedback_stats()