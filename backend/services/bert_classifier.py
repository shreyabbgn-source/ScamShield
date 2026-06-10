import os
import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
from .bert_trainer import train_bert_model, MODEL_SAVE_PATH

# Load or train on startup
if os.path.exists(os.path.join(MODEL_SAVE_PATH, "config.json")):
    print("[BERT] Loading saved model...")
    _tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_SAVE_PATH)
    _model = DistilBertForSequenceClassification.from_pretrained(MODEL_SAVE_PATH)
    print("[BERT] Model loaded.")
else:
    print("[BERT] No saved model found. Training now...")
    _model, _tokenizer = train_bert_model()

_model.eval()


def bert_scam_score(text: str) -> float:
    """
    Returns probability 0.0-1.0 that text is a scam.
    Uses fine-tuned DistilBERT — understands context not just keywords.
    """
    if not text.strip():
        return 0.5

    inputs = _tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128,
    )

    with torch.no_grad():
        outputs = _model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)
        scam_prob = probs[0][1].item()

    print(f"[BERT] Score: {round(scam_prob, 3)}")
    return round(scam_prob, 3)