from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from ..models.response import ScanResponse
from ..services.ocr import extract_text_from_bytes
from ..services.ensemble import ensemble_detect
from ..services.url_analyzer import analyze_urls_in_text
from ..services.image_analyzer import analyze_image_quality
from typing import Optional

router = APIRouter()

EVIDENCE_WEIGHTS = {
    "suspicious url":        35,
    "brand impersonation":   20,
    "kyc":                   20,
    "otp":                   18,
    "account block":         15,
    "urgency":               15,
    "24 ghante":             12,
    "click karein":          12,
    "guaranteed":            15,
    "double":                18,
    "no risk":               15,
    "task":                  12,
    "bert classifier":       10,
    "ml classifier":         10,
    "transformer":            8,
    "multiplier":            20,
    "hype language":         10,
}

def assign_weight(evidence_text: str) -> int:
    text_lower = evidence_text.lower()
    for keyword, weight in EVIDENCE_WEIGHTS.items():
        if keyword in text_lower:
            return weight
    return 8  # default weight

@router.post("/scan", response_model=ScanResponse)
async def scan_content(
    file: Optional[UploadFile] = File(None),
    caption: Optional[str] = Form(None),
    url: Optional[str] = Form(None),
):
    ocr_text = ""
    ocr_confidence = "N/A"
    text_visibility = "N/A"
    suspicious_urls = []
    brand_impersonation = []
    image_quality_result = None

    if file:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Only image files supported.")
        image_bytes = await file.read()

        ocr_result = extract_text_from_bytes(image_bytes)
        ocr_text            = ocr_result["text"]
        ocr_confidence      = ocr_result["ocr_confidence"]
        text_visibility     = ocr_result["text_visibility"]
        suspicious_urls     = ocr_result["suspicious_urls"]
        brand_impersonation = ocr_result["brand_impersonation"]

        image_quality_result = analyze_image_quality(image_bytes)

    if not ocr_text and not caption:
        raise HTTPException(status_code=400, detail="Send an image or caption text.")

    # Run ensemble detection
    result = ensemble_detect(ocr_text=ocr_text, caption=caption)

    # URL analysis on full text
    all_text = ocr_text + " " + (caption or "")
    url_analyses = analyze_urls_in_text(all_text)

    # Boost score for malicious URLs
    for ua in url_analyses:
        if ua["risk_score"] >= 70:
            result.scam_probability = min(0.98, result.scam_probability + 0.12)
            result.evidence.append(f"Malicious URL: {ua['domain']} (risk {ua['risk_score']}%)")
        elif ua["risk_score"] >= 45:
            result.scam_probability = min(0.98, result.scam_probability + 0.06)
            result.evidence.append(f"Suspicious URL: {ua['domain']} (risk {ua['risk_score']}%)")

    if brand_impersonation:
        result.scam_probability = min(0.98, result.scam_probability + 0.08)
        result.evidence += [f"Brand impersonation: {b}" for b in brand_impersonation[:2]]

    result.confidence = result.scam_probability

    # Re-evaluate risk after boosts
    p = result.scam_probability
    if p >= 0.85:
        result.risk = "CRITICAL"
    elif p >= 0.60:
        result.risk = "HIGH"
    elif p >= 0.30:
        result.risk = "MEDIUM"
    else:
        result.risk = "LOW"

    # Build weighted evidence
    weighted = []
    seen = set()
    for e in result.evidence:
        key = e[:30]
        if key not in seen:
            seen.add(key)
            weighted.append({"text": e, "weight": assign_weight(e)})
    weighted.sort(key=lambda x: x["weight"], reverse=True)

    # Attach all extra fields
    result.ocr_text           = ocr_text[:500] if ocr_text else ""
    result.ocr_confidence     = ocr_confidence
    result.text_visibility    = text_visibility
    result.suspicious_urls    = suspicious_urls
    result.brand_impersonation = brand_impersonation
    result.url_analysis       = [ua for ua in url_analyses]
    result.image_quality      = image_quality_result
    result.weighted_evidence  = weighted

    return result

#     from fastapi import APIRouter, UploadFile, File, Form, HTTPException
# from ..models.response import ScanResponse
# from ..services.ocr import extract_text_from_bytes
# from ..services.ensemble import ensemble_detect
# from ..services.qr_analyzer import analyze_qr
# from typing import Optional

# router = APIRouter()

# @router.post("/scan", response_model=ScanResponse)
# async def scan_content(
#     file: Optional[UploadFile] = File(None),
#     caption: Optional[str] = Form(None),
#     url: Optional[str] = Form(None),
# ):
#     ocr_text = ""
#     ocr_confidence = "N/A"
#     text_visibility = "N/A"
#     suspicious_urls = []
#     brand_impersonation = []
#     qr_analysis = None
#     image_bytes = None

#     if file:
#         if not file.content_type.startswith("image/"):
#             raise HTTPException(status_code=400, detail="Only image files supported.")
#         image_bytes = await file.read()

#         # OCR
#         ocr_result = extract_text_from_bytes(image_bytes)
#         ocr_text        = ocr_result["text"]
#         ocr_confidence  = ocr_result["ocr_confidence"]
#         text_visibility = ocr_result["text_visibility"]
#         suspicious_urls = ocr_result["suspicious_urls"]
#         brand_impersonation = ocr_result["brand_impersonation"]

#         # QR Code Analysis
#         qr_analysis = analyze_qr(image_bytes)
#         print(f"[QR] Found: {qr_analysis['qr_found']} | Risk: {qr_analysis['highest_risk']}")

#     if not ocr_text and not caption:
#         raise HTTPException(status_code=400, detail="Send an image or caption text.")

#     result = ensemble_detect(ocr_text=ocr_text, caption=caption)

#     # Inject extra fields
#     result.ocr_text           = ocr_text[:300] if ocr_text else ""
#     result.ocr_confidence     = ocr_confidence
#     result.text_visibility    = text_visibility
#     result.suspicious_urls    = suspicious_urls
#     result.brand_impersonation = brand_impersonation
#     result.qr_analysis        = qr_analysis

#     # Boost score if QR is suspicious
#     if qr_analysis and qr_analysis["qr_found"]:
#         qr_risk = qr_analysis["highest_risk"]
#         if qr_risk >= 70:
#             result.scam_probability = min(0.98, result.scam_probability + 0.20)
#             result.risk = "CRITICAL"
#             result.evidence.append(f"QR Code: {qr_analysis['summary']}")
#         elif qr_risk >= 40:
#             result.scam_probability = min(0.98, result.scam_probability + 0.10)
#             result.evidence.append(f"QR Code: suspicious destination detected")
#             if result.risk == "LOW":
#                 result.risk = "MEDIUM"

#     # Boost score for suspicious URLs or brand impersonation from OCR
#     if suspicious_urls or brand_impersonation:
#         result.scam_probability = min(0.98, result.scam_probability + 0.10)
#         result.confidence = result.scam_probability
#         if result.risk == "MEDIUM":
#             result.risk = "HIGH"
#         result.evidence += [f"Suspicious URL: {u}" for u in suspicious_urls[:2]]
#         result.evidence += [f"Brand impersonation: {b}" for b in brand_impersonation[:2]]

#     result.confidence = result.scam_probability
#     return result