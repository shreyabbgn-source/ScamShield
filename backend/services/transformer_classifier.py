from transformers import pipeline
import torch

print("[Transformer] Loading classifier...")

_classifier = pipeline(
    "zero-shot-classification",
    model="cross-encoder/nli-MiniLM2-L6-H768",
    device=0 if torch.cuda.is_available() else -1,
)

print("[Transformer] Ready.")

SCAM_LABELS = [
    "investment fraud",
    "financial scam",
    "job scam",
    "lottery scam",
    "phishing attack",
    "legitimate content",
    "genuine offer",
]

def transformer_scam_score(text: str) -> tuple:
    if not text.strip():
        return 0.5, "unknown"

    result = _classifier(
        text[:512],
        candidate_labels=SCAM_LABELS,
        hypothesis_template="This text is about {}.",
    )

    scores = dict(zip(result["labels"], result["scores"]))
    legitimate_score = scores.get("legitimate content", 0) + scores.get("genuine offer", 0)
    scam_score = 1.0 - legitimate_score

    scam_categories = {k: v for k, v in scores.items()
                       if k not in ["legitimate content", "genuine offer"]}
    top_category = max(scam_categories, key=scam_categories.get)

    category_map = {
        "investment fraud": "investment_scam",
        "financial scam":   "investment_scam",
        "job scam":         "job_scam",
        "lottery scam":     "lottery_scam",
        "phishing attack":  "phishing_scam",
    }

    mapped_category = category_map.get(top_category, "unknown_scam")
    print(f"[Transformer] Score: {round(scam_score, 3)} | Category: {mapped_category}")
    return round(scam_score, 3), mapped_category