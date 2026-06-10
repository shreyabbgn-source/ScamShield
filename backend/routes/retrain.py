from fastapi import APIRouter
from ..services.feedback_store import get_incorrect_samples
from ..services.bert_trainer import TRAINING_DATA, train_bert_model
import os, shutil

router = APIRouter()

@router.post("/retrain")
async def retrain_model():
    incorrect = get_incorrect_samples()
    if len(incorrect) < 3:
        return {"status": "skipped", "message": f"Only {len(incorrect)} incorrect samples — need at least 3 to retrain"}

    CATEGORIES = ["banking_scam", "investment_scam", "phishing_scam", "job_scam", "lottery_scam", "task_scam"]
    new_samples = []
    for text, category in incorrect:
        label = 1 if category in CATEGORIES else 0
        new_samples.append((text, label))

    combined = TRAINING_DATA + new_samples

    model_path = "services/bert_scam_model"
    if os.path.exists(model_path):
        shutil.rmtree(model_path)

    train_bert_model(combined)

    return {
        "status": "retrained",
        "new_samples_added": len(new_samples),
        "total_training_samples": len(combined),
    }