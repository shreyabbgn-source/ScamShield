import os
import torch
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOCAL_MODEL = os.path.join(BASE_DIR, "bert_scam_model")
HF_MODEL = "Shreyaaaxokfr/scamshield-distilbert"

if os.path.exists(
    os.path.join(LOCAL_MODEL, "config.json")
):
    print("[BERT] Using local model")

    _tokenizer = DistilBertTokenizerFast.from_pretrained(
        LOCAL_MODEL
    )

    _model = DistilBertForSequenceClassification.from_pretrained(
        LOCAL_MODEL
    )

else:
    print("[BERT] Using Hugging Face model")

    _tokenizer = DistilBertTokenizerFast.from_pretrained(
        HF_MODEL
    )

    _model = DistilBertForSequenceClassification.from_pretrained(
        HF_MODEL
    )

_model.eval()


def bert_scam_score(text: str) -> float:
    """
    Returns probability 0.0-1.0 that text is a scam.
    Uses fine-tuned DistilBERT.
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