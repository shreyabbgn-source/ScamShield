from .scam_detector import detect_scam as pattern_detect
from .ml_classifier import ml_scam_score
from .transformer_classifier import transformer_scam_score
from .bert_classifier import bert_scam_score
from ..models.response import ScanResponse

W_PATTERN = 0.25
W_ML      = 0.25
W_BERT    = 0.35
W_TRANS   = 0.15

LEGITIMATE_SIGNALS = [
    "recipe", "calories", "protein", "ingredients", "cook", "bake",
    "workout", "exercise", "fitness", "gym", "yoga",
    "discount", "sale", "offer", "shop", "store",
    "movie", "series", "episode", "concert", "event",
    "weather", "news", "result", "exam", "admission",
    "followers", "following", "likes", "views",
    "good morning", "good night", "happy birthday",
    "travel", "trip", "vacation", "hotel", "flight",
    "ipsos", "isay", "terms & conditions apply", "terms and conditions apply",
    "get paid for your opinions",
    "cybercrime.gov.in", "cyberdost", "ministry of home affairs",
    "never disclose", "be cautious", "safe online",
    "report to your bank", "contact local police", "dial 100",
    "national cyber crime", "register a complaint", "track your complaint",
    "following tips", "always ensure", "always remember",
    "precaution", "awareness", "antivirus", "strong password", "two factor",
]

SCAM_OVERRIDE_SIGNALS = [
    "register before", "claim before", "claim your reward",
    "cutt.ly", "bit.ly", "tinyurl", "shorturl",
    "dear parent", "dear customer",
    "register now to claim", "tap to claim",
    "limited time reward", "reward expires",
    "holidays from school", "school reopen",
    "received rs", "account received",
    "claim before 9", "register before 9",
]

JOB_SCAM_KEYWORDS = [
    "typing", "data entry", "work from home", "copy paste",
    "form filling", "captcha", "part time job", "earn from home",
    "typing work", "online job",
]

def has_legitimate_signal(text: str) -> bool:
    return any(sig in text.lower() for sig in LEGITIMATE_SIGNALS)

def has_scam_override(text: str) -> bool:
    return any(sig in text.lower() for sig in SCAM_OVERRIDE_SIGNALS)


def ensemble_detect(ocr_text: str = "", caption: str = "", image_bytes: bytes = None) -> ScanResponse:
    combined_text = (ocr_text + " " + (caption or "")).strip()

    pattern_result = pattern_detect(ocr_text=ocr_text, caption=caption)
    pattern_score  = pattern_result.scam_probability
    ml_score       = ml_scam_score(combined_text)
    bert_score     = bert_scam_score(combined_text)
    trans_score, trans_category = transformer_scam_score(combined_text)

    # Cap BERT/ML only if legitimate signal AND no scam override present
    if has_legitimate_signal(combined_text) and not has_scam_override(combined_text):
        bert_score = min(bert_score, 0.55)
        ml_score   = min(ml_score, 0.55)

    # Weighted ensemble
    final_score = (
        W_PATTERN * pattern_score +
        W_ML      * ml_score +
        W_BERT    * bert_score +
        W_TRANS   * trans_score
    )

    # Boost 1 — BERT very confident + Trans not dismissing
    if bert_score >= 0.85 and trans_score >= 0.20:
        final_score = max(final_score, bert_score * 0.75)

    # Boost 2 — All layers agree
    if bert_score >= 0.75 and ml_score >= 0.65 and pattern_score >= 0.50:
        final_score = max(final_score, (bert_score + ml_score + pattern_score) / 3)

    # Boost 3 — Pattern very strong
    if pattern_score >= 0.90 and ml_score >= 0.60:
        final_score = max(final_score, 0.82)

    # Boost 4 — Scam override signals + BERT confident
    if has_scam_override(combined_text) and bert_score >= 0.70:
        final_score = max(final_score, 0.85)

    # Boost 5 — BERT extremely confident alone (≥95%) → always CRITICAL
    if bert_score >= 0.95:
        final_score = max(final_score, 0.83)

    final_score = round(min(0.98, max(0.02, final_score)), 3)

    print(f"[Ensemble] Pattern={pattern_score} | ML={ml_score} | BERT={bert_score} | Trans={trans_score} | Final={final_score}")

    # Risk level
    if final_score < 0.30:
        risk = "LOW"
    elif final_score < 0.55:
        risk = "MEDIUM"
    elif final_score < 0.82:
        risk = "HIGH"
    else:
        risk = "CRITICAL"

    # Category — never inherit "Legitimate Content" when score is high
    if trans_score > 0.65:
        category = trans_category
    elif pattern_result.category not in ["Unknown", "Legitimate Content", "unknown", ""]:
        category = pattern_result.category
    else:
        category = trans_category if trans_category and trans_category != "unknown" else "suspicious_content"

    # Secondary override — if score high but category still wrong
    if final_score >= 0.55 and category in ["Legitimate Content", "Unknown", "unknown", ""]:
        category = trans_category if trans_category and trans_category != "unknown" else "suspicious_content"

    # Job scam keyword override
    if any(kw in combined_text.lower() for kw in JOB_SCAM_KEYWORDS) and final_score >= 0.55:
        category = "job_scam"

    # Evidence list
    evidence = list(pattern_result.evidence)
    if bert_score > 0.65:
        evidence.append(f"BERT classifier: {round(bert_score * 100)}% scam probability")
    if ml_score > 0.65:
        evidence.append(f"ML classifier: {round(ml_score * 100)}% scam probability")
    if trans_score > 0.60:
        evidence.append(f"Transformer: flagged as {trans_category.replace('_', ' ')}")
    if has_scam_override(combined_text):
        evidence.append("Suspicious URL or urgent claim language detected")
    if bert_score >= 0.95:
        evidence.append("BERT extremely high confidence — likely scam")

    # Explanation
    explanation = (
        f"4-layer ensemble — "
        f"Pattern: {round(pattern_score*100)}% | "
        f"ML: {round(ml_score*100)}% | "
        f"BERT: {round(bert_score*100)}% | "
        f"Transformer: {round(trans_score*100)}% | "
        f"Final: {round(final_score*100)}%. "
        f"{pattern_result.explanation if pattern_score > 0.1 else 'AI models flagged this content — manual review recommended.'}"
    )

    # Weighted evidence
    weighted_evidence = []
    for item in evidence:
        if "BERT extremely" in item:
            weight = 95
        elif "BERT" in item:
            weight = round(bert_score * 100)
        elif "ML" in item:
            weight = round(ml_score * 100)
        elif "Transformer" in item:
            weight = round(trans_score * 100)
        elif "Suspicious URL" in item:
            weight = 80
        else:
            weight = 15
        weighted_evidence.append({
            "indicator": item,
            "weight": weight,
            "text": item,
        })

    return ScanResponse(
        risk=risk,
        scam_probability=final_score,
        threat_score=round(final_score * 100),
        content_type=pattern_result.content_type,
        category=category,
        confidence=final_score,
        evidence=evidence[:6],
        weighted_evidence=weighted_evidence,
        explanation=explanation,
    )