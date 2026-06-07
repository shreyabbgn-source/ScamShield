from services.scam_detector import detect_scam as pattern_detect
from services.ml_classifier import ml_scam_score
from services.transformer_classifier import transformer_scam_score
from services.bert_classifier import bert_scam_score
from models.response import ScanResponse

W_PATTERN = 0.25
W_ML      = 0.25
W_BERT    = 0.35
W_TRANS   = 0.15

# Words that strongly indicate legitimate content
LEGITIMATE_SIGNALS = [
    "recipe", "calories", "protein", "ingredients", "cook", "bake",
    "workout", "exercise", "fitness", "gym", "yoga",
    "discount", "sale", "offer", "shop", "store",
    "movie", "series", "episode", "concert", "event",
    "weather", "news", "result", "exam", "admission",
    "followers", "following", "likes", "views",
    "good morning", "good night", "happy birthday",
    "travel", "trip", "vacation", "hotel", "flight","ipsos", "isay", "terms & conditions apply", "terms and conditions apply",
    "get paid for your opinions", "survey",
    # Government / awareness content
"cybercrime.gov.in",
"cyberdost",
"ministry of home affairs",
"never disclose",
"be cautious",
"safe online",
"report to your bank",
"contact local police",
"dial 100",
"national cyber crime",
"register a complaint",
"track your complaint",
"following tips",
"always ensure",
"always remember",
"precaution",
"awareness",
"antivirus",
"strong password",
"two factor",
]

def has_legitimate_signal(text: str) -> bool:
    text_lower = text.lower()
    return any(sig in text_lower for sig in LEGITIMATE_SIGNALS)


def ensemble_detect(ocr_text: str = "", caption: str = "", image_bytes: bytes = None) -> ScanResponse:
    combined_text = (ocr_text + " " + (caption or "")).strip()

    pattern_result = pattern_detect(ocr_text=ocr_text, caption=caption)
    pattern_score  = pattern_result.scam_probability
    ml_score       = ml_scam_score(combined_text)
    bert_score     = bert_scam_score(combined_text)
    trans_score, trans_category = transformer_scam_score(combined_text)

    # If strong legitimate signal exists, cap BERT and ML influence
    if has_legitimate_signal(combined_text):
        bert_score = min(bert_score, 0.55)
        ml_score   = min(ml_score, 0.55)

    # Weighted ensemble
    final_score = (
        W_PATTERN * pattern_score +
        W_ML      * ml_score +
        W_BERT    * bert_score +
        W_TRANS   * trans_score
    )

    # Single strong signal boost — BERT very confident + Trans not dismissing
    if bert_score >= 0.85 and trans_score >= 0.20:
        final_score = max(final_score, bert_score * 0.75)

    # Multi-layer boost — all layers agree
    if bert_score >= 0.75 and ml_score >= 0.65 and pattern_score >= 0.50:
        final_score = max(final_score, (bert_score + ml_score + pattern_score) / 3)

    # Critical override — pattern very strong
    if pattern_score >= 0.90 and ml_score >= 0.60:
        final_score = max(final_score, 0.82)

    final_score = round(min(0.98, max(0.02, final_score)), 3)

    print(f"[Ensemble] Pattern={pattern_score} | ML={ml_score} | BERT={bert_score} | Trans={trans_score} | Final={final_score}")

    if final_score < 0.30:
        risk = "LOW"
    elif final_score < 0.55:
        risk = "MEDIUM"
    elif final_score < 0.82:
        risk = "HIGH"
    else:
        risk = "CRITICAL"

    if trans_score > 0.65:
        category = trans_category
    elif pattern_result.category != "unknown":
        category = pattern_result.category
    else:
        category = trans_category

    evidence = list(pattern_result.evidence)
    if bert_score > 0.65:
        evidence.append(f"BERT classifier: {round(bert_score * 100)}% scam probability")
    if ml_score > 0.65:
        evidence.append(f"ML classifier: {round(ml_score * 100)}% scam probability")
    if trans_score > 0.60:
        evidence.append(f"Transformer: flagged as {trans_category.replace('_', ' ')}")

    explanation = (
    f"4-layer ensemble — "
    f"Pattern: {round(pattern_score*100)}% | "
    f"ML: {round(ml_score*100)}% | "
    f"BERT: {round(bert_score*100)}% | "
    f"Transformer: {round(trans_score*100)}% | "
    f"Final: {round(final_score*100)}%. "
    f"{pattern_result.explanation if pattern_score > 0.1 else 'AI models flagged this content — manual review recommended.'}"
)

    return ScanResponse(
        risk=risk,
        scam_probability=final_score,
        category=category,
        confidence=final_score,
        evidence=evidence[:6],
        explanation=explanation,
    )