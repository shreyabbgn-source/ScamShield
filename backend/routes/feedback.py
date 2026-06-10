from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from ..services.feedback_store import save_feedback, get_feedback_stats

router = APIRouter()

class FeedbackRequest(BaseModel):
    feedback: str              # 'correct' | 'incorrect'
    comment: str = ""
    predicted_risk: str
    predicted_category: str
    scam_probability: float
    caption: str = ""
    ocr_text: str = ""

@router.post("/feedback")
async def submit_feedback(req: FeedbackRequest):
    text = (req.caption + " " + req.ocr_text).strip()
    save_feedback(
        text=text,
        predicted_category=req.predicted_category,
        predicted_risk=req.predicted_risk,
        scam_probability=req.scam_probability,
        is_correct=req.feedback == "correct",
        correct_category=req.comment if req.comment.strip() else None,
    )
    return {"status": "saved"}