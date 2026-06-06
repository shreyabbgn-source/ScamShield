import csv
import os
from datetime import datetime

FEEDBACK_FILE = "feedback_data.csv"
FIELDNAMES = ["timestamp", "text", "predicted_category", "predicted_risk", "scam_probability", "is_correct", "correct_category"]

def init_feedback_file():
    if not os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()

def save_feedback(text: str, predicted_category: str, predicted_risk: str, scam_probability: float, is_correct: bool, correct_category: str = None):
    init_feedback_file()
    with open(FEEDBACK_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow({
            "timestamp": datetime.now().isoformat(),
            "text": text[:500],
            "predicted_category": predicted_category,
            "predicted_risk": predicted_risk,
            "scam_probability": round(scam_probability, 3),
            "is_correct": is_correct,
            "correct_category": correct_category or predicted_category,
        })

def get_feedback_stats():
    init_feedback_file()
    rows = []
    with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    total = len(rows)
    correct = sum(1 for r in rows if r["is_correct"] == "True")
    incorrect = total - correct
    accuracy = round((correct / total) * 100, 1) if total > 0 else 0

    category_errors = {}
    for r in rows:
        if r["is_correct"] == "False":
            key = f"{r['predicted_category']} → {r['correct_category']}"
            category_errors[key] = category_errors.get(key, 0) + 1

    return {
        "total_reviews": total,
        "correct": correct,
        "incorrect": incorrect,
        "accuracy": accuracy,
        "top_errors": sorted(category_errors.items(), key=lambda x: x[1], reverse=True)[:5],
        "recent": rows[-5:][::-1],
    }

def get_incorrect_samples():
    init_feedback_file()
    samples = []
    with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["is_correct"] == "False" and row["text"].strip():
                samples.append((row["text"], row["correct_category"]))
    return samples